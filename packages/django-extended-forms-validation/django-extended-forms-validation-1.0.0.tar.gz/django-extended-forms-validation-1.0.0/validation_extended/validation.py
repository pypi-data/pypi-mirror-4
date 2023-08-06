import re
import inspect

from django.core.validators import ValidationError
from django.forms import IntegerField, FloatField


def can_return_none(func):
    ''' Use this decorator when you want to modify cleaned value and this value can be None '''
    def inner(self, *args, **kwargs):
        self._can_return_none = True
        return func(*args, **kwargs)
    return inner


class Validator(object):
    '''
    All validators must be inherited from this class (and stored in validators.py module)
    Validator must have validate method, which accept three arguments: self, field_name, data
    Last argument accepts cleaned_data[field_name] value or cleaned_data dict depending on validator
    assigment in AutoValidated-designed form.
    For example cleaned_data dict passed if validator assigned in RequiresAll sublass

    Class atributes (actually in ClienValidated-designed form):
    "client_events" - a set of events which defines when field validation will be triggered.
    It could be tuple, list or string where events separated by space.

    "message" - error message that retrieved to client automatically as
    $(form).data().validation_data[field_name].message
    Also stored in $(field).data("rule_%rulename").message if field exist on assignment
    It is strongly recommended to use {0}-like params in formatted message instead of %s-like
    Also message stored in $(field).data().message

    "data" - any struct that retrivied to client as $(form).data().validation_data[field_name].data
    Also stored in $(field).data("rule_%rulename").data if field exist on assignment
    There is useful for porting validator to javascript. Some data structures could be stored in
    data attribute and used in python and in javascript without repeating code.

    Also validator class could have js_rules method (accepts only self argument).
    If it's empty it means that cleint field will require self-defined custom js rule with
    validator class name. Otherwise it must return dict (or list of dicts) with keys:
    "rule" - basic js-rule ('regex' for example)
    "params" (optional) - additional rule params (regex pattern for example)
    IMPORTANT: if rule is 'remote' then params is a list of fields, which must be retrieving to
    server ('*' string means all fields)

    Usage:
    class SimpleValidator(Validator):
        message = "simple validator error"
        client_events = "focusout keyup"
        data = {'values': [1, 2, 3]}

        def js_rules(self):
            pass

        def validated(self, field_name, data):
            if not data in self.data['values']:
                self.raise_error()

    Each validator can return modified value. But only the last value which is not None stored in
    cleaned_data. So if you want to modify value in validator you shold pass this validator last.
    Also if you want to return None you should decorate validate method by @can_returns_none
    In this case you should always return something because omitted return really returns None
    and this value will be stored in cleaned_data
    Validators that requires all data also can returns modified value, but they modify
    cleaned_data[field_name] instead of whole cleaned_data dict
    '''

    _can_return_none = False
    client_events = ('focusout', )

    def __init__(self, *args, **kwargs):
        # to provide compability
        pass

    def __call__(self, *args, **kwargs):
        return self.validate(*args, **kwargs)

    def raise_error(self, message=''):
        raise ValidationError(message or self.message)


class ClientValidated(object):
    '''
    ClientValidated mixin is designed for easy defining javascript validation of client
    All operations executes automatically, so just mix this class to form
    It is strongly recomended to use with AutoValidated mixin

    Usage:

    class SomeForm(AutoValidated, ClientValidated, django.forms.Form):
        ...
    '''

    def _check_basic_rules(self, fieldname):
        rules = []
        field = self.fields[fieldname]

        if field.required:
            rules.append({'rule': 'required', 'msg': self._get_message(field, 'required')})

        if isinstance(field, FloatField):
            rules.append({
                'rule': 'number',
                'events': 'keyup',
                'msg': unicode(FloatField.default_error_messages['invalid'])})
        elif isinstance(field, IntegerField):
            rules.append({
                'rule': 'digits',
                'events': 'keyup',
                'msg': unicode(IntegerField.default_error_messages['invalid'])})
        return rules

    def _get_EmailValidator_rule(self, fieldname):
        return {'rule': 'email', 'msg': self._get_message(self.fields[fieldname])}

    def _get_URLValidator_rule(self, fieldname):
        return {'rule': 'url', 'msg': self._get_message(self.fields[fieldname])}

    def _get_MaxLengthValidator_rule(self, fieldname):
        pass

    @staticmethod
    def _get_message(field, error='invalid'):
        return unicode(field.error_messages[error])

    @staticmethod
    def _get_validator_rules(name, validator):
        rules = validator.js_rules() or {'rule': name}
        if rules['rule'] == 'remote':
            rules['name'] = name
        if not 'msg' in rules and hasattr(validator, 'message'):
            rules['msg'] = validator.message
        if hasattr(validator, 'client_events'):
            events = validator.client_events
            if isinstance(events, (list, tuple)):
                rules['events'] = ' '.join(events)
            else:
                rules['events'] = events
        if hasattr(validator, 'data'):
            rules['validator_data'] = validator.data
        return rules

    def make_rules(self):
        form_rules = {}
        vmf_validators = self._get_validators_map() if hasattr(self, '_get_validators_map') else {}

        for fieldname, field in self.fields.items():
            field_rules = []
            field_rules.extend(self._check_basic_rules(fieldname))
            validators = field.validators + vmf_validators.get(fieldname, [])

            for validator in validators:
                is_class = inspect.isclass(validator)
                is_validator_cls = Validator in getattr(validator, '__mro__', [])

                validator_name = validator.__name__ if is_class else validator.__class__.__name__
                method_name = '_get_%s_rule' % validator_name
                if is_validator_cls:
                    validator = validator()

                if hasattr(self, method_name):
                    validator_rules = getattr(self, method_name)(fieldname)
                elif isinstance(validator, Validator) and hasattr(validator, 'js_rules'):
                    validator_rules = self._get_validator_rules(validator_name, validator)

                if validator_rules:
                    if not isinstance(validator_rules, (list, tuple)):
                        validator_rules = [validator_rules]
                    field_rules.extend(validator_rules)

            if field_rules:
                for rule in field_rules:
                    if not 'events' in rule:
                        rule['events'] = 'focusout'
                form_rules[fieldname] = field_rules
        return form_rules


class AutoValidated(object):
    '''
    AutoValidated mixin is designed for easy defining of form validators
    It overrides clean-method to use them.

    It's still possible to define self clean-methods. In this case it will be
    called after all validators have finished the work.
    If result of own clean-method is None or nothing is returned -
    cleaned_data will be returned.

    Nested class RequiresAll designed for overriding clean method.

    Usage:

    # IMPORTANT: AutoValidated must be defined first !!!
    class SomeForm(AutoValidated, django.forms.ModelForm):  # or django.forms.Form as base class
        class Meta:
            model = SomeModel

        class Validators:
            class RequiresAll:
                foo = [foo_validator]
            bar = [bar_validator]
            baz = [baz_validator(5)]
    '''

    def __init__(self, *args, **kwargs):
        # overriding clean methods
        if hasattr(self, 'Validators'):
            for field_name in self.Validators.__dict__.keys():
                if not field_name.startswith('__'):
                    if field_name == 'RequiresAll':
                        method_name = 'clean'
                    else:
                        method_name = 'clean_%s' % str(field_name)
                    if not hasattr(self, method_name):
                        method = lambda x = self: None
                        method.__name__ = method_name
                        method._fake = True
                    else:
                        method = getattr(self, method_name)
                    setattr(self, method_name, self._get_clean_method(method))

        # call ModelForm __init__ method
        super(AutoValidated, self).__init__(*args, **kwargs)

    def _get_validators_map(self):
        result = {}

        def extend_map(source):
            for field_name, validators_list in source.__dict__.items():
                if not field_name.startswith('__') and not field_name == 'RequiresAll':
                    if not field_name in result:
                        result[field_name] = []
                    result[field_name].extend(validators_list)

        if hasattr(self, 'Validators'):
            extend_map(self.Validators)
            if hasattr(self.Validators, 'RequiresAll'):
                extend_map(self.Validators.RequiresAll)
        return result

    @staticmethod
    def _get_validator(validator):
        return validator() if Validator in getattr(validator, '__mro__', []) else validator

    def _get_clean_method(self, method):
        def wrapper(self=self):
            if method.__name__ == 'clean':
                cleaned_data = result = self.cleaned_data.copy()
                if hasattr(self, 'Validators') and hasattr(self.Validators, 'RequiresAll'):
                    for field_name, validators_list in self.Validators.RequiresAll.__dict__.items():
                        if not field_name.startswith('__'):
                            for v in validators_list:
                                validator = self._get_validator(v)
                                validator_res = validator(field_name, cleaned_data)
                                if validator_res is not None or validator._can_return_none:
                                    result[field_name] = validator_res
            else:
                field_name = re.sub('clean_', '', method.__name__)
                field_data = self.cleaned_data[field_name]

                # call basically validators
                result = field_data
                if hasattr(self, 'Validators'):
                    for v in getattr(self.Validators, field_name):
                        validator = self._get_validator(v)
                        validator_res = validator(field_name, field_data)
                        if validator_res is not None or validator._can_return_none:
                            result = validator_res

            # call method if it contains extra validation
            if not getattr(method, '_fake', False):
                return method()

            # return field data if no raises were
            return result
        return wrapper

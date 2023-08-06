import importlib
from django.core.validators import ValidationError
from django.http import HttpResponse
from django.utils import simplejson as json

from .utils import get_all_validators
VALIDATORS_LIST = get_all_validators()


def remote_validation(request):
    data = request.POST.copy()
    validator_name = data.get('_validator')
    field_name = data.get('_field')
    form_cls = None
    if '_form[]' in data:
        form_cls_list = data.getlist('_form[]')
        form_cls = getattr(importlib.import_module(form_cls_list[0]), form_cls_list[1])
        del data['_form[]']
    del data['_field']
    del data['_validator']

    result = True
    validator = VALIDATORS_LIST.get(validator_name, None)
    if validator:
        try:
            validator()(field_name, data[field_name] if len(data) == 1 else data, form_cls)
        except ValidationError, error:
            result = error.messages[0]
    return HttpResponse(json.dumps(result), mimetype='application/json')

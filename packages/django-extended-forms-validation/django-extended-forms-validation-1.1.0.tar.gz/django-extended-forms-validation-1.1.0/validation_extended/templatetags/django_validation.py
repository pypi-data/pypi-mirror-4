import json

from django.template import Library

from ..validation import ClientValidated


register = Library()


@register.simple_tag
def validate_form(form, form_selector, **kwargs):
    if isinstance(form, ClientValidated):
        rules = form.make_rules()
        rules['settings'].update(kwargs)
        opts = '{formSelector: "%s", rules: %s, settings: %s})}' % (
            form_selector, json.dumps(rules['rules']), json.dumps(rules['settings']))
        return '<script>$(function(){$("%s").validateForm(%s)</script>' % (form_selector, opts)

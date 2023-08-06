import json

from django.template import Library
from django.conf import settings

from ..validation import ClientValidated


register = Library()


@register.simple_tag
def validate_form(form, form_selector, **kwargs):
    if isinstance(form, ClientValidated):
        rules = form.make_rules()
        kwargs['debug'] = settings.DEBUG
        return '<script>$(function(){$("%s").validateForm({rules: %s, settings: %s})})</script>' % (
            form_selector, json.dumps(rules), json.dumps(kwargs))

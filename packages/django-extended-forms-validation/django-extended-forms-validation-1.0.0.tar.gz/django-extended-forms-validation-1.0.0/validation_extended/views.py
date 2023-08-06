from django.core.validators import ValidationError
from django.http import HttpResponse
from django.utils import simplejson as json

from .utils import get_all_validators
VALIDATORS_LIST = get_all_validators()


def remote_validation(request):
    data = request.POST.copy()
    validator_name = data['__validator__']
    field_name = data['__field__']
    del data['__validator__']
    del data['__field__']

    result = True
    validator = VALIDATORS_LIST.get(validator_name, None)
    if validator:
        try:
            validator()(field_name, data[field_name] if len(data) == 1 else data)
        except ValidationError, error:
            result = error.messages[0]
    return HttpResponse(json.dumps(result), mimetype='application/json')

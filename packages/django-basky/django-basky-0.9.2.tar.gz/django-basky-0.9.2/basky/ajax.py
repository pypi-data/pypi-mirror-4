import json
from django.http import HttpResponse


def error_dict(errors, error_dict=None):
    """returns a dicts of errors for a Django form"""
    if error_dict is None:
        error_dict = {'success': 'false', 'errors': []}
    for k, v in errors.items():
        try:
            error_dict['errors'].append((k, v[0].__unicode__()))
        except AttributeError:
            error_dict['errors'].append((k, v[0]))
    return error_dict

def json_response(response_dict):
    return HttpResponse(
        json.dumps(response_dict, sort_keys=True, indent=2),
        content_type='application/json; charset=UTF-8')

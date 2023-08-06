# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils import simplejson
from inoa.utils.json import ExtendedJSONEncoder

class HttpResponseNoContent(HttpResponse):
    """
    HTTP response for a success request.
    """
    status_code = 204

def JsonResponse(data, json_cls=None, response_cls=None):
    """
    Returns an HttpResponse with JSON content type. Converts the data parameter to JSON automatically.
    Accepts two optional parameters.
    - json_cls: a subclass of simplejson.JSONEncoder
    - response_cls: a subclass of django.http.HttpResponse
    """
    json_cls = json_cls or ExtendedJSONEncoder
    response_cls = response_cls or HttpResponse
    return response_cls(simplejson.dumps(data, cls=json_cls), mimetype="application/json")

"""

    routrschema -- common guards to validate request
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

try:
    import simplejson as json
except ImportError:
    import json
import re

from webob.exc import HTTPBadRequest
from schemify import validate, ValidationError
from schemify import opt, anything

__all__ = ('RequestParams', 'qs', 'form', 'json_body',
           'ValidationError', 'opt', 'anything')

class RequestParams(object):
    """ Base class for dict-like structure validation"""

    def __init__(self, *schema, **fields):
        if schema:
            self.schema = schema[0]
        else:
            self.schema = fields

    def params(self, request):
        raise NotImplementedError()

    def update_trace(self, trace, result):
        trace.kwargs.update(result)

    def __call__(self, request, trace):
        params = self.params(request)
        try:
            result = validate(self.schema, params)
        except ValidationError as e:
            raise HTTPBadRequest(e.error)
        else:
            self.update_trace(trace, result)
        return trace

class qs(RequestParams):
    """ Guard for GET parameters"""

    def params(self, request):
        return request.GET

class form(RequestParams):
    """ Guard for POST parameters"""

    def params(self, request):
        return request.POST

class json_body(RequestParams):
    """ Guard for JSON body"""

    is_application_json = re.compile(r'application/([^\+]+\+)?json').match

    def params(self, request):
        if not self.is_application_json(request.content_type):
            raise HTTPBadRequest("only 'application/json' requests are allowed")
        return json.loads(request.body)

    def update_trace(self, trace, result):
        trace.args = trace.args + (result,)

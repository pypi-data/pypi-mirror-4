"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

=========
JRPC-utils
=========

JRPC-utils provides a set of useful classes that help you work with JSON-RPC v.2.0.

http://json-rpc.org/

Author:
    Andrey Kaygorodov, see for more info http://github.com/kaygorodov

"""

import json
import inspect

JSONRPC_VERSION = "2.0"

PARSE_ERROR_CODE = -32700
INVALID_REQUEST_CODE = -32600
METHOD_NOT_FOUND_CODE = -32601
INVALID_PARAMS_CODE = 32602
INTERNAL_ERROR_CODE = 32603
SERVER_ERROR_CODE = -32000


class JsonRpcException(Exception):
    """
    Common base class for all json rpc exceptions.
    """
    def __init__(self, message=None):
        if message is not None:
            self.message = message


class ParseError(JsonRpcException):
    """
    ParseError. Invalid JSON was received by the server. An error occurred on the server while parsing the JSON text.
    """
    code = PARSE_ERROR_CODE
    message = 'ParseError'


class InvalidRequest(JsonRpcException):
    """
    Invalid Request. The JSON sent is not a valid Request object.
    """
    code = INVALID_REQUEST_CODE
    message = 'Invalid Request'


class MethodNotFound(JsonRpcException):
    """
    Method not found. The method does not exist / is not available.
    """
    code = METHOD_NOT_FOUND_CODE
    message = 'Method not found'


class InvalidParams(JsonRpcException):
    """
    Invalid method parameter(s).
    """
    code = INVALID_PARAMS_CODE
    message = 'Invalid params'


class InternalError(JsonRpcException):
    """
    Internal JSON-RPC error.
    """
    code = INTERNAL_ERROR_CODE
    message = 'JSON-RPC Internal Error'


class ServerError(JsonRpcException):
    """
    Code: - 32000 to - 32099    Server error    Reserved for implementation - defined server - errors.
    For example:

    class MyFirstServerError(ServerError):
        CODE = -32789

    class MySecondServerError(ServerError):
        CODE = -32789
    """
    code = SERVER_ERROR_CODE
    message = 'Server error'


class JsonRpcRequest(object):
    """
    JSON RPC Request
    """
    version = None
    method = None
    params = None
    id = None

    def __init__(self, raw_request):
        """
        This method forms a JsonRpcRequest object (self) from json formatted string.
        """
        try:
            data = json.loads(raw_request)
        except ValueError:
            raise ParseError()

        if not isinstance(data, dict):
            raise InvalidRequest("Invalid request format.")

        request_id = data.get("id")
        if request_id is None:
            raise InvalidRequest("The id must be specified.")

        if not isinstance(request_id, int):
            raise InvalidRequest("The id must be integer.")

        self.id = request_id

        version = data.get("jsonrpc")

        if version != JSONRPC_VERSION:
            raise InvalidRequest("The version must be specified.")
        self.version = JSONRPC_VERSION

        method = data.get("method")
        if method is None:
            raise InvalidRequest("The method must be specified.")
        if not isinstance(method, (str, unicode,)):
            raise InvalidRequest("The method must be string.")
        if method == "":
            raise InvalidRequest("The method must not be an empty string.")

        self.method = method

        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list,)):
            raise InvalidRequest("Invalid params format.")

        self.params = params

    def get_json_representation(self, without_serialization=False):
        request = {
           "jsonrpc": self.version,
           "method": self.method,
           "params": self.params,
           "id": self.id,
        }

        if without_serialization:
            return request

        return json.dumps(request)

    def __unicode__(self):
        return self.get_json_representation()

    def __str__(self):
        return self.get_json_representation()


class JsonRpcResponse(object):
    """
    Json Rpc Response
    """
    id = None
    error_code = None
    error_message = None
    result = None

    def __init__(self, result=None, request_id=None, error_code=None, error_message=None):
        if result is None and error_code is None:
            raise Exception("You must specify result or error_code.")

        self.id = request_id
        self.error_code = error_code
        self.error_message = error_message
        self.result = result

    def get_json_representation(self, without_serialization=False):
        response = {
            "jsonrpc": JSONRPC_VERSION,
            "id": self.id,
        }

        if self.error_code is None:
            response.update({
                "result": self.result,
            })
        else:
            response.update({
                "error": {
                    "code": self.error_code,
                    "message": self.error_message
                },
            })

        if without_serialization:
            return response

        return json.dumps(response)

    def __unicode__(self):
        return self.get_json_representation()

    def __str__(self):
        return self.get_json_representation()


def get_id(raw_request):
    """
    This function tries to get id from raw_request.
    """
    try:
        data = json.loads(raw_request)
    except ValueError:
        return None

    request_id = data.get("id")
    if not isinstance(request_id, int):
        return None
    return request_id


route_paths = dict()


def resolver(method):
    try:
        func_or_class = route_paths[method]
    except KeyError:
        raise MethodNotFound()
    else:
        return func_or_class


def procedure(path):
    def wrap_func(f):
        route_paths[path] = f
        return f
    return wrap_func


class Param(object):
    validators = []  # a list of validators that the param value will be passed through

    def __init__(self, required=True, validators=[]):
        self.required = required
        self.validators.extend(validators)

    def to_python(self, value):
        """
        Overriding this functions you can add some extra transformation
        for param's value before the value will be assign to the corresponding Procedure class's field.
        """
        return value

    def validate(self, name, value):
        for validator in self.validators:
            validator(name, value)


class AutoDiscoverProcedure(type):
    """
    This metaclass adds a routing rule (method -> class) every time Procedure's subclass creates.
    """
    def __new__(mcs, name, bases, dict):
        new_class = type.__new__(mcs, name, bases, dict)

        if 'Meta' not in dict:
            raise Exception('You must specify inner class Meta for class {}'.format(name))

        meta = dict['Meta']
        if not meta.__dict__.get('abstract'):
            if 'method' not in meta.__dict__:
                raise Exception('You must specify method\'s name for class {} in inner class Meta'.format(name))

            route_paths[meta.__dict__['method']] = new_class

        return new_class


class JsonRpcProcedure(object):
    __metaclass__ = AutoDiscoverProcedure

    def handle(self, params):
        self.build_params(params)
        return self.proceed()

    def build_params(self, params):
        for field in self.__class__.__dict__:
            if isinstance(self.__class__.__dict__[field], Param):
                param = self.__class__.__dict__[field]

                if param.required and field not in params:
                    raise InvalidParams('There is not a required param {} in the request'.format(field))
                elif not param.required and field not in params:
                    setattr(self, field, None)
                else:
                    value = param.to_python(params[field])
                    param.validate(field, value)
                    setattr(self, field, value)

    def proceed(self):
        return 'not implemented'

    class Meta:
        abstract = True


def dispatch(raw_request, resolver_func):
    try:
        request = JsonRpcRequest(raw_request)
        method = resolver_func(request.method)
        if inspect.isfunction(method):
            result = method(request.params)
        elif inspect.isclass(method) and issubclass(method, JsonRpcProcedure):
            result = method().handle(request.params)
        else:
            raise Exception('Incorrect handler for method {}'.format(request.method))

        response = JsonRpcResponse(request_id=request.id, result=result)
    except JsonRpcException as e:
        response = JsonRpcResponse(request_id=get_id(raw_request), error_code=e.code, error_message=e.message)

    return response


def only_integer(name, value):
    if not isinstance(value, int):
        raise InvalidParams("Param {} must be an integer".format(name))


def only_string(name, value):
    if not isinstance(value, (str, unicode,)):
        raise InvalidParams("Param {} must be a string".format(name))


def only_list(name, value):
    if not isinstance(value, list):
        raise InvalidParams("Param {} must be a list".format(name))


class IntParam(Param):
    validators = [only_integer, ]


class StringParam(Param):
    validators = [only_string, ]


class ListParam(Param):
    validators = [only_list, ]

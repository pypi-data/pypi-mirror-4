import jrpcutils as ju
import unittest
from base import BaseCase


class SomeProcedure(ju.JsonRpcProcedure):
    int_param = ju.IntParam(required=False)
    str_param = ju.StringParam(required=False)
    list_param = ju.ListParam(required=False)
    param = ju.Param(required=False)

    class Meta:
        method = "some_procedure"


class ValidateParamCase(BaseCase):
    def test_wrong_type_for_int(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"int_param": "text"}, "id": 123}', ju.resolver)
        self.assertResponseErrorCode(response, ju.INVALID_PARAMS_CODE)

    def test_right_type_for_int(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"int_param": 2323}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, "not implemented")

    def test_wrong_type_for_str(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"str_param": 777}, "id": 123}', ju.resolver)
        self.assertResponseErrorCode(response, ju.INVALID_PARAMS_CODE)

    def test_right_type_for_str(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"str_param": "ok"}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, "not implemented")

    def test_wrong_type_for_list(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"list_param": 777}, "id": 123}', ju.resolver)
        self.assertResponseErrorCode(response, ju.INVALID_PARAMS_CODE)

    def test_right_type_for_list(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"list_param": [1, 2, 3, 4]}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, "not implemented")

    def test_base_param(self):
        """
        There are not restriction for base class ju.Param thus we can pass any
        to this param.
        """
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"param": [1, 2, 3, 4]}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, "not implemented")

        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"param": "text"}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, "not implemented")

        response = ju.dispatch('{"jsonrpc": "2.0", "method": "some_procedure", \
            "params": {"param": 145}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, "not implemented")


def check_greater_than_100(name, value):
    if value <= 100:
        raise ju.InvalidParams("Param {} must be greater than 100".format(name))


class MyCustomParam(ju.IntParam):
    validators = ju.IntParam.validators + [check_greater_than_100, ]


class ProcedureWithCustomParam(ju.JsonRpcProcedure):
    # we can declare our new class
    first_way = MyCustomParam(required=False)
    # or set an extra validator through argument validators
    second_way = ju.IntParam(validators=[check_greater_than_100, ], required=False)

    class Meta:
        method = "procedure_with_custom_param"


class ValidateCustomParamCase(BaseCase):
    def test_wrong_type_for_first_way(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "procedure_with_custom_param", \
            "params": {"first_way": "text"}, "id": 123}', ju.resolver)
        self.assertResponseErrorCode(response, ju.INVALID_PARAMS_CODE)

        response = ju.dispatch('{"jsonrpc": "2.0", "method": "procedure_with_custom_param", \
            "params": {"first_way": 99}, "id": 123}', ju.resolver)
        self.assertResponseErrorCode(response, ju.INVALID_PARAMS_CODE)

    def test_right_type_for_first_way(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "procedure_with_custom_param", \
            "params": {"first_way": 101}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, "not implemented")


    def test_wrong_type_for_second_way(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "procedure_with_custom_param", \
            "params": {"second_way": "text"}, "id": 123}', ju.resolver)
        self.assertResponseErrorCode(response, ju.INVALID_PARAMS_CODE)

        response = ju.dispatch('{"jsonrpc": "2.0", "method": "procedure_with_custom_param", \
            "params": {"second_way": 99}, "id": 123}', ju.resolver)
        self.assertResponseErrorCode(response, ju.INVALID_PARAMS_CODE)

    def test_right_type_for_second_way(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "procedure_with_custom_param", \
            "params": {"second_way": 101}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, "not implemented")

if __name__ == '__main__':
    unittest.main()

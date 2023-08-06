import jrpcutils as ju
import unittest
from base import BaseCase


@ju.procedure('func_based_procedure')
def some_procedure(params):
    return 'from some_procedure'


class MyFirstProcedure(ju.JsonRpcProcedure):
    param_1 = ju.IntParam()
    param_2 = ju.Param(required=False)

    def proceed(self):
        return 'Param 1 is {}. Param 2 is {}.'.format(self.param_1, self.param_2)

    class Meta:
        method = "my_first_class_based_procedure"


class MySecondProcedure(ju.JsonRpcProcedure):

    class Meta:
        method = "my_second_class_based_procedure"


class DispatchCase(BaseCase):

    def test_does_not_exist_procedure(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "there_is_not_its_procedure", \
                                   "id": 123}', ju.resolver)
        self.assertResponseErrorCode(response, ju.METHOD_NOT_FOUND_CODE)

    def test_procedure(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "my_first_class_based_procedure", \
                                   "params": {"param_1": 555}, "id": 123}', ju.resolver)
        self.assertResponseResult(response, 'Param 1 is 555. Param 2 is None.')

        response = ju.dispatch('{"jsonrpc": "2.0", "method": "my_first_class_based_procedure", \
                                   "params": {"param_1": 148, "param_2": "cats cannot speak" }, "id": 123}', ju.resolver)
        self.assertResponseResult(response, 'Param 1 is 148. Param 2 is cats cannot speak.')

    def test_if_we_dont_send_required_param(self):
        # we didnt specify the required param "param_1" we only specified "param_2"
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "my_first_class_based_procedure", \
                                   "params": {"param_2": 555}, "id": 123}', ju.resolver)

        self.assertResponseErrorCode(response, ju.INVALID_PARAMS_CODE)

    def test_not_implemented_procedure(self):
        response = ju.dispatch('{"jsonrpc": "2.0", "method": "my_second_class_based_procedure", \
                                         "id": 6123}', ju.resolver)
        self.assertEqual(str(response), '{"jsonrpc": "2.0", "id": 6123, "result": "not implemented"}')

if __name__ == '__main__':
    unittest.main()

import jrpcutils
import unittest


class TestJrpcUtilsMakeSuccessfulRequest(unittest.TestCase):

    def test(self):
        request = jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "update", "params": {"p1": 1}, "id": 6123}')
        self.assertEqual(request.version, jrpcutils.JSONRPC_VERSION)
        self.assertEqual(request.version, '2.0')
        self.assertEqual(request.id, 6123)
        self.assertEqual(request.method, 'update')
        self.assertEqual(request.params, dict(p1=1))

    def test_without_params(self):
        request = jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "get_ratio", "id": 3421}')
        self.assertEqual(request.version, jrpcutils.JSONRPC_VERSION)
        self.assertEqual(request.version, '2.0')
        self.assertEqual(request.id, 3421)
        self.assertEqual(request.method, 'get_ratio')
        self.assertEqual(request.params, None)

    def test_with_array_params(self):
        request = jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "sum", "params": [1, 2, 3, 4],"id": 3}')
        self.assertEqual(request.version, jrpcutils.JSONRPC_VERSION)
        self.assertEqual(request.version, '2.0')
        self.assertEqual(request.id, 3)
        self.assertEqual(request.method, 'sum')
        self.assertEqual(request.params, [1, 2, 3, 4])


class TestJrpcUtilsMakeFailedRequest(unittest.TestCase):

    def test_incorrect_json(self):
        with self.assertRaises(jrpcutils.ParseError):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "m5", "id": 145, , ,}')

    def test_missed_id(self):
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "remove"}')

    def test_empty_id(self):
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "sale", "id": ""}')

    def test_wrong_id(self):
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "buy", "id": "asdf"}')
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "buy", "id": [2, 3]}')
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "buy", "id": {"idp": 1}}')

    def test_missed_method(self):
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "id": 2321}')

    def test_empty_method(self):
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": "", "id": 2321}')

    def test_wrong_method(self):
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": [1, 2, 3], "id": 2321}')
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": 123, "id": 2321}')
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "2.0", "method": {"p1": 22}, "id": 2321}')

    def test_missed_version(self):
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"method": "add", "id": 2321}')

    def test_wrong_version(self):
        with self.assertRaises(jrpcutils.InvalidRequest):
            jrpcutils.JsonRpcRequest('{"jsonrpc": "9.99", "method": "add", "id": 2321}')


if __name__ == '__main__':
    unittest.main()

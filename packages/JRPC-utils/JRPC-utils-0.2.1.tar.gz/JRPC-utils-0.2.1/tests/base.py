import unittest


class BaseCase(unittest.TestCase):

    def assertResponseErrorCode(self, response, error_code, message=None):
        self.assertEqual(response.error_code, error_code, message)

    def assertResponseResult(self, response, result, message=None):
        self.assertEqual(response.result, result, message)

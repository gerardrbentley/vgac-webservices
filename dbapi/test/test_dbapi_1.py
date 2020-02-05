from dbapi.vgac_db import VGAC_DBAPI
from twisted.trial import unittest
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

# Original Source: https://twisted.readthedocs.io/en/twisted-17.9.0/core/howto/trial.html#core-howto-trial-twisted


class DBAPITestCase(unittest.TestCase):
    def setUp(self):
        self.dbapi = VGAC_DBAPI()

    def _test(self, operation, expected):
        builder = EnvironBuilder(method='GET', base_url='127.0.0.1:4747')
        env = builder.get_environ()
        req = Request(env)
        result = operation(req)
        self.assertEqual(result, expected)

    def _test_error(self, operation):
        self.assertRaises(TypeError, operation, "foo", 2)
        self.assertRaises(TypeError, operation, "bar", "egg")
        self.assertRaises(TypeError, operation, [3], [8, 2])
        self.assertRaises(TypeError, operation, {"e": 3}, {"r": "t"})

    def test_message(self):
        self._test(self.dbapi.message, '{"message": "test: dbapi test"}')

    # def test_subtract(self):
    #     self._test(self.dbapi.subtract, 7, 3, 4)

    # def test_multiply(self):
    #     self._test(self.dbapi.multiply, 6, 9, 54)

    # def test_divide(self):
    #     self._test(self.dbapi.divide, 12, 5, 2)

    # def test_errorAdd(self):
    #     self._test_error(self.dbapi.add)

    # def test_errorSubtract(self):
    #     self._test_error(self.dbapi.subtract)

    # def test_errorMultiply(self):
    #     self._test_error(self.dbapi.multiply)

    # def test_errorDivide(self):
    #     self._test_error(self.dbapi.divide)

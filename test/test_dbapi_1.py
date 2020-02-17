from dbapi.vgac_db import VGAC_DBAPI
from twisted.trial import unittest
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

# Original Source: https://twisted.readthedocs.io/en/twisted-17.9.0/core/howto/trial.html#core-howto-trial-twisted

import os
from io import BytesIO

try:
    from unittest.mock import Mock, call
except Exception:
    from mock import Mock, call

from six.moves.urllib.parse import parse_qs

from twisted.internet.defer import CancelledError, Deferred, fail, succeed
from twisted.trial.unittest import SynchronousTestCase
from twisted.web import server
from twisted.web.http_headers import Headers
from twisted.web.test.test_web import DummyChannel


def requestMock(
    path,
    method=b"GET",
    host=b"localhost",
    port=8080,
    isSecure=False,
    body=None,
    headers=None,
):
    if not headers:
        headers = {}

    if not body:
        body = b""

    path, qpath = (path.split(b"?", 1) + [b""])[:2]

    request = server.Request(DummyChannel(), False)
    request.site = Mock(server.Site)
    request.gotLength(len(body))
    request.content = BytesIO()
    request.content.write(body)
    request.content.seek(0)
    request.args = parse_qs(qpath)
    request.requestHeaders = Headers(headers)
    request.setHost(host, port, isSecure)
    request.uri = path
    request.prepath = []
    request.postpath = path.split(b"/")[1:]
    request.method = method
    request.clientproto = b"HTTP/1.1"

    request.setHeader = Mock(wraps=request.setHeader)
    request.setResponseCode = Mock(wraps=request.setResponseCode)

    request._written = BytesIO()
    request.finishCount = 0
    request.writeCount = 0

    def registerProducer(producer, streaming):
        request.producer = producer
        for _ in range(2):
            if request.producer:
                request.producer.resumeProducing()

    def unregisterProducer():
        request.producer = None

    def finish():
        request.finishCount += 1

        if not request.startedWriting:
            request.write(b"")

        if not request.finished:
            request.finished = True
            request._cleanup()

    def write(data):
        request.writeCount += 1
        request.startedWriting = True

        if not request.finished:
            request._written.write(data)
        else:
            raise RuntimeError(
                "Request.write called on a request after "
                "Request.finish was called."
            )

    def getWrittenData():
        return request._written.getvalue()

    request.finish = finish
    request.write = write
    request.getWrittenData = getWrittenData

    request.registerProducer = registerProducer
    request.unregisterProducer = unregisterProducer

    request.processingFailed = Mock(wraps=request.processingFailed)

    return request


class DBAPITestCase(unittest.TestCase):
    def setUp(self):
        self.dbapi = VGAC_DBAPI()

    def _test(self, operation, expected):
        # builder = EnvironBuilder(method='GET', base_url='127.0.0.1:4747')
        # env = builder.get_environ()
        # req = Request(env)
        req = requestMock(b"/")
        result = operation(req)
        self.assertEqual(result, expected)

    def _test_error(self, operation):
        self.assertRaises(TypeError, operation, "foo", 2)
        self.assertRaises(TypeError, operation, "bar", "egg")
        self.assertRaises(TypeError, operation, [3], [8, 2])
        self.assertRaises(TypeError, operation, {"e": 3}, {"r": "t"})

    def test_message(self):
        self._test(self.dbapi.message,
                   '{"status": 200, "message": "test: dbapi test"}')

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

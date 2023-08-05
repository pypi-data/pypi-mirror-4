# Copyright (C) 2012  Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
from StringIO import StringIO

from testtools import (
    run_test_with,
    TestCase,
    )
from testtools.deferredruntest import (
    assert_fails_with,
    AsynchronousDeferredRunTest,
    )
from twisted.internet import defer
from twisted.internet.error import (
    ConnectionRefusedError,
    TimeoutError,
    )
from twisted.internet.task import Clock
from twisted.python.failure import Failure
from twisted.web import (
    http,
    server,
    )
from twisted.web.client import (
    Agent,
    FileBodyProducer,
    )
from twisted.web.test.test_web import DummyRequest

from txpkgme.harness import (
    CallbackResource,
    PkgmeServiceError,
    run_with_callbacks,
    WebServer,
    wrap_pkgme_service_error,
)


class DummyPostRequest(DummyRequest):

    method = 'POST'

    def __init__(self, postpath, content='', session=None):
        DummyRequest.__init__(self, postpath, session=session)
        self.content = StringIO(content)


class CallbackResourceTests(TestCase):

    def _render(self, resource, request):
        result = resource.render(request)
        if isinstance(result, str):
            request.write(result)
            request.finish()
            return defer.succeed(None)
        elif result is server.NOT_DONE_YET:
            if request.finished:
                return defer.succeed(None)
            else:
                return request.notifyFinish()
        else:
            raise ValueError("Unexpected return value: %r" % (result,))

    @run_test_with(AsynchronousDeferredRunTest.make_factory(timeout=10))
    def test_calls_callback(self):
        got_callback = defer.Deferred()
        request = DummyPostRequest([''], content='{}')
        resource = CallbackResource(got_callback.callback)
        d = self._render(resource, request)
        def rendered(ignored):
            self.assertEquals('<html></html>', "".join(request.written))
        d.addCallback(rendered)
        return defer.gatherResults([d, got_callback])

    @run_test_with(AsynchronousDeferredRunTest.make_factory(timeout=10))
    def test_returns_method_and_body(self):
        got_callback = defer.Deferred()
        def on_post((method, body)):
            self.assertEqual("POST", method)
            self.assertEqual(["a"], json.loads(body))
        got_callback.addCallback(on_post)
        request = DummyPostRequest([''], content='["a"]')
        resource = CallbackResource(got_callback.callback)
        d = self._render(resource, request)
        return defer.gatherResults([d, got_callback])


class HarnessTests(TestCase):

    @run_test_with(AsynchronousDeferredRunTest.make_factory(timeout=10))
    def test_callback(self):
        payload = {}
        callbacks = []
        d = WebServer.start(self.reactor, 'localhost', 0)
        def check_web_server(webserver):
            callback_url = webserver.set_child(
                'callback', CallbackResource(callbacks.append))
            agent = Agent(self.reactor)
            callback_body = StringIO(json.dumps(payload))
            d = agent.request(
                'PUT', callback_url,
                bodyProducer=FileBodyProducer(callback_body))
            return d.addBoth(webserver.shut_down)
        d.addCallback(check_web_server)

        def check_response(response):
            self.assertEqual(200, response.code)
            self.assertEqual([('PUT', json.dumps(payload))], callbacks)
        d.addCallback(check_response)

        return d


class TestRunWithCallbacks(TestCase):

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=10)

    def start_webserver(self):
        return WebServer.start(self.reactor, 'localhost', 0)

    def hit_url(self, url, payload):
        agent = Agent(self.reactor)
        body = StringIO(payload)
        return  agent.request('PUT', url, bodyProducer=FileBodyProducer(body))

    def test_basic_timeout(self):
        clock = Clock()
        d = self.start_webserver()
        def server_up(webserver):
            d = run_with_callbacks(webserver, 5, clock, lambda url: None)
            return d.addBoth(webserver.shut_down)
        d.addCallback(server_up)
        clock.advance(10)
        return assert_fails_with(d, TimeoutError)

    def test_callback_hit(self):
        clock = Clock()
        payload = self.getUniqueString()
        d = self.start_webserver()
        def server_up(webserver):
            d = run_with_callbacks(
                webserver, 5, clock,
                lambda urls: self.hit_url(urls['callback_url'], payload))
            return d.addBoth(webserver.shut_down)
        d.addCallback(server_up)
        def got_response((method, body)):
            self.assertEqual(('PUT', payload), (method, body))
        return d.addCallback(got_response)

    def test_errback_hit(self):
        clock = Clock()
        payload = self.getUniqueString()
        d = self.start_webserver()
        def server_up(webserver):
            d = run_with_callbacks(
                webserver, 5, clock,
                lambda urls: self.hit_url(urls['errback_url'], payload))
            return d.addBoth(webserver.shut_down)
        d.addCallback(server_up)
        def got_response(failure):
            method, body = failure.value
            self.assertEqual(('PUT', payload), (method, body))
        return d.addErrback(got_response)

    def test_callback_after_timeout_and_shutdown(self):
        clock = Clock()
        callback_urls = {}
        d = self.start_webserver()
        def server_up(webserver):
            d = run_with_callbacks(webserver, 5, clock, callback_urls.update)
            return d.addBoth(webserver.shut_down)
        d.addCallback(server_up)
        clock.advance(10)
        payload = self.getUniqueString()
        d2 = self.hit_url(callback_urls['callback_url'], payload)
        return defer.gatherResults(
            [assert_fails_with(d, TimeoutError),
             assert_fails_with(d2, ConnectionRefusedError)])

    def test_callback_after_timeout_before_shutdown(self):
        clock = Clock()
        d = self.start_webserver()
        def server_up(webserver):
            callback_urls = {}
            d1 = run_with_callbacks(webserver, 5, clock, callback_urls.update)
            clock.advance(10)
            payload = self.getUniqueString()
            d2 = self.hit_url(callback_urls['callback_url'], payload)
            def got_response(response):
                self.assertEqual(http.GONE, response.code)
            d2.addCallback(got_response)
            d = defer.gatherResults([assert_fails_with(d1, TimeoutError), d2])
            return d.addBoth(webserver.shut_down)
        return d.addCallback(server_up)


class TestPkgmeServiceError(TestCase):

    def test_non_json_body(self):
        e = PkgmeServiceError('whatever')
        self.assertEqual('whatever', e.body)
        self.assertEqual('Non-JSON response', e.traceback)

    def test_json_body(self):
        data = {'foo': 'bar'}
        body = json.dumps(data)
        e = PkgmeServiceError(body)
        self.assertEqual(data, e.body)
        self.assertEqual('No traceback', e.traceback)
        self.assertIs(None, e.error)

    def test_error_in_json_body(self):
        data = {'error': 'foo'}
        body = json.dumps(data)
        e = PkgmeServiceError(body)
        self.assertEqual({}, e.body)
        self.assertEqual('foo', e.traceback)
        self.assertIs(None, e.error)

    def test_traceback_in_error(self):
        data = {'error': {'traceback': 'foo', 'type': 'Foo'}}
        body = json.dumps(data)
        e = PkgmeServiceError(body)
        self.assertEqual({}, e.body)
        self.assertEqual('foo', e.traceback)
        self.assertEqual({'type': 'Foo'}, e.error)


class TestWrapPkgmeServiceError(TestCase):

    def test_passthrough_non_tuple(self):
        f = Failure(TimeoutError())
        self.assertIs(f, wrap_pkgme_service_error(f))

    def test_put_in_pkgme_service_error(self):
        data = {'error': {'traceback': 'foo', 'type': 'Foo'}}
        body = json.dumps(data)
        expected = PkgmeServiceError(body)
        failure = wrap_pkgme_service_error(Failure(('PUT', body)))
        self.assertEqual(
            (expected.body, expected.traceback, expected.error),
            (failure.value.body, failure.value.traceback,
             failure.value.error))

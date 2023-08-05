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

"""
Harness that can send and receive requests to a pkgme-service.
"""

from twisted.internet import defer, reactor as mod_reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.error import TimeoutError
from twisted.python.failure import Failure
from twisted.protocols.policies import (
    ProtocolWrapper,
    WrappingFactory,
    )
from twisted.web.resource import (
    ErrorPage,
    Resource,
    )
from twisted.web import http
from twisted.web.server import Site

from pkgme_service_client.client import build_package

from .utils import parse_json


class CallbackResource(Resource):
    """A Twisted web resource that waits for a POST."""

    def __init__(self, on_post):
        """A web resource that fires a Deferred on POST.

        :param on_post: A function that will be called when a POST request is
            received. Will be fired with a tuple containing the request method
            and body.
        """
        Resource.__init__(self)
        self.on_post = on_post

    def render(self, request):
        # This means that the first request to this resource will be treated
        # as the actual callback request. I'm not sure if we're providing an
        # accurate double if we just assume the first hit is the real
        # thing. -- jml
        method = request.method
        body = request.content.getvalue()
        # If we shut down immediately, the response never gets sent.  Sadly,
        # Twisted doesn't seem to have an event for when the response is sent,
        # so we do the best we can by waiting for this cycle of the event loop
        # to finish, and thus the request to be sent.
        def shutdown():
            self.on_post((method, body))
        shutdown()
        return '<html></html>'


class NotifyOnConnectionLost(ProtocolWrapper):

    def __init__(self, factory, wrappedProtocol):
        ProtocolWrapper.__init__(self, factory, wrappedProtocol)
        self.connectionLostDeferred = defer.Deferred()

    def connectionLost(self, reason):
        ProtocolWrapper.connectionLost(self, reason)
        if self.connectionLostDeferred:
            d, self.connectionLostDeferred = self.connectionLostDeferred, None
            d.callback(None)


class DisconnectAllOnStopListening(WrappingFactory):

    protocol = NotifyOnConnectionLost

    def __init__(self, disconnectedDeferred, wrappedFactory):
        WrappingFactory.__init__(self, wrappedFactory)
        self.disconnectedDeferred = disconnectedDeferred

    def doStop(self):
        WrappingFactory.doStop(self)
        d = defer.gatherResults(
            [p.connectionLostDeferred for p in self.protocols])
        d.chainDeferred(self.disconnectedDeferred)


def _run_web_server(reactor, root, hostname, port):
    endpoint = TCP4ServerEndpoint(reactor, port)
    disconnected = defer.Deferred()
    site = DisconnectAllOnStopListening(disconnected, Site(root))
    d = endpoint.listen(site)
    def web_server_up(listening_port):
        return {
            'disconnect': disconnected,
            'listening-port': listening_port,
            }
    return d.addCallback(web_server_up)


def _url_for_port(port, hostname=None):
    # Allow for host name to be overridden.  0.0.0.0 means different things to
    # different people.
    address = port.getHost()
    if hostname is None:
        hostname = address.host
    return 'http://%s:%s' % (hostname, address.port)


class WebServer(object):

    def __init__(self, root, base_url, listening_port, disconnected):
        self._root = root
        self.base_url = base_url
        self._listening_port = listening_port
        self._disconnected = disconnected

    @classmethod
    def start(cls, reactor, hostname, port):
        root = Resource()
        d = _run_web_server(reactor, root, hostname, port)
        def server_up(details):
            port = details['listening-port']
            disconnect = details['disconnect']
            return cls(root, _url_for_port(port, hostname), port, disconnect)
        return d.addCallback(server_up)

    def shut_down(self, passthrough=None):
        d = self._listening_port.stopListening()
        # We are only properly shut down when the port has stopped
        # listening and when all the clients have disconnected.
        d = defer.gatherResults([self._disconnected, d])
        return d.addCallback(lambda x: passthrough)

    def set_child(self, name, resource):
        self._root.putChild(name, resource)
        return '%s/%s' % (self.base_url, name)


def run_with_callbacks(webserver, timeout, clock, function, *args, **kwargs):
    deferred = defer.Deferred()
    callback_url = webserver.set_child(
        'callback', CallbackResource(deferred.callback))
    errback_url = webserver.set_child(
        'errback', CallbackResource(deferred.errback))
    def got_timeout():
        time_out_resource = ErrorPage(
            http.GONE, "Timed Out", "Timed out waiting for callback response")
        webserver.set_child('callback', time_out_resource)
        webserver.set_child('errback', time_out_resource)
        deferred.errback(TimeoutError())
    timeout_call = clock.callLater(timeout, got_timeout)
    def cancel_timeout(ignored):
        if timeout_call.active():
            timeout_call.cancel()
        return ignored
    deferred.addBoth(cancel_timeout)
    theirs = defer.maybeDeferred(
        function, {'callback_url': callback_url,
                   'errback_url': errback_url}, *args, **kwargs)
    return theirs.addBoth(lambda discarded: deferred)


def send_api_request(webserver, metadata, pkgme_service_root, timeout=60,
                     clock=None):
    if clock is None:
        clock = mod_reactor
    def send_request(callbacks, metadata):
        metadata.update(callbacks)
        build_package(pkgme_service_root, metadata)
    d = run_with_callbacks(webserver, timeout, clock, send_request, metadata)
    return d.addErrback(wrap_pkgme_service_error)


class PkgmeServiceError(Exception):
    """Raised on error from a remote pkgme-service."""

    def __init__(self, body):
        error = None
        try:
            body = parse_json(body)
        except ValueError:
            traceback = "Non-JSON response"
        else:
            error = body.pop('error', None)
            if error:
                try:
                    traceback = error.pop('traceback', 'No traceback')
                except AttributeError:
                    traceback = error
                    error = None
            else:
                traceback = 'No traceback'
        self.body = body
        self.traceback = traceback
        self.error = error


def wrap_pkgme_service_error(failure):
    try:
        method, json_body = failure.value
    except ValueError:
        return failure
    return Failure(PkgmeServiceError(json_body))

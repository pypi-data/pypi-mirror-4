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

import argparse
import os
import json
from pprint import pformat
import sys
import time

from twisted.internet import reactor as mod_reactor
from twisted.internet.task import deferLater
from twisted.web.resource import Resource
from twisted.web.static import File

from .commands import (
    add_service_url_options,
    get_service_url,
    UserError,
    )
from .harness import (
    PkgmeServiceError,
    send_api_request,
    TimeoutError,
    WebServer,
    )


METADATA_FILE = 'devportal-metadata.json'
METADATA_ICONS = 'icons'


def load_metadata(metadata_path):
    """Load metadata from a JSON file and return as API dict.

    Assumes that the keys in a devportal-metadata.json file are the same as
    those expected by pkgme-service.
    """
    metadata = json.load(open(metadata_path, 'r'))
    # Things that the pkgme-service API expects that is not part of what
    # pkgme-devportal expects from devportal-metadata.json.
    extra_api_parameters = {
        'myapps_id': 42,
        }
    metadata.update(extra_api_parameters)
    icons = metadata.get(METADATA_ICONS, {})
    base_dir = os.path.abspath(os.path.dirname(metadata_path))
    for resolution, filename in icons.items():
        icons[resolution] = os.path.join(base_dir, filename)
    return metadata


def add_local_files(web_server, app_path, icons=None):
    """Create a root resource with URLs for everything pkgme will need.

    The created resource has a callback node, an errback node, a URL for
    downloading the thing to be packaged and icons (if present in the
    metadata).

    :return: An ``IResource`` and a dict to the relative URLs from keys
        that the pkgme-service will expect the URLs at.
    """
    metadata_urls = {}
    app_name = os.path.basename(app_path)
    metadata_urls['package_url'] = web_server.set_child(
        app_name, File(app_path))
    if icons:
        ICON_ROOT = 'icons'
        metadata_urls[METADATA_ICONS] = {}
        icons_container = Resource()
        icon_base = web_server.set_child(ICON_ROOT, icons_container)
        for resolution, path in icons.items():
            resolution_resource = Resource()
            icon_name = os.path.basename(path)
            icon_resource = File(path)
            resolution_resource.putChild(icon_name, icon_resource)
            icons_container.putChild(resolution, resolution_resource)
            metadata_urls[METADATA_ICONS][resolution] = (
                '%s/%s/%s' % (icon_base, resolution, icon_name))
    return metadata_urls


class ResultWriter(object):

    def write(self, success, duration, msg):
        sys.stderr.write(msg + '\n')


class OutputFileResultWriter(object):
    """Writes the output to a file in a structured manner."""

    def __init__(self, output_file, clock):
        self.output_file = output_file
        self.clock = clock

    def get_output(self, success, duration, msg):
        return json.dumps(dict(
            timestamp=self.clock.seconds(),
            message=msg.replace('\n', '  '),
            successful=success,
            duration=duration,
            ))

    def write(self, success, duration, msg):
        self.output_file.write(self.get_output(success, duration, msg))
        self.output_file.flush()


def parse_output(output):
    """Parses the output written by OutputFileResultWriter.

    Returns the output back to Python objects for easier use.

    :returns: a tuple of (timestamp, success, duration, msg)
        where timestamp is a float with the seconds past the epoch
            when the result was written
        success is a bool indicating if the response was successfully
            received
        duration is the duration it took for the server to respond
        msg is a message with more information
    """
    return json.loads(output)


def check_saved_output(output, last_run_grace, warn_duration, filename):
    """Checks the saved ouput of a run.

    It returns values suitable for use as a nagios check.

    :param last_run_grace: the number of seconds since the last run
        that are acceptable. If more time than this has elapsed an error
        return will be generated.
    :param warn_duration: the number of seconds that the last run can
        have taken before a warning is generated. If the server responded
        successfully within the timeout, but took longer than this then a
        warning return will be generated.
    :returns: a tuple of (result, message) where result is a returncode
        that nagios will understand, and message is a string with more
        information.
    """
    now = time.time()
    parts = parse_output(output)
    if not parts['successful']:
        result = 2
        suffix = ' NB: Based on results stored in %r by a cronjob' % (filename,)
        result_message = "Check failed in %f: %s.%s" % (
            parts['duration'], parts['message'], suffix)
    elif parts['timestamp'] < now - last_run_grace:
        result = 2
        result_message = "Last ran %f" % (parts['timestamp'], )
    elif parts['duration'] > warn_duration:
        result = 1
        result_message = "WARN in %f: %s" % (parts['duration'], parts['message'])
    else:
        result = 0
        result_message = "OK in %f: %s" % (parts['duration'], parts['message'])
    return result, result_message


def submit_local_files(service_root, file_path, metadata, shutdown_delay,
                       reactor, timeout=None, hostname='localhost',
                       port=0, **webserver_args):
    """Submit 'path' to pkgme-service at 'service_root' with 'metadata'.

    :return: A Deferred that files with ('PUT', json_result).
    """
    d = WebServer.start(reactor, hostname, port)
    def web_server_up(webserver):
        new_urls = add_local_files(
            webserver, file_path, metadata.get(METADATA_ICONS, None))
        metadata.update(new_urls)
        api = send_api_request(
            webserver, metadata, service_root, timeout=timeout)
        api.addBoth(delay_callbacks, shutdown_delay, reactor)
        api.addBoth(webserver.shut_down)
        return api
    return d.addCallback(web_server_up)


def delay_callbacks(value, delay, clock=None):
    if clock is None:
        clock = mod_reactor
    if not delay:
        return value
    return deferLater(clock, delay, lambda: value)


def fire_request(service_root, app_path, metadata_path, timeout,
                 hostname, port, result_writer, clock, shutdown_delay):
    successful = [False]

    start_time = clock.seconds()
    def get_duration():
        return clock.seconds() - start_time

    def got_response((method, body)):
        successful[0] = True
        result_writer.write(True, get_duration(), body)

    def got_timeout(error):
        error.trap(TimeoutError)
        result_writer.write(False, get_duration(),
                "Timed out waiting for callback. Check celery log for details.")

    def got_error(failure):
        failure.trap(PkgmeServiceError)
        error = failure.value
        msg = "Failed to build package:\n\n"
        msg += error.traceback
        msg += "\n\nOther data:\n"
        msg += pformat(error.body)
        msg += "\n"
        result_writer.write(False, get_duration(), msg)

    def disaster(error):
        msg = "UNEXPECTED ERROR\n"
        msg += error.getTraceback()
        result_writer.write(False, get_duration(), msg)

    def send_request(metadata):
        d = submit_local_files(
            service_root, app_path, metadata, shutdown_delay,
            reactor=mod_reactor,
            timeout=timeout, hostname=hostname, port=port, clock=clock)
        d.addCallback(got_response)
        d.addErrback(got_timeout)
        d.addErrback(got_error)
        d.addErrback(disaster)
        d.addBoth(lambda x: mod_reactor.stop())
        return d

    metadata = load_metadata(metadata_path)
    mod_reactor.callWhenRunning(send_request, metadata)
    mod_reactor.run()
    return successful[0]


def make_options():
    parser = argparse.ArgumentParser("Submit an application to pkgme-service")
    parser.add_argument("-t", "--timeout", dest="timeout",
                        help="time out after TIMEOUT seconds", type=int,
                        metavar="TIMEOUT", default=30)
    parser.add_argument("-p", "--port", dest="port",
                        help="port to listen on.", type=int, metavar="PORT",
                        default=0)
    parser.add_argument("-f", "--file", dest="output_file",
                        help="write the result to FILE", type=argparse.FileType('w'),
                        metavar="FILE", default=None)
    parser.add_argument("--shutdown-delay", dest="shutdown_delay", type=int,
                        help=("Delay shutting down the web server by this "
                              "many seconds."))
    # TODO: Change this to FileType.
    parser.add_argument(
        'app_path', type=str, help="Path to the application to package")
    parser.add_argument(
        'metadata_path', type=str, nargs='?', default=METADATA_FILE, help=(
            "Path to the metadata for the application"))
    parser.add_argument(
        'service_url', type=str, nargs='?', default=None,
        help="URL for pkgme-service.  Don't use this.")
    add_service_url_options(parser)
    return parser


def main():
    parser = make_options()
    options = parser.parse_args()
    try:
        service_url = get_service_url(
            options.service_url, options.remote_hostname, options.remote_url)
    except UserError, e:
        parser.error(str(e))
    clock = mod_reactor
    result_writer = ResultWriter()
    if options.output_file is not None:
        result_writer = OutputFileResultWriter(options.output_file, clock)
    successful = fire_request(
        service_url, options.app_path, options.metadata_path, options.timeout,
        options.hostname, options.port, result_writer, clock,
        options.shutdown_delay)
    if not successful:
        return 1
    return 0

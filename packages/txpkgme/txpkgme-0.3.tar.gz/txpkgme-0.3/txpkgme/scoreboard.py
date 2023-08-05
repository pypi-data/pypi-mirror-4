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
from itertools import (
    imap,
    islice,
    )
import json
import sys

from httplib2 import Http
from oauth.oauth import (
    OAuthRequest,
    OAuthConsumer,
    OAuthToken,
    OAuthSignatureMethod_PLAINTEXT,
    )
from subunit import TestProtocolClient
from testtools import PlaceHolder
from testtools.content import (
    json_content,
    text_content,
    )
from twisted.internet import defer
from twisted.internet import reactor as mod_reactor

from .commands import (
    add_service_url_options,
    get_service_url,
    UserError,
    )
from .harness import (
    PkgmeServiceError,
    send_api_request,
    WebServer,
    )
from .utils import parse_json


MYAPPS_SERVERS = {
    'vps': 'https://sca.razorgirl.info/dev/api/app-metadata/',
    'staging': 'https://developer.staging.ubuntu.com/dev/api/app-metadata/',
    'production': 'https://myapps.developer.ubuntu.com/dev/api/app-metadata/',
    }


def now():
    from datetime import datetime
    from testtools.testresult.real import utc
    return datetime.now(utc)


def _simple_error(error):
    return {'traceback': text_content(error)}


class SubunitReporter(object):

    def __init__(self, stream):
        client = TestProtocolClient(stream)
        self._client = client
        client.startTestRun()

    def _to_test(self, application):
        name = application['name'].replace(' ', '-').encode('utf8')
        return PlaceHolder('%s:%s' % (name, application['myapps_id']))

    def timestamp(self, datetime=None):
        if datetime is None:
            datetime = now()
        self._client.time(datetime)
        return datetime

    def building_package(self, application):
        self._client.startTest(self._to_test(application))
        self._client.tags(
            set(['state=%s' % application.get('state', 'UNKNOWN')]), set())

    def pkgme_failure(self, application, error):
        test = self._to_test(application)
        details = {
            'traceback': text_content(error.traceback),
            'extra_data': json_content(error.body),
            'myapps': json_content(application),
            }
        if error.error:
            details['error'] = json_content(error.error)
        self._client.addFailure(test, details=details)
        self._client.stopTest(test)

    def pkgme_success(self, application, data):
        test = self._to_test(application)
        self._client.addSuccess(
            test, details={'pkgme': json_content(data),
                           'myapps': json_content(application)})
        self._client.stopTest(test)

    def unexpected_error(self, application, failure):
        test = self._to_test(application)
        details = _simple_error(failure.getTraceback())
        details['myapps'] = json_content(application)
        self._client.addFailure(test, details=details)
        self._client.stopTest(test)


class BufferedReporter(object):

    def __init__(self, reporter):
        self._reporter = reporter
        self._building = {}
        self._now = None

    def timestamp(self):
        self._now = now()
        return self._now

    def _forward_timestamp(self, datetime):
        if datetime:
            self._reporter.timestamp(datetime)

    def _forward_result(self, method_name, application, result):
        self._forward_timestamp(self._building[application['myapps_id']])
        self._reporter.building_package(application)
        self._forward_timestamp(self._now)
        method = getattr(self._reporter, method_name)
        method(application, result)

    def building_package(self, application):
        self._building[application['myapps_id']] = self._now

    def pkgme_success(self, application, data):
        self._forward_result('pkgme_success', application, data)

    def pkgme_failure(self, application, error):
        self._forward_result('pkgme_failure', application, error)

    def unexpected_error(self, application, failure):
        self._forward_result('unexpected_error', application, failure)


def run_many(functions, num_parallel=1):
    semaphore = defer.DeferredSemaphore(num_parallel)
    deferreds = [semaphore.run(f, *a, **kw) for (f, a, kw) in functions]
    return defer.gatherResults(deferreds)


def submit_application(pkgme_root, application, reporter, hostname, timeout):
    reporter.timestamp()
    reporter.building_package(application)
    d = WebServer.start(mod_reactor, hostname=hostname, port=0)
    def got_response((method, body)):
        reporter.timestamp()
        reporter.pkgme_success(application, body)
    def got_failure(failure):
        failure.trap(PkgmeServiceError)
        reporter.timestamp()
        reporter.pkgme_failure(application, failure.value)
    def unexpected_error(f):
        reporter.timestamp()
        reporter.unexpected_error(application, f)
    d.addCallback(send_api_request, application, pkgme_root, timeout=timeout)
    d.addCallbacks(got_response, got_failure)
    d.addErrback(unexpected_error)
    return d


def load_applications(source_file=None, devportal=None, credentials_file=None):
    """Load the applications list from where ever."""
    if source_file:
        return source_file.read()

    if devportal:
        if not credentials_file:
            raise UserError(
                "Must provide credentials in order to get application list "
                "from a devportal.")
        credentials = parse_json(credentials_file.read())
        devportal_url = MYAPPS_SERVERS[devportal]
        return myapps_GET(devportal_url, credentials)

    raise UserError(
        "Cannot get application list.  Please specify either a source "
        "file or a devportal to get the list from.")


def filter_applications(apps, max_apps=None, handle_internal='keep',
                        states=None):
    if handle_internal == 'convert':
        apps = imap(_convert_internal_data, apps)
    elif handle_internal == 'hide':
        apps = (a for a in apps if 'internal_packages' not in a['package_url'])
    if states:
        apps = (a for a in apps if a['state'] in states)
    if max_apps:
        apps = islice(apps, max_apps)
    return apps


def _convert_internal_data(application):
    application = dict(application)
    application['package_url'] = application['package_url'].replace(
        'internal_packages', 'site_media/packages')
    return application


def make_options():
    parser = argparse.ArgumentParser("Resubmit all applications to pkgme-service")
    add_service_url_options(parser)
    parser.add_argument("--dry-run", dest="dry_run", action="store_true")
    parser.add_argument(
        "--internal-urls", dest="internal_urls",
        choices=("convert", "hide", "keep"), default="keep")
    json_source = parser.add_mutually_exclusive_group(required=True)
    json_source.add_argument(
        "--devportal", choices=MYAPPS_SERVERS, default="production")
    json_source.add_argument("--from-file", type=argparse.FileType('r'))
    parser.add_argument("--credentials", type=argparse.FileType('r'))
    parser.add_argument(
        "--timeout", action='store', type=int, dest='timeout', default=30,
        help=('If packaging an app takes longer than this, abort it.'))
    parser.add_argument(
        "-n", "--max-apps", action='store', type=int, dest='max_apps',
        default=0)
    parser.add_argument(
        "-s", "--include-state", action='append', dest="include_state",
        help=("Application states to include. By default, everything we "
              "get from MyApps, which is all apps that aren't Draft, "
              "Deleted or Rejected."))
    parser.add_argument("--dump-json", dest='dump_json', action='store_true')
    parser.add_argument(
        "-o", "--output-file", type=argparse.FileType('w'), default="-",
        help="Where to send the output to, defaults to stdout.")
    parser.add_argument(
        '-j', '--num-parallel', type=int, default=1,
        help="Number of requests to have in parallel.")
    return parser


def disaster(error):
    sys.stderr.write("UNEXPECTED ERROR\n")
    sys.stderr.write(error.getTraceback())
    sys.stderr.write('\n')


def submit_applications(applications, pkgme_url, reporter, hostname, timeout,
                        num_parallel=1):
    d = run_many(
        [(submit_application,
          (pkgme_url, app, reporter, hostname, timeout), {})
         for app in applications],
        num_parallel=num_parallel)
    d.addErrback(disaster)
    d.addBoth(lambda x: mod_reactor.stop())
    return d


def oauth_sign_request(url, creds, http_method='GET', realm='pkgme-service'):
    """Sign a request with OAuth credentials."""
    # XXX: This duplicates stuff in pkgme-service djpkgme.tasks, *and*
    # probably stuff in piston_mini_client and pkgme-service-python.  Can we
    # sort this out please?
    consumer = OAuthConsumer(creds['consumer_key'], creds['consumer_secret'])
    token = OAuthToken(creds['token'], creds['token_secret'])
    oauth_request = OAuthRequest.from_consumer_and_token(
        consumer, token, http_url=url, http_method=http_method)
    oauth_request.sign_request(OAuthSignatureMethod_PLAINTEXT(),
        consumer, token)
    return oauth_request.to_header(realm)


def myapps_GET(url, creds):
    """Put ``json_body`` to MyApps at ``url``."""
    # XXX: This duplicates stuff in pkgme-service djpkgme.tasks, *and*
    # probably stuff in piston_mini_client and pkgme-service-python.  Can we
    # sort this out please?
    GOOD_RESPONSES = (200,)

    headers = oauth_sign_request(url, creds, 'GET')
    headers['Content-type'] = 'application/json'
    headers['Accept'] = 'application/json'
    getter = Http(disable_ssl_certificate_validation=True)
    method = 'GET'
    response, content = getter.request(url, method=method, headers=headers)
    if response.status not in GOOD_RESPONSES:
        raise RuntimeError(url, method, response.status, content)
    return content


def run_scoreboard(args):
    content = load_applications(
        args.from_file, args.devportal, args.credentials)
    applications = filter_applications(
        parse_json(content), args.max_apps, args.internal_urls,
        args.include_state)
    if args.dump_json:
        json.dump(
            list(applications), args.output_file, sort_keys=True, indent=2)
        args.output_file.flush()
        return 0
    pkgme_url = get_service_url(None, args.remote_hostname, args.remote_url)
    reporter = SubunitReporter(sys.stdout)
    if args.num_parallel > 1:
        reporter = BufferedReporter(reporter)
    if args.dry_run:
        for app in applications:
            reporter.building_package(app)
            reporter.pkgme_success(app, {})
    else:
        mod_reactor.callWhenRunning(
            submit_applications,
            applications, pkgme_url, reporter, args.hostname, args.timeout,
            args.num_parallel)
        mod_reactor.run()
    return 0


def main():
    parser = make_options()
    args = parser.parse_args()
    try:
        return run_scoreboard(args)
    except UserError, e:
        sys.stderr.write('ERROR: ')
        sys.stderr.write(str(e))
        sys.stderr.write('\n')
        return 3


if __name__ == '__main__':
    sys.exit(main())

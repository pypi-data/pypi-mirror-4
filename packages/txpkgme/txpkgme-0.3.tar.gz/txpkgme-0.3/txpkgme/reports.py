#!/usr/bin/env python
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
from itertools import ifilter, imap
import json
from StringIO import StringIO
import sys

from subunit.filters import run_tests_from_stream
from testtools import TestByTestResult
from testtools.helpers import map_values

from .utils import dump_json


def make_base_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--include-state", action='append', dest="include_state",
        help=("Application states to include. By default, everything we "
              "get from MyApps, which is all apps that aren't Draft, "
              "Deleted or Rejected."))
    parser.add_argument(
        "-Q", "--include-queue", action='append', dest="include_queue",
        help=("Application queues to include. Either 'arb' or 'commercial'. "
              "By default, everything is included."))
    parser.add_argument(
        'subunit', type=argparse.FileType('rb'), nargs='?',
        default='-', help='subunit data to report on')
    return parser


def make_options():
    parser = make_base_options()
    parser.add_argument(
        "--show-urls", action='store_true',
        help=("Show URLs for all failing packages beneath summary."))
    return parser


SUCCESSFUL_STATUSES = ('success',)


def was_successful(result):
    return result['status'] in SUCCESSFUL_STATUSES


def calculate_success_ratio(parsed_results):
    total = len(parsed_results)
    successes = len(filter(was_successful, parsed_results))
    return successes, total - successes


def median(xs, percentile=0.5):
    if not xs:
        raise ValueError("Cannot find median of empty sequence: %r" % (xs,))
    xs = sorted(xs)
    midpoint = (len(xs) - 1) * percentile
    i = int(midpoint)
    if midpoint == i:
        return xs[i]
    else:
        return (xs[i] + xs[i + 1]) / 2.0


def get_duration(result):
    duration = result.get('duration', None)
    if duration:
        return duration.total_seconds()


def iter_times(results):
    return imap(get_duration, results)


def format_success_failure(success, failure):
    total = success + failure
    if not total:
        return "No results found"
    percentage = 100 * float(success) / float(total)
    return '\n'.join(
        ["Successful: %s" % (success,),
         "Failed: %s" % (failure,),
         "Total: %s" % (total,),
         "",
         "Percentage: %0.2f%%" % (percentage,),
         "",
         ])


def get_error_text(details):
    if not details:
        return
    traceback = details.get('traceback', None)
    if traceback:
        return traceback.strip().splitlines()[-1].strip().lstrip('|').strip()
    error = details.get('error', None)
    if error:
        return error
    return None


MULTI_ARCH = u'MULTI-ARCH'
NO_BACKEND = u'NO-BACKEND'
TIMEOUT = u'TIMEOUT'
MISSING_DEP = u'MISSING-DEP'
NOT_IMPLEMENTED_YET = u'NOT-IMPLEMENTED-YET'
UNPACKAGEABLE = u'UNPACKAGEABLE'
OTHER = u'OTHER'


def map_error(details):
    error = get_error_text(details)
    if not error:
        return
    category, extra = map_error_to_tuple(error)
    if extra is None:
        return category
    return extra


def map_error_to_tuple(error):
    if 'TimeoutError' in error:
        return TIMEOUT, None
    if error.startswith('No eligible backends'):
        return NO_BACKEND, None
    multiarch_tag = 'Only a single architecture at a time is supported.'
    if error.endswith(multiarch_tag):
        return MULTI_ARCH, None
    missing_dep_tag = "Can't find dependency for"
    if error.startswith(missing_dep_tag):
        return MISSING_DEP, error[len(missing_dep_tag):].strip().strip('"')
    if 'not implemented yet' in error:
        return (NOT_IMPLEMENTED_YET,
                error.split('not implemented yet', 1)[0].strip())
    if ' will never be implemented' in error:
        return (UNPACKAGEABLE,
                error.split(' will never be implemented', 1)[0].strip())
    return OTHER, error


def group_errors(parsed_results):
    error_to_results = {}
    for result in parsed_results:
        error = map_error(result.get('details', None))
        if not error:
            continue
        if error in error_to_results:
            error_to_results[error].append(result)
        else:
            error_to_results[error] = [result]
    return error_to_results


def format_errors(errors, show_urls=False):
    for error, results in errors:
        yield '%s: %s' % (error.strip(), len(results))
        if not show_urls:
            continue
        for result in results:
            yield '  %s' % (get_app_url(result),)


def _parse_detail(detail):
    try:
        return detail.as_text()
    except ValueError:
        return json.loads(''.join(detail.iter_bytes()))


def parse_details(details):
    return map_values(_parse_detail, details)


def parse_subunit(subunit_stream):
    output = []
    def on_test(test, status, start_time, stop_time, tags, details):
        output.append(
            {'test_id': test.id(),
             'status': status,
             'details': parse_details(details),
             'duration': stop_time - start_time,
             'tags': tags,
             })
    result = TestByTestResult(on_test)
    run_tests_from_stream(
        subunit_stream, result, passthrough_stream=StringIO())
    return output


def _encode_csv_cell(cell):
    text = unicode(cell)
    if u',' in text:
        text = u'"%s"' % (text,)
    return text.encode('utf8')


def _result_to_csv_row(result, columns):
    return ','.join(map(_encode_csv_cell, (col(result) for col in columns)))


def results_to_csv(results, output):
    columns = [
        ('app_id', get_app_id),
        ('name', get_app_name),
        ('queue', get_app_queue),
        ('state', get_app_state),
        ('successful', was_successful),
        ('backend', get_backend),
        ('error', get_error_category),
        ('duration', get_duration),
        ('url', get_app_url),
        ]
    titles, functions = zip(*columns)
    output.write(','.join('"%s"' % title for title in titles))
    output.write('\n')
    for result in results:
        output.write(_result_to_csv_row(result, functions))
        output.write('\n')


def get_app_state(test):
    for tag in test.get('tags', []):
        if tag.startswith('state='):
            return tag[6:]
    return None


def get_app_name(test):
    return test['test_id'].rsplit(':', 1)[0]


def get_app_id(test):
    return test['test_id'].rsplit(':', 1)[1]


def get_app_url(test):
    return test['details']['myapps']['package_url']


def get_backend(test):
    backend = guess_backend(
        get_error_text(test['details']),
        get_app_url(test),
        was_successful(test))
    if backend:
        return backend
    return 'UNKNOWN'


def guess_backend(error_text, url=None, successful=False):
    if not error_text:
        # The only useful information we get back about the backend actually
        # used comes from the error.  Still, we can guess which backend was
        # probably used based on a few simple heuristics.
        if url and url.endswith('.pdf'):
            return 'PDF'
        if successful:
            # The only other successful backend as of 2012-09-24 is the binary
            # backend.
            return 'binary'
        return None
    category, extra = map_error_to_tuple(error_text)
    if category == NO_BACKEND:
        return NO_BACKEND
    if category in (UNPACKAGEABLE, NOT_IMPLEMENTED_YET):
        return extra
    if category in (MISSING_DEP, MULTI_ARCH):
        return 'binary'
    return None


def get_app_queue(test):
    url = get_app_url(test)
    if '/internal_packages/' in url:
        return 'commercial'
    if '/site_media/arb/' in url:
        return 'arb'
    return None


def get_error_category(test):
    error = get_error_text(test.get('details', None))
    if not error:
        return ''
    return map_error_to_tuple(error)[0]


def make_filter(include_state=None, include_queue=None):
    def philtre(result):
        return (
            (include_state is None
             or get_app_state(result) in include_state)
            and (include_queue is None
                 or get_app_queue(result) in include_queue))
    return philtre


def report_on_subunit(results, output_stream, show_urls=False):
    """Report interesting information from 'input_stream' to 'output_stream'.
    """
    w = output_stream.write
    results = list(results)
    if not results:
        w("No results\n")
        return
    successes, failures = calculate_success_ratio(results)
    w('Summary\n')
    w('-------\n')
    w(format_success_failure(successes, failures))
    w('Median run time: ')
    w('%0.2fs\n' % (median(iter_times(results))),)
    w('95% run time: ')
    w('%0.2fs\n' % (median(iter_times(results), 0.95)),)
    w('\n')
    w('Errors\n')
    w('------\n')
    errors = sorted(group_errors(results).items())
    for line in format_errors(errors, show_urls):
        w(line)
        w('\n')


def iter_results(args):
    return ifilter(
        make_filter(args.include_state, args.include_queue),
        parse_subunit(args.subunit))


def summarize_data():
    parser = make_options()
    args = parser.parse_args()
    report_on_subunit(iter_results(args), sys.stdout, args.show_urls)
    return 0


def subunit_to_json():
    OUTPUTS = {
        'json': lambda results, output: dump_json(list(results), output),
        'csv': results_to_csv,
    }
    parser = make_base_options()
    parser.add_argument('--format', choices=OUTPUTS.keys(), default='json')
    args = parser.parse_args()
    OUTPUTS[args.format](iter_results(args), sys.stdout)
    return 0

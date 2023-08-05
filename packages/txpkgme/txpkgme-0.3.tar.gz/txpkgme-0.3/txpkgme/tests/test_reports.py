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

from datetime import timedelta
import random
from StringIO import StringIO
import traceback

from testtools import TestCase
from testtools.content import (
    json_content,
    text_content,
    )
from twisted.internet.error import TimeoutError

from txpkgme.reports import (
    calculate_success_ratio,
    get_app_queue,
    get_app_state,
    guess_backend,
    map_error,
    median,
    format_success_failure,
    MULTI_ARCH,
    NO_BACKEND,
    parse_details,
    parse_subunit,
    TIMEOUT,
    )


def get_stack_trace(f, *a, **kw):
    try:
        raise f(*a, **kw)
    except:
        return traceback.format_exc()


class TestFormatSuccessFailure(TestCase):

    def test_basic(self):
        output = format_success_failure(1, 2)
        self.assertEqual(
            '\n'.join(
                ["Successful: 1",
                 "Failed: 2",
                 "Total: 3",
                 "",
                 "Percentage: 33.33%",
                 "",
                 ]), output)

    def test_zero(self):
        output = format_success_failure(0, 0)
        self.assertEqual("No results found", output)


class TestParseSubunit(TestCase):

    def test_empty(self):
        self.assertEqual([], parse_subunit(StringIO()))

    def test_simple_success(self):
        subunit_data = """
time: 2012-01-01 00:00:00.000000Z
test: foo:32
time: 2012-01-01 00:00:01.000000Z
success: foo:32
time: 2012-01-02 00:00:00.000000Z
"""
        stream = StringIO(subunit_data)
        self.assertEqual(
            [{'test_id': 'foo:32', 'status': 'success',
              'tags': set(), 'details': {},
              'duration': timedelta(seconds=1)}],
            parse_subunit(stream))

    def test_tags(self):
        subunit_data = """
time: 2012-01-01 00:00:00.000000Z
test: foo:32
tags: something
time: 2012-01-01 00:00:01.000000Z
success: foo:32
time: 2012-01-02 00:00:00.000000Z
"""
        stream = StringIO(subunit_data)
        self.assertEqual(
            [{'test_id': 'foo:32', 'status': 'success',
              'tags': set(['something']),
              'details': {}, 'duration': timedelta(seconds=1)}],
            parse_subunit(stream))


    def test_details(self):
        details = {'foo': text_content('bar'),
                   'bar': json_content({'baz': 'qux'})}
        self.assertEqual(
            {'foo': 'bar', 'bar': {'baz': 'qux'}}, parse_details(details))


class TestCalculateSuccessRatio(TestCase):

    def test_empty(self):
        self.assertEqual((0, 0), calculate_success_ratio([]))

    def test_single_success(self):
        data = [{'status': 'success'}]
        success, failure = calculate_success_ratio(data)
        self.assertEqual((1, 0), (success, failure))

    def test_single_failure(self):
        data = [{'status': 'failure'}]
        success, failure = calculate_success_ratio(data)
        self.assertEqual((0, 1), (success, failure))


class TestMapError(TestCase):

    def test_timeout(self):
        tb = get_stack_trace(
            TimeoutError, "User timeout caused connection failure.")
        timeout_details = {'traceback': tb}
        self.assertEqual(TIMEOUT, map_error(timeout_details))

    def test_no_backend(self):
        content = (
            'No eligible backends for /tmp/tmpH94djh/working. Tried '
            'binary, pdf. The following backends were disallowed by '
            'policy: cmake, dummy, vala, python.')
        details = {'traceback': content}
        self.assertEqual(NO_BACKEND, map_error(details))

    def test_unrecognized_from_server(self):
        content = 'IOError: Disk space full'
        details = {'error': content}
        self.assertEqual(content, map_error(details))

    def test_no_error(self):
        self.assertIs(None, map_error({'error': {}}))
        self.assertIs(None, map_error({}))
        self.assertIs(None, map_error({'other-data': {}}))

    def test_multiarch(self):
        content = (
            "Found architecture 'i386' for '/tmp/tmpy7mW1g/working/libx.so.0' "
            "but also found architecture 'amd64' earlier. Only a single "
            "architecture at a time is supported.")
        details = {'traceback': content}
        self.assertEqual(MULTI_ARCH, map_error(details))

    def test_backend_script_failure(self):
        big_script_failure = """\
/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/backends/binary/all_info failed with returncode 1. Output:
 | Traceback (most recent call last):
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/backends/binary/all_info", line 13, in <module>
 |     main()
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/backends/binary/all_info", line 9, in main
 |     BinaryBackend().dump_json()
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/metadata.py", line 465, in dump_json
 |     info = self.get_info(self.get_metadata())
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/metadata.py", line 453, in get_info
 |     info[element] = self._calculate_info_element(element, metadata)
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/metadata.py", line 232, in _calculate_info_element
 |     return method(metadata, *args, **kwargs)
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/binary.py", line 348, in get_build_depends
 |     return ', '.join(guess_dependencies(self.path))
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/binary.py", line 305, in guess_dependencies
 |     libraries = get_shared_library_dependencies(binaries)
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/binary.py", line 210, in get_shared_library_dependencies
 |     libraries = needed_libraries_from_objdump(paths)
 |   File "/var/lib/juju/units/pkgme-service-0/charm/pkgme-service/sourcecode/pkgme-devportal/devportalbinary/binary.py", line 201, in needed_libraries_from_objdump
 |     "Can not handle '%s'" % architecture)
 | devportalbinary.binary.UnsupportedArchitecture: Can not handle 'i386:x86-64'
"""
        details = {'traceback': big_script_failure}
        mapped = map_error(details)
        self.assertEqual(
            "devportalbinary.binary.UnsupportedArchitecture: Can not handle 'i386:x86-64'",
            mapped)

    def test_unrecognized_local(self):
        try:
            1/0
        except ZeroDivisionError:
            tb = traceback.format_exc()
        details = {'traceback': tb}
        self.assertEqual(tb.splitlines()[-1].strip(), map_error(details))


class TestGetState(TestCase):

    def test_no_tags(self):
        self.assertEqual(None, get_app_state({}))

    def test_empty_tags(self):
        self.assertEqual(None, get_app_state({'tags': set()}))

    def test_irrelevant_tags(self):
        self.assertEqual(None, get_app_state({'tags': set(['foo', 'bar'])}))

    def test_state(self):
        test = {'tags': set(['state=Published'])}
        self.assertEqual('Published', get_app_state(test))


class TestGetAppQueue(TestCase):

    def test_arb(self):
        url = 'http://myapps.developer.ubuntu.com/site_media/arb/packages/2012/02/freestuff.tar.gz'
        queue = get_app_queue({'details': {'myapps': {'package_url': url}}})
        self.assertEquals('arb', queue)

    def test_commercial(self):
        url = 'https://myapps.developer.ubuntu.com/internal_packages/2011/06/whatever.tar.gz'
        queue = get_app_queue({'details': {'myapps': {'package_url': url}}})
        self.assertEquals('commercial', queue)


class TestGuessBackend(TestCase):

    def test_no_eligible(self):
        backend = guess_backend('No eligible backends')
        self.assertEqual(NO_BACKEND, backend)

    def test_unimplemented(self):
        backend = guess_backend('Foo Bar not implemented yet')
        self.assertEqual('Foo Bar', backend)

    def test_unimplementable(self):
        backend = guess_backend('Foo Bar will never be implemented')
        self.assertEqual('Foo Bar', backend)

    def test_no_error(self):
        backend = guess_backend(None)
        self.assertIs(None, backend)

    def test_unrecognized_string(self):
        backend = guess_backend(self.getUniqueString())
        self.assertIs(None, backend)

    def test_pdf_url(self):
        backend = guess_backend(None, 'http://example.com/foo.pdf')
        self.assertEqual('PDF', backend)

    def test_timeout(self):
        backend = guess_backend("TimeoutError")
        self.assertEqual(None, backend)

    def test_missing_dep_implies_binary(self):
        backend = guess_backend("Can't find dependency for 'libfoo.so'")
        self.assertEqual('binary', backend)

    def test_multi_arch_implies_binary(self):
        backend = guess_backend(
            "Only a single architecture at a time is supported.")
        self.assertEqual('binary', backend)

    def test_successful_non_pdf_is_binary(self):
        backend = guess_backend(None, 'http://example.com/whatever', True)
        self.assertEqual('binary', backend)


def shuffle(sequence):
    shuffled = list(sequence)
    random.shuffle(shuffled)
    return shuffled


def num_less_than(sequence, limit):
    return len([1 for x in sequence if x <= limit])


def ratio_less_than(sequence, limit):
    return num_less_than(sequence, limit) / float(len(sequence))


class TestMedian(TestCase):

    def test_odd_length(self):
        self.assertEqual(2, median(shuffle([1, 2, 3])))
        self.assertEqual(3, median(shuffle([1, 2, 3, 4, 5])))

    def test_even_length(self):
        self.assertEqual(2.5, median(shuffle([1, 2, 3, 4])))
        self.assertEqual(3.5, median(shuffle([1, 2, 3, 4, 5, 6])))

    def test_singleton(self):
        self.assertEqual(1, median([1]))

    def test_percentile(self):
        self.assertEqual(8.5, median(shuffle(range(10)), 0.9))
        self.assertEqual(17.5, median(shuffle(range(20)), 0.9))
        self.assertEqual(89.5, median(shuffle(range(100)), 0.9))

    def assertMedianConsistent(self, sequence, percentile):
        point = median(sequence, percentile)
        self.assertEqual(ratio_less_than(sequence, point), percentile)

    def test_consistency(self):
        self.assertMedianConsistent(shuffle(range(10)), 0.9)
        self.assertMedianConsistent(shuffle(range(20)), 0.9)
        self.assertMedianConsistent(shuffle(range(100)), 0.9)

    def test_empty_sequence(self):
        self.assertRaises(ValueError, median, [])

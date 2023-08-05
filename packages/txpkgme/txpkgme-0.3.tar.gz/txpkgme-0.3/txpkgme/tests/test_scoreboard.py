from datetime import (
    datetime,
    timedelta,
    )
import json
import os

from fixtures import (
    Fixture,
    MonkeyPatch,
    TempDir,
    )
from StringIO import StringIO
from testtools import TestCase
from testtools.matchers import (
    Contains,
    ContainsDict,
    Equals,
    MatchesDict,
    )
from testtools.testresult.real import utc
from twisted.python.failure import Failure

from txpkgme.harness import PkgmeServiceError
from txpkgme.reports import parse_subunit
from txpkgme.scoreboard import (
    BufferedReporter,
    _convert_internal_data,
    filter_applications,
    make_options,
    run_scoreboard,
    SubunitReporter,
    )


def make_app(factory, name=None, myapps_id=None, state='UNKNOWN'):
    if name is None:
        name = factory.getUniqueString()
    if myapps_id is None:
        myapps_id = factory.getUniqueInteger()
    return {
        'name': name,
        'myapps_id': myapps_id,
        'state': state}


def make_error(data):
    return PkgmeServiceError(json.dumps(data))


def make_failure():
    try:
        1/0
    except ZeroDivisionError:
        return Failure()


class DeterministicClock(Fixture):

    def __init__(self, times):
        super(DeterministicClock, self).__init__()
        self._times = times

    def setUp(self):
        super(DeterministicClock, self).setUp()
        self.useFixture(
            MonkeyPatch('txpkgme.scoreboard.now', iter(self._times).next))


def _advancing_times(start, interval):
    now = start
    while True:
        yield now
        now += interval


def AdvancingClock(start=None, interval=None):
    if start is None:
        start = datetime(2012, 1, 1, tzinfo=utc)
    if interval is None:
        interval = timedelta(seconds=1)
    return DeterministicClock(_advancing_times(start, interval))


class TestSubunitReporter(TestCase):

    def test_extended_character_name(self):
        name = u'\u2603'
        app = make_app(self, name)
        test = SubunitReporter(StringIO())._to_test(app)
        self.assertEqual(
            '%s:%s' % (name.encode('utf8'), app['myapps_id']), test.id())

    def test_success(self):
        app = make_app(self)
        data = {'foo': 'bar'}
        stream = StringIO()
        reporter = SubunitReporter(stream)
        reporter.building_package(app)
        reporter.pkgme_success(app, data)
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(
            test, ContainsDict(
                {'details': Equals({'pkgme': data,
                                    'myapps': app}),
                 'tags': Equals(set(['state=UNKNOWN'])),
                 'status': Equals('success'),
                 'test_id': Equals('%s:%s' % (app['name'], app['myapps_id'])),
                 }))

    def test_success_with_state(self):
        state = self.getUniqueString()
        app = make_app(self, state=state)
        stream = StringIO()
        reporter = SubunitReporter(stream)
        reporter.building_package(app)
        reporter.pkgme_success(app, {})
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(
            test, ContainsDict(
                {'tags': Equals(set(['state=%s' % (state,)]))}))

    def test_failure(self):
        app = make_app(self)
        error = make_error({})
        stream = StringIO()
        reporter = SubunitReporter(stream)
        reporter.building_package(app)
        reporter.pkgme_failure(app, error)
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(
            test, ContainsDict(
                {'details': Equals(
                        {u'extra_data': {},
                         u'traceback': 'No traceback',
                         u'myapps': app}),
                 'status': Equals('failure'),
                 'test_id': Equals('%s:%s' % (app['name'], app['myapps_id'])),
                 }))

    def test_error(self):
        app = make_app(self)
        error = make_failure()
        stream = StringIO()
        reporter = SubunitReporter(stream)
        reporter.building_package(app)
        reporter.unexpected_error(app, error)
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(
            test, ContainsDict(
                {'details': MatchesDict(
                        {u'traceback': Contains('ZeroDivisionError'),
                         u'myapps': Equals(app)}),
                 'status': Equals('failure'),
                 'test_id': Equals('%s:%s' % (app['name'], app['myapps_id'])),
                 }))

    def test_timestamp(self):
        self.useFixture(AdvancingClock())
        app = make_app(self)
        stream = StringIO()
        reporter = SubunitReporter(stream)
        a = reporter.timestamp()
        reporter.building_package(app)
        b = reporter.timestamp()
        reporter.pkgme_success(app, {})
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(test, ContainsDict({'duration': Equals(b - a)}))

    def test_explicit_timestamp(self):
        self.useFixture(AdvancingClock())
        app = make_app(self)
        stream = StringIO()
        reporter = SubunitReporter(stream)
        a = datetime(2012, 5, 12, tzinfo=utc)
        reporter.timestamp(a)
        reporter.building_package(app)
        b = datetime(2012, 5, 13, tzinfo=utc)
        reporter.timestamp(b)
        reporter.pkgme_success(app, {})
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(test, ContainsDict({'duration': Equals(b - a)}))


class TestBufferedReporter(TestCase):

    def test_building_package_doesnt_send(self):
        stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(stream))
        reporter.building_package(make_app(self))
        self.assertEqual('', stream.getvalue())

    def test_matches_non_buffered_success(self):
        app = make_app(self)
        buffer_stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(buffer_stream))
        reporter.building_package(app)
        reporter.pkgme_success(app, {})
        stream = StringIO()
        reporter = SubunitReporter(stream)
        reporter.building_package(app)
        reporter.pkgme_success(app, {})
        self.assertEqual(stream.getvalue(), buffer_stream.getvalue())

    def test_matches_non_buffered_failure(self):
        app = make_app(self)
        buffer_stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(buffer_stream))
        reporter.building_package(app)
        reporter.pkgme_failure(app, make_error({}))
        stream = StringIO()
        reporter = SubunitReporter(stream)
        reporter.building_package(app)
        reporter.pkgme_failure(app, make_error({}))
        self.assertEqual(stream.getvalue(), buffer_stream.getvalue())

    def test_matches_non_buffered_error(self):
        app = make_app(self)
        failure = make_failure()
        buffer_stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(buffer_stream))
        reporter.building_package(app)
        reporter.unexpected_error(app, failure)
        stream = StringIO()
        reporter = SubunitReporter(stream)
        reporter.building_package(app)
        reporter.unexpected_error(app, failure)
        self.assertEqual(stream.getvalue(), buffer_stream.getvalue())

    def test_timestamp_success(self):
        self.useFixture(AdvancingClock())
        app = make_app(self)
        stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(stream))
        a = reporter.timestamp()
        reporter.building_package(app)
        b = reporter.timestamp()
        reporter.pkgme_success(app, {})
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(test, ContainsDict({'duration': Equals(b - a)}))

    def test_timestamp_failure(self):
        self.useFixture(AdvancingClock())
        app = make_app(self)
        stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(stream))
        a = reporter.timestamp()
        reporter.building_package(app)
        b = reporter.timestamp()
        reporter.pkgme_failure(app, make_error({}))
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(test, ContainsDict({'duration': Equals(b - a)}))

    def test_timestamp_error(self):
        self.useFixture(AdvancingClock())
        app = make_app(self)
        stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(stream))
        a = reporter.timestamp()
        reporter.building_package(app)
        b = reporter.timestamp()
        reporter.unexpected_error(app, make_failure())
        stream.seek(0)
        [test] = parse_subunit(stream)
        self.assertThat(test, ContainsDict({'duration': Equals(b - a)}))

    def test_concurrent_results_timing(self):
        times = [
            datetime(2012, 1, 1, tzinfo=utc),
            datetime(2012, 1, 2, tzinfo=utc),
            datetime(2012, 1, 4, tzinfo=utc),
            datetime(2012, 1, 8, tzinfo=utc),
            ]
        self.useFixture(DeterministicClock(times))
        app1 = make_app(self, name='foo')
        app2 = make_app(self, name='bar')
        stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(stream))
        a = reporter.timestamp()
        reporter.building_package(app1)
        b = reporter.timestamp()
        reporter.building_package(app2)
        c = reporter.timestamp()
        reporter.pkgme_success(app1, {})
        d = reporter.timestamp()
        reporter.pkgme_success(app2, {})
        stream.seek(0)
        parsed = parse_subunit(stream)
        [test1, test2] = parsed
        self.assertEqual(c - a, test1['duration'])
        self.assertEqual(d - b, test2['duration'])

    def test_interleaved_results(self):
        # Interleaved results to a BufferedReporter look like sequential
        # results to a normal reporter.
        app1 = make_app(self, name='foo')
        app2 = make_app(self, name='bar')
        interleaved_stream = StringIO()
        reporter = BufferedReporter(SubunitReporter(interleaved_stream))
        reporter.building_package(app1)
        reporter.building_package(app2)
        reporter.pkgme_success(app1, {})
        reporter.pkgme_success(app2, {})
        straight_stream = StringIO()
        reporter = SubunitReporter(straight_stream)
        reporter.building_package(app1)
        reporter.pkgme_success(app1, {})
        reporter.building_package(app2)
        reporter.pkgme_success(app2, {})
        self.assertEqual(
            straight_stream.getvalue(), interleaved_stream.getvalue())


class TestExternalRewrite(TestCase):

    def test_modified_internal(self):
        # When running externally from the data centre, we want to use
        # external URLs.
        data = {
            'package_url': (
                'https://myapps.developer.ubuntu.com/internal_packages/2011/'
                '05/example_1.1.0_with_valid_control.tar_.gz'),
            'arbitrary': 'fooey',
            }
        new_data = _convert_internal_data(data)
        data['package_url'] = (
            "https://myapps.developer.ubuntu.com/site_media/packages/"
            "2011/05/example_1.1.0_with_valid_control.tar_.gz")
        self.assertEqual(data, new_data)

    def test_unmodified_icon(self):
        # Icons have public URLs always.
        icons =  {
            '48x48': ('https://software-center.ubuntu.com/site_media/icons/'
                      '2011/05/fluendo-dvd.png'),
            }
        data = {
            'package_url': (
                'https://myapps.developer.ubuntu.com/internal_packages/2011/'
                '05/example_1.1.0_with_valid_control.tar_.gz'),
            'arbitrary': 'fooey',
            'icons': icons,
            }
        expected_icons = {
            '48x48': (
                'https://software-center.ubuntu.com/site_media/icons/'
                '2011/05/fluendo-dvd.png'),
            }
        new_data = _convert_internal_data(data)
        self.assertEqual(expected_icons, new_data['icons'])


class TestFilterApplications(TestCase):

    def test_default_unfiltered(self):
        apps = [
            {'state': 'ReviewPending',
             'package_name': 'foo',
             },
            {'state': 'Published',
             'package_name': 'bar',
             },
            ]
        filtered = filter_applications(apps)
        self.assertEqual(apps, list(filtered))

    def test_empty_states_means_all(self):
        apps = [
            {'state': 'ReviewPending',
             'package_name': 'foo',
             },
            {'state': 'Published',
             'package_name': 'bar',
             },
            ]
        filtered = filter_applications(apps, states=[])
        self.assertEqual(apps, list(filtered))

    def test_provide_states_means_only_those(self):
        published = {
            'state': 'Published',
            'package_name': 'bar',
            }
        apps = [
            {'state': 'ReviewPending',
             'package_name': 'foo',
             },
            published,
            ]
        filtered = filter_applications(apps, states=['Published'])
        self.assertEqual([published], list(filtered))

    def test_max_apps_last(self):
        a = {
            'state': 'Published',
            'package_name': 'a',
            }
        b = {
            'state': 'ReviewPending',
            'package_name': 'b',
            }
        c = {
            'state': 'Published',
            'package_name': 'c',
            }
        filtered = filter_applications(
            [a, b, c], states=['Published'], max_apps=2)
        self.assertEqual([a, c], list(filtered))


class TestRunScoreboard(TestCase):

    def get_args(self, *args):
        return make_options().parse_args(list(args))

    def test_no_include_state(self):
        path = self.useFixture(TempDir()).path
        input_data = ['foo', 'bar']
        input_file = os.path.join(path, 'input.json')
        with open(input_file, 'w') as f:
            json.dump(input_data, f)
        output_file = os.path.join(path, 'output.json')
        args = self.get_args(
            '--from-file', input_file,
            '--dump-json',
            '--output-file', output_file)
        return_code = run_scoreboard(args)
        self.assertEqual(0, return_code)
        self.assertEqual(
            json.load(open(input_file, 'r')),
            json.load(open(output_file, 'r')))

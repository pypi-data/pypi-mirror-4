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
import os
import time

from fixtures import (
    TempDir,
    )
from testtools import TestCase
from testtools._spinner import (
    DeferredNotFired,
    extract_result,
    )
from twisted.internet.defer import Deferred
from twisted.internet.task import Clock
from twisted.web.resource import Resource

from txpkgme.submitfromdisk import (
    add_local_files,
    check_saved_output,
    delay_callbacks,
    OutputFileResultWriter,
    parse_output,
)
from txpkgme.harness import WebServer


class DelayCallbacksTest(TestCase):

    def test_no_delay(self):
        clock = Clock()
        marker = object()
        d = Deferred()
        d.addBoth(delay_callbacks, 0, clock)
        d.callback(marker)
        self.assertIs(marker, extract_result(d))

    def test_stops_firing(self):
        clock = Clock()
        marker = object()
        d = Deferred()
        d.addBoth(delay_callbacks, 5, clock)
        d.callback(marker)
        self.assertRaises(DeferredNotFired, extract_result, d)

    def test_fires_after_time(self):
        clock = Clock()
        marker = object()
        delay = 5
        d = Deferred()
        d.addBoth(delay_callbacks, 5, clock)
        d.callback(marker)
        clock.advance(delay + 1)
        self.assertIs(marker, extract_result(d))

    def test_failure(self):
        clock = Clock()
        delay = 5
        d = Deferred()
        d.addCallback(lambda x: 1/0)
        d.addBoth(delay_callbacks, 5, clock)
        d.callback(None)
        clock.advance(delay + 1)
        self.assertRaises(ZeroDivisionError, extract_result, d)



class OutputFileResultWriterTests(TestCase):

    def write(self, success, duration, msg, clock=None):
        if clock is None:
            clock = Clock()
        temp_dir = self.useFixture(TempDir()).path
        filename = os.path.join(temp_dir, "file")
        writer = OutputFileResultWriter(open(filename, 'w'), clock)
        writer.write(success, duration, msg)
        with open(filename) as f:
            contents = json.load(f)
        return contents

    def test_writes_timestamp(self):
        clock = Clock()
        contents = self.write(True, 0, 'foo', clock=clock)
        self.assertEquals(clock.seconds(), contents['timestamp'])

    def test_writes_success(self):
        contents = self.write(True, 0, 'foo')
        self.assertEquals(True, contents['successful'])

    def test_writes_failure(self):
        contents = self.write(False, 0, 'foo')
        self.assertEquals(False, contents['successful'])

    def test_writes_duration(self):
        duration = 14.3
        contents = self.write(True, duration, 'foo')
        self.assertEquals(duration, contents['duration'])

    def test_writes_msg(self):
        msg = 'foo'
        contents = self.write(True, 14.3, msg)
        self.assertEquals(msg, contents['message'])

    def test_removes_newlines_from_msg(self):
        msg = 'foo\nbar'
        contents = self.write(True, 14.3, msg)
        self.assertEquals(msg.replace("\n", "  "), contents['message'])


class ParseOutputTests(TestCase):

    def setUp(self):
        super(ParseOutputTests, self).setUp()
        self.clock = Clock()
        self.writer = OutputFileResultWriter("filename", self.clock)

    def test_splits_in_to_four_parts(self):
        result = parse_output(self.writer.get_output(False, 0, 'foo'))
        self.assertEqual(4, len(result))

    def test_parses_timestamp(self):
        result = parse_output(self.writer.get_output(False, 0, 'foo'))
        self.assertEqual(self.clock.seconds(), result['timestamp'])

    def test_parses_success(self):
        result = parse_output(self.writer.get_output(True, 0, 'foo'))
        self.assertEqual(True, result['successful'])

    def test_parses_failure(self):
        result = parse_output(self.writer.get_output(False, 0, 'foo'))
        self.assertEqual(False, result['successful'])

    def test_parses_duration(self):
        result = parse_output(self.writer.get_output(False, 14.3, 'foo'))
        self.assertEqual(14.3, result['duration'])

    def test_parses_msg(self):
        result = parse_output(self.writer.get_output(False, 14.3, 'foo bar'))
        self.assertEqual('foo bar', result['message'])


class CheckSavedOutputTests(TestCase):

    def setUp(self):
        super(CheckSavedOutputTests, self).setUp()
        self.clock = Clock()
        self.writer = OutputFileResultWriter("filename", self.clock)

    def test_failed_with_filename(self):
        duration = 12.4
        msg = "SOME ERROR"
        result, message = check_saved_output(
            self.writer.get_output(False, duration, msg), 100, 10,
            "filename")
        self.assertEqual(2, result)
        self.assertEqual(
            "Check failed in %f: %s. NB: Based on results stored "
            "in 'filename' by a cronjob" % (duration, msg),
            message)

    def test_long_ago(self):
        duration = 12.4
        msg = "SOME PASS"
        result, message = check_saved_output(
            self.writer.get_output(True, duration, msg), 100, 10,
            "filename")
        self.assertEqual(2, result)
        self.assertEqual("Last ran %f" % (self.clock.seconds()), message)

    def test_soft_timeout(self):
        duration = 12.4
        msg = "SOME PASS"
        self.clock.advance(time.time())
        result, message = check_saved_output(
            self.writer.get_output(True, duration, msg), 100, 10,
            "filename")
        self.assertEqual(1, result)
        self.assertEqual("WARN in %f: %s" % (duration, msg), message)

    def test_success(self):
        duration = 8.4
        msg = "SOME PASS"
        self.clock.advance(time.time())
        result, message = check_saved_output(
            self.writer.get_output(True, duration, msg), 100, 10,
            "filename")
        self.assertEqual(0, result)
        self.assertEqual("OK in %f: %s" % (duration, msg), message)


class TestAddLocalFiles(TestCase):

    def test_app_url(self):
        temp_dir = self.useFixture(TempDir()).path
        path = os.path.join(temp_dir, 'foo.pdf')
        with open(path, 'w') as fd:
            fd.write('hello world')
        root = Resource()
        base_url = 'http://whatever.example.com/'
        webserver = WebServer(root, base_url, None, None)
        add_local_files(webserver, path)
        app = root.children['foo.pdf']
        self.assertEqual(path, app.path)

    def test_serve_icons(self):
        temp_dir = self.useFixture(TempDir()).path
        path = os.path.join(temp_dir, 'foo.pdf')
        icons = {
            '48x48': '/foo/bar/baz.png',
            '64x64': '/foo/qux/baz.png',
            }
        root = Resource()
        base_url = 'http://whatever.example.com/'
        webserver = WebServer(root, base_url, None, None)
        add_local_files(webserver, path, icons)
        icon48 = root.children['icons'].children['48x48'].children['baz.png']
        icon64 = root.children['icons'].children['64x64'].children['baz.png']
        self.assertEqual('/foo/bar/baz.png', icon48.path)
        self.assertEqual('/foo/qux/baz.png', icon64.path)

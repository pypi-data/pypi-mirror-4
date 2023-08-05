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
import json

from testtools import TestCase

from txpkgme.utils import (
    get_extension,
    parse_json,
    serialize_extra,
    )


class TestParseJSON(TestCase):

    def test_good(self):
        good = '{"a": 1, "b": "good"}'
        self.assertEqual(json.loads(good), parse_json(good))

    def test_None(self):
        bad = None
        e = self.assertRaises(TypeError, parse_json, bad)
        self.assertEqual('expected string or buffer, got None', str(e))

    def test_bad(self):
        bad = 'not json'
        e = self.assertRaises(ValueError, parse_json, bad)
        self.assertIn(bad, str(e))


class TestSerializeExtra(TestCase):

    def test_not_time(self):
        self.assertRaises(TypeError, serialize_extra, object())

    def test_timedelta(self):
        duration = timedelta(1)
        self.assertEqual(duration.total_seconds(), serialize_extra(duration))

    def test_set(self):
        data = set(['a', 'b', 'c'])
        self.assertEqual(sorted(list(data)), serialize_extra(data))


class TestGetExtension(TestCase):

    def test_simple(self):
        self.assertEqual('txt', get_extension('foo.txt'))
        self.assertEqual('exe', get_extension('foo.exe'))

    def test_tarball(self):
        self.assertEqual('tar.gz', get_extension('foo.tar.gz'))
        self.assertEqual('tar.bz2', get_extension('foo.tar.bz2'))

    def test_none(self):
        self.assertEqual('', get_extension('foo'))

    def test_version_bits_ignored(self):
        self.assertEqual('tar.gz', get_extension('foo-1.2.3.tar.gz'))
        self.assertEqual('tar.gz', get_extension('foo-1.2.3ubuntu1.tar.gz'))

    def test_upload_repeats_ignored(self):
        self.assertEqual('tar.gz', get_extension('foo.tar___.gz'))
        self.assertEqual('tar.gz', get_extension('foo.tar_2.gz'))

    def test_from_url(self):
        url = (
            'http://myapps.developer.ubuntu.com/site_media/arb/packages/2011/'
            '12/crabhack-1.2.tar.gz')
        self.assertEqual('tar.gz', get_extension(url))
        url = (
            'http://myapps.developer.ubuntu.com/site_media/arb/packages/2012/'
            '09/unity-lens-youtube.tar.gz')
        self.assertEqual('tar.gz', get_extension(url))
        url = (
            'http://myapps.developer.ubuntu.com/site_media/arb/packages/2012/'
            '08/vault-ppa')
        self.assertEqual('', get_extension(url))

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

from testtools import TestCase

from txpkgme.nobackend import (
    gather_files_from_backend_reasons,
    gather_no_backend_data,
    is_archive,
    parse_backend_reasons,
    split_supplement_data,
    )


class TestParseBackendReasons(TestCase):

    def test_actual_reasons(self):
        data = (
            "No eligible backends for /tmp/tmp5eTX2_/working. "
            "Tried binary (No ELF binaries found.), "
            "deb-bin (No .debs found: ['MM3.tar.lzma']), "
            "deb-src (No .dsc found: ['MM3.tar.lzma']), "
            "jar (No .jars found: ['MM3.tar.lzma']), "
            "pdf (File is not a PDF: 'MM3.tar.lzma'), "
            "python-stub (No setup.py found), "
            "text (File is not a .txt: 'MM3.tar.lzma'). "
            "The following backends were disallowed by policy: "
            "cmake, dummy, vala, python, unity-webapps")
        parsed = parse_backend_reasons(data)
        self.assertEqual(
            {'binary': ("No ELF binaries found", None),
             'deb-bin': ("No .debs found", "['MM3.tar.lzma']"),
             'deb-src': ("No .dsc found", "['MM3.tar.lzma']"),
             'jar': ("No .jars found", "['MM3.tar.lzma']"),
             'pdf': ("File is not a PDF", "'MM3.tar.lzma'"),
             'python-stub': ("No setup.py found", None),
             'text': ("File is not a .txt", "'MM3.tar.lzma'"),
             }, parsed)

    def test_more_reasons(self):
        data = (
            "No eligible backends for /tmp/tmp7AKzSf/working. "
            "Tried binary (No ELF binaries found.), "
            "deb-bin (No .debs found: ['README.markdown', 'etc', "
            "'Makefile', 'usr']), "
            "deb-src (No .dsc found: ['README.markdown', 'etc', "
            "'Makefile', 'usr']), "
            "jar (No .jars found: ['README.markdown', 'etc', "
            "'Makefile', 'usr']), "
            "pdf (More files than just a PDF: ['Makefile', "
            "'README.markdown', 'etc', 'usr']), "
            "python-stub (No setup.py found), "
            "text (More files than just a .txt: ['Makefile', "
            "'README.markdown', 'etc', 'usr']). The following "
            "backends were disallowed by policy: cmake, dummy, vala, "
            "python, unity-webapps.")
        parsed = parse_backend_reasons(data)
        self.assertEqual(
            {'binary': ("No ELF binaries found", None),
             'deb-bin': ("No .debs found",
                         "['README.markdown', 'etc', 'Makefile', 'usr']"),
             'deb-src': ("No .dsc found",
                         "['README.markdown', 'etc', 'Makefile', 'usr']"),
             'jar': ("No .jars found",
                     "['README.markdown', 'etc', 'Makefile', 'usr']"),
             'pdf': ("More files than just a PDF",
                     "['Makefile', 'README.markdown', 'etc', 'usr']"),
             'python-stub': ("No setup.py found", None),
             'text': ("More files than just a .txt",
                      "['Makefile', 'README.markdown', 'etc', 'usr']"),
             }, parsed)

    def test_not_reasons(self):
        self.assertIs(None, parse_backend_reasons("Any other message"))


class TestSplitSupplementtData(TestCase):

    def test_split_supplement(self):
        data = {
            'binary': ("No ELF binaries found", None),
            'deb-bin': ("No .debs found",
                        "['README.markdown', 'etc', 'Makefile', 'usr']"),
            'deb-src': ("No .dsc found",
                        "['README.markdown', 'etc', 'Makefile', 'usr']"),
            'jar': ("No .jars found",
                    "['README.markdown', 'etc', 'Makefile', 'usr']"),
            'pdf': ("More files than just a PDF",
                    "['Makefile', 'README.markdown', 'etc', 'usr']"),
            'python-stub': ("No setup.py found", None),
            'text': ("More files than just a .txt",
                     "['Makefile', 'README.markdown', 'etc', 'usr']"),
            }
        data, supplements = split_supplement_data(data)
        self.assertEqual(
            set(["['README.markdown', 'etc', 'Makefile', 'usr']",
                 "['Makefile', 'README.markdown', 'etc', 'usr']"]),
            supplements)
        self.assertEqual(
            {'binary': "No ELF binaries found",
             'deb-bin': "No .debs found",
             'deb-src': "No .dsc found",
             'jar': "No .jars found",
             'pdf': "More files than just a PDF",
             'python-stub': "No setup.py found",
             'text': "More files than just a .txt",
             }, data)


class TestGatherFilesFromBackendReasons(TestCase):

    def test_single_file(self):
        data = set(["['MM3.tar.lzma']", "'MM3.tar.lzma'"])
        files = gather_files_from_backend_reasons(data)
        self.assertEqual(set(['MM3.tar.lzma']), files)

    def test_multiple_files(self):
        data = set(
            ["['README.markdown', 'etc', 'Makefile', 'usr']",
             "['Makefile', 'README.markdown', 'etc', 'usr']",])
        files = gather_files_from_backend_reasons(data)
        self.assertEqual(
            set(['README.markdown', 'etc', 'Makefile', 'usr']), files)


class FullNoReasonTests(TestCase):

    def test_backend(self):
        data = (
            "No eligible backends for /tmp/tmp5eTX2_/working. "
            "Tried binary (No ELF binaries found.), "
            "deb-bin (No .debs found: ['MM3.tar.lzma']), "
            "deb-src (No .dsc found: ['MM3.tar.lzma']), "
            "jar (No .jars found: ['MM3.tar.lzma']), "
            "pdf (File is not a PDF: 'MM3.tar.lzma'), "
            "python-stub (No setup.py found), "
            "text (File is not a .txt: 'MM3.tar.lzma'). "
            "The following backends were disallowed by policy: "
            "cmake, dummy, vala, python, unity-webapps")
        result = {
            'details': {
                'traceback': data,
                'myapps': {
                    'myapps_id': 42,
                    'package_url': 'http://example.com/thing',
                    },
                },
            }
        report = gather_no_backend_data(result)
        reasons, supplements = split_supplement_data(
            parse_backend_reasons(data))
        self.assertEqual(
            {'url': 'http://example.com/thing',
             'id': 42,
             'files': gather_files_from_backend_reasons(supplements),
             'reasons': reasons,
             }, report)


class IsArchiveTests(TestCase):

    def test_not_archive(self):
        self.assertEqual(
            False,
            is_archive({'url': 'http://example.com/foo.jpg',
                        'files': set(['foo.jpg'])}))

    def test_archive(self):
        self.assertEqual(
            True,
            is_archive({'url': 'http://example.com/foo.tar.gz',
                        'files': set(['foo'])}))

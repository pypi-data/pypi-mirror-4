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

from itertools import ifilter
import json
import os
import re
import sys

from .reports import (
    dump_json,
    iter_results,
    make_base_options,
    map_error,
    NO_BACKEND,
    )
from .utils import (
    count,
    format_counts,
    get_extension,
    rename_key,
    )


_backend_re = r'([A-Za-z-]+ \([^)]+\))'
def parse_backend_reasons(data, _backend_re=re.compile(_backend_re)):
    """Turn a 'no eligible data' message into actual data.

    Returns a dict mapping backend name to (reason, supplement), where
    'reason' is something like "No setup.py found" and 'supplement' is
    any supplementary information (e.g. a string representing a list of
    files).  'supplement' can be None if there's nothing useful to include.
    """
    if not data.startswith("No eligible backends for"):
        return
    result = {}
    _, data = data.split('. Tried ', 1)
    data, _ = data.split('. The following ')
    backends = _backend_re.split(data)
    for backend in backends:
        if backend in ('', ', '):
            continue
        name, message = backend.strip().split(' ', 1)
        message = message.strip('()')
        if ':' in message:
            message, supplement = message.split(':')
            supplement = supplement.strip()
        else:
            supplement = None
        result[name] = (message.strip().rstrip('.'), supplement)
    return result


def split_supplement_data(data):
    """Split the supplementary data out of parsed backend reasons.

    Takes a dict from the output of parse_backend_reasons and splits out
    the supplementary data into a set.

    :return: (backend_to_reason_dict, set_of_supplementary_data)
    """
    core_data = {}
    supplements = set()
    for backend, (core, supplement) in data.items():
        core_data[backend] = core
        if supplement:
            supplements.add(supplement)
    return core_data, supplements


def gather_files_from_backend_reasons(supplements):
    """Return a set of filenames from discovered supplementary data.

    Most of the supplementary data we get back from pkgme are filenames or
    lists of filenames.  This extracts those, always returning a set of
    filenames.
    """
    files = set()
    for supplement in supplements:
        # Strings are encoded with repr() on the wire.  We can safely (if
        # hackishly) decode by relying on the similarity of Python repr()
        # format to JSON.  All we have to do is change single quotes to double
        # quotes.a
        parsed = json.loads(supplement.replace("'", '"'))
        if isinstance(parsed, list):
            files |= set(parsed)
        else:
            files.add(parsed)
    return files


def _no_backend(result):
    return map_error(result.get('details', None)) == NO_BACKEND


def gather_no_backend_data(result):
    """Turn a single parsed result into data about why there are no backends.

    Used for the why-no-backend script.
    """
    details = result['details']
    reasons = parse_backend_reasons(details.get('traceback', ''))
    if not reasons:
        return
    core, supplements = split_supplement_data(reasons)
    files = gather_files_from_backend_reasons(supplements)
    myapps = details['myapps']
    return {
        'url': myapps['package_url'],
        'id': myapps['myapps_id'],
        'reasons': core,
        'files': files,
        }


def is_archive(backend_data):
    """Is ``backend_data`` an archive? Has it been unpacked to files?"""
    basename = os.path.basename(backend_data['url'])
    return set([basename]) != backend_data['files']


def is_singleton_archive(backend_data):
    """Is ``backend_data`` an archive that unpacks to a single top-level file?

    Specifically, a file with no extension.  We single these out because they
    are very likely to be directories.
    """
    return (
        is_archive(backend_data) and
        count(map(get_extension, backend_data['files'])) == {'': 1})


def dump_fingerprints(results, output):
    """Report on the 'fingerprints' of things we couldn't package.

    A 'fingerprint' is a stab at classifying a package based on the files
    we know are in it.  Currently, it's just a count of the extensions.
    """
    fingerprints = []
    for b in results:
        extensions = count(map(get_extension, b['files']))
        extensions = sorted(rename_key(extensions, '', '(none)').items())
        fingerprint = ','.join('%s=%s' % (k, v) for k, v in extensions)
        fingerprints.append(fingerprint)
    output.write(format_counts("Fingerprints", count(fingerprints)))


def dump_urls(data, output):
    """Report for why-no-backends, showing only the URLs.
    """
    for result in data:
        output.write(result['url'])
        output.write('\n')
        output.flush()


def summarize_no_backends(data, output):
    """Produce a summary of the no backend data.

    Three sections: reasons; URL extensions; unpacked file extensions.

    The first are the reasons that backends reported for not wanting things,
    along with how often they were reported.

    The second are the file extensions of the URLs that we could not find
    backends for.

    The third are the file extensions of all the unpacked files.
    """
    reasons = sum([r['reasons'].values() for r in data], [])
    urls = [r['url'] for r in data]
    files = sum([list(r['files']) for r in data], [])
    w = output.write
    w(format_counts("Reasons", count(reasons)))
    extensions = count(map(get_extension, urls))
    w(format_counts(
            "URL extensions",
            rename_key(extensions, '', '(no extension)')))
    extensions = count(map(get_extension, files))
    w(format_counts(
            "Unpacked file extensions",
            rename_key(extensions, '', '(no extension)')))


def browse_archives(data, output):
    """Report each package, showing archive contents and what extensions.

    Only shows archives, since that's all it's really useful for.
    """
    w = output.write
    for result in data:
        if not is_archive(result):
            continue
        basename = os.path.basename(result['url'])
        w(basename)
        w(' (id=%s)' % (result['id']))
        w('\n')
        w('  Files: ')
        files = list(result['files'])
        w(', '.join(files))
        w('\n')
        exts = count(map(get_extension, result['files']))
        exts = rename_key(exts, '', '(no extension)')
        exts = ['%s: %s' % (ext, n) for ext, n in exts.items()]
        w('  Extensions: ')
        w(', '.join(exts))
        w('\n')
        w('\n')


# Reports we can get on why certain packages don't have backends.  Each report
# takes a list of backend data (i.e. a list of results from
# gather_no_backend_data) and a stream-like object to output the report to.
WHY_NO_BACKEND_REPORTS = {
    'urls-only': dump_urls,
    'summary': summarize_no_backends,
    'full': dump_json,
    'browse-archives': browse_archives,
    'fingerprints': dump_fingerprints,
    }


def no_backend_options():
    parser = make_base_options()
    parser.add_argument('--report', choices=WHY_NO_BACKEND_REPORTS, default='full')
    archive_filter = parser.add_mutually_exclusive_group()
    archive_filter.add_argument(
        '--archives-only', action='store_true',
        help="Only include packages that have been unpacked")
    archive_filter.add_argument(
        '--no-archives', action='store_true',
        help="Only include packages to be built from a single file (e.g. PNGs)")
    singleton_filter = parser.add_mutually_exclusive_group()
    singleton_filter.add_argument(
        '--singletons-only', action='store_true',
        help="Only include archives that unpack to a single file or directory")
    singleton_filter.add_argument(
        '--no-singletons', action='store_true',
        help="Only include archives that unpack to multiple files or directories")
    return parser


def why_no_backends():
    """Script to get information on why some things have no backends."""
    parser = no_backend_options()
    args = parser.parse_args()
    results = ifilter(_no_backend, iter_results(args))
    output = map(gather_no_backend_data, results)
    if args.archives_only:
        output = filter(is_archive, output)
    elif args.no_archives:
        output = filter(lambda x: not(is_archive(x)), output)
    if args.singletons_only:
        output = filter(is_singleton_archive, output)
    elif args.no_singletons:
        output = filter(lambda x: not(is_singleton_archive(x)), output)
    reporter = WHY_NO_BACKEND_REPORTS[args.report]
    reporter(output, sys.stdout)
    return 0

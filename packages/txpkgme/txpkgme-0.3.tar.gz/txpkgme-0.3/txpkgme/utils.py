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
import re
import os


def parse_json(json_data):
    """Return a Python data structure corresponding to ``json_data``.

    Use this rather than ``json.loads`` directly to get a richer error message
    when JSON data cannot be decoded.

    :param json_data: A string containing JSON data.
    :raises ValueError: If the JSON data could not be parsed.
    :return: A Python data structure.
    """
    try:
        return json.loads(json_data)
    except ValueError:
        raise ValueError('No JSON object could be decoded: %r' % (json_data,))
    except TypeError, e:
        raise TypeError('%s, got %r' % (e, json_data))


def dump_json(results, output_stream, indent=2):
    json.dump(results, output_stream, indent=indent, default=serialize_extra)
    output_stream.write('\n')


def serialize_extra(obj):
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    if isinstance(obj, set):
        return sorted(list(obj))
    raise TypeError("%r is not JSON serializable" % (obj,))


def rename_key(dct, old, new):
    """Return a dict where the key 'old' has been renamed to 'new'.

    If 'old' is not in dct, then just return a copy of dct.
    """
    # XXX: Untested.
    dct = dict(dct)
    if old in dct:
        dct[new] = dct.pop(old)
    return dct


def count(items):
    # XXX: Untested.
    counts = {}
    for item in items:
        counts.setdefault(item, 0)
        counts[item] += 1
    return counts


def format_counts(title, counts):
    # XXX: Untested.
    title_len = len(title)
    label_len = max(map(len, counts.keys()))
    number_len = max(map(len, map(str, counts.values())))
    lines = [
        title,
        '=' * title_len,
        ]
    for label, number in sorted(counts.items()):
        lines.append(
            '%s   %s' % (
                ('%s:' % (label,)).ljust(label_len + 1),
                str(number).rjust(number_len),
                ))
    lines.extend(['', ''])
    return '\n'.join(lines)


def _scrub_extension(ext, _version_gunk_re=re.compile(r'_+[0-9]*$')):
    if not ext[0].isalpha():
        return
    return _version_gunk_re.sub('', ext)


def get_extension(path):
    path = os.path.basename(path)
    exts = path.split('.')[1:]
    exts = filter(bool, map(_scrub_extension, exts))
    return '.'.join(exts)

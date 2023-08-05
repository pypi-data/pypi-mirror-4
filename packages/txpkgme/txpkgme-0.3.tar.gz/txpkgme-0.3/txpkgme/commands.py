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

from pkgme_service_client.client import PkgmeAPI


class UserError(Exception):
    """Raised when the user can't run the command properly."""


def get_service_url(service_url, remote_hostname, remote_url):
    """Get the service URL to connect to.

    If more than one is specified, error out.

    :param service_url: The URL they specified as an argument.
    :param remote_hostname: The -H option.
    :param remote_url: The -U option.
    """
    # XXX: service_url is deprecated.  If we can guarantee that production
    # doesn't specify it as an argument, then we can get rid of this part of
    # the code.
    num_given = len(
        [x for x in [service_url, remote_hostname, remote_url] if x])
    if num_given > 1:
        raise UserError("service_url and remote hostname both specified.")
    if service_url:
        return service_url
    if remote_hostname:
        return 'https://%s/pkgme/api/1.0' % (remote_hostname,)
    if remote_url:
        return remote_url
    return PkgmeAPI.default_service_root


def add_service_url_options(parser):
    parser.add_argument("--public-host-name", dest="hostname",
                        help=("A host name that the pkgme-service can "
                              "understand and reach"),
                        type=str, metavar="", default="localhost")
    parser.add_argument("-H", "--remote-host-name", dest="remote_hostname",
                        help=("The remote host to connect to.  Assumes a "
                              "standard deployment path for the URL. "),
                        type=str)
    parser.add_argument("-U", "--remote-url", dest="remote_url",
                        help=("The remote url to connect to. Must point to a "
                              "pkgme-service API."),
                        type=str)

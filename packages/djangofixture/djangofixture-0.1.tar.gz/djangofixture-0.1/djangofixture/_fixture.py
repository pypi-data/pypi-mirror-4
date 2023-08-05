# Copyright (C) 2012  Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import errno
import subprocess
import sys
import time
from urllib2 import (
    URLError,
    urlopen,
    )

from fixtures import Fixture
from testtools.content import (
    Content,
    UTF8_TEXT,
    )


class TimeoutError(Exception):
    """Raised when something times out."""


def poll(poll_interval, max_tries, predicate, *args, **kwargs):
    for i in range(max_tries):
        if predicate(*args, **kwargs):
            return
        time.sleep(poll_interval)
    raise TimeoutError("Timed out waiting for %r" % (predicate,))


def _is_server_up(url):
    try:
        response = urlopen(url)
    except URLError, e:
        error_no = getattr(e.reason, 'errno', None)
        if error_no in (errno.ECONNREFUSED, errno.ECONNRESET):
            return False
        raise
    except IOError, e:
        if e.errno in (errno.ECONNREFUSED, errno.ECONNRESET):
            return False
        raise
    return response.code == 200


def poll_until_running(url, poll_interval=0.05, max_tries=100):
    try:
        poll(poll_interval, max_tries, _is_server_up, url)
    except TimeoutError:
        raise TimeoutError("Timed out waiting for %s to come up" % (url,))


def get_manage_location():
    return 'django_project/manage.py'


class DjangoFixture(Fixture):
    """A simple Django service, with database.

    Essentially does 'runserver'.
    """

    def __init__(self, all_clear_path, port=8001):
        super(DjangoFixture, self).__init__()
        self._all_clear_path = all_clear_path
        # XXX: parallelism: Hard-code the port to run on for now. Don't know
        # how to figure out what port it's actually listening on.
        self._port = port

    def setUp(self):
        super(DjangoFixture, self).setUp()
        process = subprocess.Popen(
            [sys.executable, get_manage_location(),
             'runserver', '--noreload', str(self._port)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.addCleanup(process.terminate)
        self.addCleanup(
            self.addDetail,
            'runserver-log',
            Content(
                UTF8_TEXT,
                process.stdout.readlines))
        self.base_url = 'http://localhost:%s' % (self._port,)
        all_clear_url = '%s/%s' % (self.base_url, self._all_clear_path)
        try:
            poll_until_running(all_clear_url)
        except:
            # fixtures don't get cleaned up automatically if setUp fails.
            self.cleanUp()
            raise

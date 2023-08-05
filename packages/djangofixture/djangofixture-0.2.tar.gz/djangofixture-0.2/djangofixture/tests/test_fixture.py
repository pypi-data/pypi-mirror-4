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

from fixtures import FakeLogger
from libpathod import test as pathod_test
from testtools import TestCase

from djangofixture._fixture import _is_server_up


class TestDjangoFixture(TestCase):

    def test_importable(self):
        from djangofixture import DjangoFixture
        DjangoFixture


class IsServerUpTests(TestCase):

    def setUp(self):
        super(IsServerUpTests, self).setUp()
        self.useFixture(FakeLogger(name="pathod", level="WARN"))

    def test_no_server(self):
        # Hope that this port isn't in use
        self.assertEqual(False, _is_server_up('http://localhost:9082/'))

    def test_connection_reset(self):
        with pathod_test.Daemon() as server:
            # disconnect after 0 bytes
            self.assertEqual(False, _is_server_up(server.p('200:d0')))

    def test_404(self):
        with pathod_test.Daemon() as server:
            self.assertEqual(False, _is_server_up(server.p('404:b"NotFound"')))

    def test_502(self):
        with pathod_test.Daemon() as server:
            self.assertEqual(False, _is_server_up(server.p('502:b"ServerDown"')))

    def test_200(self):
        with pathod_test.Daemon() as server:
            self.assertEqual(True, _is_server_up(server.p('200:b"OK"')))

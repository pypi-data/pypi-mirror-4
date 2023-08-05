# copyright 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-database.
#
# logilab-database is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-database is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-database. If not, see <http://www.gnu.org/licenses/>.
import unittest

from logilab.common.testlib import MockConnection

from logilab.database import get_db_helper


class SQLiteHelperTC(unittest.TestCase):

    def setUp(self):
        self.cnx = MockConnection( () )
        self.helper = get_db_helper('sqlite')

    def test_type_map(self):
        self.assertEqual(self.helper.TYPE_MAPPING['Datetime'], 'timestamp')
        self.assertEqual(self.helper.TYPE_MAPPING['String'], 'text')
        self.assertEqual(self.helper.TYPE_MAPPING['Password'], 'bytea')
        self.assertEqual(self.helper.TYPE_MAPPING['Bytes'], 'bytea')


if __name__ == '__main__':
    unittest.main()

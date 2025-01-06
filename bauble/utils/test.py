#
# Copyright (c) 2005,2006,2007,2008,2009 Brett Adams <brett@belizebotanic.org>
# Copyright (c) 2012-2015 Mario Frasca <mario@anche.no>
# Copyright 2017 Jardín Botánico de Quito
#
# This file is part of ghini.desktop.
#
# ghini.desktop is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ghini.desktop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ghini.desktop. If not, see <http://www.gnu.org/licenses/>.
#
# test.py
#
# Description: test for bauble.utils
import unittest

import bauble.db as db
import bauble.utils as utils
from bauble.error import CheckConditionError
from bauble.test import BaubleTestCase
from bauble.utils import topological_sort
from nose import SkipTest
#from pyparsing import *
#from sqlalchemy import *
from sqlalchemy import MetaData, Table, ForeignKey, Column, Integer, Sequence





class UtilsGTKTests(unittest.TestCase):

    def test_create_message_details_dialog(self):
        raise SkipTest("Not Implemented")
        details = """these are the lines that i want to test
asdasdadasddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
dasd
asd
addasdadadad"""
        msg = "msg"
        d = utils.create_message_details_dialog(msg, details)
        d.run()

    def test_create_message_dialog(self):
        raise SkipTest("Not Implemented")
        msg = "msg"
        # msg = ' this is a longer message to test that the dialog width is correct.....but what if it keeps going'
        d = utils.create_message_dialog(msg)
        d.run()

    def test_search_tree_model(self):
        from gi.repository import Gtk

        model = Gtk.TreeStore(str)

        # the rows that should be found
        to_find = []

        row = model.append(None, ["1"])
        model.append(row, ["1.1"])
        to_find.append(model.append(row, ["something"]))
        model.append(row, ["1.3"])

        row = model.append(None, ["2"])
        to_find.append(model.append(row, ["something"]))
        model.append(row, ["2.1"])

        to_find.append(model.append(None, ["something"]))

        root = model.get_iter_first()
        results = utils.search_tree_model(model[root], "something")
        self.assertTrue(
            sorted([model.get_path(r) for r in results]), sorted(to_find)
        )


class UtilsTests(unittest.TestCase):

    def test_xml_safe(self):
        class test:
            def __str__(self):
                return repr(self)

            def __unicode__(self):
                return repr(self)

        import re

        assert re.match("&lt;.*?&gt;", utils.xml_safe(str(test())))
        assert re.match("&lt;.*?&gt;", utils.xml_safe(str(test())))
        assert utils.xml_safe("test string") == "test string"
        assert utils.xml_safe("test string") == "test string"
        assert utils.xml_safe("test< string") == "test&lt; string"
        assert utils.xml_safe("test< string") == "test&lt; string"

    def test_range_builder(self):
        assert utils.range_builder("1-3") == [1, 2, 3]
        assert utils.range_builder("1-3,5-7") == [1, 2, 3, 5, 6, 7]
        assert utils.range_builder("1-3,5") == [1, 2, 3, 5]
        assert utils.range_builder("1-3,5,7-9") == [1, 2, 3, 5, 7, 8, 9]
        assert utils.range_builder("1,2,3,4") == [1, 2, 3, 4]
        assert utils.range_builder("11") == [11]

        # bad range strings
        assert utils.range_builder("-1") == []
        assert utils.range_builder("a-b") == []
        # self.assertRaises(ParseException, utils.range_builder, '-1')
        self.assertRaises(CheckConditionError, utils.range_builder, "2-1")
        # self.assertRaises(ParseException, utils.range_builder, 'a-b')

    def test_get_urls(self):
        text = "There a link in here: http://bauble.belizebotanic.org"
        urls = utils.get_urls(text)
        self.assertTrue(
            urls == [(None, "http://bauble.belizebotanic.org")], urls
        )

        text = (
            "There a link in here: http://bauble.belizebotanic.org "
            "and some text afterwards."
        )
        urls = utils.get_urls(text)
        self.assertTrue(
            urls == [(None, "http://bauble.belizebotanic.org")], urls
        )

        text = (
            "There is a link here: http://bauble.belizebotanic.org "
            "and here: https://belizebotanic.org and some text afterwards."
        )
        urls = utils.get_urls(text)
        self.assertTrue(
            urls
            == [
                (None, "http://bauble.belizebotanic.org"),
                (None, "https://belizebotanic.org"),
            ],
            urls,
        )

        text = (
            "There a labeled link in here: "
            "[BBG]http://bauble.belizebotanic.org and some text afterwards."
        )
        urls = utils.get_urls(text)
        self.assertTrue(
            urls == [("BBG", "http://bauble.belizebotanic.org")], urls
        )


class UtilsDBTests(BaubleTestCase):

    def setUp(self):
        super().setUp()
        from sqlalchemy.orm import configure_mappers


        configure_mappers()

    def tearDown(self):
        super().tearDown()
        from bauble.db import engine, metadata

        metadata.drop_all(engine)

    def test_find_dependent_tables(self):

        from bauble.db import engine, metadata

        # table1 does't depend on any tables
        table1 = Table(
            "table1", metadata, Column("id", Integer, primary_key=True)
        )

        # table2 depends on table1
        table2 = Table(
            "table2",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("table1", Integer, ForeignKey("table1.id")),
        )

        # table3 depends on table2
        table3 = Table(
            "table3",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("table2", Integer, ForeignKey("table2.id")),
            Column("table4", Integer, ForeignKey("table4.id")),
        )

        # table4 depends on table2
        table4 = Table(
            "table4",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("table2", Integer, ForeignKey("table2.id")),
        )

        # Use the same connection and metadata as the application
        with db.engine.begin() as connection:
            metadata.create_all(bind=connection)

        # tables that depend on table 1 are 3, 4, 2
        depends = list(utils.find_dependent_tables(table1, metadata))
        print("table1: %s" % [table.name for table in depends])
        self.assertTrue(list(depends) == [table2, table4, table3])

        # tables that depend on table 2 are 3, 4
        depends = list(utils.find_dependent_tables(table2, metadata))
        print("table2: %s" % [table.name for table in depends])
        self.assertTrue(depends == [table4, table3])

        # no tables depend on table 3
        depends = list(utils.find_dependent_tables(table3, metadata))
        print("table3: %s" % [table.name for table in depends])
        self.assertTrue(depends == [])

        # table that depend on table 4 are 3
        depends = list(utils.find_dependent_tables(table4, metadata))
        print("table4: %s" % [table.name for table in depends])
        self.assertTrue(depends == [table3])


class ResetSequenceTests(BaubleTestCase):

    def setUp(self):
        super().setUp()
        # self.metadata = MetaData()
        # self.metadata.bind = db.engine
        from sqlalchemy.orm import configure_mappers
        from bauble.db import engine, metadata        

        configure_mappers()

        # Drop and recreate tables to start with a clean database
        with engine.begin() as connection:
            metadata.drop_all(bind=connection, checkfirst=True)
            metadata.create_all(bind=connection)

    def tearDown(self):
        from bauble.db import engine, metadata

        # Clean up database after tests
        with engine.begin() as connection:
            metadata.drop_all(bind=connection)

        super().tearDown()

    @staticmethod
    def get_currval(col):
        if db.engine.name == "postgresql":
            name = "{}_{}_seq".format(col.table.name, col.name)
            stmt = "select currval('%s');" % name
            return db.engine.execute(stmt).fetchone()[0]
        elif db.engine.name == "sqlite":
            stmt = "select max({}) from {}".format(col.name, col.table.name)
            return db.engine.execute(stmt).fetchone()[0] + 1

    def test_no_col_sequence(self):
        # Test utils.reset_sequence on a column without a Sequence()
        #
        # This only tests that reset_sequence() doesn't fail if there is
        # no sequence.

        from bauble.db import engine, metadata

        # test that a column without an explicit sequence works
        table = Table(
            "test_reset_sequence",
            self.metadata,
            Column("id", Integer, primary_key=True),
        )

        # Create the table in the database
        with engine.begin() as connection:
            metadata.create_all(bind=connection)
        
        # Insert a record into the table
        with engine.begin() as connection:
            connection.execute(table.insert().values(id=1))

        utils.reset_sequence(table.c.id)

    def test_empty_col_sequence(self):
        # Test utils.reset_sequence on a column without a Sequence()
        #
        # This only tests that reset_sequence() doesn't fail if there is
        # no sequence.
        from bauble.db import metadata, engine

        # Define a table without an explicit sequence
        table = Table(
            "test_reset_sequence",
            metadata,
            Column("id", Integer, primary_key=True),
        )

        # Create the table
        with engine.begin() as connection:
            metadata.create_all(bind=connection)

        # Test reset_sequence on the column (table is empty)
        utils.reset_sequence(table.c.id)

    def test_with_col_sequence(self):
        # UPDATE: 10/18/2011 -- we don't use Sequence() explicitly,
        # just autoincrement=True on primary_key columns so this test
        # probably isn't necessary

        from bauble.db import metadata, engine
        import bauble.utils as utils

        # Define a table with an explicit sequence
        table = Table(
            "test_reset_sequence",
            metadata,
            Column(
                "id",
                Integer,
                Sequence("test_reset_sequence_id_seq"),
                primary_key=True,
                unique=True,
            ),
        )

        # Create the table
        with engine.begin() as connection:
            metadata.create_all(bind=connection)

        # Insert records into the table
        rangemax = 10
        with engine.begin() as connection:
            for i in range(1, rangemax + 1):
                connection.execute(table.insert().values(id=i))

        # Reset the sequence
        utils.reset_sequence(table.c.id)

        # Verify the sequence has been reset
        currval = self.get_currval(table.c.id)
        self.assertTrue(currval > rangemax, f"Sequence value {currval} is not greater than {rangemax}.")

class TopologicalSortTests(unittest.TestCase):
    def test_empty_dependencies(self):
        r = topological_sort(["a", "b", "c"], [])
        self.assertTrue("a" in r)
        self.assertTrue("b" in r)
        self.assertTrue("c" in r)

    def test_full_dependencies(self):
        r = topological_sort(["a", "b", "c"], [("a", "b"), ("b", "c")])
        self.assertTrue("a" in r)
        self.assertTrue("b" in r)
        self.assertTrue("c" in r)
        self.assertEqual(r.pop(), "c")
        self.assertEqual(r.pop(), "b")
        self.assertEqual(r.pop(), "a")

    def test_partial_dependencies(self):
        r = topological_sort(["b", "e"], [("a", "b"), ("b", "c"), ("b", "d")])
        print(r)
        self.assertTrue("e" in r)
        r.remove("e")
        any = {r.pop(), r.pop()}
        self.assertEqual(any, {"c", "d"})
        self.assertEqual(r.pop(), "b")
        # self.assertEquals(r, [])

    def test_empty_input_full_dependencies(self):
        topological_sort([], [("a", "b"), ("b", "c"), ("b", "d")])
        # self.assertEquals(r, [])

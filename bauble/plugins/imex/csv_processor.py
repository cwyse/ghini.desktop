#
# Copyright 2008-2010 Brett Adams
# Copyright 2012-2015 Mario Frasca <mario@anche.no>.
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
# csv import/export
#
# Description: have to name this module csv_ in order to avoid conflict
# with the system csv module
#
import csv
import logging
import os
#import traceback
#from gettext import gettext as _

#import bauble.db as db
#import bauble.pluginmgr as pluginmgr
#import bauble.task
import bauble.utils as utils
#from bauble import pb_set_fraction
#from bauble.error import BaubleError
#from gi.repository import Gtk
from bauble.plugins.imex.unicode_utils import UnicodeReader, UnicodeWriter, InvalidDataError
import sqlalchemy as sa
from sqlalchemy import Boolean
#from sqlalchemy import ColumnDefault
#from sqlalchemy import inspect
#from sqlalchemy import func
#from sqlalchemy.exc import DataError
#from sqlalchemy.orm import configure_mappers
#from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.elements import ClauseElement


logger = logging.getLogger(__name__)
QUOTE_STYLE = csv.QUOTE_MINIMAL
QUOTE_CHAR = '"'


class CSVProcessor:
    def __init__(self, table, filename, session, defaults, update_every):
        """
        Initialize the CSV processor.

        :param table: SQLAlchemy Table object to insert data into.
        :param filename: Path to the CSV file.
        :param session: SQLAlchemy session object.
        :param defaults: Precomputed default values for the table.
        :param update_every: Number of rows to process before yielding and committing.
        """
        self.table = table
        self.filename = filename
        self.session = session
        self.defaults = defaults
        self.update_every = update_every
        self.column_keys = None  # Determined after file analysis
        self.insert_stmt = None  # Prepared insert statement
        self.values = []  # Batch of rows to insert

    @staticmethod
    def _toposort_file(filename, key_pairs):
        """
        filename: the csv file to sort

        key_pairs: tuples of the form (parent, child) where for each
        line in the file the line[parent] needs to be sorted before
        any of the line[child].  parent is usually the name of the
        foreign_key column and child is usually the column that the
        foreign key points to, e.g ('parent_id', 'id')
        """
        f = open(filename)
        reader = UnicodeReader(f, quotechar=QUOTE_CHAR, quoting=QUOTE_STYLE)

        # create a dictionary of the lines mapped to the child field
        bychild = {}
        for line in reader:
            for parent, child in key_pairs:
                bychild[line[child]] = line
        f.close()
        fields = reader.reader.fieldnames
        del reader

        # create pairs from the values in the lines where pair[0]
        # should come before pair[1] when the lines are sorted
        pairs = []
        for line in list(bychild.values()):
            for parent, child in key_pairs:
                if line[parent] and line[child]:
                    pairs.append((line[parent], line[child]))

        # sort the keys and flatten the lines back into a list
        sorted_keys = utils.topological_sort(list(bychild.keys()), pairs)
        sorted_lines = []
        for key in sorted_keys:
            sorted_lines.append(bychild[key])

        # write a temporary file of the sorted lines
        import tempfile

        tmppath = tempfile.mkdtemp()
        head, tail = os.path.split(filename)
        filename = os.path.join(tmppath, tail)
        tmpfile = open(filename, "w")
        tmpfile.write("%s\n" % ",".join(fields))
        writer = UnicodeWriter(
            tmpfile, fields=fields, quotechar=QUOTE_CHAR, quoting=QUOTE_STYLE
        )
        writer.writerows(sorted_lines)
        tmpfile.flush()
        tmpfile.close()
        del writer
        return filename
        
    def prepare_file(self):
        """
        Prepare the file by determining column keys and sorting rows if necessary.
        """
        csv_columns = self._extract_csv_columns()
        if self._has_self_referencing_keys():
            self.filename = self._sort_by_foreign_keys()

        self.column_keys = list(csv_columns.union(self.defaults.keys()))
        self.insert_stmt = self.table.insert()
    
    def process_rows(self):
        """
        Process the CSV rows, applying defaults and preparing for batch insertion.
        Yields control after every `update_every` rows for GUI updates.
        """
        steps_so_far = 0

        with open(self.filename) as f:
            reader = UnicodeReader(f, quotechar=QUOTE_CHAR, quoting=QUOTE_STYLE)
            for row in reader:
                cleaned_row = self._process_row(row)
                self.values.append(cleaned_row)
                steps_so_far += 1

                if steps_so_far % self.update_every == 0:
                    self._insert_batch()
                    yield steps_so_far

        # Insert remaining rows
        if self.values:
            self._insert_batch()

        yield steps_so_far

    def _extract_csv_columns(self):
        with open(self.filename) as f:
            reader = UnicodeReader(f, quotechar=QUOTE_CHAR, quoting=QUOTE_STYLE)
            next(reader)  # Skip the header
            return set(reader.reader.fieldnames)

    def _has_self_referencing_keys(self):
        return any(fk.column.table == self.table for fk in self.table.foreign_keys)

    def _sort_by_foreign_keys(self):
        key_pairs = [(fk.parent.name, fk.column.name) for fk in self.table.foreign_keys if fk.column.table == self.table]
        return self._toposort_file(self.filename, key_pairs)

    def _process_row(self, row):
        """
        Normalize and apply defaults to a single row from the CSV file.
        """
        cleaned_row = {}
        for column in self.column_keys:
            value = row.get(column, self.defaults.get(column))
            cleaned_row[column] = self._normalize_value(value, column)
        return cleaned_row

    def _normalize_value(self, value, column):
        """
        Normalize the value for a given column, handling types and defaults.
        """
        # Skip SQLAlchemy objects (e.g., expressions like `func.now()`)
        if isinstance(value, ClauseElement):
            return value  # Return as-is for SQL expressions like `now()`

        if value in (None, '', 'None'):  # Treat these as None
            return None
        try:
            column_type = self.table.c[column].type
            if isinstance(column_type, Boolean):
                return value.lower() == 'true' if isinstance(value, str) else bool(value)
            elif isinstance(column_type, sa.Integer):
                return int(value)
            elif isinstance(column_type, sa.Float):
                return float(value)
            elif isinstance(column_type, sa.Enum):
                if value not in column_type.enums:
                    raise InvalidDataError(f"Invalid value for column '{column}': {value}. "
                                            f"Allowed values are: {column_type.enums}")
                return value
        except ValueError:
            raise InvalidDataError(f"Invalid value for column '{column}': {value}")
        return value

    def _insert_batch(self):
        """
        Insert the current batch of rows into the database.
        """
        self.session.execute(self.insert_stmt.values(self.values))
        self.values.clear()  # Clear the batch after insertion

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
import logging
import sys

import pytest

from bauble import db, pluginmgr
from bauble.error import BaubleError
from bauble.prefs import prefs

# Global configuration
from typing import Any
from collections.abc import Generator
SQLITE_URI: str
logger: Any = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
prefs.testing = True

# 🔹 Configure Test Databases (SQLite & PostgreSQL)
SQLITE_URI = "sqlite:////tmp/sqlite_test_db"
POSTGRESQL_URI: str = "postgresql://ghini:9yuzebes@192.168.40.32/pytest_db"  # ⚠️ Update this!
URI = SQLITE_URI


# Fixtures for Pytest
@pytest.fixture(scope="session")
def init_bauble() -> None:
    """
    Initialize the database and plugins for testing.
    """
    prefs.init()
    prefs.testing = True
    try:
        db.open(URI, verify=False)
    except Exception as e:
        print(e, file=sys.stderr)
        raise BaubleError("Failed to connect to the database.")
    if not db.engine:
        raise BaubleError("Database engine is not initialized.")

    pluginmgr.load()
    db.metadata.create_all(bind=db.engine)  # Ensure all tables exist
    pluginmgr.init(force=True)


@pytest.fixture(scope="function")
def db_session(init_bauble) -> Generator[None, None, None]:
    """
    Manages test-level transaction savepoint and cleanup.
    """
    db.Session.remove()
    connection = db.engine.connect()
    transaction = connection.begin()
    nested = connection.begin_nested()  # Savepoint

    @sa.event.listens_for(db.Session(), "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield  # Let the test use db.Session()
    finally:
        db.Session.remove()
        nested.rollback()
        transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def clean_db(db_session) -> None:
    """Drops and recreates all tables for a fully clean database before each test."""
    db.metadata.drop_all(bind=db.engine)  # 🔥 Drop all tables
    db.metadata.create_all(bind=db.engine)  # 🔄 Recreate schema


@pytest.fixture
def mock_logger(request) -> Generator[Any, None, None]:
    """
    Capture logs during tests. Automatically detects the test module's logger
    name unless overridden by the test class or function.
    """
    from bauble.test import MockLoggingHandler

    handler = MockLoggingHandler()

    # Default to the test module's dotted path (e.g., bauble.test.test_asktpl)
    long_test_module_path = request.node.fspath.dirname.replace(
        "/", "."
    )  # Convert to dotted path
    test_module_name = request.node.fspath.basename.rsplit(".", 1)[
        0
    ]  # Remove .py extension
    test_module_path = long_test_module_path.removeprefix(
        ".app."
    )  # Remove .app. suffix
    default_logger_name = f"{test_module_path}.{test_module_name}"

    # Check if the test class or function has a logger_name attribute
    test_class = request.cls
    test_func = request.function
    logger_name = (
        getattr(test_class, "logger_name", None)
        or getattr(test_func, "logger_name", None)
        or default_logger_name
    )

    # Set up the logger
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    yield handler
    logger.removeHandler(handler)

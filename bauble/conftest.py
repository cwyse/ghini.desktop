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
from bauble.prefs import prefs
from bauble.error import BaubleError

# Global configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
prefs.testing = True
URI = "sqlite:///:memory:"

# Fixtures for Pytest
@pytest.fixture(scope="session")
def init_bauble():
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

@pytest.fixture(scope="session")
def db_session(init_bauble):
    """
    Provide a database session tied to the global Session from db.open.
    Rolls back after each test to maintain test isolation.
    """
    session = db.Session()
    db.metadata.create_all(bind=db.engine)  # Ensure tables exist
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(autouse=True)
def clean_db(db_session):
    """
    Clean the database before running a test by removing all records.
    """
    db.metadata.drop_all(bind=db.engine)
    db.metadata.create_all(bind=db.engine)
    yield
    db.metadata.drop_all(bind=db.engine)

@pytest.fixture
def mock_logger(request):
    """
    Capture logs during tests. Automatically detects the test module's logger
    name unless overridden by the test class or function.
    """
    from bauble.test import MockLoggingHandler
    handler = MockLoggingHandler()
    
    # Default to the test module's dotted path (e.g., bauble.test.test_asktpl)
    long_test_module_path = request.node.fspath.dirname.replace("/", ".")  # Convert to dotted path
    test_module_name = request.node.fspath.basename.rsplit(".", 1)[0]  # Remove .py extension
    test_module_path = long_test_module_path.removeprefix(".app.")  # Remove .app. suffix
    default_logger_name = f"{test_module_path}.{test_module_name}"

    # Check if the test class or function has a logger_name attribute
    test_class = request.cls
    test_func = request.function
    logger_name = getattr(test_class, "logger_name", None) or \
                  getattr(test_func, "logger_name", None) or \
                  default_logger_name

    # Set up the logger
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    yield handler
    logger.removeHandler(handler)
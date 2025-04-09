#
# Copyright 2005-2010 Brett Adams <brett@belizebotanic.org>
# Copyright 2015-2017 Mario Frasca <mario@anche.no>.
# Copyright 2017 Jardín Botánico de Quito
# Copyright 2018 Ilja Everilä
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
import datetime
import json
import logging
import os
import re
from gettext import gettext as _
from sqlalchemy import asc
import bauble.btypes as types
import bauble.error as error
import bauble.utils as utils
import gi
import sqlalchemy.orm as orm
from bauble.utils import parse_date
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from sqlalchemy import event
from sqlalchemy import inspect
from sqlalchemy import select
#from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import class_mapper
from sqlalchemy import insert
#from sqlalchemy.orm import Query




logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


try:
    import sqlalchemy as sa

    parts = tuple(int(i) for i in sa.__version__.split(".")[:2])
    if parts < (0, 6):
        msg = _(
            "This version of Ghini requires SQLAlchemy 0.6 or greater. "
            "You are using version %s. "
            "Please download and install a newer version of SQLAlchemy "
            "from http://www.sqlalchemy.org or contact your system "
            "administrator."
        ) % ".".join(parts)
        raise error.SQLAlchemyVersionError(msg)
except ImportError:
    msg = _(
        "SQLAlchemy not installed. Please install SQLAlchemy from "
        "http://www.sqlalchemy.org"
    )
    raise


def sqlalchemy_debug(verbose):
    if verbose:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.orm.unitofwork").setLevel(logging.DEBUG)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARN)
        logging.getLogger("sqlalchemy.orm.unitofwork").setLevel(logging.WARN)


SQLALCHEMY_DEBUG = False
sqlalchemy_debug(SQLALCHEMY_DEBUG)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

def get_or_create(session, model, defaults=None, **kwargs):
    """
    Retrieve or create an instance of the given model.
    
    :param session: SQLAlchemy session.
    :param model: The model class.
    :param defaults: Optional dictionary of default values to use if creating a new instance.
    :param kwargs: Filtering criteria for retrieving the instance.
    :return: A tuple (instance, created), where `instance` is the retrieved or created instance, 
             and `created` is a boolean indicating whether the instance was created.
    """
    defaults = defaults or {}
    
    # Build a query to find an existing instance matching kwargs
    stmt = select(model).filter_by(**kwargs)
    instance = session.scalars(stmt).first()
    
    if instance:
        # Return the existing instance with `created` set to False
        return instance, False
    
    # Create a new instance if none was found
    try:
        instance = model(**{**kwargs, **defaults})
        session.add(instance)
        session.flush()  # Persist the new instance and assign primary key
        return instance, True
    except IntegrityError:
        # Handle potential race conditions in a multi-threaded or concurrent environment
        session.rollback()
        instance = session.scalars(stmt).first()
        return instance, False


def natsort(attr, obj):
    """return the naturally sorted list of the object attribute

    meant to be curried.  the main role of this function is to invert
    the order in which the function getattr receives its arguments.

    attr is in the form <attribute> but can also specify a path from the
    object to the attribute, like <a1>.<a2>.<a3>, in which case each
    step should return a single database object until the last step
    where the result should be a list of objects.

    e.g.:
    from functools import partial
    partial(natsort, 'accessions')(species)
    partial(natsort, 'species.accessions')(vern_name)
    """
    from bauble import utils

    jumps = attr.split(".")
    for attr in jumps:
        obj = getattr(obj, attr)
    return sorted(obj, key=utils.natsort_key)

#from sqlalchemy.orm import aliased
def get_orm_entity_by_name(entity_name):
    """
    Dynamically resolve an ORM entity (class) from its name.

    Handles plural forms like `genera` by resolving relationships.

    :param entity_name: The name of the entity to resolve.
    :return: The ORM entity class or aliased entity if applicable.
    :raises ValueError: If the entity cannot be resolved.
    """
    from bauble.db import MapperBase  # Ensure you're using the correct base
    from sqlalchemy.orm import aliased

    # Normalize the entity name to lowercase for case-insensitive matching
    entity_name = entity_name.lower()

    # Check if the name exists directly in the class registry
    orm_entity = MapperBase._class_registry.get(entity_name)
    if orm_entity:
        return orm_entity

    # Handle plural cases dynamically
    if entity_name == "genera":
        genus_entity = MapperBase._class_registry.get("genus")
        if not genus_entity:
            raise ValueError("Genus not found in class registry")
        # Return aliased genus for queries
        return aliased(genus_entity)

    # Raise an error for unresolved names
    raise ValueError(f"Cannot resolve ORM entity for name: {entity_name}")


class MapperBase(DeclarativeMeta):
    """
    MapperBase adds the id, _created and _last_updated columns to all
    tables.  It also maintains a class registry for ORM-mapped classes.

    In general there is no reason to use this class directly other
    than to extend it to add more default columns to all the bauble
    tables.
    """
    _class_registry = {}

    def __init__(cls, classname, bases, dict_):
        if "__tablename__" in dict_:
            cls.id = sa.Column(
                "id", sa.Integer, primary_key=True, autoincrement=True
            )
            cls._created = sa.Column(
                "_created",
                types.DateTime(),
                default=datetime.datetime.utcnow(),
            )
            cls._last_updated = sa.Column(
                "_last_updated",
                types.DateTime(),
                default=datetime.datetime.utcnow(),
                onupdate=datetime.datetime.utcnow(),
            )
        if "top_level_count" not in dict_:
            cls.top_level_count = lambda x: {classname: 1}
        if "search_view_markup_pair" not in dict_:
            cls.search_view_markup_pair = lambda x: (
                utils.xml_safe(str(x)),
                "(%s)" % type(x).__name__,
            )

        # Add the class to the registry
        MapperBase._class_registry[classname.lower()] = cls

        super().__init__(classname, bases, dict_)

        # Automatically add event listeners for insert, update, delete
        MapperBase._register_event_listeners(cls)

    @staticmethod
    def add_history_entry(operation, instance):
        """
        Helper function to add a history entry.

        This logs changes to the history table for a given operation
        (`insert`, `update`, or `delete`) on an ORM-mapped instance.
        """
        session = orm.object_session(instance)
        if not session:
            logger.warning("No session found for instance: %s", instance)
            return

        user = current_user() or "unknown"
        row = {
            c.name: utils.utf8(getattr(instance, c.name))
            for c in instance.__table__.columns
        }

        table = History.__table__
        stmt = table.insert().values(
            table_name=instance.__tablename__,
            table_id=getattr(instance, "id", None),
            values=str(row),
            operation=operation,
            user=user,
            timestamp=datetime.datetime.now(),
        )
        session.execute(stmt)
        logger.debug("History entry added: %s", stmt)
        
    @staticmethod
    def _register_event_listeners(cls):
        """
        Registers SQLAlchemy ORM event listeners for a mapped class.
        """
        @event.listens_for(cls, "after_insert")
        def after_insert(mapper, connection, target):
            logger.debug(f"Insert event for {target.__tablename__}")
            MapperBase.add_history_entry("insert", target)

        @event.listens_for(cls, "after_update")
        def after_update(mapper, connection, target):
            logger.debug(f"Update event for {target.__tablename__}")
            MapperBase.add_history_entry("update", target)

        @event.listens_for(cls, "after_delete")
        def after_delete(mapper, connection, target):
            logger.debug(f"Delete event for {target.__tablename__}")
            MapperBase.add_history_entry("delete", target)

    @classmethod
    def query_with_default_order(cls, session):
        """
        Return a query object for the class, applying the default order if specified.
        """
        query = session.query(cls)
        if hasattr(cls, "order_by") and cls.order_by:
            query = query.order_by(*cls.order_by)
        return query
        
engine = None
"""A :class:`sqlalchemy.engine.base.Engine` used as the default
connection to the database.
"""


Session = None
"""
bauble.db.Session is created after the database has been opened with
:func:`bauble.db.open()`. bauble.db.Session should be used when you need
to do ORM based activities on a bauble database.  To create a new
Session use::Uncategorized

    session = bauble.db.Session()

When you are finished with the session be sure to close the session
with :func:`session.close()`. Failure to close sessions can lead to
database deadlocks, particularly when using PostgreSQL based
databases.
"""

class TypedBaseMixin:
    id: int
    _created: datetime.datetime
    _last_updated: datetime.datetime


Base = declarative_base(cls=TypedBaseMixin, metaclass=MapperBase)
"""
All tables/mappers in Ghini which use the SQLAlchemy declarative
plugin for declaring tables and mappers should derive from this class.

An instance of :class:`sqlalchemy.ext.declarative.Base`
"""


metadata = Base.metadata
"""The default metadata for all Ghini tables.

An instance of :class:`sqlalchemy.schema.Metadata`
"""

history_base = declarative_base(metadata=metadata)


class History(history_base):
    """
    The history table records ever changed made to every table that
    inherits from :ref:`Base`

    :Table name: history

    :Columns:
      id: :class:`sqlalchemy.types.Integer`
        A unique identifier.
      table_name: :class:`sqlalchemy.types.String`
        The name of the table the change was made on.
      table_id: :class:`sqlalchemy.types.Integer`
        The id in the table of the row that was changed.
      values: :class:`sqlalchemy.types.String`
        The changed values.
      operation: :class:`sqlalchemy.types.String`
        The type of change.  This is usually one of insert, update or delete.
      user: :class:`sqlalchemy.types.String`
        The name of the user who made the change.
      timestamp: :class:`sqlalchemy.types.DateTime`
        When the change was made.
    """

    __tablename__ = "history"
    id = sa.Column(sa.Integer, primary_key=True)
    table_name = sa.Column(sa.Text, nullable=False)
    table_id = sa.Column(sa.Integer, nullable=False, autoincrement=False)
    values = sa.Column(sa.Text, nullable=False)
    operation = sa.Column(sa.Text, nullable=False)
    user = sa.Column(sa.Text)
    timestamp = sa.Column(types.DateTime, nullable=False)


def open(uri, verify=True, show_error_dialogs=False):
    """
    Open a database connection. This function sets `bauble.db.engine` to
    the opened engine.

    Returns `bauble.db.engine` if successful, else returns None, and
    `bauble.db.engine` remains unchanged.

    :param uri: The URI of the database to open.
    :type uri: str
    :param verify: Whether the database we connect to should be verified
        as one created by Ghini. Mostly for testing.
    :type verify: bool
    :param show_error_dialogs: Whether to display error dialogs. Mostly for testing.
    :type show_error_dialogs: bool
    """
    logger.debug(f"db.open({uri})")
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.pool import NullPool, SingletonThreadPool
    from sqlalchemy.exc import SQLAlchemyError
    import bauble.prefs

    global engine, Session

    # Create the SQLAlchemy engine
    try:
        poolclass = (
            SingletonThreadPool if bauble.prefs.testing else NullPool
        )

        connect_args = {}
        if "sqlite" in uri and bauble.prefs.testing:
            connect_args["timeout"] = 30  # SQLite supports this, PostgreSQL does not

        new_engine = sa.create_engine(
            uri,
            echo=SQLALCHEMY_DEBUG,
            poolclass=poolclass,
            future=True,  # Enable SQLAlchemy 2.0 features
            connect_args=connect_args  # Add connect_args here
        )
        # TODO: there is a problem here: the code may cause an exception, but we
        # immediately loose the 'new_engine', which should know about the
        # encoding used in the exception string.
        new_engine.connect().close()  # Ensure connection can be established
    except SQLAlchemyError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    def _bind():
        """
        Bind the engine and configure the session factory.
        """
        global engine, Session
        if engine is not None:
            engine.dispose()
        engine = new_engine
        metadata.bind = engine
        Session = scoped_session(
            sessionmaker(bind=engine, autoflush=False, future=True)
        )

    # Skip verification if not requested
    if not verify:
        _bind()
        return engine

    try:
        verify_connection(new_engine, show_error_dialogs)
        _bind()
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        raise

    # Ensure mappers are configured
    from sqlalchemy.orm import configure_mappers
    configure_mappers()

    return engine

from sqlalchemy import text, inspect

def create_triggers(connection):
    """
    Creates triggers for all TEXT columns in SQLite to convert empty strings to NULL.
    Adds constraints in PostgreSQL to prevent empty strings.
    """
    inspector = inspect(connection)

    if connection.engine.name == "sqlite":
        logger.info("Creating SQLite triggers to normalize empty strings to NULL.")

        # Loop through all tables
        for table_name in inspector.get_table_names():
            # Get column details
            columns = inspector.get_columns(table_name)
            
            for column in columns:
                col_name = column['name']
                col_type = column['type'].__class__.__name__.lower()

                # Only apply triggers to TEXT columns
                if "text" in col_type or "varchar" in col_type:
                    trigger_name = f"normalize_empty_strings_{table_name}_{col_name}"

                    connection.execute(text(f"""
                        CREATE TRIGGER IF NOT EXISTS {trigger_name}
                        BEFORE INSERT OR UPDATE ON {table_name}
                        FOR EACH ROW
                        WHEN NEW.{col_name} = ''
                        BEGIN
                            UPDATE {table_name} SET {col_name} = NULL WHERE rowid = NEW.rowid;
                        END;
                    """))

        connection.commit()

    elif connection.engine.name == "postgresql":
        logger.info("Adding PostgreSQL column constraints to prevent empty strings.")

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)

            for column in columns:
                col_name = column['name']
                col_type = column['type'].__class__.__name__.lower()

                if "text" in col_type or "varchar" in col_type:
                    connection.execute(text(f"""
                        ALTER TABLE {table_name} ALTER COLUMN {col_name} SET DEFAULT NULL;
                    """))

        connection.commit()


def create(import_defaults=True):
    """
    Create a new Ghini database at the current connection.

    :param import_defaults: A flag that is passed to each plugin's
        `install()` method to indicate whether it should import its
        default data. Mainly used for testing. Default is True.
    :type import_defaults: bool
    """
    logger.debug("Entered db.create()")
    
    if not engine:
        raise ValueError("Engine is None. Not connected to a database.")

    import datetime
    import bauble
    import bauble.meta as meta
    from bauble import pluginmgr

    try:
        with engine.begin() as connection:
            # Ensure all mappers are configured before creating tables
            from sqlalchemy.orm import configure_mappers
            configure_mappers()

            # Drop and recreate all tables
            logger.debug("Dropping and recreating all tables.")
            metadata.drop_all(bind=connection, checkfirst=True)
            metadata.create_all(bind=connection)

            # 🛠️ Add triggers or column constraints for ALL TEXT columns
            create_triggers(connection)

            # Populate the Bauble meta table
            meta_table = meta.BaubleMeta.__table__

            # Insert VERSION_KEY
            logger.debug("Inserting version key.")
            version_stmt = insert(meta_table).values(
                name=meta.VERSION_KEY, value=str(bauble.version)
            )
            connection.execute(version_stmt)

            # Insert CREATED_KEY
            logger.debug("Inserting created timestamp.")
            import time
            tzlocal = datetime.timezone(
                -datetime.timedelta(seconds=time.timezone)
            )
            created_stmt = insert(meta_table).values(
                name=meta.CREATED_KEY, value=str(datetime.datetime.now(tz=tzlocal))
            )
            connection.execute(created_stmt)

        # Install plugins
        try:
            logger.debug("Installing plugins.")
            pluginmgr.install("all", import_defaults, force=True)
        except Exception as e:
            logger.warning(f"Plugin installation failed: {e}")
            raise

        logger.info("Database created successfully.")

    except Exception as e:
        logger.error(f"Error while creating the database: {e}")
        raise

def verify_connection(engine, show_error_dialogs=False):
    """
    Test whether a connection to an engine is a valid Ghini database.
    Raises an error for the first problem it finds with the database.

    :param engine: The engine to test.
    :type engine: sqlalchemy.engine.Engine
    :param show_error_dialogs: Flag to show error dialogs for issues. Default=False.
    :type show_error_dialogs: bool
    """
    logger.debug(f"Entered verify_connection(show_error_dialogs={show_error_dialogs})")
    import bauble
    import bauble.meta as meta

    def handle_error(error_cls, message):
        """
        Handle database connection errors, optionally showing error dialogs.
        """
        if show_error_dialogs:
            utils.message_dialog(message, Gtk.MessageType.ERROR)
        raise error_cls(message)

    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        # Check if the database has any tables
        if not table_names:
            handle_error(error.EmptyDatabaseError, _("The database is empty."))

        # Check for the presence of the bauble meta table
        if meta.BaubleMeta.__tablename__ not in table_names:
            handle_error(
                error.MetaTableError,
                _(
                    "The database does not have the bauble meta table. "
                    "This may indicate a corrupt database or one created "
                    "with an incompatible version of Ghini."
                ),
            )

        # if we don't close this session before raising an exception then we
        # will probably get deadlocks....i'm not really sure why
        # Create a temporary session for schema validation
        from sqlalchemy.orm import sessionmaker
        with sessionmaker(bind=engine, autoflush=False, future=True)() as session:
            # Check for the presence of the "created" timestamp
            created_stmt = select(meta.BaubleMeta).where(meta.BaubleMeta.name == meta.CREATED_KEY)
            if not session.execute(created_stmt).scalar_one_or_none():
                handle_error(
                    error.TimestampError,
                    _("The database lacks a 'created' timestamp in the bauble meta table."
                    "This usually means that there was a problem when you created the "
                    "database or the database you connected to wasn't created with Ghini."),
                )

            # Check for the "version" key and validate compatibility
            version_stmt = select(meta.BaubleMeta).where(meta.BaubleMeta.name == meta.VERSION_KEY)
            version_row = session.execute(version_stmt).scalar_one_or_none()

            if not version_row:
                handle_error(
                    error.VersionError(None),
                    _("The database lacks a 'version' key in the bauble meta table."),
                )

            try:
                major, minor, _ = map(int, version_row.value.split("."))
                if (str(major), str(minor)) != bauble.version_tuple[:2]:
                    handle_error(
                        error.VersionError(version_row.value),
                        _(
                            "You are using Ghini version %(version)s while the "
                            "database you have connected to was created with "
                            "version %(db_version)s\n\nSome things might not work as "
                            "or some of your data may become unexpectedly "
                            "corrupted."                            
                        )
                        % {"version": bauble.version, "db_version": version_row.value},
                    )
            except ValueError:
                handle_error(
                    error.VersionError(version_row.value),
                    _("Invalid version format in the bauble meta table."),
                )

        logger.info("Database connection successfully verified.")
        return True

    except Exception as e:
        logger.error(f"Error during database verification: {e}")
        raise


# def make_note_class(name, compute_serializable_fields=None, as_dict=None, retrieve=None):
def make_note_class(
    name,
    related_class,
    compute_serializable_fields=None,
    as_dict=None,
    retrieve=None,
):
    """
    Create a Note class with a relationship to the related_class using back_populates.

    :param name: The name of the related class (e.g., 'Genus', 'Species').
    :param related_class: The class to which the Note is related.
    :param compute_serializable_fields: Optional callable to compute serializable fields.
    :param as_dict: Optional callable to define how the object is serialized.
    :param retrieve: Optional callable to define how to retrieve the object.
    """
    from sqlalchemy import Integer
    
    class_name = f"{name}Note"
    table_name = f"{name.lower()}_note"

    def is_defined(self):
        return bool(self.user and self.category and self.note)

    def is_empty(self):
        return not self.user and not self.category and not self.note

    @classmethod
    def retrieve_or_create(cls, session, keys, create=True, update=True):
        """
        Retrieve or create a database object corresponding to keys.
        """
        original_category = keys.get("category", "")

        # Handle special cases for unique categories
        if create and (original_category.startswith("[") and original_category.endswith("]") or original_category == "<picture>"):
            import uuid
            keys["category"] = str(uuid.uuid4())

        # Call the parent class's retrieve_or_create
        try:
            result = super(globals()[class_name], cls).retrieve_or_create(
                session, keys, create, update
            )
            keys["category"] = original_category
            if result:
                result.category = original_category
            return result
        except AttributeError as e:
            logger.error(f"Parent class does not implement retrieve_or_create: {e}")
            raise
    
    @classmethod
    def retrieve_default(cls, session, keys):
        """
        Retrieve a default instance of the class based on the provided keys.

        :param cls: The class type being queried.
        :param session: The SQLAlchemy session.
        :param keys: A dictionary of filtering criteria.
        :return: The instance if found, otherwise None.
        """
        from sqlalchemy import select

        try:
            # Start with a base query
            stmt = select(cls)

            # Join and filter based on `name`
            if "name" in keys:
                related_name = keys["name"].lower()
                related_class = globals().get(keys["name"].lower())
                if related_class:
                    fk_attr = getattr(cls, f"{related_name}_id", None)
                    assert fk_attr is not None, f"Expected attribute '{related_name}_id' not found on {cls.__name__}"
                    stmt = stmt.join(related_class, 
                                     related_class.id == fk_attr).where(related_class.code == keys[keys["name"].lower()]
                    )

            # Add filters for `date`
            if "date" in keys:
                stmt = stmt.where(cls.date == keys["date"])

            # Add filters for `category`
            if "category" in keys:
                stmt = stmt.where(cls.category == keys["category"])

            # Execute the query and fetch the result
            result = session.execute(stmt).scalars().one_or_none()

            return result

        except Exception as e:
            # Log the exception and return None
            logger.error(f"Error in retrieve_default for {cls.__name__}: {e}")
            return None

    # Default as_dict implementation
    def as_dict_default(self):
        result = Serializable.as_dict(self)
        result[name.lower()] = getattr(self, name.lower()).code
        return result

    as_dict = as_dict or as_dict_default
    retrieve = retrieve or retrieve_default

    bases = (Base,)
    fields = {
        "__tablename__": table_name,
        "id": sa.Column(Integer, primary_key=True, autoincrement=True),
        "date": sa.Column(types.Date, default=datetime.datetime.utcnow()),
        "user": sa.Column(sa.Unicode(64), default=""),
        "category": sa.Column(sa.Unicode(32), default=""),
        "type": sa.Column(sa.Unicode(32), default=""),
        "note": sa.Column(sa.UnicodeText, nullable=False),
        name.lower()
        + "_id": sa.Column(
            sa.Integer, sa.ForeignKey(name.lower() + ".id"), nullable=False
        ),
        name.lower(): sa.orm.relationship(
            related_class.__name__,
            uselist=False,
            back_populates="notes",
            cascade="all, delete-orphan",
            single_parent=True,
        ),
        "retrieve": classmethod(retrieve),
        "retrieve_or_create": classmethod(retrieve_or_create),
        "is_defined": is_defined,
        "as_dict": as_dict,
        # Define the order_by attribute for this class
        "order_by": [asc(f"{table_name}.date")],
    }
    if compute_serializable_fields is not None:
        bases = (Base, Serializable)
        fields["compute_serializable_fields"] = classmethod(
            compute_serializable_fields
        )

    result = type(class_name, bases, fields)

    return result

class WithNotes:
    """
    A mixin to provide dynamic attribute access to notes based on categories.
    """
    key_pattern = re.compile(r"{[^:]+:(.*)}")

    def __getattr__(self, name):
        """
        Retrieve a value from corresponding notes.

        The result can be:
        - An atomic value
        - A list of values
        - A dictionary

        :param name: The attribute name to retrieve.
        :return: The corresponding value(s) or raises AttributeError if not found.
        """
        # Ignore SQLAlchemy-related attributes
        if name.startswith("_sa"):
            raise AttributeError(name)

        result = []
        is_dict = False

        for note in self.notes:
            category = note.category
            note_text = note.note

            if category is None:
                continue

            if category == f"[{name}]":
                result.append(note_text)
            elif category.startswith(f"{{{name}:") and category.endswith("}"):
                is_dict = True
                match = self.key_pattern.match(category)
                if match:
                    key = match.group(1)
                    result.append((key, note_text))
            elif category == f"<{name}>":
                # Attempt to parse note text as JSON
                parsed_note = self._parse_json_safe(note_text)
                if parsed_note:
                    return parsed_note

        if not result:
            raise AttributeError(name)

        return dict(result) if is_dict else result

    @staticmethod
    def _parse_json_safe(text):
        """
        Parse text as JSON, fallback to the original text if parsing fails.

        Attempts parsing in two forms:
        - As a directly parsable JSON string.
        - As a normalized key-value format using `replace` and `re.sub`.

        :param text: The text to parse.
        :return: Parsed JSON object or the original text.
        """

        try:
            # Attempt parsing after normalizing the key-value structure
            normalized_text = re.sub(r"(\w+)[ ]*(?=:)", r'"\g<1>"', text.replace(";", ","))
            return json.loads(normalized_text)
        except json.JSONDecodeError as e:
            pass

        try:
            normalized_text = re.sub(r"(\w+)[ ]*(?=:)", r'"\g<1>"', text)
            # Try parsing the text as-is
            return json.loads(normalized_text)
        except json.JSONDecodeError:
            logger.debug("JSON parsing failed: %s. Returning raw text: %s", e, text)
            return text

class DefiningPictures:
    """
    A mixin to define picture handling for notes.
    """

    @property
    def pictures(self):
        """
        Retrieve a list of Gtk.Image objects from notes with the "<picture>" category.

        :return: List of Gtk.Image objects.
        """
        result = []

        for note in self.notes:
            if note.category == "<picture>":
                box = Gtk.VBox()  # Contains the image or the error message
                utils.ImageLoader(box, note.note).start()
                result.append(box)

        return result

class DefiningPictures:
    @property
    def pictures(self):
        """A list of Gtk.Image objects."""
        result = []
        for note in self.notes:
            if note.category != "<picture>":
                continue
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)  # Updated for GTK 3.24+
            utils.ImageLoader(box, note.note).start()
            result.append(box)
        return result



class Serializable:
    """
    A base class for serializable ORM objects.
    """
    import re

    single_cap_re = re.compile("([A-Z])")
    link_keys = []

    def as_dict(self):
        """
        Convert the object to a dictionary representation.
        """
        result = {
            col: getattr(self, col)
            for col in list(self.__table__.columns.keys())
            if col not in ["id"]
            and col[0] != "_"
            and getattr(self, col) is not None
            and getattr(self, col) != ""
            and not col.endswith("_id")
        }
        result["object"] = self.single_cap_re.sub(
            r"_\1", self.__class__.__name__
        ).lower()[1:]
        return result

    @classmethod
    def correct_field_names(cls, keys):
        """
        Correct keys dictionary according to class attributes.

        Exchange format may use different keys than class attributes.
        """
        pass

    @classmethod
    def compute_serializable_fields(cls, session, keys):
        """
        Create objects corresponding to keys (class dependent).

        :param session: The SQLAlchemy session.
        :param keys: A dictionary of keys for filtering or creation.
        :return: A dictionary of serializable fields.
        """
        return {}

    @classmethod
    def retrieve_or_create(cls, session, keys, create=True, update=True):
        """
        Return a database object corresponding to keys, creating or updating as necessary.

        :param session: SQLAlchemy session
        :param keys: Dictionary of key-value pairs for lookup or creation
        :param create: Whether to create a new object if one doesn't exist
        :param update: Whether to update an existing object
        :return: The retrieved or created object
        """
        logger.debug("initial value of keys: %s", keys)

        # First attempt to retrieve the object
        is_in_session = cls.retrieve(session, keys)
        logger.debug("2 value of keys: %s", keys)

        if not create and not is_in_session:
            logger.debug("not creating from %s; returning None (1)", str(keys))
            return None

        if is_in_session and not update:
            logger.debug("returning not updated existing %s", is_in_session)
            return is_in_session

        try:
            # Compute any additional fields required for serialization
            extradict = cls.compute_serializable_fields(session, keys)
            cls.correct_field_names(keys)  # Correct field names
        except error.NoResultException:
            if not is_in_session:
                logger.debug("returning None (2)")
                return None
            else:
                extradict = {}
        except Exception as e:
            logger.exception("Unexpected error during serialization field computation")
            raise

        logger.debug("3 value of keys: %s", keys)

        # Parse timestamps in keys
        for timestamp_key in ["_created", "_last_updated"]:
            if timestamp_key in keys:
                keys[timestamp_key] = parse_date(keys[timestamp_key])

        logger.debug("3½ value of keys: %s", keys)

        # Handle linking keys (Python-side properties, not DB associations)
        link_values = {k: keys.pop(k) for k in cls.link_keys if k in keys}
        logger.debug("link_values: %s", link_values)

        # Remove keys that are not mapped columns or special cases
        mapped_columns = {col.key for col in class_mapper(cls).columns}
        keys = {k: v for k, v in keys.items() if k in mapped_columns}

        keys.update(extradict)  # Add extra computed fields
        logger.debug("4 value of keys: %s", keys)

        if not is_in_session and create:
            # Handle recursive creation of linked objects
            for key, link_value in link_values.items():
                if link_value:
                    logger.debug("Recursive call to construct_from_dict for %s", link_value)
                    keys[key] = construct_from_dict(session, link_value)

            # Create a new object if it doesn't exist
            logger.debug("Creating new %s with %s", cls, keys)
            result = cls(**keys)
            session.add(result)
        elif is_in_session and update:
            result = is_in_session

            # Handle recursive updates of linked objects
            for key, link_value in link_values.items():
                if link_value:
                    logger.debug("Recursive call to construct_from_dict for %s", link_value)
                    setattr(result, key, construct_from_dict(session, link_value))

            # Update fields on the existing object
            for k, v in keys.items():
                if isinstance(v, dict) and v.get("__class__") == "datetime":
                    millis = v.get("millis", 0)
                    v = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=millis)
                setattr(result, k, v)

            logger.debug("Updated existing %s with %s", result, keys)

        # Ensure changes are flushed to the database
        session.flush()
        logger.debug("Returning %s", result)
        return result
        
def construct_from_dict(session, obj, create=True, update=True):
    """
    Construct an object from a dictionary representation.
    
    :param session: SQLAlchemy session.
    :param obj: Dictionary containing object data.
    :param create: Whether to create the object if it doesn't exist.
    :param update: Whether to update the object if it exists.
    :return: The constructed or retrieved object.
    """
    logger.debug("construct_from_dict %s", obj)
    
    klass = None
    
    # Determine the class of the object
    if "object" in obj:
        klass = class_of_object(obj["object"])
    if klass is None and "rank" in obj:
        klass_name = obj["rank"].capitalize()
        klass = globals().get(klass_name)
        del obj["rank"]  # Explicitly remove 'rank' after extracting its value
    
    if not klass:
        raise ValueError(f"Unable to determine class for object: {obj}")
    
    # Use the class's `retrieve_or_create` method to handle the object
    return klass.retrieve_or_create(session, obj, create=create, update=update)


def class_of_object(obj_name):
    """
    Determine the class that implements the object.
    
    :param obj_name: Name of the object.
    :return: The class that implements the object.
    """
    class_name = "".join(part.capitalize() for part in obj_name.split("_"))
    cls = globals().get(class_name)
    
    if cls is None:
        from bauble import pluginmgr
        cls = pluginmgr.provided.get(class_name)
    
    if not cls:
        raise ValueError(f"Class not found for object: {obj_name}")
    
    return cls


class current_user_functor:
    """
    Implement the current_user function and allow overriding.
    
    This is designed to return the current user's name from the database 
    or the system, with support for overriding.
    """

    def __init__(self):
        self.override_value = None

    def override(self, value=None):
        """
        Override the current user value.
        
        :param value: The username to override with. If None, reset the override.
        """
        self.override_value = value

    def __call__(self):
        """
        Retrieve the current user name from the database or system.
        
        :return: The current user name.
        """
        if self.override_value:
            return self.override_value

        try:
            if engine.name.startswith("postgresql"):
                result = engine.execute(sa.text("SELECT current_user")).fetchone()
                return result[0] if result else None
            elif engine.name.startswith("mysql"):
                result = engine.execute(sa.text("SELECT current_user()")).fetchone()
                return result[0] if result else None
            else:
                raise TypeError("Unsupported database engine for user retrieval.")
        except Exception:
            logger.debug("Falling back to system environment for user name retrieval.")
            return (
                os.getenv("USER")
                or os.getenv("USERNAME")
                or os.getenv("LOGNAME")
                or os.getenv("LNAME")
            )


# Instantiate the current_user function
current_user = current_user_functor()

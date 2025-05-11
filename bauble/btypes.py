#
# Copyright (c) 2005,2006,2007,2008,2009 Brett Adams <brett@belizebotanic.org>
# Copyright (c) 2012-2017 Mario Frasca <mario@anche.no>
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
# types.py
#
import logging
from datetime import datetime, timezone
from gettext import gettext as _
from threading import Lock

import bauble.error as error
import sqlalchemy.types as types
from bauble.utils import parse_date

_prefs_lock = Lock()  # ✅ Add this at the module level

logger = logging.getLogger(__name__)

from typing import Protocol, runtime_checkable


@runtime_checkable
class BaseModelProtocol(Protocol):
    id: int

# TODO: store all times as UTC or support timezones
class FreezableList(list):
    def __init__(self, *args):
        super().__init__(*args)
        self._frozen = False

    def freeze(self):
        self._frozen = True

    def _check_mutation(self):
        if self._frozen:
            raise AssertionError("Attempt to modify Enum.values after initialization")

    # Mutation methods we override to check
    def __setitem__(self, key, value):
        self._check_mutation()
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self._check_mutation()
        super().__delitem__(key)

    def append(self, item):
        self._check_mutation()
        super().append(item)

    def extend(self, iterable):
        self._check_mutation()
        super().extend(iterable)

    def insert(self, index, item):
        self._check_mutation()
        super().insert(index, item)

    def pop(self, index=-1):
        self._check_mutation()
        return super().pop(index)

    def remove(self, item):
        self._check_mutation()
        super().remove(item)

    def clear(self):
        self._check_mutation()
        super().clear()

    def sort(self, *args, **kwargs):
        self._check_mutation()
        super().sort(*args, **kwargs)

    def reverse(self):
        self._check_mutation()
        super().reverse()

class EnumError(error.BaubleError):
    """Raised when a bad value is inserted or returned from the Enum type"""

#        types.Enum("s. lat.", "s. str.", "", name="qualifier_enum"),
class Enum(types.TypeDecorator):
    """A database independent Enum type. The value is stored in the database as a Unicode string."""
    
    impl = types.Unicode  # Stored as Unicode in the database
    cache_ok = True

    def __hash__(self):
        """Ensure SQLAlchemy can cache this type safely."""
        return hash((tuple(self.values), self.empty_to_none, self.strict))

    def __repr__(self):
        return f"Enum(values={self.values}, empty_to_none={self.empty_to_none}, strict={self.strict})"

    def __eq__(self, other):
        if not isinstance(other, Enum):
            return False
        return (
            self.values == other.values and
            self.empty_to_none == other.empty_to_none and
            self.strict == other.strict
        )
    
    def __init__(self, values, empty_to_none=False, strict=True, translations=None, **kwargs):
        """
        :param values: A list of valid values for the column.
        :param empty_to_none: Treat the empty string '' as None. None must be in the values list for this to be set.
        :param strict: Enforce strict validation on the values.
        :param translations: A dictionary of value -> translation mappings.
        """
        logger.debug("Enum::init %s %s %s", type(self).__name__, values, empty_to_none)
        # Remove omit_aliases if present
        kwargs.pop("omit_aliases", None)        
        
        super().__init__()
        # Validate values
        if not values or not isinstance(values, (list, set, tuple)):
            raise ValueError("Enum requires a list or tuple of values")
        if not all(isinstance(x, (str, type(None))) for x in values):
            raise ValueError("Enum requires string values (or None)")
        if len(values) != len(set(values)):
            raise ValueError("Enum requires unique values")
        
        # Ensure None is present if `empty_to_none` is True
        if empty_to_none and None not in values:
            raise EnumError(_("You have configured empty_to_none=True, but None is not in the values list"))

        # Convert values to a **mutable list**
        #self.values = list(values)  # ✅ Now mutable
        self.values = FreezableList(values)
        self.values.freeze()  # prevent later changes
        self.strict = strict
        self.empty_to_none = empty_to_none
        
        # Ensure translations is always a dictionary
        self.translations = translations if isinstance(translations, dict) else {}

        # Determine max length for database storage
        max_length = max(len(v) for v in values if v is not None)
        self.impl = types.Unicode(max_length)

        # Call the parent class's constructor
        super().__init__()

    def __setattr__(self, key, value):
        """
        Allow modifying `values` dynamically while ensuring correct behavior.
        """
        if key == "values" and hasattr(self, "values"):
            object.__setattr__(self, key, value)
        else:
            super().__setattr__(key, value)

    def process_bind_param(self, value, dialect):
        """
        Process the value going into the database.
        """
        logger.debug(f"Enum::process_bind_param {type(self).__name__} {type(value).__name__}({value})")

        # Handle empty strings as None if configured
        if self.empty_to_none and not value:
            value = None

        # Convert None to empty string if needed
        if value is None and None not in self.values and '' in self.values:
            value = ''

        # Validate the value
        if value not in self.values:
            raise EnumError(
                _(
                    f"{type(value).__name__}({value}) not in Enum.values: {self.values}"
                )
            )

        return value


    def process_result_value(self, value, dialect):
        """
        Process the value returned from the database.
        """
        if self.strict and value not in self.values:
            raise ValueError(f"Value '{value}' is not in Enum values: {self.values}")
        return value

    def copy(self):
        """
        Create a copy of the Enum type with the same configuration.
        """
        return Enum(
            values=self.values.copy(),  # ✅ Preserve mutability
            empty_to_none=self.empty_to_none,
            strict=self.strict,
            translations=self.translations.copy(),
        )


class DateTime(types.TypeDecorator):
    """
    A DateTime type that ensures timezone-aware storage and retrieval.
    """
    impl = types.DateTime
    cache_ok = True

    import re
    _rx_tz = re.compile('[+-]')

    def __init__(self):
        super().__init__()

    def process_bind_param(self, value, dialect):
        """
        Convert value (string or datetime) into a proper datetime object, 
        ensuring timezone awareness if needed.
        """
        if value is None:
            return value

        if isinstance(value, str):
            # Dynamically fetch preferences for date parsing
            from bauble import prefs
            dayfirst = prefs.parse_dayfirst_pref
            yearfirst = prefs.parse_yearfirst_pref

            # Parse the string into a datetime object
            from bauble.utils import parse_date  # Ensure this is available
            result = parse_date(value, dayfirst=dayfirst, yearfirst=yearfirst)
            return result

        if isinstance(value, datetime) and value.tzinfo is None:
            # Assume naive datetime is in UTC
            value = value.replace(tzinfo=timezone.utc)

        return value


    def process_result_value(self, value, dialect):
        """
        Ensure retrieved datetime is timezone-aware.
        """
        if value is None:
            return value

        if isinstance(value, datetime) and value.tzinfo is None:
            # Convert naive datetime to UTC
            value = value.replace(tzinfo=timezone.utc)

        return value

    def copy(self):
        """
        Return a copy of this type.
        """
        return DateTime()

    def __repr__(self):
        return f"DateTime(cache_ok={self.cache_ok})"

    def __eq__(self, other):
        if not isinstance(other, DateTime):
            return NotImplemented
        return self.cache_ok == other.cache_ok
    
    def __hash__(self):
        """Ensure SQLAlchemy can cache this type safely."""
        return hash("DateTimeType")  # ✅ Use a static hash to prevent issues
    
class Date(types.TypeDecorator):
    """
    A Date type that allows Date strings
    """
    impl = types.Date
    cache_ok = True  # SQLAlchemy caching compatibility

    def __init__(self):
        super().__init__()
        self._dayfirst = None
        self._yearfirst = None

    def __hash__(self):
        """Ensure SQLAlchemy can cache this type safely."""
        return hash("DateType")  # ✅ Static hash ensures uniqueness without breaking SQLAlchemy caching
    
    def _initialize_date_prefs(self):
        """
        Initialize dayfirst and yearfirst preferences if not already set.
        """
        global _prefs_lock
        with _prefs_lock:
            if self._dayfirst is None or self._yearfirst is None:
                from bauble import prefs
                self._dayfirst = prefs.prefs[prefs.parse_dayfirst_pref]
                self._yearfirst = prefs.prefs[prefs.parse_yearfirst_pref]
                logger.debug(f"Date preferences initialized: dayfirst={self._dayfirst}, yearfirst={self._yearfirst}")

    def process_bind_param(self, value, dialect):
        """
        Convert value to a database-compatible date format.
        """
        if not isinstance(value, str):
            return value
        self._initialize_date_prefs()
        parsed_date = parse_date(value, dayfirst=self._dayfirst, yearfirst=self._yearfirst)
        logger.debug(f"Processed bind param: input={value}, parsed_date={parsed_date}")
        return parsed_date.date()

    def process_result_value(self, value, dialect):
        """
        Convert the database value back to a Python date object.
        """
        logger.debug(f"Processing result value: {value}")
        return value

    def copy(self):
        """
        Create a copy of the Date type with the same configuration.
        """
        return Date()
    
    def __repr__(self):
        return f"Date(cache_ok={self.cache_ok})"

    def __eq__(self, other):
        if not isinstance(other, Date):
            return NotImplemented
        return self.cache_ok == other.cache_ok    

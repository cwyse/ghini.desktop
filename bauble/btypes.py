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
from gettext import gettext as _

import bauble.error as error
import sqlalchemy.types as types
from bauble.utils import parse_date
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# TODO: store all times as UTC or support timezones


class EnumError(error.BaubleError):
    """Raised when a bad value is inserted or returned from the Enum type"""

#        types.Enum("s. lat.", "s. str.", "", name="qualifier_enum"),
class Enum(types.TypeDecorator):
    """A database independent Enum type. The value is stored in the database as a Unicode string."""
    
    impl = types.Unicode  # Stored as Unicode in the database
    cache_ok = True

    def __repr__(self):
        return f"Enum(values={self.values}, empty_to_none={self.empty_to_none}, strict={self.strict})"

    def __eq__(self, other):
        return (
            isinstance(other, Enum) and
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
        
        # Validate the provided values
        if values is None or len(values) == 0:
            raise EnumError(_("Enum requires a list of values"))
        if not set(type(x) for x in values).issubset({type(None), str}):
            raise EnumError(_("Enum requires string values (or None)"))
        if len(values) != len(set(values)):
            raise EnumError(_("Enum requires the values to be unique"))
        
        # Configure translations
        translations = translations or {}
        self.translations = {v: v for v in values}
        self.translations.update(translations)
        
        # Ensure None is present if `empty_to_none` is True
        if empty_to_none and None not in values:
            raise EnumError(_("You have configured empty_to_none=True, but None is not in the values list"))
        
        self.values = values[:]  # Copy values to avoid reference issues
        self.strict = strict
        self.empty_to_none = empty_to_none

        # Determine the maximum length of the values for the column size
        max_length = max(len(v) for v in values if v is not None)
        self.impl = types.Unicode(max_length)  # Set the underlying SQL column type

        # Call the parent class's constructor
        super().__init__(**kwargs)


    def process_bind_param(self, value, dialect):
        """
        Process the value going into the database.
        """
        logger.debug(f"Enum::process_bind_param {type(self).__name__} {type(value).__name__}({value})")

        # Handle empty strings as None if configured
        if self.empty_to_none and not value:
            value = None

        # Convert None to empty string if None is not in values but an empty string is
        if value is None and None not in self.values and '' in self.values:
            value = ''

        # Validate the value against the allowed values
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
            raise EnumError(
                _(
                    f"Value '{value}' is not in Enum.values: {self.values}"
                )
            )
        return value

    def copy(self):
        """
        Create a copy of the Enum type with the same configuration.
        """
        return Enum(
            values=self.values,
            empty_to_none=self.empty_to_none,
            strict=self.strict,
            translations=self.translations,
        )


class DateTime(types.TypeDecorator):
    """
    A DateTime type that ensures timezone-aware storage and retrieval.
    """
    impl = types.DateTime
    cache_ok = True

    import re
    _rx_tz = re.compile('[+-]')

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

    def _initialize_date_prefs(self):
        """
        Initialize dayfirst and yearfirst preferences if not already set.
        """
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

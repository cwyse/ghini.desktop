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

logger = logging.getLogger(__name__)


# TODO: store all times as UTC or support timezones


class EnumError(error.BaubleError):
    """Raised when a bad value is inserted or returned from the Enum type"""

#        types.Enum("s. lat.", "s. str.", "", name="qualifier_enum"),
class Enum(types.TypeDecorator):
    """A database independent Enum type. The value is stored in the
    database as a Unicode string.
    """

    impl = types.Unicode  # Stored as Unicode in the database
    cache_ok = True  # SQLAlchemy caching compatibility

    def __init__(
        self,
        values,
        empty_to_none=False,
        strict=True,
        translations={},
        **kwargs
    ):
        """
        : param values: A list of valid values for column.
        :param empty_to_none: Treat the empty string '' as None.  None
        must be in the values list in order to set empty_to_none=True.
        :param strict:
        :param translations: A dictionary of values->translation
        """
        # create the translations from the values and set those from
        # the translations argument, this way if some translations are
        # missing then the translation will be the same as value
        logger.debug(
            "Enum::init {} {} {}".format(
                type(self).__name__, values, empty_to_none
            )
        )
        # Ensure all values are unique and non-empty
#        if not values or len(set(values)) != len(values):
#            duplicates = [v for v in values if values.count(v) > 1]
#            raise EnumError(_("Enum requires unique, non-empty values. Duplicates: {}").format(duplicates))
        if values is None or len(values) == 0:
            raise EnumError(_("Enum requires a list of values"))

        # Ensure all values are strings or None
        if not {type(x) for x in values}.issubset({type(None), str}):
            raise EnumError(_("Enum requires string values (or None)"))

        # Configure translations
        self.translations = {v: v for v in values}
        if translations:
            self.translations.update(translations)
        
        if empty_to_none and (None not in values):
            raise EnumError(
                _(
                    "You have configured empty_to_none=True but "
                    "None is not in the values lists"
                )
            )        
        self.values = values[:]  # copy, not reference
        self.strict = strict
        self.empty_to_none = empty_to_none
        # the length of the string/unicode column should be the
        # longest string in values
        max_length = max([len(v) for v in values if v is not None])
        self.impl = types.Unicode(max_length)
        super().__init__(**kwargs)

    def process_bind_param(self, value, dialect):
        """
        Process the value going into the database.
        """
        logger.debug(
            "Enum::process_bind_param {} {}({})".format(
                type(self).__name__, type(value).__name__, value
            )
        )
        if (self.empty_to_none) and (not value):
            value = None
        if value is None and None not in self.values and "" in self.values:
            value = ""
        if value not in self.values:
            raise EnumError(
                _(
                    "%(type_name)s(%(value)s) not in Enum.values: %(all_values)s"
                )
                % {
                    "value": value,
                    "type_name": type(value).__name__,
                    "all_values": self.values,
                }
            )
        return value

    def process_result_value(self, value, dialect):
        """
        Process the value returned from the database.
        """
        # if self.strict and value not in self.values:
        #     raise ValueError(_('"%s" not in Enum.values') % value)
        return value

    def copy(self):
        return Enum(self.values, self.empty_to_none, self.strict)


def get_dayfirst_yearfirst():
    """
    Retrieve preferences for dayfirst and yearfirst parsing.
    """
    from bauble.prefs import prefs, parse_dayfirst_pref, parse_yearfirst_pref
    return prefs[parse_dayfirst_pref], prefs[parse_yearfirst_pref]

class DateTime(types.TypeDecorator):
    """
    A DateTime type that allows strings
    """

    impl = types.DateTime
    cache_ok = True

    import re

    _rx_tz = re.compile("[+-]")

    def process_bind_param(self, value, dialect):
        if not isinstance(value, str):
            return value
        try:
            DateTime._dayfirst
            DateTime._yearfirst
        except AttributeError:
            #import bauble.prefs as prefs
            #DateTime._dayfirst = prefs.prefs[prefs.parse_dayfirst_pref]
            #DateTime._yearfirst = prefs.prefs[prefs.parse_yearfirst_pref]
            from bauble.prefs import prefs, parse_dayfirst_pref, parse_yearfirst_pref
            DateTime._dayfirst = prefs.prefs[parse_dayfirst_pref]
            DateTime._yearfirst = prefs.prefs[parse_yearfirst_pref]
        result = parse_date(
            value, dayfirst=DateTime._dayfirst, yearfirst=DateTime._yearfirst
        )
        return result

    def process_result_value(self, value, dialect):
        return value

    def copy(self):
        return DateTime()


class Date(types.TypeDecorator):
    """
    A Date type that allows Date strings
    """

    impl = types.Date
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if not isinstance(value, str):
            return value
        try:
            Date._dayfirst
            Date._yearfirst
        except AttributeError:
            import bauble.prefs as prefs

            Date._dayfirst = prefs.prefs[prefs.parse_dayfirst_pref]
            Date._yearfirst = prefs.prefs[prefs.parse_yearfirst_pref]
        return parse_date(
            value, dayfirst=Date._dayfirst, yearfirst=Date._yearfirst
        ).date()

    def process_result_value(self, value, dialect):
        return value

    def copy(self):
        return Date()

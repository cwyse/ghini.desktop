#
# Copyright 2008-2010 Brett Adams
# Copyright 2014-2017 Mario Frasca <mario@anche.no>.
# Copyright 2016 Ross Demuth <rossdemuth123@gmail.com>
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
import re
from gettext import gettext as _

import bauble.utils.desktop as desktop
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _open_link(data=None, *args, **kwargs):
    """Open a web link"""
    logger.debug(
        "_open_link received data={}, args={}, kwargs={}".format(data, args, kwargs)
    )
    desktop.open(data)


import re

from gi.repository import Gtk


class BaubleLinkButton:
    """
    A button that acts as a link, but instead of using subclassing,
    it uses composition to wrap around a Gtk.LinkButton.
    """

    _base_uri = "%s"
    _space = "_"
    title = _("Search")
    tooltip = None
    pt = re.compile(r"%\(([a-z_\.]*)\)s")

    def __init__(self, title=_("Search"), tooltip=None):
        # Create the Gtk.LinkButton instance
        self.link_button = Gtk.LinkButton(label=title, uri="")
        self.set_tooltip(tooltip or title)

        # Find the fields based on the URI pattern
        self.fields = self.pt.findall(self._base_uri)

    def set_tooltip(self, tooltip_text):
        """Set the tooltip text for the link button."""
        self.link_button.set_tooltip_text(tooltip_text)

    def set_string(self, row):
        """
        Set the URI for the link button based on a row's values.

        The row can be an object with attributes matching the pattern
        in the URI (_base_uri).
        """
        if not self.fields:
            s = str(row)
            self.link_button.set_uri(self._base_uri % s.replace(" ", self._space))
        else:
            values = {}
            for key in self.fields:
                value = row
                for step in key.split("."):
                    value = getattr(value, step, "-")
                values[key] = str(value) if value == str(value) else ""
            self.link_button.set_uri(self._base_uri % values)

    def get_widget(self):
        """
        Returns the Gtk.LinkButton widget.
        This can be added to any container as a regular widget.
        """
        return self.link_button

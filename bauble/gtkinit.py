# bauble/gtkinit.py
import sys
from gettext import gettext as _

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Champlain", "0.12")
gi.require_version("GtkChamplain", "0.12")
gi.require_version("GtkClutter", "1.0")

__all__ = [
    "Champlain",
    "Clutter",
    "Gdk",
    "GdkPixbuf",
    "Gio",
    "GLib",
    "GObject",
    "Gtk",
    "GtkChamplain",
    "GtkClutter",
    "Pango",
]

try:
    from gi.repository import (  # Ensures compatibility
        Champlain,
        Clutter,
        Gdk,
        GdkPixbuf,
        Gio,
        GLib,
        GObject,
        Gtk,
        GtkChamplain,
        GtkClutter,
        Pango,
    )
except ImportError as e:
    print(_("** Error: could not import Gtk and/or GObject"))
    print(e)
    if sys.platform == "win32":
        print(_("Please make sure that GTK_ROOT\\bin is in your PATH."))
    sys.exit(1)

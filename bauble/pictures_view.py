#
# Copyright 2015 Mario Frasca <mario@anche.no>.
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
import logging

import bauble.utils as utils
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class PicturesView(Gtk.Box):
    """shows pictures corresponding to selection.

    at any time, no more than one PicturesView object will exist.

    when activated, the PicturesView object will be informed of changes
    to the selection and whatever the selection contains, the
    PicturesView object will ask each object in the selection to please
    return pictures, so that the PicturesView object can display them.

    if an object in the selection does not know of pictures (like it
    raises an exception because it does not define the 'pictures'
    property), the PicturesView object will silently accept the failure.

    """

    def __init__(self, parent=None, fake=False):
        logger.debug(
            "entering PicturesView.__init__(parent=%s, fake=%s)"
            % (parent, fake)
        )
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.fake = fake
        if self.fake:
            return
        
        import os

        from bauble import paths

        glade_file = os.path.join(paths.lib_dir(), "pictures_view.glade")
        self.widgets = utils.BuilderWidgets(glade_file)

        # Remove parent reference from builder and add to the new parent
        self.widgets.remove_parent(self.widgets.scrolledwindow2)
        parent.add(self.widgets.scrolledwindow2)
        parent.show_all()
        self.widgets.scrolledwindow2.show()


    def set_selection(self, selection):
        """
        Updates the view based on the current selection.

        If an object in the selection contains a `pictures` property, its
        pictures will be displayed.
        """
        logger.debug(f"Setting selection: {selection}")
        if self.fake:
            return

        self.ghini_box = self.widgets.pictures_box

        # Clear existing children
        for child in self.ghini_box.get_children():
            child.destroy()

        for obj in selection or []:
            try:
                pics = obj.pictures
            except AttributeError:
                logger.debug(f"Object {obj} does not define 'pictures' attribute")
                pics = []

            for pic in pics:
                logger.debug(f"Object {obj} has picture {pic}")
                picture_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                picture_box.add(pic)
                self.ghini_box.pack_start(picture_box, False, False, 0)
                self.ghini_box.reorder_child(picture_box, 0)
                picture_box.show_all()
                pic.show()

        self.ghini_box.show_all()

    def add_picture(self, picture=None):
        """
        Adds a new picture to the model.
        """
        if picture is None:
            logger.warning("add_picture() called with no picture provided.")
            return None

        picture_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        picture_box.add(picture)

        self.ghini_box.pack_start(picture_box, False, False, 0)
        picture_box.show_all()

        return picture_box


floating_window = None


def show_pictures_callback(selection):
    """activate a modal window showing plant pictures.

    the current selection defines what pictures should be shown. it
    makes sense for plant, accession and species.

    plants: show the pictures directly associated to them;

    accessions: show all pictures for the plants in the selected
    accessions.

    species: show the voucher.
    """
    if floating_window is not None:
        floating_window.set_selection(selection)

#
# Copyright 2008-2010 Brett Adams
# Copyright 2012-2015 Mario Frasca <mario@anche.no>.
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
# geography.py
#
from operator import itemgetter

import bauble.db as db
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session

def get_species_in_geographic_area(geo):
    """
    Return all the Species that have distribution in geo
    """
    session = object_session(geo)
    if not session:
        ValueError(
            "get_species_in_geographic_area(): geographic_area is not in a session"
        )

    # get all the geographic_area children under geo
    from bauble.plugins.plants.species_model import (
        Species,
        SpeciesDistribution,
    )

    # get the children of geo
    geo_table = geo.__table__
    master_ids = {geo.id}
    # populate master_ids with all the geographic_area ids that represent
    # the children of particular geographic_area id

    def get_geographic_area_children(parent_id):
        """
        Recursively retrieve the children geographic areas of a given parent.

        Args:
            parent_id (int): The ID of the parent geographic area.

        Returns:
            list: A list of IDs representing the children geographic areas.
        """
        stmt = select(geo_table.c.id).where(geo_table.c.parent_id == parent_id)

        # Use the session for query execution
        result = db.session.execute(stmt)
        kids = [row.id for row in result.scalars()]
        
        for kid in kids:
            # Recursively fetch the children of the current child
            grand_kids = get_geographic_area_children(kid)
            master_ids.update(grand_kids)

        return kids
    geokids = get_geographic_area_children(geo.id)
    master_ids.update(geokids)
    from sqlalchemy import bindparam

    q = (
        session.execute(select(Species)).scalars()
        .join(SpeciesDistribution)
        .where(
            SpeciesDistribution.geographic_area_id.in_(
                bindparam("master_ids", expanding=True)
            )
        )
        .params(master_ids=master_ids)
    )
    return list(q)


class GeographicAreaMenu(Gtk.Menu):

    def __init__(self, callback):
        super().__init__()
        geographic_area_table = GeographicArea.__table__

        # Query the database for the geographic area information
        geos = db.session.execute(
            select(
                geographic_area_table.c.id,
                geographic_area_table.c.name,
                geographic_area_table.c.parent_id
            )
        ).fetchall()

        geos_hash = {}
        # TODO: i think the geo_hash should be calculated in an idle
        # function so that starting the editor isn't delayed while the
        # hash is being built
        for geo_id, name, parent_id in geos:
            if parent_id not in geos_hash:
                geos_hash[parent_id] = []
            geos_hash[parent_id].append((geo_id, name))

        # Sort each list of children by name
        for kids in geos_hash.values():
            kids.sort(key=itemgetter(1))  # sort by name

        def get_kids(pid):
            try:
                return geos_hash[pid]
            except KeyError:
                return []

        def has_kids(pid):
            try:
                return len(geos_hash[pid]) > 0
            except KeyError:
                return False

        def build_menu(geo_id, name):
            item = Gtk.MenuItem(name)
            if not has_kids(geo_id):
                if item.get_submenu() is None:
                    item.connect("activate", callback, geo_id)
                    # self.view.connect(item, 'activate',
                    #                   self.on_activate_add_menu_item, geo_id)
                return item

            kids_added = False
            submenu = Gtk.Menu()
            # removes two levels of kids with the same name, there must be a
            # better way to do this but i got tired of thinking about it
            kids = get_kids(geo_id)
            if len(kids) > 0:
                kids_added = True
            for kid_id, kid_name in kids:  # get_kids(geo_id):
                submenu.append(build_menu(kid_id, kid_name))

            if kids_added:
                sel_item = Gtk.MenuItem(name)
                submenu.insert(sel_item, 0)
                submenu.insert(Gtk.SeparatorMenuItem(), 1)
                item.set_submenu(submenu)
                # self.view.connect(sel_item, 'activate',callback, geo_id)
                sel_item.connect("activate", callback, geo_id)
            else:
                item.connect("activate", callback, geo_id)
            return item

        def populate():
            """
            add geographic_area value to the menu, any top level items that don't
            have any kids are appended to the bottom of the menu
            """
            if not geos_hash:
                # we would get here if the GeographicArea menu is populate,
                # usually during a unit test
                return
            no_kids = []
            for geo_id, geo_name in geos_hash[None]:
                if geo_id not in list(geos_hash.keys()):
                    no_kids.append((geo_id, geo_name))
                else:
                    self.append(build_menu(geo_id, geo_name))

            for geo_id, geo_name in sorted(no_kids):
                self.append(build_menu(geo_id, geo_name))

            self.show_all()

        from gi.repository import GObject

        GObject.idle_add(populate)


class GeographicArea(db.Base):
    """
    Represents a geographic_area unit.

    :Table name: geographic_area

    :Columns:
        *name*:

        *tdwg_code*:

        *iso_code*:

        *parent_id*:

    :Properties:
        *children*:

    :Constraints:
    """

    __tablename__ = "geographic_area"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), nullable=False)
    tdwg_code = Column(String(6))
    iso_code = Column(String(7))
    parent_id = Column(Integer, ForeignKey("geographic_area.id"))

    def __str__(self):
        return self.name


# late bindings
GeographicArea.children = relationship(
    "GeographicArea",
    primaryjoin=GeographicArea.parent_id == GeographicArea.id,
    cascade="all",
    back_populates="parent",
    order_by=[GeographicArea.name],
)

GeographicArea.parent = relationship(
    "GeographicArea",
    back_populates="children",
    remote_side=[GeographicArea.__table__.c.id],
)

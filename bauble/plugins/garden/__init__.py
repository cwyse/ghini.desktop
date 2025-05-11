#
# Copyright 2008-2010 Brett Adams
# Copyright 2015 Mario Frasca <mario@anche.no>.
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
#
import logging
import re
from gettext import gettext as _

from sqlalchemy import select
from sqlalchemy.orm import object_session, selectinload

import bauble
import bauble.db as db
import bauble.pluginmgr as pluginmgr
import bauble.search as search
import bauble.utils as utils
from bauble.plugins.garden.accession import (
    Accession,
    AccessionEditor,
    AccessionInfoBox,
    AccessionNote,
    acc_context_menu,
)

# from bauble.plugins.garden.accession import Verification
from bauble.plugins.garden.institution import (
    Institution,
    InstitutionCommand,
    InstitutionTool,
    start_institution_editor,
)
from bauble.plugins.garden.location import (
    Location,
    LocationEditor,
    LocationInfoBox,
    loc_context_menu,
)
from bauble.plugins.garden.picture_importer import PictureImporterTool
from bauble.plugins.garden.plant import (
    Plant,
    PlantEditor,
    PlantInfoBox,
    PlantNote,
    PlantSearch,
    default_plant_delimiter,
    plant_context_menu,
    plant_delimiter_key,
)
from bauble.plugins.garden.pocket_server import PocketServerTool

# from bauble.plugins.garden.source import ContactPresenter
from bauble.plugins.garden.source import (
    Collection,
    Contact,
    ContactInfoBox,
    Source,
    collection_context_menu,
    create_contact,
    source_detail_context_menu,
)
from bauble.utils import safe_set_props, safe_set_text
from bauble.view import SearchView

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# from bauble.plugins.garden.propagation import *

# other ideas:
# - cultivation table
# - conservation table


class GardenPlugin(pluginmgr.Plugin):
    depends = ["PlantsPlugin"]
    tools = [InstitutionTool, PictureImporterTool, PocketServerTool]
    commands = [InstitutionCommand]
    provides = {
        "Accession": Accession,
        "AccessionNote": AccessionNote,
        "Location": Location,
        "Plant": Plant,
        "PlantNote": PlantNote,
        "Source": Source,
        "Contact": Contact,
        "Collection": Collection,
    }

    @classmethod
    def install(cls, *args, **kwargs):
        pass

    @classmethod
    def init(cls):
        """Initialize the GardenPlugin."""
        pluginmgr.provided.update(cls.provides)
        cls._setup_search_metas()
        cls._setup_gui_menus()

        # Initialize the default plant delimiter if not already present
        import bauble.meta as meta

        # Use the session context manager to ensure proper resource handling
        with db.Session() as session:
            meta.get_default(plant_delimiter_key, default_plant_delimiter, session)

        # Prompt for institution setup if not already configured
        institution = Institution()
        if bauble.gui is not None and not institution.name:
            start_institution_editor()

    @staticmethod
    def _setup_search_metas():
        """Configure search strategies and row metadata."""
        from functools import partial

        from bauble.plugins.plants import Species

        mapper_search = search.get_strategy("MapperSearch")

        # Set up Accession
        mapper_search.add_meta(("accession", "acc"), Accession, ["code"])
        SearchView.row_meta[Accession].set(
            children=partial(db.natsort, "plants"),
            infobox=AccessionInfoBox,
            context_menu=acc_context_menu,
        )

        # Set up Location
        mapper_search.add_meta(("location", "loc"), Location, ["name", "code"])
        SearchView.row_meta[Location].set(
            children=partial(db.natsort, "plants"),
            infobox=LocationInfoBox,
            context_menu=loc_context_menu,
        )

        # Set up Plant
        mapper_search.add_meta(("plant", "planting"), Plant, ["code"])
        search.add_strategy(PlantSearch)
        SearchView.row_meta[Plant].set(
            infobox=PlantInfoBox, context_menu=plant_context_menu
        )

        # Set up Contact
        def sd_kids(detail):
            session = object_session(detail)
            if session is None:
                raise ValueError(
                    "The provided detail object is not associated with a session."
                )
            results = (
                session.execute(
                    select(Accession)
                    .join(Source)
                    .join(Contact)
                    .options(selectinload(Species.species))
                    .where(Contact.id == detail.id)
                )
                .scalars()
                .all()
            )
            return results

        mapper_search.add_meta(
            ("contact", "contacts", "person", "org", "source"), Contact, ["name"]
        )
        SearchView.row_meta[Contact].set(
            children=sd_kids,
            infobox=ContactInfoBox,
            context_menu=source_detail_context_menu,
        )

        # Set up Collection
        def coll_kids(coll):
            return sorted(coll.source.accession.plants, key=utils.natsort_key)

        mapper_search.add_meta(("collection", "col", "coll"), Collection, ["locale"])
        SearchView.row_meta[Collection].set(
            children=coll_kids,
            infobox=AccessionInfoBox,
            context_menu=collection_context_menu,
        )

        # Species metadata
        SearchView.row_meta[Species].child = "accessions"

    @classmethod
    def _setup_gui_menus(cls):
        """Set up GUI menus dynamically."""
        if bauble.gui is None:
            return

        import os.path

        from bauble import paths

        base = os.path.join(paths.lib_dir(), "plugins", "garden")

        # Insert Menu
        insert_menu = bauble.gui.insert_menu
        if insert_menu is None:
            logger.error("Insert menu not found!")
            return

        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        insert_menu.append(Gtk.SeparatorMenuItem())

        # from bauble.ui import GUI

        # Add items to Insert menu
        bauble.gui.add_to_insert_menu(
            AccessionEditor, _("Accession"), "insert-new.png", base
        )
        bauble.gui.add_to_insert_menu(
            PlantEditor, _("Planting"), "insert-new.png", base
        )
        bauble.gui.add_to_insert_menu(
            LocationEditor, _("Location"), "insert-new.png", base
        )
        insert_menu.append(Gtk.SeparatorMenuItem())
        bauble.gui.add_to_insert_menu(create_contact, _("Contact"), "user", base)

        # if the plant delimiter isn't in the bauble meta then add the default
        import bauble.meta as meta

        meta.get_default(plant_delimiter_key, default_plant_delimiter)

        institution = Institution()
        if not institution.name:
            start_institution_editor()

        insert_menu.show_all()


def init_location_comboentry(presenter, combo, on_select, required=True):
    """associate custom completion to combobox internal entry

    This method allows us to have completions on the location entry based on
    the location code, location name and location string as well as
    selecting a location from a combo drop down.

    :param presenter:
    :param combo:
    :param on_select: a one-parameter function

    """
    PROBLEM = "UNKNOWN_LOCATION"
    re_code_name_splitter = re.compile(r"\(([^)]+)\) ?(.*)")

    def cell_data_func(col, cell, model, treeiter, data=None):
        safe_set_text(cell, utils.utf8(model[treeiter][0]))

    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    completion = Gtk.EntryCompletion()
    cell = Gtk.CellRendererText()  # set up the completion renderer
    completion.pack_start(cell, True)
    completion.set_cell_data_func(cell, cell_data_func)
    completion.set_popup_set_width(False)

    entry = combo.get_child()
    entry.set_completion(completion)

    combo.clear()
    cell = Gtk.CellRendererText()
    combo.pack_start(cell, True)
    combo.set_cell_data_func(cell, cell_data_func)

    model = Gtk.ListStore(object)
    model.append(("",))
    for loc in sorted(
        presenter.session.execute(select(Location)).scalars().all(),
        key=lambda loc: utils.natsort_key(loc.code),
    ):
        model.append((loc,))
    combo.set_model(model)
    completion.set_model(model)

    def match_func(completion, key, treeiter, data=None):
        logger.debug("match_func")
        loc = completion.get_model()[treeiter][0]
        return (loc.name and loc.name.lower().startswith(key.lower())) or (
            loc.code and loc.code.lower().startswith(key.lower())
        )

    completion.set_match_func(match_func)

    def on_match_select(completion, model, treeiter):
        logger.debug("on_match_select")
        value = model[treeiter][0]
        on_select(value)
        safe_set_props(entry, "text", str(value))
        presenter.remove_problem(PROBLEM, entry)
        presenter.refresh_sensitivity()
        return True

    presenter.view.connect(completion, "match-selected", on_match_select)

    def on_entry_changed(entry, presenter):
        logger.debug("on_entry_changed(%s, %s)", entry, presenter)
        text = utils.utf8(entry.get_text())

        if not text and not required:
            presenter.remove_problem(PROBLEM, entry)
            on_select(None)
            return
        # see if the text matches a completion string
        completion = entry.get_completion()
        compl_model = completion.get_model()

        def _cmp(row, data):
            return utils.utf8(row[0]) == data

        found = utils.search_tree_model(compl_model, text, _cmp)
        if len(found) == 1:
            completion.emit("match-selected", compl_model, found[0])
            return True
        # if text looks like '(code) name', then split it into the two
        # parts, then see if the text matches exactly a code or name
        match = re_code_name_splitter.match(text)
        if match:
            code, name = match.groups()
        else:
            code = name = text
        codes = list(
            presenter.session.execute(
                select(Location).where(
                    utils.ilike(Location.code, "%s" % utils.utf8(code))
                )
            ).scalars()
        )
        names = presenter.session.execute(
            select(Location).where(utils.ilike(Location.name, "%s" % utils.utf8(name)))
        ).scalars()
        if len(codes) == 1:
            logger.debug("location matches code")
            location = codes[0]
            presenter.remove_problem(PROBLEM, entry)
            on_select(location)
        elif len(names) == 1:
            logger.debug("location matches name")
            location = names[0]
            presenter.remove_problem(PROBLEM, entry)
            on_select(location)
        else:
            logger.debug("location %s does not match anything" % text)
            presenter.add_problem(PROBLEM, entry)
        return True

    presenter.view.connect(entry, "changed", on_entry_changed, presenter)

    def on_combo_changed(combo, *args):
        # model = combo.get_model()
        i = combo.get_active_iter()
        if not i:
            return
        location = combo.get_model()[i][0]
        safe_set_props(combo.get_child(), "text", str(location))

    presenter.view.connect(combo, "changed", on_combo_changed)


plugin = GardenPlugin

# make names visible to db module
db.Accession = Accession
db.AccessionNote = AccessionNote
db.Plant = Plant
db.PlantNote = PlantNote
db.Location = Location

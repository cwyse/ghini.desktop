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
import logging
import os
import threading
from functools import reduce
from gettext import gettext as _
from typing import Any, Optional

from bauble import paths, pluginmgr, utils
from bauble.editor import GenericEditorPresenter, GenericEditorView
from bauble.gtkinit import Pango
from bauble.plugins.plants import Species
from bauble.plugins.plants.taxon_lookup import (
    TaxonLookupProvider,
    TaxonLookupRequest,
    TaxonLookupResult,
    TaxonLookupStatus,
    WfoTaxonLookupProvider,
)

logger: Any = logging.getLogger(__name__)


def safe_set_text(gtk_widget, text) -> None:
    """
    Sets the text of a Gtk widget replacing None with an empty string.

    :param label: Instance of a Gtk widget
    :param text: The text to set, which may be None
    """
    if text is None:
        text = ""
    gtk_widget.set_text(text)


def _result_display_name(result: TaxonLookupResult) -> str:
    return result.matched_name or result.canonical_name or ""


def _best_result(
    query: str, results: list[TaxonLookupResult]
) -> Optional[TaxonLookupResult]:
    if not results:
        return None
    if len(results) == 1:
        return results[0]

    import difflib

    scored = [
        (
            difflib.SequenceMatcher(
                a=query,
                b=item.canonical_name or item.matched_name or "",
            ).ratio(),
            item.status,
            item,
        )
        for item in results
    ]
    _score, _status, found = sorted(scored, key=lambda item: item[:2])[-1]
    return found


def build_batch_lookup_rows(
    binomials: list[str],
    provider: TaxonLookupProvider,
) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for binomial in binomials:
        try:
            response = provider.lookup(TaxonLookupRequest(name=binomial))
            result = _best_result(binomial, response.results)
        except Exception as err:
            logger.warning("batch taxonomy lookup failed for %s: %s", binomial, err)
            result = None

        if result is None:
            rows.append(
                [False, NO_ICON, binomial, "", "", _("No match"), "", "", False]
            )
            continue

        matched_name = _result_display_name(result)
        acceptable = result.status in (
            TaxonLookupStatus.ACCEPTED,
            TaxonLookupStatus.SYNONYM,
        )
        row = [
            acceptable,
            acceptable and YES_ICON or NO_ICON,
            binomial,
            matched_name,
            result.authorship or "",
            result.status.title().replace("_", " "),
            "",
            "",
            acceptable,
        ]

        if result.status == TaxonLookupStatus.SYNONYM and result.accepted_provider_id:
            try:
                accepted_response = provider.lookup(
                    TaxonLookupRequest(name=result.accepted_provider_id)
                )
                accepted_result = _best_result(
                    result.accepted_provider_id, accepted_response.results
                )
            except Exception as err:
                logger.warning(
                    "batch taxonomy accepted-name lookup failed for %s: %s",
                    result.accepted_provider_id,
                    err,
                )
                accepted_result = None
            if accepted_result is not None:
                row[ACCEPTED_BINOMIAL] = _result_display_name(accepted_result)
                row[ACCEPTED_AUTHORSHIP] = accepted_result.authorship or ""
                rows.append(row)
                rows.append(
                    [
                        True,
                        YES_ICON,
                        "",
                        _result_display_name(accepted_result),
                        accepted_result.authorship or "",
                        "Accepted",
                        "",
                        "",
                        True,
                    ]
                )
                continue

        rows.append(row)
    return rows


def start_taxonomy_check():
    """run the batch taxonomy check (BTC)"""

    view = GenericEditorView(
        os.path.join(paths.lib_dir(), "plugins", "plants", "taxonomy_check.glade"),
        parent=None,
        root_widget_name="dialog1",
    )
    model = type("BTCStatus", (object,), {})()
    model.page = 1
    model.selection = view.get_selection()
    model.tick_off = None
    model.report = None

    if model.selection is None:
        return
    from sqlalchemy.orm import object_session

    presenter = BatchTaxonomicCheckPresenter(
        model,
        view,
        refresh_view=True,
        session=object_session(model.selection[0]),
    )
    error_state = presenter.start()
    if error_state:
        if presenter.session.in_transaction():
            presenter.session.rollback()
    else:
        presenter.commit_changes()
        from bauble import gui

        view = gui.get_view()
        if hasattr(view, "update"):
            view.update()
    presenter.cleanup()
    return error_state


def species_to_fix(ssn, binomial, author, create: bool = False):
    if binomial.find(" ") == -1:
        return None
    binomial = utils.to_unicode(binomial)
    author = utils.to_unicode(author)
    parts = binomial.split(" ")
    if len(parts) == 4:
        gen_epithet, sp_epithet, rank, epithet = parts
    else:
        gen_epithet, sp_epithet = binomial.split(" ", 1)
        rank = epithet = None
    result = Species.retrieve_or_create(
        ssn,
        {
            "object": "taxon",
            "rank": "species",
            "ht-epithet": gen_epithet,
            "epithet": sp_epithet,
            "ht-rank": "genus",
            "author": author,
        },
        create=create,
    )
    if rank is not None:
        result.infrasp1 = epithet
        result.infrasp1_rank = rank
        result.author = None
        result.infrasp1_author = author
    return result


ACCEPTABLE: int = 0
STOCK_ID: int = 1
OLD_BINOMIAL: int = 2
NEW_BINOMIAL: int = 3
AUTHORSHIP: int = 4
TAXON_STATUS: int = 5
ACCEPTED_BINOMIAL: int = 6
ACCEPTED_AUTHORSHIP: int = 7
TO_PROCESS: int = 8

YES_ICON: str = "gtk-yes"
NO_ICON: str = "gtk-no"


def set_row_active(tick_off_row, to_process) -> None:
    tick_off_row[TO_PROCESS] = to_process
    stock_id = to_process and YES_ICON or NO_ICON
    tick_off_row[STOCK_ID] = stock_id


class BatchTaxonomicCheckPresenter(GenericEditorPresenter):
    """
    The batch taxonomy check (BTC) can run if you have an equal rank
    selection of taxa in your search results. The BTC queries WFO directly
    through the normalized taxonomic lookup interface and then lets the user
    review the returned rows before applying them.

    the Model of the BTC is a list of tuples.

    """

    tick_off_list: Any
    binomials: Any
    widget_to_field_map: Any = {}
    view_accept_buttons: Any = ["ok_button"]

    def __init__(
        self,
        *args,
        lookup_provider: Optional[TaxonLookupProvider] = None,
        **kwargs,
    ) -> None:
        self.lookup_provider = lookup_provider or WfoTaxonLookupProvider()
        super().__init__(*args, **kwargs)
        self.refresh_visible_frame()
        self.tick_off_list = self.view.widgets.liststore2
        self.binomials = [
            item.str(remove_zws=True)
            for item in self.model.selection
            if isinstance(item, Species) and item.sp != ""
        ]

    def refresh_visible_frame(self) -> None:
        for i in range(1, 4):
            frame_id = "frame%d" % i
            self.view.widget_set_visible(frame_id, i == self.model.page)
        self.view.widget_set_sensitive("ok_button", self.model.page == 3)

    def on_frame1_next(self, *args) -> None:
        "query WFO and populate the liststore2 before moving to frame 2"
        self.view.widget_set_sensitive("button1", False)
        self.view.widget_set_value(
            "file_path_entry", _("Querying WFO for selected taxa...")
        )
        self.tick_off_list.clear()

        def worker() -> None:
            rows = build_batch_lookup_rows(self.binomials, self.lookup_provider)
            from bauble.gtkinit import GLib

            GLib.idle_add(self._finish_frame1_lookup, rows)

        threading.Thread(target=worker, daemon=True).start()

    def _finish_frame1_lookup(self, rows) -> bool:
        self.tick_off_list.clear()
        for row in rows:
            self.tick_off_list.append(row)
        self.view.widget_set_sensitive("button1", True)
        self.view.widget_set_value("file_path_entry", _("WFO lookup complete"))
        self.on_frame_next()
        return False

    def on_frame2_next(self, *args) -> None:
        "execute all that is selected in liststore2 and move to frame 3"
        self.on_frame_next(*args)
        tb = self.view.widgets.textbuffer3
        tag_bold = tb.create_tag(None, weight=Pango.Weight.BOLD)
        tag_red = tb.create_tag(
            None, weight=Pango.Weight.BOLD, foreground=Pango.Color("red")
        )
        safe_set_text(tb, "")

        for row in self.tick_off_list:
            if row[TO_PROCESS] is False:
                tb.insert_at_cursor(
                    "skipping %s\n" % (row[OLD_BINOMIAL] or row[NEW_BINOMIAL])
                )
                continue
            if row[OLD_BINOMIAL] == "":
                tb.insert_with_tags(
                    tb.get_end_iter(),
                    f"new taxon {row[NEW_BINOMIAL]}",
                    tag_bold,
                )
                obj = species_to_fix(
                    self.session,
                    row[NEW_BINOMIAL],
                    row[AUTHORSHIP],
                    create=True,
                )
            else:
                if row[TAXON_STATUS] == "Synonym":
                    accepted = species_to_fix(
                        self.session,
                        row[ACCEPTED_BINOMIAL],
                        row[ACCEPTED_AUTHORSHIP],
                        create=True,
                    )
                else:
                    accepted = None
                obj = species_to_fix(
                    self.session,
                    row[OLD_BINOMIAL],
                    row[AUTHORSHIP],
                    create=False,
                )
                if obj is None:
                    tb.insert_with_tags(
                        tb.get_end_iter(),
                        f"bad taxon {row[OLD_BINOMIAL]}",
                        tag_bold,
                        tag_red,
                    )
                    continue
                tb.insert_with_tags(
                    tb.get_end_iter(),
                    f"update taxon {row[OLD_BINOMIAL]}",
                    tag_bold,
                )

                gen_epithet, sp_epithet = utils.to_unicode(row[NEW_BINOMIAL]).split(
                    " ", 1
                )
                obj.genus.genus = gen_epithet
                obj.sp = sp_epithet
                if accepted:
                    obj.accepted = accepted
            tb.insert_with_tags(tb.get_end_iter(), f" {row[AUTHORSHIP]}\n", tag_bold)

    def on_frame_next(self, *args) -> None:
        self.model.page += 1
        self.refresh_visible_frame()

    def on_frame_previous(self, *args) -> None:
        self.model.page -= 1
        self.refresh_visible_frame()

    def on_copy_to_clipboard_button_clicked(self, *args) -> None:
        text = "\n".join(self.binomials)
        from bauble.gtkinit import Gtk

        clipboard = Gtk.Clipboard()
        safe_set_text(clipboard, text)

    def on_lookup_button_clicked(self, *args) -> None:
        self.on_frame1_next(*args)

    def on_tick_off_view_row_activated(
        self, view, path, column, data: Optional[Any] = None
    ) -> None:
        """toggle the selected row

        if selected row goes YES and is a synonym, also next row goes YES.
        if selected row goes NO and previous is synonym, previous goes NO.
        """
        if self.tick_off_list[path][ACCEPTABLE]:
            tick_off_item = self.tick_off_list[path]
            to_process = not tick_off_item[TO_PROCESS]
            set_row_active(tick_off_item, to_process)
            if to_process and tick_off_item[TAXON_STATUS] == "Synonym":
                next_row_path = (path[0] + 1,)
                set_row_active(self.tick_off_list[next_row_path], to_process)
            if not to_process and tick_off_item[OLD_BINOMIAL] == "":
                prev_row_path = (path[0] - 1,)
                set_row_active(self.tick_off_list[prev_row_path], to_process)

    def on_toggle_all_clicked(self, *args):
        all_active = reduce(
            lambda a, b: a and b,
            [row[TO_PROCESS] for row in self.tick_off_list if row[ACCEPTABLE]],
        )
        to_process = not all_active
        for row in self.tick_off_list:
            if not row[ACCEPTABLE]:
                continue
            row[TO_PROCESS] = to_process
            stock_id = to_process and YES_ICON or NO_ICON
            row[STOCK_ID] = stock_id


class TaxonomyCheckTool(pluginmgr.Tool):
    item_position: int = 15
    label: Any = _("Taxonomy check")
    icon_name: str = "taxonomy_check.png"
    icon_dir: str = "plugins/plants"

    @classmethod
    def start(cls) -> None:
        start_taxonomy_check()

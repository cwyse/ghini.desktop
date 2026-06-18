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
# Species table definition
#
import logging
import os
import traceback
import weakref
from gettext import gettext as _
from typing import Any, Optional

import bauble
import bauble.editor as editor
import bauble.paths as paths
import bauble.utils as utils
from bauble.gtkinit import Gdk, GLib, Gtk
from bauble.plugins.plants.family import Family
from bauble.plugins.plants.genus import Genus, GenusSynonym
from bauble.plugins.plants.geography import GeographicAreaMenu
from bauble.plugins.plants.species_model import Habit as Habit
from bauble.plugins.plants.species_model import Species as Species
from bauble.plugins.plants.species_model import (
    SpeciesDistribution as SpeciesDistribution,
)
from bauble.plugins.plants.species_model import SpeciesSynonym as SpeciesSynonym
from bauble.plugins.plants.species_model import VernacularName as VernacularName
from bauble.plugins.plants.species_model import (
    CultureDuration,
    CultureEnvironment,
    CultureRecommendedPropagation,
    CultureSoilDrainage,
    CultureSoilType,
    CultureSunlight,
    SpeciesCultureProfile,
    SpeciesCultureProfileMonth,
    culture_growth_rate_values,
    culture_maintenance_values,
    culture_watering_values,
)
from bauble.plugins.plants.species_model import compare_rank as compare_rank
from bauble.plugins.plants.species_model import (
    ensure_autonym_for_species as ensure_autonym_for_species,
)
from bauble.plugins.plants.species_model import (
    infrasp_rank_values as infrasp_rank_values,
)
from bauble.prefs import prefs
from bauble.utils import safe_set_props
from sqlalchemy import func, inspect as sa_inspect, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.session import object_session

logger: Any = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def safe_set_text(gtk_widget, text) -> None:
    """
    Sets the text of a Gtk widget replacing None with an empty string.

    :param label: Instance of a Gtk widget
    :param text: The text to set, which may be None
    """
    if text is None:
        text = ""
    gtk_widget.set_text(text)


_CULTURE_RANGE_FIELDS = (
    ("light", _("Light"), "light_min", "light_max", int, 0, 10, _("0-10")),
    (
        "soil_moisture",
        _("Soil moisture"),
        "soil_moisture_min",
        "soil_moisture_max",
        int,
        0,
        10,
        _("0-10"),
    ),
    (
        "atmospheric_humidity",
        _("Atmospheric humidity"),
        "atmospheric_humidity_min",
        "atmospheric_humidity_max",
        int,
        0,
        10,
        _("0-10"),
    ),
    ("soil_ph", _("Soil pH"), "soil_ph_min", "soil_ph_max", float, 0, 14, _("0-14")),
    (
        "temperature",
        _("Temperature C"),
        "temperature_min_c",
        "temperature_max_c",
        float,
        None,
        None,
        _("C"),
    ),
    (
        "hardiness_zone",
        _("Hardiness zone"),
        "hardiness_zone_min",
        "hardiness_zone_max",
        int,
        1,
        13,
        _("1-13"),
    ),
    (
        "soil_nutrient",
        _("Soil nutrients"),
        "soil_nutrient_min",
        "soil_nutrient_max",
        int,
        0,
        10,
        _("0-10"),
    ),
    (
        "soil_texture",
        _("Soil texture"),
        "soil_texture_min",
        "soil_texture_max",
        int,
        0,
        10,
        _("0-10"),
    ),
)

_CULTURE_SINGLE_NUMBER_FIELDS = (
    (
        "soil_salinity_tolerance",
        _("Soil salinity tolerance"),
        int,
        0,
        10,
        _("0-10"),
    ),
)

_CULTURE_ENUM_FIELDS = (
    ("watering", _("Watering"), culture_watering_values),
    ("growth_rate", _("Growth rate"), culture_growth_rate_values),
    ("maintenance", _("Maintenance"), culture_maintenance_values),
)

_CULTURE_BOOLEAN_FIELDS = (
    ("drought_tolerant", _("Drought tolerant")),
    ("salt_tolerant", _("Salt tolerant")),
    ("frost_sensitive", _("Frost sensitive")),
    ("indoor_suitable", _("Indoor suitable")),
    ("greenhouse_required", _("Greenhouse required")),
)

_CULTURE_TEXT_FIELDS = (
    ("culture_notes", _("Culture notes")),
    ("source_citation", _("Source citation")),
)
_CULTURE_HIDDEN_TEXT_FIELDS = ("local_notes",)

_CULTURE_LOOKUP_FIELDS = (
    ("duration_terms", CultureDuration, "duration", _("Duration")),
    ("sunlight_terms", CultureSunlight, "sunlight", _("Sunlight")),
    ("soil_drainage_terms", CultureSoilDrainage, "soil_drainage", _("Soil drainage")),
    ("soil_type_terms", CultureSoilType, "soil_type", _("Soil type")),
    (
        "recommended_propagation_terms",
        CultureRecommendedPropagation,
        "recommended_propagation",
        _("Recommended propagation"),
    ),
    ("environment_terms", CultureEnvironment, "environment", _("Environment")),
)

_CULTURE_MONTH_TYPES = (
    (
        "growth",
        _("Active growth"),
        _("Months when the species is normally in active vegetative growth."),
    ),
    ("bloom", _("Bloom"), _("Months when flowering is normally expected.")),
    ("fruit", _("Fruit"), _("Months when fruit is normally expected.")),
    (
        "pruning",
        _("Pruning"),
        _("General pruning or cut-back window; leave blank if not relevant."),
    ),
)
_CULTURE_MONTH_LABELS = (
    _("Jan"),
    _("Feb"),
    _("Mar"),
    _("Apr"),
    _("May"),
    _("Jun"),
    _("Jul"),
    _("Aug"),
    _("Sep"),
    _("Oct"),
    _("Nov"),
    _("Dec"),
)


def _culture_widget_name(*parts):
    return "culture_" + "_".join(str(part) for part in parts)


class CulturePresenter(editor.GenericEditorPresenter):
    """Presenter for species-level culture guidance."""

    PROBLEM_BAD_NUMBER = "culture-bad-number"
    PROBLEM_BAD_RANGE = "culture-bad-range"

    def __init__(self, parent) -> None:
        super().__init__(parent.model, parent.view)
        self.parent_ref = weakref.ref(parent)
        self._dirty = False
        self._refreshing = False
        self._lookup_buttons = {}
        self._populate_enum_widgets()
        self._populate_lookup_widgets()
        self._connect_widgets()
        self.refresh_view()

    def is_dirty(self):
        return self._dirty

    def _mark_dirty(self) -> None:
        self._dirty = True
        self.parent_ref().refresh_sensitivity()

    def _profile(self):
        return self.model.culture_profile

    def _ensure_profile(self):
        if self.model.culture_profile is None:
            self.model.culture_profile = SpeciesCultureProfile()
        return self.model.culture_profile

    def _populate_enum_widgets(self) -> None:
        for field, _label, values in _CULTURE_ENUM_FIELDS:
            combo = self.view.culture_widgets[_culture_widget_name(field, "combo")]
            combo.append("", "")
            for value in values:
                combo.append(value, value.replace("_", " ").capitalize())

    def _populate_lookup_widgets(self) -> None:
        for attr, klass, prefix, _label in _CULTURE_LOOKUP_FIELDS:
            box = self.view.culture_widgets[_culture_widget_name(prefix, "box")]
            for child in box.get_children():
                box.remove(child)
            stmt = (
                select(klass)
                .where(klass.active.is_(True))
                .order_by(klass.sort_order, klass.label)
            )
            for term in self.session.scalars(stmt):
                name = _culture_widget_name(prefix, term.code, "check")
                button = Gtk.CheckButton(label=term.label)
                self.view.register_culture_widget(name, button)
                button.set_tooltip_text(term.description or term.label)
                box.add(button)
                self._lookup_buttons[(attr, term.code)] = button
                self.view.connect(button, "toggled", self.on_lookup_toggled, attr, term)
            box.show_all()

    def _connect_widgets(self) -> None:
        for (
            _key,
            _label,
            min_field,
            max_field,
            _parser,
            _minimum,
            _maximum,
            _hint,
        ) in _CULTURE_RANGE_FIELDS:
            for field in (min_field, max_field):
                widget = self.view.culture_widgets[_culture_widget_name(field, "entry")]
                self.view.connect(widget, "changed", self.on_number_changed, field)

        for (
            field,
            _label,
            _parser,
            _minimum,
            _maximum,
            _hint,
        ) in _CULTURE_SINGLE_NUMBER_FIELDS:
            widget = self.view.culture_widgets[_culture_widget_name(field, "entry")]
            self.view.connect(widget, "changed", self.on_number_changed, field)

        for field, _label, _values in _CULTURE_ENUM_FIELDS:
            widget = self.view.culture_widgets[_culture_widget_name(field, "combo")]
            self.view.connect(widget, "changed", self.on_enum_changed, field)

        for field, _label in _CULTURE_BOOLEAN_FIELDS:
            widget = self.view.culture_widgets[_culture_widget_name(field, "check")]
            self.view.connect(widget, "toggled", self.on_boolean_toggled, field)

        for field, _label in _CULTURE_TEXT_FIELDS:
            widget = self.view.culture_widgets[_culture_widget_name(field, "textview")]
            self.view.connect(
                widget.get_buffer(), "changed", self.on_text_changed, field
            )

        for month_type, _label, _tooltip in _CULTURE_MONTH_TYPES:
            for month in range(1, 13):
                name = _culture_widget_name("month", month_type, month, "check")
                widget = self.view.culture_widgets[name]
                self.view.connect(
                    widget, "toggled", self.on_month_toggled, month_type, month
                )

    def _field_spec(self, field):
        for (
            _key,
            _label,
            min_field,
            max_field,
            parser,
            minimum,
            maximum,
            _hint,
        ) in _CULTURE_RANGE_FIELDS:
            if field in (min_field, max_field):
                return parser, minimum, maximum
        for (
            name,
            _label,
            parser,
            minimum,
            maximum,
            _hint,
        ) in _CULTURE_SINGLE_NUMBER_FIELDS:
            if field == name:
                return parser, minimum, maximum
        return str, None, None

    def _range_pair(self, field):
        for (
            _key,
            _label,
            min_field,
            max_field,
            _parser,
            _minimum,
            _maximum,
            _hint,
        ) in _CULTURE_RANGE_FIELDS:
            if field in (min_field, max_field):
                return min_field, max_field
        return None

    def _parse_number(self, widget, field):
        text = widget.get_text().strip()
        if text == "":
            self.remove_problem((self.PROBLEM_BAD_NUMBER, field), widget)
            return True, None
        parser, minimum, maximum = self._field_spec(field)
        try:
            value = parser(text)
        except ValueError:
            self.add_problem((self.PROBLEM_BAD_NUMBER, field), widget)
            return False, None
        if (minimum is not None and value < minimum) or (
            maximum is not None and value > maximum
        ):
            self.add_problem((self.PROBLEM_BAD_NUMBER, field), widget)
            return False, None
        self.remove_problem((self.PROBLEM_BAD_NUMBER, field), widget)
        return True, value

    def _validate_range_pair(self, pair) -> bool:
        if pair is None:
            return True
        min_field, max_field = pair
        min_widget = self.view.culture_widgets[_culture_widget_name(min_field, "entry")]
        max_widget = self.view.culture_widgets[_culture_widget_name(max_field, "entry")]
        ok_min, min_value = self._parse_number(min_widget, min_field)
        ok_max, max_value = self._parse_number(max_widget, max_field)
        problem_id = (self.PROBLEM_BAD_RANGE, min_field, max_field)
        if ok_min and ok_max and min_value is not None and max_value is not None:
            if min_value > max_value:
                self.add_problem(problem_id, [min_widget, max_widget])
                return False
        self.remove_problem(problem_id, min_widget)
        self.remove_problem(problem_id, max_widget)
        return ok_min and ok_max

    def on_number_changed(self, widget, field) -> None:
        if self._refreshing:
            return
        ok, value = self._parse_number(widget, field)
        self._validate_range_pair(self._range_pair(field))
        if ok:
            setattr(self._ensure_profile(), field, value)
            self._mark_dirty()
        else:
            self.parent_ref().refresh_sensitivity()

    def on_enum_changed(self, widget, field) -> None:
        if self._refreshing:
            return
        value = widget.get_active_id() or None
        setattr(self._ensure_profile(), field, value)
        self._mark_dirty()

    def on_boolean_toggled(self, widget, field) -> None:
        if self._refreshing:
            return
        setattr(self._ensure_profile(), field, widget.get_active())
        self._mark_dirty()

    def on_text_changed(self, buffer, field) -> None:
        if self._refreshing:
            return
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        value = buffer.get_text(start, end, False).strip() or None
        setattr(self._ensure_profile(), field, value)
        self._mark_dirty()

    def on_lookup_toggled(self, widget, attr, term) -> None:
        if self._refreshing:
            return
        profile = self._ensure_profile()
        terms = getattr(profile, attr)
        if widget.get_active():
            if term not in terms:
                terms.append(term)
        elif term in terms:
            terms.remove(term)
        self._mark_dirty()

    def on_month_toggled(self, widget, month_type, month) -> None:
        if self._refreshing:
            return
        profile = self._ensure_profile()
        existing = [
            item
            for item in profile.months
            if item.month_type == month_type and item.month == month
        ]
        if widget.get_active() and not existing:
            profile.months.append(
                SpeciesCultureProfileMonth(month_type=month_type, month=month)
            )
        elif not widget.get_active():
            for item in existing:
                profile.months.remove(item)
                utils.delete_or_expunge(item)
        self._mark_dirty()

    def profile_is_empty(self, profile=None) -> bool:
        profile = profile or self._profile()
        if profile is None:
            return True
        scalar_fields = []
        for (
            _key,
            _label,
            min_field,
            max_field,
            _parser,
            _minimum,
            _maximum,
            _hint,
        ) in _CULTURE_RANGE_FIELDS:
            scalar_fields.extend([min_field, max_field])
        scalar_fields.extend(
            field
            for field, _label, _parser, _minimum, _maximum, _hint in _CULTURE_SINGLE_NUMBER_FIELDS
        )
        scalar_fields.extend(field for field, _label, _values in _CULTURE_ENUM_FIELDS)
        scalar_fields.extend(field for field, _label in _CULTURE_BOOLEAN_FIELDS)
        scalar_fields.extend(field for field, _label in _CULTURE_TEXT_FIELDS)
        scalar_fields.extend(_CULTURE_HIDDEN_TEXT_FIELDS)
        if any(getattr(profile, field) not in (None, "") for field in scalar_fields):
            return False
        if any(
            getattr(profile, attr)
            for attr, _klass, _prefix, _label in _CULTURE_LOOKUP_FIELDS
        ):
            return False
        return not profile.months

    def cleanup_empty_profile(self) -> None:
        profile = self._profile()
        if profile is None or not self.profile_is_empty(profile):
            return
        self.model.culture_profile = None
        utils.delete_or_expunge(profile)

    def refresh_view(self) -> None:
        profile = self._profile()
        self._refreshing = True
        try:
            for (
                _key,
                _label,
                min_field,
                max_field,
                _parser,
                _minimum,
                _maximum,
                _hint,
            ) in _CULTURE_RANGE_FIELDS:
                for field in (min_field, max_field):
                    widget = self.view.culture_widgets[
                        _culture_widget_name(field, "entry")
                    ]
                    value = "" if profile is None else getattr(profile, field)
                    value = "" if value is None else str(value)
                    safe_set_text(widget, value)
                    self.remove_problem((self.PROBLEM_BAD_NUMBER, field), widget)

            for (
                field,
                _label,
                _parser,
                _minimum,
                _maximum,
                _hint,
            ) in _CULTURE_SINGLE_NUMBER_FIELDS:
                widget = self.view.culture_widgets[_culture_widget_name(field, "entry")]
                value = "" if profile is None else getattr(profile, field)
                value = "" if value is None else str(value)
                safe_set_text(widget, value)
                self.remove_problem((self.PROBLEM_BAD_NUMBER, field), widget)

            for field, _label, _values in _CULTURE_ENUM_FIELDS:
                widget = self.view.culture_widgets[_culture_widget_name(field, "combo")]
                widget.set_active_id(
                    "" if profile is None else getattr(profile, field) or ""
                )

            for field, _label in _CULTURE_BOOLEAN_FIELDS:
                widget = self.view.culture_widgets[_culture_widget_name(field, "check")]
                widget.set_active(bool(profile is not None and getattr(profile, field)))

            for field, _label in _CULTURE_TEXT_FIELDS:
                widget = self.view.culture_widgets[
                    _culture_widget_name(field, "textview")
                ]
                text = "" if profile is None else getattr(profile, field) or ""
                widget.get_buffer().set_text(text)

            for attr, _klass, _prefix, _label in _CULTURE_LOOKUP_FIELDS:
                selected = set()
                if profile is not None:
                    selected = {term.code for term in getattr(profile, attr)}
                for (button_attr, code), button in self._lookup_buttons.items():
                    if button_attr == attr:
                        button.set_active(code in selected)

            active_months = set()
            if profile is not None:
                active_months = {
                    (item.month_type, item.month) for item in profile.months
                }
            for month_type, _label, _tooltip in _CULTURE_MONTH_TYPES:
                for month in range(1, 13):
                    name = _culture_widget_name("month", month_type, month, "check")
                    self.view.culture_widgets[name].set_active(
                        (month_type, month) in active_months
                    )
        finally:
            self._refreshing = False


class SpeciesEditorPresenter(editor.GenericEditorPresenter):

    initializing: bool
    session: Any
    _dirty: bool
    omonym_box: Any
    species_check_messages: Any
    genus_check_messages: Any
    species_space: bool
    vern_presenter: Any
    synonyms_presenter: Any
    dist_presenter: Any
    infrasp_presenter: Any
    notes_presenter: Any
    pictures_presenter: Any
    PROBLEM_INVALID_GENUS: int = 1

    widget_to_field_map: Any = {
        "sp_genus_entry": "genus",
        "sp_species_entry": "epithet",
        "sp_author_entry": "author",
        "sp_hybrid_check": "hybrid",
        "sp_cvgroup_entry": "cv_group",
        "sp_spqual_combo": "sp_qual",
        "sp_awards_entry": "awards",
        "sp_label_dist_entry": "label_distribution",
        "sp_habit_comboentry": "habit",
    }
    field_length_validators: Any = {
        "sp_species_entry": editor.MaxLengthValidator(
            64, editor.UnicodeOrNoneValidator()
        ),
        "sp_author_entry": editor.MaxLengthValidator(
            128, editor.UnicodeOrNoneValidator()
        ),
        "sp_cvgroup_entry": editor.MaxLengthValidator(
            50, editor.UnicodeOrNoneValidator()
        ),
    }

    def __init__(self, model, view) -> None:
        super().__init__(model, view)
        self.initializing = True
        self.create_toolbar()
        self.session = object_session(model)
        self._dirty = False
        self.omonym_box = None
        self.species_check_messages = []
        self.genus_check_messages = []
        self.species_space = False  # do not accept spaces in epithet
        self.init_fullname_widgets()
        self.vern_presenter = VernacularNamePresenter(self)
        self.synonyms_presenter = SynonymsPresenter(self)
        self.dist_presenter = DistributionPresenter(self)
        self.infrasp_presenter = InfraspPresenter(self)
        self.culture_presenter = CulturePresenter(self)

        # Ignore this warning:  g_value_get_int: assertion 'G_VALUE_HOLDS_INT (value)' failed
        # It is a known python bug:  https://bugzilla.gnome.org/show_bug.cgi?id=708676
        import warnings

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", message=".*g_value_get_int.*set_text.*", category=Warning
            )

        notes_parent = self.view.widgets.notes_parent_box
        notes_parent.foreach(notes_parent.remove)
        self.notes_presenter = editor.NotesPresenter(self, "notes", notes_parent)

        pictures_parent = self.view.widgets.pictures_parent_box
        pictures_parent.foreach(pictures_parent.remove)
        self.pictures_presenter = editor.PicturesPresenter(
            self, "notes", pictures_parent
        )

        self.init_enum_combo("sp_spqual_combo", "sp_qual")

        def cell_data_func(column, cell, model, treeiter, data=None):
            safe_set_text(cell, str(model[treeiter][0]))

        combo = self.view.widgets.sp_habit_comboentry
        model = Gtk.ListStore(str, object)
        list(
            [
                model.append(p)
                for p in [
                    (str(h), h) for h in self.session.execute(select(Habit)).scalars()
                ]
            ]
        )
        utils.setup_text_combobox(combo, model)

        def on_focus_out(entry, event):
            # check if the combo has a problem then check if the value
            # in the entry matches one of the habit codes and if so
            # then change the value to the habit
            code = entry.get_text()
            try:
                utils.set_combo_from_value(
                    combo,
                    code.lower(),
                    cmp=lambda r, v: str(r[1].code).lower() == v,
                )
            except ValueError:
                pass

        combo.get_child().connect("focus-out-event", on_focus_out)

        # set the model values in the widgets
        self.refresh_view()

        # connect habit comboentry widget and child entry
        self.view.connect(
            "sp_habit_comboentry", "changed", self.on_habit_comboentry_changed
        )

        # connect signals
        def gen_get_completions(text):
            clause = utils.ilike(Genus.genus, f"{text}%")
            stmt = select(Genus).where(clause).order_by(Genus.genus)

            logger.debug(
                "Genus completion query: %s",
                stmt.compile(compile_kwargs={"literal_binds": True}),
            )

            result = list(self.session.scalars(stmt))
            logger.debug(
                "Genus completion query returned: %s", [g.genus for g in result]
            )
            return result

        def sp_species_TPL_callback(found, accepted):
            # both found and accepted are dictionaries, their keys here
            # relevant: 'Species hybrid marker', 'Species', 'Authorship',
            # 'Taxonomic status in TPL'.

            # we can provide the user the option to accept spellings
            # corrections in 'Species', the full value of 'Authorship', and
            # full acceptedy links. it's TWO boxes that we might show. or
            # one if nothing matches.

            self.view.close_boxes()
            if found:
                found = {k: utils.to_unicode(v) for k, v in list(found.items())}
                found_s = {
                    k: utils.xml_safe(utils.to_unicode(v))
                    for k, v in list(found.items())
                }
            if accepted:
                accepted = {k: utils.to_unicode(v) for k, v in list(accepted.items())}
                accepted_s = {
                    k: utils.xml_safe(utils.to_unicode(v))
                    for k, v in list(accepted.items())
                }

            msg_box_msg = _("No match found on World Flora Online")

            if not (found is None and accepted is None):

                # if inserted data matches found, just say so.
                if (
                    self.model.epithet == found["Species"]
                    and self.model.author == found["Authorship"]
                    and self.model.hybrid == (found["Species hybrid marker"] == "×")
                ):
                    msg_box_msg = _("your data matches World Flora Online")
                else:
                    cit = (
                        "<i>{Genus}</i> {Species hybrid marker}"
                        "<i>{Species}</i> {Authorship} ({Family})"
                    ).format(**found_s)
                    msg = (
                        _(
                            "%s is the closest match for your data.\n"
                            "Do you want to accept it?"
                        )
                        % cit
                    )
                    b1 = box = self.view.add_message_box(utils.MESSAGE_BOX_YESNO)
                    box.message = msg

                    def on_response_found(button, response):
                        self.view.remove_box(b1)
                        if response:
                            self.set_model_attr("epithet", found["Species"])
                            self.set_model_attr("author", found["Authorship"])
                            self.set_model_attr(
                                "hybrid", found["Species hybrid marker"] == "×"
                            )
                            self.refresh_view()
                            self.refresh_fullname_label()

                    box.on_response = on_response_found
                    self.view.add_box(box)
                    self.species_check_messages.append(box)
                    box.show()
                    msg_box_msg = None

                if self.model.accepted is None and accepted is not None:
                    if not accepted:  # infraspecific synonym, can't handle
                        msg = _(
                            "closest match is a synonym of something at "
                            "infraspecific rank, which I cannot handle."
                        )
                        b2 = box = self.view.add_message_box(utils.MESSAGE_BOX_INFO)
                        box.message = msg

                        def on_response_accepted(button, response):
                            self.view.remove_box(b2)

                    else:
                        # synonym is at rank species, this is fine
                        cit = (
                            "<i>{Genus}</i> {Species hybrid marker}"
                            "<i>{Species}</i> {Authorship} ({Family})"
                        ).format(**accepted_s)
                        msg = (
                            _(
                                "%s is the accepted taxon for your data.\n"
                                "Do you want to add it?"
                            )
                            % cit
                        )
                        b2 = box = self.view.add_message_box(utils.MESSAGE_BOX_YESNO)
                        box.message = msg

                        def on_response_accepted(button, response):
                            self.view.remove_box(b2)
                            if response:
                                hybrid = (
                                    accepted["Species hybrid marker"]
                                    == Species.hybrid_char
                                )
                                self.model.accepted = Species.retrieve_or_create(
                                    self.session,
                                    {
                                        "object": "taxon",
                                        "rank": "species",
                                        "ht-rank": "genus",
                                        "familia": accepted["Family"],
                                        "ht-epithet": accepted["Genus"],
                                        "epithet": accepted["Species"],
                                        "author": accepted["Authorship"],
                                        "hybrid": hybrid,
                                    },
                                )
                                self.refresh_view()
                                self.refresh_fullname_label()

                    box.on_response = on_response_accepted
                    self.view.add_box(box)
                    self.species_check_messages.append(box)
                    box.show()
                    msg_box_msg = None

            if msg_box_msg is not None:
                b0 = self.view.add_message_box(utils.MESSAGE_BOX_INFO)
                b0.message = msg_box_msg
                b0.on_response = lambda b, r: self.view.remove_box(b0)
                self.view.add_box(b0)
                self.species_check_messages.append(b0)
                b0.show()

        def on_sp_species_button_clicked(widget, event=None):
            # the real activity runs in a separate thread.
            from .ask_tpl import AskTPL

            while self.species_check_messages:
                kid = self.species_check_messages.pop()
                self.view.widgets.remove_parent(kid)

            binomial = f"{self.model.genus} {self.model.epithet}"
            timeout = prefs.get("network_timeout", 4)
            AskTPL(binomial, sp_species_TPL_callback, timeout=timeout, gui=True).start()
            b0 = self.view.add_message_box(utils.MESSAGE_BOX_INFO)
            b0.message = _("querying World Flora Online")
            b0.on_response = lambda b, r: self.view.remove_box(b0)
            self.view.add_box(b0)
            b0.show()
            if event is not None:
                return False

        self.view.connect("sp_species_button", "clicked", on_sp_species_button_clicked)

        # called when a genus is selected from the genus completions
        def on_select(value):
            logger.debug(f"on select: {value}")
            if isinstance(value, str):
                value = self.session.scalars(
                    select(Genus).where(Genus.genus == value)
                ).first()

            while self.genus_check_messages:
                kid = self.genus_check_messages.pop()
                self.view.widgets.remove_parent(kid)
            self.set_model_attr("genus", value)
            if not value:  # no choice is a fine choice
                return
            # is value considered a synonym?

            syn = self.session.scalars(
                select(GenusSynonym).where(GenusSynonym.synonym_id == value.id)
            ).first()
            if not syn:
                # chosen value is not a synonym, also fine
                return

            # value is a synonym: user alert needed
            msg = _(
                "The genus <b>%(synonym)s</b> is a synonym of "
                "<b>%(genus)s</b>.\n\nWould you like to choose "
                "<b>%(genus)s</b> instead?"
            ) % {"synonym": syn.synonym, "genus": syn.genus}
            box = None

            def on_response(button, response):
                self.view.remove_box(box)
                if response:
                    self.set_model_attr("genus", syn.genus)
                    self.refresh_view()
                    self.refresh_fullname_label()

            box = self.view.add_message_box(utils.MESSAGE_BOX_YESNO)
            box.message = msg
            box.on_response = on_response
            self.view.add_box(box)
            self.genus_check_messages.append(box)
            box.show()

        on_select(self.model.genus)

        self.assign_completions_handler(
            "sp_genus_entry",
            gen_get_completions,
            on_select=on_select,  # 'genus',
        )
        self.assign_simple_handler(
            "sp_cvgroup_entry",
            "cv_group",
            self.field_length_validators["sp_cvgroup_entry"],
        )
        self.assign_simple_handler(
            "sp_spqual_combo", "sp_qual", editor.UnicodeOrNoneValidator()
        )
        self.assign_simple_handler(
            "sp_label_dist_entry",
            "label_distribution",
            editor.UnicodeOrNoneValidator(),
        )
        self.assign_simple_handler(
            "sp_awards_entry", "awards", editor.UnicodeOrNoneValidator()
        )

        try:
            import bauble.plugins.garden

            bauble.plugins.garden  # fake its usage
            if self.model not in self.model.new:
                self.view.widgets.sp_ok_and_add_button.set_sensitive(True)
        except Exception:
            pass
        self.initializing = False

    def set_visible_buttons(self, visible) -> None:
        self.view.widgets.sp_ok_and_add_button.set_visible(visible)
        self.view.widgets.sp_next_button.set_visible(visible)

    def on_sp_species_entry_changed(self, widget, *args) -> None:
        self.on_text_entry_changed(widget, *args)
        self.on_entry_changed_clear_boxes(widget, *args)

    def on_text_entry_changed(self, widget, value: Optional[Any] = None):
        widget_name = self.widget_get_name(widget)
        validator = self.field_length_validators.get(widget_name)
        if validator is None:
            return super().on_text_entry_changed(widget, value)

        attr = self.widget_to_field_map.get(widget_name)
        if attr is None:
            return None
        value = self.view.widget_get_value(widget)
        problem_id = f"BAD_VALUE_{attr}"
        try:
            value = validator.to_python(value)
        except editor.ValidatorError:
            self.add_problem(problem_id, widget)
            self.view.set_accept_buttons_sensitive(False)
            return value
        self.remove_problem(problem_id, widget)
        self.set_model_attr(attr, value)
        return value

    def on_entry_changed_clear_boxes(self, widget, *args) -> None:
        while self.species_check_messages:
            kid = self.species_check_messages.pop()
            self.view.widgets.remove_parent(kid)

    def on_habit_comboentry_changed(self, combo, *args) -> None:
        """
        Changed handler for sp_habit_comboentry.

        We don't need specific handlers for either comboentry because
        the validation is done in the specific Gtk.Entry handlers for
        the child of the combo entries.
        """
        treeiter = combo.get_active_iter()
        if not treeiter:
            return
        value = combo.get_model()[treeiter][1]
        self.set_model_attr("habit", value)
        # the entry change handler does the validation of the model
        safe_set_text(combo.get_child(), str(value))
        combo.get_child().set_position(-1)

    def __del__(self) -> None:
        # we have to delete the views in the child presenters manually
        # to avoid the circular reference
        del self.vern_presenter.view
        del self.synonyms_presenter.view
        del self.dist_presenter.view
        del self.notes_presenter.view
        del self.infrasp_presenter.view
        del self.culture_presenter.view

    def is_dirty(self):
        return (
            self._dirty
            or self.pictures_presenter.is_dirty()
            or self.vern_presenter.is_dirty()
            or self.synonyms_presenter.is_dirty()
            or self.dist_presenter.is_dirty()
            or self.infrasp_presenter.is_dirty()
            or self.notes_presenter.is_dirty()
            or self.culture_presenter.is_dirty()
        )

    def has_child_problems(self) -> bool:
        return bool(
            self.problems
            or self.vern_presenter.problems
            or self.synonyms_presenter.problems
            or self.dist_presenter.problems
            or self.notes_presenter.problems
            or self.pictures_presenter.problems
            or self.infrasp_presenter.problems
            or self.culture_presenter.problems
        )

    def set_model_attr(self, field, value, validator: Optional[Any] = None) -> None:
        """
        Resets the sensitivity on the ok buttons and the name widgets
        when values change in the model
        """
        super().set_model_attr(field, value, validator)
        self._dirty = True
        sensitive = True
        if self.has_child_problems():
            sensitive = False
        elif not self.model.genus:
            sensitive = False
        self.view.set_accept_buttons_sensitive(sensitive)

    def refresh_sensitivity(self) -> None:
        """
        :param self:
        """
        self.view.set_accept_buttons_sensitive(
            self.is_dirty()
            and self.model.genus is not None
            and not self.has_child_problems()
        )

    def init_fullname_widgets(self):
        """
        initialized the signal handlers on the widgets that are relative to
        building the fullname string in the sp_fullname_label widget
        """
        self.refresh_fullname_label()

        def refresh(*args):
            return self.refresh_fullname_label(*args)

        widgets = [
            "sp_genus_entry",
            "sp_species_entry",
            "sp_author_entry",
            "sp_cvgroup_entry",
            "sp_spqual_combo",
        ]
        for widget_name in widgets:
            self.view.connect_after(widget_name, "changed", refresh)
        self.view.connect_after("sp_hybrid_check", "toggled", refresh)

    def on_sp_species_entry_insert_text(self, entry, text, length, position):
        """remove all spaces from epithet"""
        while self.species_check_messages:
            kid = self.species_check_messages.pop()
            self.view.widgets.remove_parent(kid)

        new_text = text
        entry.get_text()
        # get position from entry, can't trust position parameter
        cursor_pos = entry.get_position()

        # Prepare new text
        if "×" in new_text:
            self.species_space = True
        if "*" in new_text:
            self.species_space = True
            new_text = new_text.replace("*", " × ")
        if not self.species_space:
            new_text = new_text.replace(" ", "")
        if new_text != "":
            # Construct the final text to be set
            # Insert the text at cursor (block handler to avoid recursion).
            entry.handler_block_by_func(self.on_sp_species_entry_insert_text)
            entry.insert_text(new_text, cursor_pos)
            entry.handler_unblock_by_func(self.on_sp_species_entry_insert_text)

            new_pos = cursor_pos + len(new_text)
            # Can't modify the cursor position from within this handler,
            # so we add it to be done at the end of the main loop:
            GLib.idle_add(entry.set_position, new_pos)

        # We handled the signal so stop it from being processed further.
        try:
            entry.stop_emission_by_name("insert-text")
        except Exception as e:
            logger.debug("Could not stop species entry insert-text emission: %s", e)

        return True

    def ensure_string(self, value):
        """
        Ensure the input is a string. If bytes, decode to UTF-8. Otherwise, str().
        """
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)

    def refresh_fullname_label(self, widget: Optional[Any] = None) -> None:
        """
        set the value of sp_fullname_label to either '--' if there
        is a problem or to the name of the string returned by Species.str
        """
        logger.debug(f"SpeciesEditorPresenter:refresh_fullname_label {widget}")
        if len(self.problems) > 0 or self.model.genus is None:
            self.view.set_label("sp_fullname_label", "--")
            return
        sp_str = self.ensure_string(self.model.str(markup=True, authors=True))
        self.view.set_label("sp_fullname_label", sp_str)
        if self.model.genus is not None:
            genus = self.model.genus
            epithet = self.view.widget_get_value("sp_species_entry")
            genus_state = sa_inspect(genus)
            genus_id = genus_state.identity[0] if genus_state.identity else genus.id
            if genus_id is None:
                return

            omonym = self.session.scalars(
                select(Species).where(
                    Species.genus_id == genus_id, Species.epithet == epithet
                )
            ).first()

            logger.debug(f"looking for {genus} {epithet}, found {omonym}")
            if omonym in [None, self.model]:
                # should not warn, so check warning and remove
                if self.omonym_box is not None:
                    self.view.remove_box(self.omonym_box)
                    self.omonym_box = None
            elif self.omonym_box is None:  # should warn, but not twice
                msg = _(
                    "This binomial name is already in your collection"
                    ", as %s.\n\n"
                    "Are you sure you want to insert it again?"
                ) % omonym.str(authors=True, markup=True)

                def on_response(button, response):
                    self.view.remove_box(self.omonym_box)
                    self.omonym_box = None
                    if response:
                        logger.warning("yes")
                    else:
                        self.view.widget_set_value("sp_species_entry", "")

                box = self.omonym_box = self.view.add_message_box(
                    utils.MESSAGE_BOX_YESNO
                )
                box.message = msg
                box.on_response = on_response
                self.view.add_box(box)
                box.show()

    def cleanup(self) -> None:
        super().cleanup()
        self.vern_presenter.cleanup()
        self.synonyms_presenter.cleanup()
        self.dist_presenter.cleanup()
        self.infrasp_presenter.cleanup()
        self.culture_presenter.cleanup()

    def start(self):
        r = self.view.start()
        return r

    def refresh_view(self) -> None:
        for widget, field in list(self.widget_to_field_map.items()):
            if field == "genus_id":
                value = self.model.genus
            else:
                value = getattr(self.model, field)
            logger.debug(f"{widget}, {field}, {type(value)}({value})")
            self.view.widget_set_value(widget, value)

        utils.set_widget_value(
            self.view.widgets.sp_habit_comboentry, self.model.habit or ""
        )
        self.vern_presenter.refresh_view(self.model.default_vernacular_name)
        self.synonyms_presenter.refresh_view()
        self.dist_presenter.refresh_view()
        self.culture_presenter.refresh_view()


class InfraspPresenter(editor.GenericEditorPresenter):
    """ """

    parent_ref: Any
    _dirty: bool
    table_rows: Any

    def __init__(self, parent) -> None:
        """
        :param parent: the parent SpeciesEditorPresenter
        """
        super().__init__(parent.model, parent.view)
        self.parent_ref = weakref.ref(parent)
        self._dirty = False
        self.view.connect("add_infrasp_button", "clicked", self.append_infrasp)

        # will table.resize() remove the children??
        self.view.widgets.infrasp_table
        for item in self.view.widgets.infrasp_table.get_children():
            if not isinstance(item, Gtk.Label):
                self.view.widgets.remove_parent(item)

        self.table_rows = []
        for index in range(1, 5):
            infrasp = self.model.get_infrasp(index)
            if infrasp != (None, None, None):
                self.append_infrasp()

    def is_dirty(self):
        return self._dirty

    def append_infrasp(self, *args):
        """ """
        # TODO: it is very slow to add rows to the widget...maybe if
        # we disable event on the table until all the rows have been
        # added
        level = len(self.table_rows) + 1
        row = InfraspPresenter.Row(self, level)
        self.table_rows.append(row)
        if level >= 4:
            self.view.widgets.add_infrasp_button.set_sensitive(False)
        return row

    class Row:

        presenter: Any
        species: Any
        level: Any
        rank_combo: Any
        epithet_entry: Any
        author_entry: Any
        remove_button: Any

        def __init__(self, presenter, level) -> None:
            """ """
            self.presenter = presenter
            self.species = presenter.model
            table = self.presenter.view.widgets.infrasp_table
            table.get_allocated_height()
            table.get_allocated_width()
            self.level = level

            rank, epithet, author = self.species.get_infrasp(self.level)

            # rank combo
            self.rank_combo = Gtk.ComboBox()
            self.rank_combo.set_hexpand(False)
            self.rank_combo.set_vexpand(False)
            self.presenter.view.init_translatable_combo(
                self.rank_combo, infrasp_rank_values, cmp=compare_rank
            )
            utils.set_widget_value(self.rank_combo, rank)
            presenter.view.connect(
                self.rank_combo, "changed", self.on_rank_combo_changed
            )
            table.attach(self.rank_combo, 0, level, 1, 1)

            # epithet entry
            self.epithet_entry = Gtk.Entry()
            self.epithet_entry.set_hexpand(True)
            self.epithet_entry.set_vexpand(False)
            utils.set_widget_value(self.epithet_entry, epithet)
            presenter.view.connect(
                self.epithet_entry, "changed", self.on_epithet_entry_changed
            )
            table.attach(self.epithet_entry, 1, level, 1, 1)

            # author entry
            self.author_entry = Gtk.Entry()
            self.author_entry.set_hexpand(True)
            self.author_entry.set_vexpand(False)
            utils.set_widget_value(self.author_entry, author)
            presenter.view.connect(
                self.author_entry, "changed", self.on_author_entry_changed
            )
            table.attach(self.author_entry, 2, level, 1, 1)

            self.remove_button = Gtk.Button()
            self.remove_button.set_hexpand(
                False
            )  # No horizontal expansion; filling is enough
            self.remove_button.set_vexpand(False)  # No vertical expansion
            img = Gtk.Image.new_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON)
            # 7. issue_gtk_button_image_api (REMOVED, pack GtkImage manually inside GtkButton)
            if Gtk.get_major_version() >= 4:
                self.remove_button.set_child(img)
            else:
                self.remove_button.add(img)
                self.remove_button.show_all()
            presenter.view.connect(
                self.remove_button, "clicked", self.on_remove_button_clicked
            )
            table.attach(self.remove_button, 3, level, 1, 1)
            table.show_all()

        def on_remove_button_clicked(self, *args) -> None:
            # remove the widgets
            table = self.presenter.view.widgets.infrasp_table

            # remove the infrasp from the species and reset the levels
            # on the remaining infrasp that have a higher level than
            # the one being deleted
            table.remove(self.rank_combo)
            table.remove(self.epithet_entry)
            table.remove(self.author_entry)
            table.remove(self.remove_button)

            self.set_model_attr("rank", None)
            self.set_model_attr("epithet", None)
            self.set_model_attr("author", None)

            # move all the infrasp values up a level
            for i in range(self.level + 1, 5):
                rank, epithet, author = self.species.get_infrasp(i)
                self.species.set_infrasp(i - 1, rank, epithet, author)

            self.presenter._dirty = False
            self.presenter.parent_ref().refresh_fullname_label()
            self.presenter.parent_ref().refresh_sensitivity()
            self.presenter.view.widgets.add_infrasp_button.set_sensitive(True)

        def set_model_attr(self, attr, value) -> None:
            infrasp_attr = Species.infrasp_attr[self.level][attr]
            setattr(self.species, infrasp_attr, value)
            self.presenter._dirty = True
            self.presenter.parent_ref().refresh_fullname_label()
            self.presenter.parent_ref().refresh_sensitivity()

        def on_rank_combo_changed(self, combo, *args) -> None:
            logger.info(f"on_rank_combo_changed({combo}, {args})")
            model = combo.get_model()
            it = combo.get_active_iter()
            value = model[it][0]
            if value is not None:
                self.set_model_attr("rank", str(model[it][0]))
            else:
                self.set_model_attr("rank", None)

        def on_epithet_entry_changed(self, entry, *args) -> None:
            logger.info(f"on_epithet_entry_changed({entry}, {args})")
            value = entry.get_text()
            if not value:  # if None or ''
                value = None
            self.set_model_attr("epithet", value)
            # now warn if same binomial is already in database

        def on_author_entry_changed(self, entry, *args) -> None:
            logger.info(f"on_author_entry_changed({entry}, {args})")
            value = entry.get_text()
            if not value:  # if None or ''
                value = None
            self.set_model_attr("author", value)


class DistributionPresenter(editor.GenericEditorPresenter):
    """ """

    parent_ref: Any
    session: Any
    _dirty: bool
    remove_menu: Any
    geo_menu: Any

    def __init__(self, parent) -> None:
        """
        :param parent: the parent SpeciesEditorPresenter
        """
        super().__init__(parent.model, parent.view)
        self.parent_ref = weakref.ref(parent)
        self.session = parent.session
        self._dirty = False
        self.remove_menu = Gtk.Menu()
        self.remove_menu.attach_to_widget(self.view.widgets.sp_dist_remove_button, None)
        self.view.connect(
            "sp_dist_add_button",
            "button-press-event",
            self.on_add_button_pressed,
        )
        self.view.connect(
            "sp_dist_remove_button",
            "button-press-event",
            self.on_remove_button_pressed,
        )
        self.view.widgets.sp_dist_add_button.set_sensitive(False)

        def _init_geo():
            add_button = self.view.widgets.sp_dist_add_button
            self.geo_menu = GeographicAreaMenu(self.on_activate_add_menu_item)
            self.geo_menu.menu.attach_to_widget(add_button, None)
            add_button.set_sensitive(True)

        GLib.idle_add(_init_geo)

    def refresh_view(self) -> None:
        label = self.view.widgets.sp_dist_label
        s = ", ".join([str(d) for d in self.model.distribution or []])
        safe_set_text(label, s)

    def on_add_button_pressed(self, button, event) -> None:
        self.geo_menu.popup(
            None,
            None,
            None,
            None,
            button=event.get_button(),  # 1. issue_gdkevent_structs
            activate_time=event.time,
        )

    def on_remove_button_pressed(self, button, event) -> None:
        # clear the menu
        for c in self.remove_menu.get_children():
            self.remove_menu.remove(c)
        # add distributions to menu
        for dist in self.model.distribution:
            item = Gtk.MenuItem(str(dist))
            self.view.connect(item, "activate", self.on_activate_remove_menu_item, dist)
            self.remove_menu.append(item)
        self.remove_menu.show_all()
        self.remove_menu.popup(
            None,
            None,
            None,
            None,
            event.get_button(),
            event.time,  # 1. issue_gdkevent_structs
        )

    def on_activate_add_menu_item(self, widget, geoid: Optional[Any] = None) -> None:
        logger.debug(f"on_activate_add_menu_item {widget} {geoid}")
        from bauble.plugins.plants.geography import GeographicArea

        geo = (
            self.session.execute(select(GeographicArea).where(id=geoid)).scalars().one()
        )
        # check that this geography isn't already in the distributions
        if geo in [d.geographic_area for d in self.model.distribution]:
            logger.debug(f"{geo} already in {self.model}")
            return
        dist = SpeciesDistribution(geographic_area=geo)
        self.model.distribution.append(dist)
        logger.debug([str(d) for d in self.model.distribution])
        self._dirty = True
        self.refresh_view()
        self.parent_ref().refresh_sensitivity()

    def on_activate_remove_menu_item(self, widget, dist) -> None:
        self.model.distribution.remove(dist)
        utils.delete_or_expunge(dist)
        self.refresh_view()
        self._dirty = True
        self.parent_ref().refresh_sensitivity()

    def is_dirty(self):
        return self._dirty


class VernacularNamePresenter(editor.GenericEditorPresenter):
    # TODO: change the background of the entries and desensitize the
    # name/lang entries if the name conflicts with an existing vernacular
    # name for this species
    """
    in the VernacularNamePresenter we don't really use self.model, we
    more rely on the model in the TreeView which are VernacularName
    objects
    """
    parent_ref: Any
    session: Any
    _dirty: bool
    treeview: Any
    _active_cell_edit: Optional[tuple[Any, str, str]]

    def __init__(self, parent) -> None:
        """
        :param parent: the parent SpeciesEditorPresenter
        """
        super().__init__(parent.model, parent.view)
        self.parent_ref = weakref.ref(parent)
        self.session = parent.session
        self._dirty = False
        self._active_cell_edit = None
        self.init_treeview(self.model.vernacular_names)
        self.view.connect("sp_vern_add_button", "clicked", self.on_add_button_clicked)
        self.view.connect(
            "sp_vern_remove_button", "clicked", self.on_remove_button_clicked
        )

    def is_dirty(self):
        """
        @return True or False if the vernacular names have changed.
        """
        return self._dirty

    def on_add_button_clicked(self, button, data: Optional[Any] = None) -> None:
        """
        Add the values in the entries to the model.
        """
        treemodel = self.treeview.get_model()
        column = self.treeview.get_column(0)
        vn = VernacularName(name="")
        self.model.vernacular_names.append(vn)
        treeiter = treemodel.append([vn])
        path = treemodel.get_path(treeiter)
        self.treeview.set_cursor(path, column, start_editing=True)
        if len(treemodel) == 1:
            # self.set_model_attr('default_vernacular_name', vn)
            self.model.default_vernacular_name = vn

    def on_remove_button_clicked(self, button, data: Optional[Any] = None) -> None:
        """
        Removes the currently selected vernacular name from the view.
        """
        tree = self.view.widgets.vern_treeview
        path, col = tree.get_cursor()
        treemodel = tree.get_model()
        vn = treemodel[path][0]

        msg = _(
            "Are you sure you want to remove the vernacular " "name <b>%s</b>?"
        ) % utils.xml_safe(vn.name)
        if (
            vn.name
            and vn not in self.session.new
            and not utils.yes_no_dialog(msg, parent=self.view.get_window())
        ):
            return

        treemodel.remove(treemodel.get_iter(path))
        self.model.vernacular_names.remove(vn)
        utils.delete_or_expunge(vn)
        if not self.model.default_vernacular_name:
            # if there is only one value in the tree then set it as the
            # default vernacular name
            first = treemodel.get_iter_first()
            if first:
                #                 self.set_model_attr('default_vernacular_name',
                #                                     tree_model[first][0])
                self.model.default_vernacular_name = treemodel[first][0]
        self.parent_ref().refresh_sensitivity()
        self._dirty = True

    def on_default_toggled(self, cell, path, data: Optional[Any] = None) -> None:
        """
        Default column callback.
        """
        active = cell.get_active()
        if not active:  # then it's becoming active
            vn = self.treeview.get_model()[path][0]
            self.set_model_attr("default_vernacular_name", vn)
        self._dirty = True
        self.parent_ref().refresh_sensitivity()

    def on_cell_edited(self, cell, path, new_text, prop) -> None:
        self._set_cell_value(path, new_text, prop)
        self._active_cell_edit = None

    def on_cell_editing_started(self, cell, editable, path, prop) -> None:
        path_text = path.to_string() if isinstance(path, Gtk.TreePath) else str(path)
        self._active_cell_edit = (editable, path_text, prop)
        if hasattr(editable, "connect"):
            self.view.connect(
                editable, "changed", self.on_cell_editing_changed, path_text, prop
            )
            self.view.connect(
                editable,
                "focus-out-event",
                self.on_cell_editing_focus_out,
                path_text,
                prop,
            )
            self.view.connect(
                editable,
                "key-press-event",
                self.on_cell_editing_key_press,
                path_text,
                prop,
            )

    def on_cell_editing_changed(self, editable, path, prop) -> None:
        self._set_cell_value(path, editable.get_text(), prop)

    def on_cell_editing_focus_out(self, editable, event, path, prop) -> bool:
        self._set_cell_value(path, editable.get_text(), prop)
        return False

    def on_cell_editing_key_press(self, editable, event, path, prop) -> bool:
        if (
            prop == "name"
            and event.keyval == Gdk.KEY_Tab
            and not (event.state & Gdk.ModifierType.SHIFT_MASK)
        ):
            self._set_cell_value(path, editable.get_text(), prop)
            self._edit_vernacular_cell(path, self.view.widgets.vn_lang_column)
            return True
        if (
            prop == "language"
            and event.keyval
            in (
                Gdk.KEY_ISO_Left_Tab,
                Gdk.KEY_Tab,
            )
            and (event.state & Gdk.ModifierType.SHIFT_MASK)
        ):
            self._set_cell_value(path, editable.get_text(), prop)
            self._edit_vernacular_cell(path, self.view.widgets.vn_name_column)
            return True
        return False

    def _edit_vernacular_cell(self, path, column) -> None:
        tree_path = (
            path
            if isinstance(path, Gtk.TreePath)
            else Gtk.TreePath.new_from_string(str(path))
        )
        self._active_cell_edit = None
        self.treeview.set_cursor(tree_path, column, True)

    def sync_active_cell_edit(self) -> None:
        active_edit = self._active_cell_edit
        if not active_edit:
            return
        editable, path, prop = active_edit
        if hasattr(editable, "get_text"):
            self._set_cell_value(path, editable.get_text(), prop)

    def _set_cell_value(self, path, new_text, prop) -> None:
        treemodel = self.treeview.get_model()
        try:
            treeiter = treemodel.get_iter(path)
        except (TypeError, ValueError, GLib.Error):
            treeiter = treemodel.get_iter_from_string(str(path))
        if treeiter is None:
            return
        vn = treemodel[treeiter][0]
        if getattr(vn, prop) == new_text:
            return  # didn't change
        setattr(vn, prop, new_text)
        self._dirty = True
        self.parent_ref().refresh_sensitivity()

    def init_treeview(self, model) -> None:
        """
        Initialized the list of vernacular names.

        The columns and cell renderers are loaded from the .glade file
        so we just need to customize them a bit.
        """
        self.treeview = self.view.widgets.vern_treeview
        if not isinstance(self.treeview, Gtk.TreeView):
            return

        def _name_data_func(column, cell, model, treeiter, data=None):
            v = model[treeiter][0]
            cell.set_property(
                "text", v.name.decode("utf-8") if isinstance(v.name, bytes) else v.name
            )
            # just added so change the background color to indicate it's new
            if v.id is None:  # hasn't been committed
                cell.set_property("foreground", "blue")
            else:
                cell.set_property("foreground", None)

        self.view.widgets.vn_name_column
        # column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        cell = self.view.widgets.vn_name_cell
        self.view.widgets.vn_name_column.set_cell_data_func(cell, _name_data_func)
        self.view.connect(cell, "edited", self.on_cell_edited, "name")
        self.view.connect(cell, "editing-started", self.on_cell_editing_started, "name")

        def _lang_data_func(column, cell, model, treeiter, data=None):
            v = model[treeiter][0]
            cell.set_property("text", v.language)
            # just added so change the background color to indicate it's new
            # if not v.isinstance:`
            if v.id is None:  # hasn't been committed
                cell.set_property("foreground", "blue")
            else:
                cell.set_property("foreground", None)

        cell = self.view.widgets.vn_lang_cell
        self.view.widgets.vn_lang_column.set_cell_data_func(cell, _lang_data_func)
        self.view.connect(cell, "edited", self.on_cell_edited, "language")
        self.view.connect(
            cell, "editing-started", self.on_cell_editing_started, "language"
        )

        def _default_data_func(column, cell, model, iter, data=None):
            v = model[iter][0]
            try:
                cell.set_property("active", v == self.model.default_vernacular_name)
                return
            except AttributeError as e:
                logger.debug(f"AttributeError {e}")
            cell.set_property("active", False)

        cell = self.view.widgets.vn_default_cell
        self.view.widgets.vn_default_column.set_cell_data_func(cell, _default_data_func)
        self.view.connect(cell, "toggled", self.on_default_toggled)

        utils.clear_model(self.treeview)

        # add the vernacular names to the tree
        tree_model = Gtk.ListStore(object)
        for vn in model:
            tree_model.append([vn])
        self.treeview.set_model(tree_model)

        self.view.connect(self.treeview, "cursor-changed", self.on_tree_cursor_changed)

    def on_tree_cursor_changed(self, tree, data: Optional[Any] = None) -> None:
        path, column = tree.get_cursor()
        self.view.widgets.sp_vern_remove_button.set_sensitive(True)

    def refresh_view(self, default_vernacular_name) -> None:
        tree_model = self.treeview.get_model()
        # if len(self.model) > 0 and default_vernacular_name is None:
        vernacular_names = self.model.vernacular_names
        default_vernacular_name = self.model.default_vernacular_name
        if len(vernacular_names) > 0 and default_vernacular_name is None:
            msg = _(
                "This species has vernacular names but none of them are "
                "selected as the default. The first vernacular name in "
                "the list has been automatically selected."
            )
            utils.message_dialog(msg)
            first = tree_model.get_iter_first()
            value = tree_model[first][0]
            tree_model.get_path(first)
            # self.set_model_attr('default_vernacular_name', value)
            self.model.default_vernacular_name = value
            self._dirty = True
            self.parent_ref().refresh_sensitivity()
        elif default_vernacular_name is None:
            return


class SynonymsPresenter(editor.GenericEditorPresenter):

    parent_ref: Any
    session: Any
    _selected: Any
    _dirty: bool
    treeview: Any
    PROBLEM_INVALID_SYNONYM: int = 1

    def __init__(self, parent) -> None:
        """
        :param parent: the parent SpeciesEditorPresenter
        """
        super().__init__(parent.model, parent.view)
        self.parent_ref = weakref.ref(parent)
        self.session = parent.session
        safe_set_props(self.view.widgets.sp_syn_entry, "text", "")
        self.init_treeview()

        def sp_get_completions(text):
            query = (
                self.session.execute(
                    select(Species)
                    .join(Genus, Species.genus_id == Genus.id)
                    .where(utils.ilike(Genus.genus, f"{text}%"))
                    .where(Species.id != self.model.id)
                    .order_by(Genus.genus, Species.epithet)
                )
            ).scalars()
            return query

        def on_select(value):
            sensitive = True
            if value is None:
                sensitive = False
            self.view.widgets.sp_syn_add_button.set_sensitive(sensitive)
            self._selected = value

        self.assign_completions_handler(
            "sp_syn_entry", sp_get_completions, on_select=on_select
        )
        on_select(None)  # set to default state

        self._selected = None
        self.view.connect("sp_syn_add_button", "clicked", self.on_add_button_clicked)
        self.view.connect(
            "sp_syn_remove_button", "clicked", self.on_remove_button_clicked
        )
        self._dirty = False

    def is_dirty(self):
        return self._dirty

    def init_treeview(self) -> None:
        """
        initialize the Gtk.TreeView
        """
        self.treeview = self.view.widgets.sp_syn_treeview

        def _syn_data_func(column, cell, model, treeiter, data=None):
            v = model[treeiter][0]
            cell.set_property("text", str(v))
            # just added so change the background color to indicate it's new
            if not hasattr(v, "id") or v.id is None:
                cell.set_property("foreground", "blue")
            else:
                cell.set_property("foreground", None)

        col = self.view.widgets.syn_column
        col.set_cell_data_func(self.view.widgets.syn_cell, _syn_data_func)

        utils.clear_model(self.treeview)
        tree_model = Gtk.ListStore(object)
        for syn in self.model._synonyms:
            tree_model.append([syn])
        self.treeview.set_model(tree_model)
        self.view.connect(self.treeview, "cursor-changed", self.on_tree_cursor_changed)

    def on_tree_cursor_changed(self, tree, data: Optional[Any] = None) -> None:
        """ """
        path, column = tree.get_cursor()
        self.view.widgets.sp_syn_remove_button.set_sensitive(True)

    def refresh_view(self) -> None:
        """
        doesn't do anything
        """
        return

    def on_add_button_clicked(self, button, data: Optional[Any] = None) -> None:
        """
        Adds the synonym from the synonym entry to the list of synonyms for
        this species.
        """
        syn = SpeciesSynonym(species=self.model, synonym=self._selected)
        tree_model = self.treeview.get_model()
        tree_model.append([syn])
        self._selected = None
        entry = self.view.widgets.sp_syn_entry
        safe_set_text(entry, "")
        entry.set_position(-1)
        self.view.widgets.sp_syn_add_button.set_sensitive(False)
        self.view.widgets.sp_syn_add_button.set_sensitive(False)
        self._dirty = True
        self.parent_ref().refresh_sensitivity()

    def on_remove_button_clicked(self, button, data: Optional[Any] = None) -> None:
        """
        removes the currently selected synonym from the list of synonyms for
        this species
        """
        # TODO: maybe we should only ask 'are you sure' if the selected value
        # is an instance, this means it will be deleted from the database
        tree = self.view.widgets.sp_syn_treeview
        path, col = tree.get_cursor()
        tree_model = tree.get_model()
        value = tree_model[tree_model.get_iter(path)][0]
        s = value.synonym.str(markup=True)
        msg = (
            f"Are you sure you want to remove {s} as a synonym to the "
            "current species?\n\n<i>Note: This will not remove the species "
            f"{s} from the database.</i>"
        )
        if not utils.yes_no_dialog(msg, parent=self.view.get_window()):
            return

        tree_model.remove(tree_model.get_iter(path))
        self.model.synonyms.remove(value.synonym)
        utils.delete_or_expunge(value)
        # TODO: ** important ** this doesn't respect any unique
        # contraints on the species for synonyms and allow a
        # species to have another species as a synonym multiple
        # times...see below

        # TODO: using session.flush here with an argument is
        # deprecated in SA 0.5 and will probably removed in SA
        # 0.6...but how do we only flush the one value..unless we
        # create a new session, merge it, commit that session,
        # close it and then refresh the same object in
        # self.session

        # make the change in synonym immediately available so that if
        # we try to add the same species again we don't break the
        # SpeciesSynonym UniqueConstraint

        # tmp_session = db.Session()
        # tmp_value = tmp.session.merge(value)
        # tmp.session.commit()
        # tmp.session.close()
        # self.session.refresh(value)
        # self.session.flush([value])
        self._dirty = True
        self.parent_ref().refresh_sensitivity()


class SpeciesEditorView(editor.GenericEditorView):

    _tooltips: Any
    boxes: Any
    expanders_pref_map: Any = {}
    # {'sp_infra_expander': 'editor.species.infra.expanded',
    # 'sp_meta_expander': 'editor.species.meta.expanded'}

    _tooltips = {
        "sp_genus_entry": _("Genus"),
        "sp_species_entry": _("Species epithet"),
        "sp_author_entry": _("Species author"),
        "sp_hybrid_check": _("Species hybrid flag"),
        "sp_cvgroup_entry": _("Cultivar group"),
        "sp_spqual_combo": _("Species qualifier"),
        "sp_dist_frame": _("Species distribution"),
        "sp_vern_frame": _("Vernacular names"),
        "sp_syn_frame": _("Species synonyms"),
        "sp_label_dist_entry": _(
            "The distribution string that will be used "
            "on the label.  If this entry is blank then "
            "the species distribution will be used"
        ),
        "sp_habit_comboentry": _("The habit of this species"),
        "sp_awards_entry": _("The awards this species have been given"),
        "sp_cancel_button": _("Cancel your changes"),
        "sp_ok_button": _("Save your changes"),
        "sp_ok_and_add_button": _(
            "Save your changes and add an " "accession to this species"
        ),
        "sp_next_button": _("Save your changes and add another " "species "),
    }

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        the constructor

        :param parent: the parent window
        """
        filename = os.path.join(
            paths.lib_dir(), "plugins", "plants", "species_editor.glade"
        )
        super().__init__(filename, parent=parent)
        self.culture_widgets = {}
        self.add_culture_tab()
        self.attach_completion(
            "sp_genus_entry",
            self.genus_completion_cell_data_func,
            match_func=self.genus_match_func,
        )
        self.attach_completion("sp_syn_entry", self.syn_cell_data_func)
        self.set_accept_buttons_sensitive(False)
        self.widgets.notebook.set_current_page(0)
        self.restore_state()
        self.boxes = set()

    def register_culture_widget(self, name, widget):
        widget.set_name(name)
        self.culture_widgets[name] = widget
        return widget

    def _culture_section(self, parent, title):
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        frame.set_border_width(6)
        label = Gtk.Label()
        label.set_markup(
            "<b>%s</b>" % GLib.markup_escape_text(str(title), len(str(title)))
        )
        frame.set_label_widget(label)
        frame.set_label_align(0.02, 0.5)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_border_width(8)
        frame.add(box)
        parent.pack_start(frame, False, False, 0)
        return box

    def _culture_entry(self, name, width=7):
        entry = Gtk.Entry()
        entry.set_width_chars(width)
        entry.set_max_width_chars(width)
        entry.set_input_purpose(Gtk.InputPurpose.NUMBER)
        return self.register_culture_widget(name, entry)

    def _culture_textview(self, name):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(96)
        scrolled.set_shadow_type(Gtk.ShadowType.IN)
        textview = Gtk.TextView()
        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        textview.set_left_margin(6)
        textview.set_right_margin(6)
        textview.set_top_margin(6)
        textview.set_bottom_margin(6)
        scrolled.add(textview)
        self.register_culture_widget(name, textview)
        return scrolled

    def add_culture_tab(self) -> None:
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        page.set_border_width(10)
        scrolled.add(page)

        ranges = self._culture_section(page, _("Ranges"))
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        ranges.pack_start(grid, False, False, 0)
        headers = ("", _("Min"), _("Max"), _("Scale"))
        for column, label in enumerate(headers):
            header = Gtk.Label(label=label)
            header.set_xalign(0)
            grid.attach(header, column, 0, 1, 1)
        for row, (
            _key,
            label,
            min_field,
            max_field,
            _parser,
            _minimum,
            _maximum,
            hint,
        ) in enumerate(_CULTURE_RANGE_FIELDS, 1):
            field_label = Gtk.Label(label=label)
            field_label.set_xalign(0)
            grid.attach(field_label, 0, row, 1, 1)
            grid.attach(
                self._culture_entry(_culture_widget_name(min_field, "entry")),
                1,
                row,
                1,
                1,
            )
            grid.attach(
                self._culture_entry(_culture_widget_name(max_field, "entry")),
                2,
                row,
                1,
                1,
            )
            scale_label = Gtk.Label(label=hint)
            scale_label.set_xalign(0)
            grid.attach(scale_label, 3, row, 1, 1)

        next_row = len(_CULTURE_RANGE_FIELDS) + 1
        for row_offset, (field, label, _parser, _minimum, _maximum, hint) in enumerate(
            _CULTURE_SINGLE_NUMBER_FIELDS
        ):
            row = next_row + row_offset
            field_label = Gtk.Label(label=label)
            field_label.set_xalign(0)
            grid.attach(field_label, 0, row, 1, 1)
            grid.attach(
                self._culture_entry(_culture_widget_name(field, "entry")),
                1,
                row,
                1,
                1,
            )
            scale_label = Gtk.Label(label=hint)
            scale_label.set_xalign(0)
            grid.attach(scale_label, 3, row, 1, 1)

        controlled = self._culture_section(page, _("Controlled values"))
        controlled_grid = Gtk.Grid()
        controlled_grid.set_row_spacing(6)
        controlled_grid.set_column_spacing(12)
        controlled.pack_start(controlled_grid, False, False, 0)
        for row, (field, label, _values) in enumerate(_CULTURE_ENUM_FIELDS):
            field_label = Gtk.Label(label=label)
            field_label.set_xalign(0)
            controlled_grid.attach(field_label, 0, row, 1, 1)
            combo = Gtk.ComboBoxText()
            self.register_culture_widget(_culture_widget_name(field, "combo"), combo)
            controlled_grid.attach(combo, 1, row, 1, 1)

        flags = self._culture_section(page, _("Flags"))
        flags_grid = Gtk.Grid()
        flags_grid.set_row_spacing(4)
        flags_grid.set_column_spacing(12)
        flags.pack_start(flags_grid, False, False, 0)
        for index, (field, label) in enumerate(_CULTURE_BOOLEAN_FIELDS):
            button = Gtk.CheckButton(label=label)
            self.register_culture_widget(_culture_widget_name(field, "check"), button)
            flags_grid.attach(button, index % 2, index // 2, 1, 1)

        for _attr, _klass, prefix, label in _CULTURE_LOOKUP_FIELDS:
            box = self._culture_section(page, label)
            flow = Gtk.FlowBox()
            flow.set_selection_mode(Gtk.SelectionMode.NONE)
            flow.set_max_children_per_line(4)
            self.register_culture_widget(_culture_widget_name(prefix, "box"), flow)
            box.pack_start(flow, False, False, 0)

        months = self._culture_section(page, _("Months"))
        month_grid = Gtk.Grid()
        month_grid.set_row_spacing(4)
        month_grid.set_column_spacing(5)
        months.pack_start(month_grid, False, False, 0)
        for column, label in enumerate(_CULTURE_MONTH_LABELS, 1):
            month_label = Gtk.Label(label=label)
            month_grid.attach(month_label, column, 0, 1, 1)
        for row, (month_type, label, tooltip) in enumerate(_CULTURE_MONTH_TYPES, 1):
            row_label = Gtk.Label(label=label)
            row_label.set_xalign(0)
            row_label.set_tooltip_text(tooltip)
            month_grid.attach(row_label, 0, row, 1, 1)
            for month in range(1, 13):
                name = _culture_widget_name("month", month_type, month, "check")
                button = Gtk.CheckButton()
                self.register_culture_widget(name, button)
                month_grid.attach(button, month, row, 1, 1)

        notes = self._culture_section(page, _("Notes"))
        for field, label in _CULTURE_TEXT_FIELDS:
            notes.pack_start(Gtk.Label(label=label, xalign=0), False, False, 0)
            notes.pack_start(
                self._culture_textview(_culture_widget_name(field, "textview")),
                False,
                False,
                0,
            )

        self.widgets.notebook.append_page(scrolled, Gtk.Label(label=_("Culture")))
        scrolled.show_all()

    def get_window(self):
        """
        Returns the top level window or dialog.
        """
        return self.widgets.species_dialog

    @staticmethod
    def genus_match_func(completion, key, iter, data: Optional[Any] = None):
        """
        match against both str(genus) and str(genus.genus) so that we
        catch the genera with hybrid flags in their name when only
        entering the genus name
        """
        genus = completion.get_model()[iter][0]
        if str(genus).lower().startswith(key.lower()) or str(
            genus.genus
        ).lower().startswith(key.lower()):
            return True
        return False

    def set_accept_buttons_sensitive(self, sensitive) -> None:
        """
        set the sensitivity of all the accept/ok buttons for the editor dialog
        """
        self.widgets.sp_ok_button.set_sensitive(sensitive)
        try:
            import bauble.plugins.garden

            bauble.plugins.garden  # fake usage
            self.widgets.sp_ok_and_add_button.set_sensitive(sensitive)
        except Exception:
            pass
        self.widgets.sp_next_button.set_sensitive(sensitive)

    def connect_actions(self):
        dialog = self.get_window()
        self.widgets.sp_cancel_button.connect(
            "clicked", lambda b: dialog.response(Gtk.ResponseType.CANCEL)
        )
        self.widgets.sp_ok_button.connect(
            "clicked", lambda b: dialog.response(Gtk.ResponseType.OK)
        )
        self.widgets.sp_ok_and_add_button.connect(
            "clicked", lambda b: dialog.response(11)
        )
        self.widgets.sp_next_button.connect("clicked", lambda b: dialog.response(22))

    @staticmethod
    def genus_completion_cell_data_func(
        column, renderer, model, treeiter, data: Optional[Any] = None
    ) -> None:
        """ """
        v = model[treeiter][0]
        renderer.set_property("text", f"{Genus.str(v)} ({Family.str(v.family)})")

    @staticmethod
    def syn_cell_data_func(
        column, renderer, model, treeiter, data: Optional[Any] = None
    ) -> None:
        """ """
        v = model[treeiter][0]
        renderer.set_property("text", str(v))

    def save_state(self) -> None:
        """
        save the current state of the gui to the preferences
        """
        for expander, pref in list(self.expanders_pref_map.items()):
            prefs[pref] = self.widgets[expander].get_expanded()

    def restore_state(self) -> None:
        """
        restore the state of the gui from the preferences
        """
        for expander, pref in list(self.expanders_pref_map.items()):
            expanded = prefs.get(pref, True)
            self.widgets[expander].set_expanded(expanded)

    def start(self):
        """
        starts the views, essentially calls run() on the main dialog
        """
        return self.get_window().run()


class SpeciesEditor(editor.GenericModelViewPresenterEditor):

    # these have to correspond to the response values in the view
    parent: Any
    _committed: Any
    presenter: Any
    view: Any
    RESPONSE_OK_AND_ADD: int = 11
    RESPONSE_NEXT: int = 22
    ok_responses: Any = (RESPONSE_OK_AND_ADD, RESPONSE_NEXT)

    def __init__(
        self,
        model: Optional[Any] = None,
        parent: Optional[Any] = None,
        is_dependent_window: bool = False,
    ) -> None:
        """
        :param model: a species instance or None
        :param parent: the parent window or None
        """
        if model is None:
            model = Species()
        super().__init__(model, parent)
        if not parent and bauble.gui:
            parent = bauble.gui.window
        self.parent = parent
        self._committed = []

        view = SpeciesEditorView(parent=self.parent)
        self.presenter = SpeciesEditorPresenter(self.model, view)
        self.presenter.set_visible_buttons(not is_dependent_window)

        # I do not follow this: we have a MVP model, but also an extra
        # 'Editor' thing and is it stealing functionality from either the
        # view or the presenter?
        self.view = view

        # set default focus
        if self.model.genus is None:
            view.widgets.sp_genus_entry.grab_focus()
        else:
            view.widgets.sp_species_entry.grab_focus()

    def handle_response(self, response):
        """
        @return: return True if the editor is ready to be closed, False if
        we want to keep editing, if any changes are committed they are stored
        in self._committed
        """
        # TODO: need to do a __cleanup_model before the commit to do things
        # like remove the insfraspecific information that's attached to the
        # model if the infraspecific rank is None
        not_ok_msg = "Are you sure you want to lose your changes?"
        if response == Gtk.ResponseType.OK or response in self.ok_responses:
            try:
                if self.presenter.is_dirty():
                    self.commit_changes()
                    self._committed.append(self.model)
            except DBAPIError as e:
                msg = _("Error committing changes.\n\n%s") % utils.xml_safe(e.orig)
                logger.debug(traceback.format_exc())
                utils.message_details_dialog(msg, str(e), Gtk.MessageType.ERROR)
                return False
            except Exception as e:
                msg = _(
                    "Unknown error when committing changes. See the "
                    "details for more information.\n\n%s"
                ) % utils.xml_safe(e)
                logger.debug(traceback.format_exc())
                utils.message_details_dialog(
                    msg, traceback.format_exc(), Gtk.MessageType.ERROR
                )
                return False
        elif (
            self.presenter.is_dirty()
            and utils.yes_no_dialog(not_ok_msg)
            or not self.presenter.is_dirty()
        ):
            if self.session.in_transaction():
                self.session.rollback()
            self.view.close_boxes()
            return True
        else:
            return False

        more_committed = None
        if response == self.RESPONSE_NEXT:
            self.presenter.cleanup()
            e = SpeciesEditor(Species(genus=self.model.genus), self.parent)
            more_committed = e.start()
        elif response == self.RESPONSE_OK_AND_ADD:
            from bauble.plugins.garden.accession_editor import AccessionEditor
            from bauble.plugins.garden.models import Accession

            state = sa_inspect(self.model)
            species_id = state.identity[0] if state.identity else self.model.id
            e = AccessionEditor(Accession(species_id=species_id), parent=self.parent)
            more_committed = e.start()

        if more_committed is not None:
            if isinstance(more_committed, list):
                self._committed.extend(more_committed)
            else:
                self._committed.append(more_committed)

        self.view.close_boxes()
        return True

    def commit_changes(self) -> None:
        # if self.model.epithet or cv_group is empty and
        # self.model.infrasp_rank=='cv.' and self.model.infrasp
        # then show a dialog saying we can't commit and return

        # if self.model.hybrid is None and self.model.infrasp_rank is None:
        #     self.model.infrasp = None
        #     self.model.infrasp_author = None
        #     self.model.cv_group = None

        self.presenter.vern_presenter.sync_active_cell_edit()

        # remove incomplete vernacular names
        for vn in self.model.vernacular_names or []:
            if vn.name in (None, ""):
                self.model.vernacular_names.remove(vn)
                utils.delete_or_expunge(vn)
                del vn
        self.presenter.culture_presenter.cleanup_empty_profile()
        ensure_autonym_for_species(self.session, self.model)
        super().commit_changes()

    def start(self):
        count = self.session.scalar(select(func.count()).select_from(Genus))
        if count == 0:
            msg = _(
                "You must first add or import at least one genus into the "
                "database before you can add species."
            )
            utils.message_dialog(msg)
            return

        while True:
            response = self.presenter.start()
            self.presenter.view.save_state()
            if self.handle_response(response):
                break

        self.presenter.cleanup()
        self.session.close()  # cleanup session
        return self._committed


def edit_species(
    model: Optional[Any] = None,
    parent_view: Optional[Any] = None,
    is_dependent_window: bool = False,
):
    kkk = SpeciesEditor(model, parent_view, is_dependent_window)
    kkk.start()
    result = kkk._committed
    del kkk
    return result

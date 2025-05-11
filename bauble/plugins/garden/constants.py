#
# Copyright 2008-2010 Brett Adams
# Copyright 2015-2017 Mario Frasca <mario@anche.no>.
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
from gettext import gettext as _

prop_type_values = {
    "Seed": _("Seed"),
    "UnrootedCutting": _("Unrooted cutting"),
}

prop_type_results = {
    "Seed": "SEDL",
    "UnrootedCutting": "RCUT",
}

cutting_type_values = {
    "Nodal": _("Nodal"),
    "InterNodal": _("Internodal"),
    "Other": _("Other"),
}

tip_values = {
    "Intact": _("Intact"),
    "Removed": _("Removed"),
    "None": _("None"),
    None: "",
}

leaves_values = {
    "Intact": _("Intact"),
    "Removed": _("Removed"),
    "None": _("None"),
    None: "",
}

flower_buds_values = {"Removed": _("Removed"), "None": _("None"), None: ""}

wound_values = {
    "No": _("No"),
    "Single": _("Singled"),
    "Double": _("Double"),
    "Slice": _("Slice"),
    None: "",
}

hormone_values = {"Liquid": _("Liquid"), "Powder": _("Powder"), "No": _("No")}

bottom_heat_unit_values = {"F": _("°F"), "C": _("°C"), None: ""}

length_unit_values = {"mm": _("mm"), "cm": _("cm"), "in": _("in"), None: ""}

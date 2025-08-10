#
# Copyright 2008-2010 Brett Adams
# Copyright 2015-2016 Mario Frasca <mario@anche.no>.
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
# bauble/plugins/garden/models/contact.py

import logging
from gettext import gettext as _
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional, Type

import bauble.btypes as types
from bauble.db import Base, Serializable, WithNotes, make_note_class
import bauble.utils as utils
from sqlalchemy import Column, Unicode, UnicodeText, asc, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import mapped_column, relationship

if TYPE_CHECKING:
    # for static type checking only; at runtime SQLAlchemy will look it up by string
    from .source import Source

logger = logging.getLogger(__name__)

source_type_values: Any = [
    ("Expedition", _("Expedition")),
    ("GeneBank", _("Gene Bank")),
    ("BG", _("Botanic Garden or Arboretum")),
    ("Research/FieldStation", _("Research/Field Station")),
    ("Staff", _("Staff member")),
    ("UniversityDepartment", _("University Department")),
    ("Club", _("Horticultural Association/Garden Club")),
    ("MunicipalDepartment", _("Municipal department")),
    ("Commercial", _("Nursery/Commercial")),
    ("Individual", _("Individual")),
    ("Other", _("Other")),
    ("Unknown", _("Unknown")),
    (None, ""),
]


#
# Contact aka Source Detail
#
def compute_serializable_fields(
    cls: Type["Contact"], session: SQLAlchemySession, keys: Dict[str, Any]
) -> Dict[str, Any]:
    result: Dict[str, Any] = {"contact": None}

    parent_keys = {"name": keys["contact"]}
    result["contact"] = Contact.retrieve_or_create(session, parent_keys, create=False)

    return result


class Contact(Base, Serializable, WithNotes):
    __tablename__: str = "contact"

    # ITF2 - E6 - Donor
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Any = Column(Unicode(75), unique=True)
    # extra description, not included in E6
    description = Column(UnicodeText)
    # ITF2 - E5 - Donor Type Flag
    source_type = Column(
        types.Enum(
            values=[i[0] for i in source_type_values],
            translations=dict(source_type_values),
            omit_aliases=False,
        ),
        default=None,
    )
    order_by: ClassVar = [asc(name)]

    sources: Mapped["Source"] = relationship(
        "Source",
        uselist=False,
        back_populates="source_detail",
        cascade="all, delete-orphan",
        single_parent=True,
        active_history=True,
    )

    def __str__(self) -> str:
        return str(self.name) if self.name is not None else ""

    def search_view_markup_pair(self):
        """provide the two lines describing object for SearchView row."""
        safe = utils.xml_safe
        return (safe(self.name), safe(self.source_type or ""))

    @classmethod
    def retrieve(
        cls, session: SQLAlchemySession, keys: Dict[str, Any]
    ) -> Optional["Contact"]:
        try:
            return (
                session.execute(select(cls).where(cls.name == keys["name"]))
                .scalars()
                .one()
            )
        except:
            return None


# hook up notes
ContactNote: Any = make_note_class("Contact", Contact, compute_serializable_fields)
Contact.notes: Mapped["ContactNote"] = relationship(
    "ContactNote",
    back_populates="contact",
    cascade="all, delete-orphan",
    single_parent=True,
    uselist=True,
)

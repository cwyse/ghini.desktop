#
# Copyright (c) 2005,2006,2007,2008,2009 Brett Adams <brett@belizebotanic.org>
# Copyright (c) 2012-2018 Mario Frasca <mario@anche.no>
# Copyright 2017 Jardín Botánico de Quito
# Copyright 2018 Tanager Botanical Garden <tanagertourism@gmail.com>
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

# Delayed imports to resolve circular dependencies
from bauble.test import BaubleTestCase
from bauble.utils import natsort_key  # Import only what's necessary
from bauble.plugins.report.jinja2 import Jinja2FormatterPlugin
from bauble.plugins.report import get_pertinent_objects
from sqlalchemy import select

logger = logging.getLogger(__name__)


# Modify desktop.open here to avoid cyclic import
def disable_desktop_open():
    try:
        import bauble.utils.desktop as desktop
        desktop.open = lambda x: x
    except ImportError:
        logger.error("Failed to import and disable desktop.open")


disable_desktop_open()


# Centralize delayed imports
def dynamic_import(module_name, class_name):
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)

class Jinja2FormatterTests(BaubleTestCase):

    def __init__(self, *args):
        super().__init__(*args)

    def setUp(self, *args):
        super().setUp()
        self._populate_test_data()

    def tearDown(self, *args):
        super().tearDown()

    def _populate_test_data(self):
        Family = dynamic_import("bauble.plugins.plants", "Family")
        Genus = dynamic_import("bauble.plugins.plants", "Genus")
        Species = dynamic_import("bauble.plugins.plants", "Species")
        GeographicArea = dynamic_import("bauble.plugins.plants", "GeographicArea")
        SpeciesDistribution = dynamic_import("bauble.plugins.plants", "SpeciesDistribution")
        VernacularName = dynamic_import("bauble.plugins.plants", "VernacularName")
        Accession = dynamic_import("bauble.plugins.garden", "Accession")
        Location = dynamic_import("bauble.plugins.garden", "Location")
        Plant = dynamic_import("bauble.plugins.garden.plant", "Plant")

        fctr = gctr = sctr = actr = pctr = 0
        for f in range(2):
            fctr += 1
            family = Family(id=fctr, family=f"fam{fctr}")
            self.session.add(family)
            for g in range(2):
                gctr += 1
                genus = Genus(id=gctr, family=family, genus=f"gen{gctr}")
                self.session.add(genus)
                for s in range(2):
                    sctr += 1
                    sp = Species(id=sctr, genus=genus, sp=f"sp{sctr}")
                    geo = GeographicArea(id=sctr, name=f"Mexico{sctr}")
                    dist = SpeciesDistribution(geographic_area_id=sctr)
                    sp.distribution.append(dist)
                    vn = VernacularName(id=sctr, species=sp, name=f"name{sctr}")
                    self.session.add_all([sp, geo, dist, vn])
                    for a in range(2):
                        actr += 1
                        acc = Accession(id=actr, species=sp, code=f"{actr}")
                        self.session.add(acc)
                        for p in range(2):
                            pctr += 1
                            loc = Location(id=pctr, code=f"{pctr}", name=f"site{pctr}")
                            plant = Plant(
                                id=pctr,
                                accession=acc,
                                location=loc,
                                code=f"{pctr}",
                                quantity=1,
                            )
                            self.session.add_all([loc, plant])
        self.session.commit()

    def test_format_all_templates(self):
        Plant = dynamic_import("bauble.plugins.garden.plant", "Plant")

        selection = self.execute(select()).scalars().all()
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        for i, template_name in enumerate(filter(lambda x: x.endswith(".jj2"), os.listdir(templates_dir))):
            template_path = os.path.join(templates_dir, template_name)
            domain = Jinja2FormatterPlugin.get_iteration_domain(template_path)

            if domain == "":
                self.assertEqual(template_name[:5], "base.")
                continue

            cls = {
                "plant": Plant,
                "accession": dynamic_import("bauble.plugins.garden", "Accession"),
                "species": dynamic_import("bauble.plugins.plants", "Species"),
                "location": dynamic_import("bauble.plugins.garden", "Location"),
            }.get(domain, Plant)  # Default to Plant if domain is unknown

            todo = (
                sorted(get_pertinent_objects(cls, selection), key=natsort_key)
                if cls
                else selection
            )

            logger.debug(f"Formatting template: {template_path}")
            report = Jinja2FormatterPlugin.format(todo, template=template_path)
            self.assertIsInstance(report, bytes)


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
import pytest
from bauble.plugins.garden import Accession, Location, Plant
from bauble.plugins.plants import Family, Genus, Species, GeographicArea, SpeciesDistribution, VernacularName
from bauble.plugins.report import get_pertinent_objects
from bauble.plugins.report.mako import MakoFormatterPlugin
from sqlalchemy import select
from bauble import utils
from bauble.plugins.report.utils import Code39
from bauble.plugins.report import SVG

logger = logging.getLogger(__name__)

# TURN OFF desktop.open for this module so that the test doesn't open the report
desktop_open = lambda x: x


@pytest.fixture(scope="module", autouse=True)
def setup_database(session):
    """
    Fixture to set up the database for the tests.
    """
    fctr = gctr = sctr = actr = pctr = 0
    for f in range(2):
        fctr += 1
        family = Family(id=fctr, family="fam%s" % fctr)
        session.add(family)
        for g in range(2):
            gctr += 1
            genus = Genus(id=gctr, family=family, genus="gen%s" % gctr)
            session.add(genus)
            for s in range(2):
                sctr += 1
                sp = Species(id=sctr, genus=genus, sp="sp%s" % sctr)
                geo = GeographicArea(id=sctr, name="Mexico%s" % sctr)
                dist = SpeciesDistribution(geographic_area_id=sctr)
                sp.distribution.append(dist)
                vn = VernacularName(
                    id=sctr, species=sp, name="name%s" % sctr
                )
                session.add_all([sp, geo, dist, vn])
                for a in range(2):
                    actr += 1
                    acc = Accession(id=actr, species=sp, code="%s" % actr)
                    session.add(acc)
                    for p in range(2):
                        pctr += 1
                        loc = Location(
                            id=pctr, code="%s" % pctr, name="site%s" % pctr
                        )
                        plant = Plant(
                            id=pctr,
                            accession=acc,
                            location=loc,
                            code="%s" % pctr,
                            quantity=1,
                        )
                        session.add_all([loc, plant])
    session.commit()


@pytest.mark.parametrize("use_qr", [False, True])
def test_format_mako_templates(session, use_qr):
    """
    Test formatting all mako templates with or without QR codes.
    """
    selection = session.execute(select(Plant)).scalars().all()
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

    for i, template_name in enumerate(os.listdir(templates_dir)):
        if not template_name.endswith(".mako"):
            continue

        is_qr_template = "-qr." in template_name
        if use_qr != is_qr_template:
            continue

        filename = os.path.join(templates_dir, template_name)
        domain = MakoFormatterPlugin.get_iteration_domain(filename)

        if domain == "":
            assert template_name.startswith("base.")
            continue

        cls_mapping = {
            "plant": Plant,
            "accession": Accession,
            "species": Species,
            "location": Location,
        }

        cls = cls_mapping.get(domain, None)
        if not cls:
            todo = selection
        else:
            todo = sorted(get_pertinent_objects(cls, selection), key=utils.natsort_key)

        logger.debug("Formatting ›%s‹" % filename)
        report = MakoFormatterPlugin.format(todo, template=filename)

        assert isinstance(report, bytes)


def test_format_qr_postscript_templates(session):
    """
    Test formatting mako templates with QR codes and PostScript.
    """
    selection = session.execute(select(Plant)).scalars().all()
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

    for i, template_name in enumerate(os.listdir(templates_dir)):
        if not template_name.endswith(".mako"):
            continue
        if "-qr." not in template_name or not template_name.endswith((".ps.mako", ".eps.mako")):
            continue

        filename = os.path.join(templates_dir, template_name)
        domain = MakoFormatterPlugin.get_iteration_domain(filename)
        cls_mapping = {
            "plant": Plant,
            "accession": Accession,
            "species": Species,
            "location": Location,
        }
        cls = cls_mapping[domain]
        todo = sorted(get_pertinent_objects(cls, selection), key=utils.natsort_key)

        report = MakoFormatterPlugin.format(todo, template=filename)

        assert isinstance(report, bytes)


@pytest.mark.skip(reason="Related to issue #363")
def test_format_qr_svg_templates(session):
    """
    Test formatting mako templates with QR codes and SVG.
    """
    plants = session.execute(select(Plant)).scalars().all()
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

    for template_name in os.listdir(templates_dir):
        if not template_name.endswith(".mako") or "-qr." not in template_name or not template_name.endswith(".svg"):
            continue

        filename = os.path.join(templates_dir, template_name)
        options = {
            name: default
            for (name, _, default, _) in MakoFormatterPlugin.get_options(filename)
        }

        report = MakoFormatterPlugin.format(plants, template=filename, **options)

        assert isinstance(report, bytes)




class TestSvgProduction:
    def test_add_text_a(self):
        g, x, y = SVG.add_text(0, 0, "a", 2)
        assert y == 0
        assert x == 31
        assert (
            g
            == '<g transform="translate(0, 0)scale(2)">\n'
            '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
            "</g>"
        )

    def test_add_text_tildes(self):
        g, x, y = SVG.add_text(0, 0, "áà", 2)
        assert y == 0
        assert x == 62
        assert (
            g
            == '<g transform="translate(0, 0)scale(2)">\n'
            '<use transform="translate(0,0)" xlink:href="#s1-u00e1"/>\n'
            '<use transform="translate(15.5,0)" xlink:href="#s1-u00e0"/>\n'
            "</g>"
        )

    def test_add_text_align_right1(self):
        g, x, y = SVG.add_text(0, 0, "áà", 2, align=1)
        assert y == 0
        assert x == 0
        assert (
            g
            == '<g transform="translate(-62.0, 0.0)scale(2)">\n'
            '<use transform="translate(0,0)" xlink:href="#s1-u00e1"/>\n'
            '<use transform="translate(15.5,0)" xlink:href="#s1-u00e0"/>\n'
            "</g>"
        )

    def test_add_text_align_right2(self):
        g, x, y = SVG.add_text(0, 0, "áà", 2, align=0.5)
        assert y == 0
        assert x == 31.0
        assert (
            g
            == '<g transform="translate(-31.0, 0.0)scale(2)">\n'
            '<use transform="translate(0,0)" xlink:href="#s1-u00e1"/>\n'
            '<use transform="translate(15.5,0)" xlink:href="#s1-u00e0"/>\n'
            "</g>"
        )

    @pytest.mark.parametrize(
        "rotate, expected_x, expected_y",
        [
            (0, 31, 0),
            (90, 0, 31),
            (-90, 0, -31),
            (180, -31, 0),
        ],
    )
    def test_add_text_a_rotated_endpoint(self, rotate, expected_x, expected_y):
        g, x, y = SVG.add_text(0, 0, "a", 2, align=0, rotate=rotate)
        assert pytest.approx(x) == expected_x
        assert pytest.approx(y) == expected_y

    @pytest.mark.parametrize(
        "rotate, expected_x, expected_y",
        [
            (0, 15.5, 0),
            (90, 0, 15.5),
            (-90, 0, -15.5),
            (180, -15.5, 0),
        ],
    )
    def test_add_text_a_rotated_aligned_endpoint(self, rotate, expected_x, expected_y):
        g, x, y = SVG.add_text(0, 0, "a", 2, align=0.5, rotate=rotate)
        assert pytest.approx(x) == expected_x
        assert pytest.approx(y) == expected_y

    @pytest.mark.parametrize(
        "rotate, expected_g",
        [
            (
                0,
                '<g transform="translate(0, 0)scale(2)">\n'
                '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
                "</g>",
            ),
            (
                90,
                '<g transform="translate(0, 0)scale(2)rotate(90)">\n'
                '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
                "</g>",
            ),
            (
                -90,
                '<g transform="translate(0, 0)scale(2)rotate(-90)">\n'
                '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
                "</g>",
            ),
            (
                180,
                '<g transform="translate(0, 0)scale(2)rotate(180)">\n'
                '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
                "</g>",
            ),
        ],
    )
    def test_add_text_a_rotated_glyph(self, rotate, expected_g):
        g, x, y = SVG.add_text(0, 0, "a", 2, align=0, rotate=rotate)
        assert g == expected_g

    @pytest.mark.parametrize(
        "rotate, expected_g",
        [
            (
                0,
                '<g transform="translate(-15.5, 0.0)scale(2)">\n'
                '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
                "</g>",
            ),
            (
                90,
                '<g transform="translate(0.0, -15.5)scale(2)rotate(90)">\n'
                '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
                "</g>",
            ),
            (
                -90,
                '<g transform="translate(0.0, 15.5)scale(2)rotate(-90)">\n'
                '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
                "</g>",
            ),
            (
                180,
                '<g transform="translate(15.5, 0.0)scale(2)rotate(180)">\n'
                '<use transform="translate(0,0)" xlink:href="#s1-u0061"/>\n'
                "</g>",
            ),
        ],
    )
    def test_add_text_a_rotated_aligned_glyph(self, rotate, expected_g):
        g, x, y = SVG.add_text(0, 0, "a", 2, align=0.5, rotate=rotate)
        g = g.replace("-0.0", "0.0")  # Ignore sign on zero
        assert g == expected_g



class TestCode39:
    def test_code39_path_0(self):
        g = Code39.path("0", 10)
        assert (
            g
            == "M 0,0 0,10 "
            "M 2,10 2,0 "
            "M 6,0 6,10 "
            "M 7,10 7,0 "
            "M 8,0 8,10 "
            "M 10,10 10,0 "
            "M 11,0 11,10 "
            "M 12,10 12,0 "
            "M 14,0 14,10"
        )

    def test_code39_path_dot(self):
        g = Code39.path(".", 10)
        assert (
            g
            == "M 0,0 0,10 "
            "M 1,10 1,0 "
            "M 2,0 2,10 "
            "M 6,10 6,0 "
            "M 8,0 8,10 "
            "M 10,10 10,0 "
            "M 11,0 11,10 "
            "M 12,10 12,0 "
            "M 14,0 14,10"
        )

    def test_code39_path_dot_5(self):
        g = Code39.path(".", 5)
        assert (
            g
            == "M 0,0 0,5 "
            "M 1,5 1,0 "
            "M 2,0 2,5 "
            "M 6,5 6,0 "
            "M 8,0 8,5 "
            "M 10,5 10,0 "
            "M 11,0 11,5 "
            "M 12,5 12,0 "
            "M 14,0 14,5"
        )

    def test_code39_letter_dot_5(self):
        g = Code39.letter(".", 5)
        assert (
            g
            == '<path d="M 0,0 0,5 M 1,5 1,0 M 2,0 2,5 M 6,5 6,0 M 8,0 8,5 M 10,5 10,0 M 11,0 11,5 M 12,5 12,0 M 14,0 14,5" style="stroke:#0000ff;stroke-width:1"/>'
        )

    def test_code39_translated_letter_dot_5(self):
        g = Code39.letter(".", 5, (5, 8))
        assert (
            g
            == '<path transform="translate(5,8)" d="M 0,0 0,5 M 1,5 1,0 M 2,0 2,5 M 6,5 6,0 M 8,0 8,5 M 10,5 10,0 M 11,0 11,5 M 12,5 12,0 M 14,0 14,5" style="stroke:#0000ff;stroke-width:1"/>'
        )

    def test_code39_text(self):
        g, x, y = SVG.add_code39(0, 0, "010810", unit=1, height=7)
        assert y == 0
        assert x == 127
        assert (
            g
            == '<g transform="translate(0,0)scale(1,1)translate(0,0)"><path transform="translate(0,0)" d="M 0,0 0,7 M 4,7 4,0 M 6,0 6,7 M 7,7 7,0 M 8,0 8,7 M 10,7 10,0 M 11,0 11,7 M 12,7 12,0 M 14,0 14,7" style="stroke:#0000ff;stroke-width:1"/>'
            "<path transform=\"translate(16,0)\" d=\"M 0,0 0,7 M 2,7 2,0 M 6,0 6,7 M 7,7 7,0 M 8,0 8,7 M 10,7 10,0 M 11,0 11,7 M 12,7 12,0 M 14,0 14,7\" style=\"stroke:#0000ff;stroke-width:1\"/>"
            # Add similar lines to complete the full path structure here...
            "</g>"
        )

    @pytest.mark.parametrize(
        "align, expected_x, expected_g",
        [
            (
                0.5,
                23.5,
                '<g transform="translate(0,0)scale(1,1)translate(-23.5,0)">'
                '<path transform="translate(0,0)" d="M 0,0 0,7 M 4,7 4,0 M 6,0 6,7 M 7,7 7,0 M 8,0 8,7 M 10,7 10,0 M 11,0 11,7 M 12,7 12,0 M 14,0 14,7" style="stroke:#0000ff;stroke-width:1"/>'
                "</g>",
            ),
            (
                0,
                47,
                '<g transform="translate(0,0)scale(1,1)translate(0,0)">'
                '<path transform="translate(0,0)" d="M 0,0 0,7 M 4,7 4,0 M 6,0 6,7 M 7,7 7,0 M 8,0 8,7 M 10,7 10,0 M 11,0 11,7 M 12,7 12,0 M 14,0 14,7" style="stroke:#0000ff;stroke-width:1"/>'
                "</g>",
            ),
            (
                1,
                0,
                '<g transform="translate(0,0)scale(1,1)translate(-47,0)">'
                '<path transform="translate(0,0)" d="M 0,0 0,7 M 4,7 4,0 M 6,0 6,7 M 7,7 7,0 M 8,0 8,7 M 10,7 10,0 M 11,0 11,7 M 12,7 12,0 M 14,0 14,7" style="stroke:#0000ff;stroke-width:1"/>'
                "</g>",
            ),
        ],
    )
    def test_code39_text_alignment(self, align, expected_x, expected_g):
        g, x, y = SVG.add_code39(0, 0, "0", unit=1, height=7, align=align)
        assert y == 0
        assert x == expected_x
        assert g == expected_g
        import pytest


class TestQRCode:
    path = '<path stroke="#000" class="pyqrline" d="M0 0.5h7m1 0h3m1 0h1m1 0h7m-21 1h1m5 0h1m2 0h2m3 0h1m5 0h1m-21 1h1m1 0h3m1 0h1m3 0h1m3 0h1m1 0h3m1 0h1m-21 1h1m1 0h3m1 0h1m1 0h1m2 0h2m1 0h1m1 0h3m1 0h1m-21 1h1m1 0h3m1 0h1m3 0h2m2 0h1m1 0h3m1 0h1m-21 1h1m5 0h1m2 0h1m1 0h1m2 0h1m5 0h1m-21 1h7m1 0h1m1 0h1m1 0h1m1 0h7m-12 1h1m2 0h1m-11 1h1m1 0h3m1 0h2m3 0h1m3 0h1m2 0h1m-18 1h2m2 0h2m3 0h1m1 0h2m3 0h2m-21 1h5m1 0h1m1 0h1m3 0h4m1 0h4m-21 1h4m1 0h1m2 0h2m1 0h2m2 0h2m2 0h1m-20 1h2m3 0h2m1 0h3m4 0h1m1 0h1m1 0h2m-13 1h1m1 0h3m4 0h1m2 0h1m-21 1h7m2 0h2m5 0h2m1 0h2m-21 1h1m5 0h1m1 0h3m1 0h1m1 0h1m4 0h1m-20 1h1m1 0h3m1 0h1m1 0h1m1 0h2m2 0h1m1 0h2m1 0h2m-21 1h1m1 0h3m1 0h1m2 0h1m4 0h2m3 0h1m-20 1h1m1 0h3m1 0h1m1 0h1m3 0h2m1 0h1m2 0h1m1 0h1m-21 1h1m5 0h1m2 0h3m1 0h5m1 0h1m-20 1h7m3 0h1m2 0h3m2 0h3"/>'

    def test_can_get_qr_as_string(self):
        g = SVG.add_qr(0, 0, "test")
        parts = g.split("\n")
        assert len(parts) == 1
        assert parts[0] == self.path

    def test_can_get_qr_as_string_translated(self):
        g = SVG.add_qr(30, 10, "test")
        parts = g.split("\n")
        assert len(parts) == 3
        assert parts[0] == '<g transform="translate(30,10)">'
        assert parts[1] == self.path
        assert parts[2] == "</g>"

    def test_can_get_qr_as_string_translated_framed(self):
        g = SVG.add_qr(
            30, 10, "http://ghini.readthedocs.io/en/ghini-3.1-dev/", side=30
        )
        parts = g.split("\n")
        assert len(parts) == 3
        assert parts[0].startswith(
            '<g transform="translate(30,10)scale(0.731707317073'
        )
        assert parts[2] == "</g>"

        g = SVG.add_qr(30, 10, "2014.0018.2", side=30)
        parts = g.split("\n")
        assert len(parts) == 3
        assert parts[0] == '<g transform="translate(30,10)scale(1.2)">'
        assert parts[2] == "</g>"

        g = SVG.add_qr(30, 10, "2014.0018", side=30)
        parts = g.split("\n")
        assert len(parts) == 3
        assert parts[0].startswith(
            '<g transform="translate(30,10)scale(1.4285714'
        )
        assert parts[2] == "</g>"

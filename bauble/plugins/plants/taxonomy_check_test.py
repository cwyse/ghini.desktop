# Copyright 2018 Mario Frasca <mario@anche.no>.
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

import pytest
from bauble.plugins.plants.family import Family
from bauble.plugins.plants.genus import Genus
from sqlalchemy import text

from .taxonomy_check import build_batch_lookup_rows
from .taxonomy_check import species_to_fix as species_to_fix
from .taxon_lookup import (
    TaxonLookupRequest,
    TaxonLookupResponse,
    TaxonLookupResult,
    TaxonLookupStatus,
)


class FakeProvider:
    name = "wfo"

    def __init__(self, responses) -> None:
        self.responses = responses
        self.requests = []

    def lookup(self, request: TaxonLookupRequest) -> TaxonLookupResponse:
        self.requests.append(request.name)
        return self.responses.get(
            request.name,
            TaxonLookupResponse(request=request, provider=self.name, results=[]),
        )


@pytest.fixture(scope="function")
def setup_data(db_session):
    """
    Fixture to initialize the test database with required data.
    """
    family1 = Family(epithet="Amaranthaceae")
    family2 = Family(epithet="Fabaceae")
    genus1 = Genus(family=family1, epithet="Salsola")
    genus2 = Genus(family=family2, epithet="Trifolium")
    db_session.add_all([family1, family2, genus1, genus2])
    if db_session.in_transaction():
        db_session.commit()
    return db_session


@pytest.fixture(autouse=True)
def clear_family_table(db_session) -> None:
    """
    Ensure the family table is cleared before each test.
    """
    db_session.execute(text("DELETE FROM genus"))
    db_session.execute(text("DELETE FROM family"))
    if db_session.in_transaction():
        db_session.commit()


@pytest.mark.usefixtures("db_session", "setup_data")
class TestTaxonomyCheck:
    def test_batch_lookup_uses_wfo_mapping(self) -> None:
        accepted = TaxonLookupResult(
            submitted_name="Guidedgenus guidedspecies",
            provider="wfo",
            provider_id="wfo-accepted",
            matched_name="Guidedgenus guidedspecies",
            genus="Guidedgenus",
            species="guidedspecies",
            family="Guidedaceae",
            authorship="Guided Author",
            rank="species",
            status=TaxonLookupStatus.ACCEPTED,
            accepted_provider_id="wfo-accepted",
            title="Guidedgenus guidedspecies Guided Author",
        )
        synonym = TaxonLookupResult(
            submitted_name="Guidedgenus dailyensis",
            provider="wfo",
            provider_id="wfo-synonym",
            matched_name="Guidedgenus dailyensis",
            genus="Guidedgenus",
            species="dailyensis",
            family="Guidedaceae",
            authorship="Guided Author",
            rank="species",
            status=TaxonLookupStatus.SYNONYM,
            accepted_provider_id="wfo-accepted",
            title="Guidedgenus dailyensis Guided Author",
        )
        accepted_match = TaxonLookupResult(
            submitted_name="wfo-accepted",
            provider="wfo",
            provider_id="wfo-accepted",
            matched_name="Guidedgenus guidedspecies",
            genus="Guidedgenus",
            species="guidedspecies",
            family="Guidedaceae",
            authorship="Guided Author",
            rank="species",
            status=TaxonLookupStatus.ACCEPTED,
            accepted_provider_id="wfo-accepted",
            title="Guidedgenus guidedspecies Guided Author",
        )
        provider = FakeProvider(
            {
                "Guidedgenus guidedspecies": TaxonLookupResponse(
                    request=TaxonLookupRequest(name="Guidedgenus guidedspecies"),
                    provider="wfo",
                    results=[accepted],
                ),
                "Guidedgenus dailyensis": TaxonLookupResponse(
                    request=TaxonLookupRequest(name="Guidedgenus dailyensis"),
                    provider="wfo",
                    results=[synonym],
                ),
                "wfo-accepted": TaxonLookupResponse(
                    request=TaxonLookupRequest(name="wfo-accepted"),
                    provider="wfo",
                    results=[accepted_match],
                ),
                "No match": TaxonLookupResponse(
                    request=TaxonLookupRequest(name="No match"),
                    provider="wfo",
                    results=[],
                ),
            }
        )

        rows = build_batch_lookup_rows(
            ["Guidedgenus guidedspecies", "Guidedgenus dailyensis", "No match"],
            provider,
        )

        assert provider.requests == [
            "Guidedgenus guidedspecies",
            "Guidedgenus dailyensis",
            "wfo-accepted",
            "No match",
        ]
        assert rows[0][2:6] == [
            "Guidedgenus guidedspecies",
            "Guidedgenus guidedspecies",
            "Guided Author",
            "Accepted",
        ]
        assert rows[0][8] is True
        assert rows[1][2:6] == [
            "Guidedgenus dailyensis",
            "Guidedgenus dailyensis",
            "Guided Author",
            "Synonym",
        ]
        assert rows[1][6:8] == ["Guidedgenus guidedspecies", "Guided Author"]
        assert rows[2][2:6] == [
            "",
            "Guidedgenus guidedspecies",
            "Guided Author",
            "Accepted",
        ]
        assert rows[3][2:6] == ["No match", "", "", "No match"]
        assert rows[3][8] is False

    def test_species_author(self, db_session) -> None:
        """
        Test that the species author is correctly handled.
        """
        s = species_to_fix(db_session, "Salsola kali", "L.", True)
        assert s is not None
        assert s.epithet == "kali"
        assert s.author == "L."
        assert s.infraspecific_rank == ""
        assert s.infraspecific_epithet == ""
        assert s.infraspecific_author == ""

    def test_subspecies_author(self, db_session) -> None:
        """
        Test that the subspecies author is correctly handled.
        """
        s = species_to_fix(
            db_session, "Salsola kali subsp. tragus", "(L.) Čelak.", True
        )
        assert s is not None
        assert s.epithet == "kali"
        assert s.author is None
        assert s.infraspecific_rank == "subsp."
        assert s.infraspecific_epithet == "tragus"
        assert s.infraspecific_author == "(L.) Čelak."

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
import difflib
import logging
import threading
from typing import Any, Callable, Optional, Union

import requests

logger: Any = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AskTPL(threading.Thread):
    _stop: bool
    binomial: Any
    threshold: Any
    callback: Any
    timeout: Any
    gui: Any
    running: Any = None

    def __init__(
        self,
        binomial: Optional[str],
        callback: Callable[
            [
                Optional[dict[str, Any]],
                Optional[Union[dict[str, Any], list[dict[str, Any]]]],
            ],
            None,
        ],
        threshold: float = 0.8,
        timeout: int = 4,
        gui: bool = False,
        group: Optional[Any] = None,
        verbose: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(group=group, target=None, name=None)
        logger.debug(
            "new %s, already running %s.",
            self.name,
            self.running and self.running.name,
        )
        if self.running is not None:
            if self.running.binomial == binomial:
                logger.debug(
                    "already requesting %s, ignoring repeated request",
                    binomial,
                )
                binomial = None
            else:
                logger.debug(
                    "running different request (%s), stopping it, starting %s",
                    self.running.binomial,
                    binomial,
                )
                self.running.stop()
        if binomial:
            self.__class__.running = self
        self._stop = False
        self.binomial = binomial
        self.threshold = threshold
        self.callback = callback
        self.timeout = timeout
        self.gui = gui

    def stop(self) -> None:
        self._stop = True

    def stopped(self) -> bool:
        return self._stop

    def run(self) -> None:
        def extract_family(wfo_path: str) -> Optional[str]:
            parts = wfo_path.split("$")
            parts = parts[0].split("/")
            if len(parts) > 3:
                return parts[-3]  # Third-to-last element
            return None

        def extract_species(wfo_path: str) -> Optional[str]:
            parts = wfo_path.split("$")
            parts = parts[0].split("/")
            if len(parts) > 3:
                return parts[-1]  # Third-to-last element
            return None

        def query_wfo_api(input_string: str) -> Any:
            url = "https://list.worldfloraonline.org/gql.php"
            query = """
            query ($inputString: String!) {
                taxonNameMatch(inputString: $inputString) {
                    inputString
                    searchString
                    match {
                        id
                        title
                        fullNameStringPlain
                        genusString
                        speciesString
                        authorsString
                        role
                        rank
                        wfoPath
                        currentPreferredUsage {
                            hasName {
                                id
                            }
                        }
                    }
                    candidates {
                        id
                        title
                        fullNameStringPlain
                        genusString
                        speciesString
                        authorsString
                        role
                        rank
                        wfoPath
                        currentPreferredUsage {
                            hasName {
                                id
                            }
                        }
                    }
                }
            }
            """
            variables = {"inputString": input_string}
            response = requests.post(url, json={"query": query, "variables": variables})
            return response.json()

        def ask_wfo(name: str) -> Optional[list[dict[str, Any]]]:
            result = query_wfo_api(name)
            data = result.get("data", {}).get("taxonNameMatch", {})

            if "match" in data and data["match"]:
                match = data["match"]
                family = extract_family(match["wfoPath"])
                species = extract_species(match["wfoPath"])
                return [
                    {
                        "ID": match["id"],
                        "FullName": match["fullNameStringPlain"],
                        "Genus": match["genusString"],
                        "Species": (
                            species
                            if match["speciesString"] is None
                            else match["speciesString"]
                        ),
                        "role": match[
                            "role"
                        ],  # accepted, synonym, unplaced, deprecated
                        "Accepted ID": (
                            match["id"]
                            if match.get("currentPreferredUsage")
                            and match["currentPreferredUsage"]["hasName"]["id"]
                            == match["id"]
                            else None
                        ),
                        "Taxonomic status": (
                            "Accepted"
                            if match.get("currentPreferredUsage")
                            and match["currentPreferredUsage"]["hasName"]["id"]
                            == match["id"]
                            else (
                                "Synonym"
                                if match.get("currentPreferredUsage")
                                else "Unplaced"
                            )
                        ),
                        "Genus hybrid marker": (
                            "×"
                            if match["fullNameStringPlain"].startswith("×")
                            and match["genusString"] == "null"
                            else ""
                        ),
                        "Species hybrid marker": (
                            "× "
                            if " × " in match["fullNameStringPlain"]
                            and match["speciesString"] == "null"
                            else ""
                        ),
                        "Authorship": match["authorsString"],
                        "Family": family,
                        "Title": match["title"],
                    }
                ]
            elif "candidates" in data and data["candidates"]:
                candidates = []
                for candidate in data["candidates"]:
                    family = extract_family(candidate["wfoPath"])
                    species = extract_species(candidate["wfoPath"])
                    candidates.append(
                        {
                            "ID": candidate["id"],
                            "FullName": candidate["fullNameStringPlain"],
                            "Genus": candidate["genusString"],
                            "Species": (
                                species
                                if candidate["speciesString"] is None
                                else candidate["speciesString"]
                            ),
                            "role": candidate[
                                "role"
                            ],  # accepted, synonym, unplaced, deprecated
                            "Accepted ID": (
                                candidate["id"]
                                if candidate.get("currentPreferredUsage")
                                and candidate["currentPreferredUsage"]["hasName"]["id"]
                                == candidate["id"]
                                else None
                            ),
                            "Taxonomic status": (
                                "Accepted"
                                if candidate.get("currentPreferredUsage")
                                and candidate["currentPreferredUsage"]["hasName"]["id"]
                                == candidate["id"]
                                else (
                                    "Synonym"
                                    if candidate.get("currentPreferredUsage")
                                    else "Unplaced"
                                )
                            ),
                            "Genus hybrid marker": (
                                "×"
                                if candidate["fullNameStringPlain"].startswith("×")
                                and candidate["genusString"] == "null"
                                else ""
                            ),
                            "Species hybrid marker": (
                                "×"
                                if " × " in candidate["fullNameStringPlain"]
                                and candidate["speciesString"] == "null"
                                else ""
                            ),
                            "Authorship": candidate["authorsString"],
                            "Family": family,
                            "Title": candidate["title"],
                        }
                    )
                return candidates
            else:
                return None

        class ShouldStopNow(Exception):
            pass

        class NoResult(Exception):
            pass

        if self.binomial is None:
            return
        found: Optional[dict[str, Any]] = None
        accepted: Optional[Union[dict[str, Any], list[dict[str, Any]]]] = None
        try:
            accepted = None
            logger.debug("%s before first query", self.name)
            candidates = ask_wfo(self.binomial)
            if not candidates:  # ✅ FIX: Handle empty results properly
                logger.info("nothing matches")  # ✅ Log correct message
                return  # ✅ Exit instead of raising NoResult
            logger.debug("%s after first query", self.name)
            if self.stopped():
                raise ShouldStopNow("after first query")
            if len(candidates) > 1:
                for item in candidates:
                    g, s = item["Genus"], item["Species"]
                    seq = difflib.SequenceMatcher(a=self.binomial, b=f"{g} {s}")
                    item["_score_"] = seq.ratio()

                found = sorted(
                    candidates,
                    key=lambda a: (a["_score_"], a["Taxonomic status"]),
                )[-1]
                logger.debug("best match has score %s", found["_score_"])
                if found["_score_"] < self.threshold:
                    found["_score_"] = 0
            elif candidates:
                found = candidates.pop()
            else:
                raise NoResult
            logger.debug("found this: %s", str(found))
            if found["Accepted ID"]:
                # accepted = found
                accepted_list = ask_wfo(found["FullName"])
                accepted = accepted_list[0] if accepted_list else None

                logger.debug("ask_tpl on the Accepted ID returns %s", accepted)
                if accepted is None:
                    logger.debug(
                        "taxon %s %s (%s) is marked as synonym. "
                        "accepted form (%s) is at infraspecific rank.",
                        found["Genus"],
                        found["Species"],
                        found["ID"],
                        found["Accepted ID"],
                    )
                logger.debug("%s after second query", self.name)
            if self.stopped():
                raise ShouldStopNow("after second query")
        except ShouldStopNow:
            logger.debug("%s interrupted : do not invoke callback", self.name)
            return
        except Exception as e:
            import traceback

            logger.warning(traceback.format_exc())
            logger.debug(
                "%s (%s)%s : completed with trouble",
                self.name,
                type(e).__name__,
                e,
            )
            self.__class__.running = None
            found = None
            accepted = None

        self.__class__.running = None
        logger.debug(f"{self.name} before invoking callback")
        if self.gui:
            from bauble.gtkinit import GLib

            GLib.idle_add(self.callback, found, accepted)
        else:
            self.callback(found, accepted)


def citation(d: dict[str, Any]) -> str:
    # return (
    #     "%(Genus hybrid marker)s%(Genus)s "
    #     "%(Species hybrid marker)s%(Species)s "
    #     # "%(Infraspecific rank)s %(Infraspecific epithet)s "
    #     "%(Authorship)s (%(Family)s)" % d
    # ).replace("   ", " ")
    return ("{Title} ({Family})".format(**d)).replace("   ", " ")


from typing import Any


def what_to_do_with_it(
    found: Optional[dict[str, Any]],
    accepted: Optional[Union[dict[str, Any], list[dict[str, Any]]]],
) -> None:
    if found is None and accepted is None:
        logger.info("nothing matches")
        return
    if found is not None:
        logger.info("%s", citation(found))
    if accepted == []:
        logger.info("invalid reference in tpl.")
    if isinstance(accepted, dict):
        logger.info("%s - is its accepted form", citation(accepted))

#
# Copyright (c) 2021, 2022 Astroncia <kestraly@gmail.com>
# Copyright (c) 2023 yuki-chan-nya <yukichandev@proton.me>
#
# This file is part of kotori.
#
# kotori is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kotori is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kotori. If not, see <https://www.gnu.org/licenses/>.
#
# The Font Awesome pictograms are licensed under the CC BY 4.0 License.
# https://fontawesome.com/
# https://creativecommons.org/licenses/by/4.0/
#
import os
import gettext
import logging
import json
import codecs
import time
import requests
import io
import zipfile
from pathlib import Path
from kotori.crossplatform import LOCAL_DIR
from kotori.epg_xmltv import parse_as_xmltv
from kotori.epg_zip import parse_epg_zip
from kotori.epg_txt import parse_txt

os.environ["LANG"] = "ru_RU"
_ = gettext.gettext
logger = logging.getLogger(__name__)

EPG_CACHE_VERSION = 1


def load_epg(epg_url, user_agent):
    """Load EPG file"""
    logger.info("Loading EPG...")
    logger.info(f"Address: '{epg_url}'")
    if os.path.isfile(epg_url.strip()):
        epg_file = open(epg_url.strip(), "rb")
        epg = epg_file.read()
        epg_file.close()
    else:
        epg_req = requests.get(
            epg_url,
            headers={"User-Agent": user_agent},
            stream=True,
            timeout=35,
            verify=False,
        )
        logger.info(f"EPG URL status code: {epg_req.status_code}")
        epg = epg_req.content
    logger.info("EPG loaded")
    return epg


def merge_two_dicts(dict1, dict2):
    """Merge two dictionaries"""
    dict_new = dict1.copy()
    dict_new.update(dict2)
    return dict_new


def fetch_epg(settings, catchup_days1, return_dict1):
    """Parsing EPG"""
    programmes_epg = {}
    prog_ids = {}
    epg_ok = True
    exc = None
    epg_failures = []
    epg_exceptions = []
    epg_icons = {}
    epg_settings_url = [settings["epg"]]
    if "," in epg_settings_url[0]:
        epg_settings_url[0] = "^^::MULTIPLE::^^" + ":::^^^:::".join(
            epg_settings_url[0].split(",")
        )
    if epg_settings_url[0].startswith("^^::MULTIPLE::^^"):
        epg_settings_url = (
            epg_settings_url[0].replace("^^::MULTIPLE::^^", "").split(":::^^^:::")
        )
    epg_i = 0
    for epg_url_1 in epg_settings_url:
        epg_i += 1
        try:
            return_dict1["epg_progress"] = _(
                "Updating TV guide... (loading {}/{})"
            ).format(epg_i, len(epg_settings_url))

            epg = load_epg(epg_url_1, settings["ua"])

            return_dict1["epg_progress"] = _(
                "Updating TV guide... (parsing {}/{})"
            ).format(epg_i, len(epg_settings_url))

            try:
                # XMLTV
                pr_xmltv = parse_as_xmltv(
                    epg, settings, catchup_days1, return_dict1, epg_i, epg_settings_url
                )
                programmes_epg = merge_two_dicts(programmes_epg, pr_xmltv[0])
                prog_ids = merge_two_dicts(prog_ids, pr_xmltv[1])
                try:
                    epg_icons = merge_two_dicts(epg_icons, pr_xmltv[2])
                except Exception:
                    pass
            except Exception:
                zip_epg = io.BytesIO(epg)
                if zipfile.is_zipfile(zip_epg):  # ZIP
                    logger.info("ZIP file detected")
                    epg = ""
                    pr_zip = parse_epg_zip(zip_epg)
                    if isinstance(pr_zip, list) and pr_zip[0] == "xmltv":
                        # XMLTV
                        pr_xmltv = parse_as_xmltv(
                            pr_zip[1],
                            settings,
                            catchup_days1,
                            return_dict1,
                            epg_i,
                            epg_settings_url,
                        )
                        programmes_epg = merge_two_dicts(programmes_epg, pr_xmltv[0])
                        prog_ids = merge_two_dicts(prog_ids, pr_xmltv[1])
                        try:
                            epg_icons = merge_two_dicts(epg_icons, pr_xmltv[2])
                        except Exception:
                            pass
                    else:
                        programmes_epg = merge_two_dicts(programmes_epg, pr_zip)
                elif epg[0:6] == b"tv.all":  # TXT (TV.ALL)
                    zip_epg = None
                    programmes_epg = merge_two_dicts(programmes_epg, parse_txt(epg))
                else:
                    zip_epg = None
                    raise Exception("Unknown EPG format or parsing failed!")

            # Sort EPG entries by start time
            for program_epg in programmes_epg:
                programmes_epg[program_epg].sort(
                    key=lambda programme: programme["start"]
                )

            epg_failures.append(False)
            logger.info("Parsing done!")
            logger.info("Parsing EPG...")
        except Exception as exc0:
            logger.warning("Failed parsing EPG!")
            epg_failures.append(True)
            epg_exceptions.append(exc0)
    if False not in epg_failures:
        epg_ok = False
        exc = epg_exceptions[0]
    return_dict1["epg_progress"] = ""
    logger.info("Parsing EPG done!")
    return [{}, programmes_epg, epg_ok, exc, prog_ids, epg_icons]


def worker(sys_settings, catchup_days1, return_dict1):
    """Worker running from multiprocess"""
    epg = fetch_epg(sys_settings, catchup_days1, return_dict1)
    return_dict1["epg_progress"] = _("Updating TV guide...")
    return [epg[0], epg[1], True, epg[2], epg[3], epg[4], epg[5]]


def is_program_actual(sets0, epg_ready, force=False, future=False):
    if not epg_ready and not force:
        return True
    if future:
        current_time = time.time() + 86400  # 1 day
    else:
        current_time = time.time()
    if sets0:
        for prog1 in sets0:
            pr1 = sets0[prog1]
            for p in pr1:
                if current_time > p["start"] and current_time < p["stop"]:
                    return True
    return False


def load_epg_cache(settings_m3u, settings_epg, epg_ready):
    try:
        file_epg1 = open(str(Path(LOCAL_DIR, "epg.cache")), "rb")
        file1_json = json.loads(
            codecs.decode(codecs.decode(file_epg1.read(), "zlib"), "utf-8")
        )
        file_epg1.close()
        epg_cache_version = -1
        try:
            if "cache_version" in file1_json:
                epg_cache_version = file1_json["cache_version"]
        except Exception:
            pass
        if epg_cache_version != EPG_CACHE_VERSION:
            logger.info("Ignoring epg.cache, EPG cache version changed")
            os.remove(str(Path(LOCAL_DIR, "epg.cache")))
            file1_json = {}
        else:
            current_url = file1_json["current_url"]
            system_timezone = file1_json["system_timezone"]
            if (
                current_url[0] == settings_m3u
                and current_url[1] == settings_epg
                and system_timezone == json.dumps(time.tzname)
            ):
                pass
            else:
                logger.info("Ignoring epg.cache, something changed")
                os.remove(str(Path(LOCAL_DIR, "epg.cache")))
                file1_json = {}
    except Exception:
        file1_json = {}
    if "tvguide_sets" in file1_json:
        file1_json["programmes_1"] = {
            prog3.lower(): file1_json["tvguide_sets"][prog3]
            for prog3 in file1_json["tvguide_sets"]
        }
        file1_json["is_program_actual"] = is_program_actual(
            file1_json["tvguide_sets"], epg_ready, force=True, future=True
        )
    return file1_json


def save_epg_cache(tvguide_sets_arg, settings_arg, prog_ids_arg, epg_icons_arg):
    if tvguide_sets_arg:
        if not settings_arg["nocacheepg"]:
            file2 = open(str(Path(LOCAL_DIR, "epg.cache")), "wb")
            file2.write(
                codecs.encode(
                    bytes(
                        json.dumps(
                            {
                                "cache_version": EPG_CACHE_VERSION,
                                "system_timezone": json.dumps(time.tzname),
                                "tvguide_sets": tvguide_sets_arg,
                                "current_url": [
                                    str(settings_arg["m3u"]),
                                    str(settings_arg["epg"]),
                                ],
                                "prog_ids": prog_ids_arg,
                                "epg_icons": epg_icons_arg,
                            }
                        ),
                        "utf-8",
                    ),
                    "zlib",
                )
            )
            file2.close()

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
import logging
import xml.etree.ElementTree as ET
from kotori.lang import lang1

logger = logging.getLogger(__name__)
_ = lang1.gettext
all_channels = _("All channels")


def parse_xspf(xspf):
    logger.info("Trying parsing as XSPF...")
    array = []
    tree = ET.ElementTree(ET.fromstring(xspf)).getroot()
    for track in tree.findall("{*}trackList/{*}track"):
        title = track.find("{*}title").text.strip()
        group = ""
        try:
            group = track.find("{*}album").text.strip()
        except Exception:
            pass
        if not group:
            group = all_channels
        location = track.find("{*}location").text.strip()
        array.append(
            {
                "title": title,
                "tvg-name": "",
                "tvg-ID": "",
                "tvg-logo": "",
                "tvg-group": group,
                "tvg-url": "",
                "catchup": "default",
                "catchup-source": "",
                "catchup-days": "1",
                "useragent": "",
                "referer": "",
                "url": location,
            }
        )
    return [array, []]

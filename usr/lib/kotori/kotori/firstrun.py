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
from pathlib import Path
from kotori.crossplatform import LOCAL_DIR


def firstrun():
    if not os.path.isfile(Path(LOCAL_DIR, "playlists.json")):
        if not os.path.isdir(LOCAL_DIR):
            os.mkdir(LOCAL_DIR)
        with open(
            Path(LOCAL_DIR, "playlists.json"), "w", encoding="utf8"
        ) as playlists_file:
            playlists_file.write(
                '{"SkyNet": {"m3u": "https://xspf.skynet.ru/",'
                ' "epg": "https://sayori-q.github.io/epg/epg.xml.gz'
                '", "epgoffset": 0.0}}'
            )
        with open(
            Path(LOCAL_DIR, "settings.json"), "w", encoding="utf8"
        ) as settings_file:
            settings_file.write(
                '{"m3u": "https://xspf.skynet.ru/", '
                '"epg": "https://sayori-q.github.io/epg/epg.xml.gz"}'
            )

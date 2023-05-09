#
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
import json
from pathlib import Path
from kotori.crossplatform import LOCAL_DIR


class KotoriData:
    write_lock = False


def read_option(name):
    options = {}

    if os.path.isfile(Path(LOCAL_DIR, "player_data.json")):
        options_file = open(
            str(Path(LOCAL_DIR, "player_data.json")), "r", encoding="utf8"
        )
        options = json.loads(options_file.read())
        options_file.close()

    if name in options:
        return options[name]
    else:
        return None


def write_option(name, value):
    while KotoriData.write_lock:
        pass

    KotoriData.write_lock = True

    options = {}

    if os.path.isfile(Path(LOCAL_DIR, "player_data.json")):
        options_file = open(
            str(Path(LOCAL_DIR, "player_data.json")), "r", encoding="utf8"
        )
        options = json.loads(options_file.read())
        options_file.close()

    options[name] = value

    options_file = open(str(Path(LOCAL_DIR, "player_data.json")), "w", encoding="utf8")
    options_file.write(f"{json.dumps(options)}\n")
    options_file.close()

    KotoriData.write_lock = False

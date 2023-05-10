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
import logging
import json
import traceback
from functools import partial
from kotori.lang import lang1
from kotori.qt import get_qt_library
from kotori.qt6compat import qaction
from kotori.options import read_option

qt_library, QtWidgets, QtCore, QtGui, QShortcut = get_qt_library()
logger = logging.getLogger(__name__)
_ = lang1.gettext


class KotoriData:
    menubar_ready = False
    first_run = False
    first_run1 = False
    menubars = {}
    data = {}
    cur_vf_filters = []
    keyboard_sequences = []
    if qt_library == "PyQt6":
        str_offset = " " * 44
    else:
        str_offset = ""


def ast_mpv_seek(secs):
    logger.info(f"Seeking to {secs} seconds")
    KotoriData.player.command("seek", secs)


def ast_mpv_speed(spd):
    logger.info(f"Set speed to {spd}")
    KotoriData.player.speed = spd


def kotori_trackset(track, type1):
    KotoriData.kotori_track_set(track, type1)
    KotoriData.redraw_menubar()


def send_mpv_command(name, act, cmd):
    if cmd == "__AST_VFBLACK__":
        cur_window_pos = KotoriData.get_curwindow_pos()
        cmd = (
            f"lavfi=[pad=iw:iw*sar/{cur_window_pos[0]}*{cur_window_pos[1]}:0:(oh-ih)/2]"
        )
    if cmd == "__AST_SOFTSCALING__":
        cur_window_pos = KotoriData.get_curwindow_pos()
        cmd = f"lavfi=[scale={cur_window_pos[0]}:-2]"
    logger.info(f'Sending mpv command: "{name} {act} \\"{cmd}\\""')
    KotoriData.player.command(name, act, cmd)


def get_active_vf_filters():
    return KotoriData.cur_vf_filters


def apply_vf_filter(vf_filter, e_l):
    try:
        if e_l.isChecked():
            send_mpv_command(
                vf_filter.split("::::::::")[0], "add", vf_filter.split("::::::::")[1]
            )
            KotoriData.cur_vf_filters.append(vf_filter)
        else:
            send_mpv_command(
                vf_filter.split("::::::::")[0], "remove", vf_filter.split("::::::::")[1]
            )
            KotoriData.cur_vf_filters.remove(vf_filter)
    except Exception as e_4:
        logger.error("ERROR in vf-filter apply")
        logger.error("")
        e4_traceback = traceback.format_exc()
        logger.error(e4_traceback)
        KotoriData.show_exception(
            e_4, e4_traceback, "\n\n" + _("Error applying filters")
        )


def get_seq():
    return KotoriData.keyboard_sequences


def qkeysequence(seq):
    s_e = QtGui.QKeySequence(seq)
    KotoriData.keyboard_sequences.append(s_e)
    return s_e


def kbd(k_1):
    return qkeysequence(KotoriData.get_keybind(k_1))


def alwaysontop_action():
    try:
        aot_f = open(KotoriData.aot_file, "w", encoding="utf-8")
        aot_f.write(
            json.dumps({"alwaysontop": KotoriData.alwaysontopAction.isChecked()})
        )
        aot_f.close()
    except Exception:
        pass
    if KotoriData.alwaysontopAction.isChecked():
        logger.info("Always on top enabled now")
        KotoriData.enable_always_on_top()
    else:
        logger.info("Always on top disabled now")
        KotoriData.disable_always_on_top()


def reload_menubar_shortcuts():
    KotoriData.playlists.setShortcut(kbd("show_playlists"))
    KotoriData.reloadPlaylist.setShortcut(kbd("reload_playlist"))
    KotoriData.m3uEditor.setShortcut(kbd("show_m3u_editor"))
    KotoriData.exitAction.setShortcut(kbd("app.quit"))
    KotoriData.playpause.setShortcut(kbd("mpv_play"))
    KotoriData.stop.setShortcut(kbd("mpv_stop"))
    KotoriData.normalSpeed.setShortcut(kbd("(lambda: set_playback_speed(1.00))"))
    KotoriData.prevchannel.setShortcut(kbd("prev_channel"))
    KotoriData.nextchannel.setShortcut(kbd("next_channel"))
    KotoriData.fullscreen.setShortcut(kbd("mpv_fullscreen"))
    KotoriData.compactmode.setShortcut(kbd("showhideeverything"))
    KotoriData.csforchannel.setShortcut(kbd("main_channel_settings"))
    KotoriData.screenshot.setShortcut(kbd("do_screenshot"))
    KotoriData.muteAction.setShortcut(kbd("mpv_mute"))
    KotoriData.volumeMinus.setShortcut(kbd("my_down_binding_execute"))
    KotoriData.volumePlus.setShortcut(kbd("my_up_binding_execute"))
    KotoriData.showhideplaylistAction.setShortcut(kbd("key_t"))
    KotoriData.showhidectrlpanelAction.setShortcut(kbd("lowpanel_ch_1"))
    KotoriData.alwaysontopAction.setShortcut(kbd("alwaysontop"))
    KotoriData.streaminformationAction.setShortcut(kbd("open_stream_info"))
    KotoriData.showepgAction.setShortcut(kbd("show_tvguide_2"))
    KotoriData.forceupdateepgAction.setShortcut(kbd("force_update_epg"))
    KotoriData.sortAction.setShortcut(kbd("show_sort"))
    KotoriData.settingsAction.setShortcut(kbd("show_settings"))
    sec_keys_1 = [
        kbd("(lambda: mpv_seek(-10))"),
        kbd("(lambda: mpv_seek(10))"),
        kbd("(lambda: mpv_seek(-60))"),
        kbd("(lambda: mpv_seek(60))"),
        kbd("(lambda: mpv_seek(-600))"),
        kbd("(lambda: mpv_seek(600))"),
    ]
    sec_i_1 = -1
    for i_1 in KotoriData.secs:
        sec_i_1 += 1
        i_1.setShortcut(qkeysequence(sec_keys_1[sec_i_1]))


def init_menubar(data):
    # File

    KotoriData.playlists = qaction(_("&Playlists"), data)
    KotoriData.playlists.setShortcut(kbd("show_playlists"))
    KotoriData.playlists.triggered.connect(lambda: KotoriData.show_playlists())

    KotoriData.reloadPlaylist = qaction(_("&Update current playlist"), data)
    KotoriData.reloadPlaylist.setShortcut(kbd("reload_playlist"))
    KotoriData.reloadPlaylist.triggered.connect(lambda: KotoriData.reload_playlist())

    KotoriData.m3uEditor = qaction(_("&m3u Editor") + KotoriData.str_offset, data)
    KotoriData.m3uEditor.setShortcut(kbd("show_m3u_editor"))
    KotoriData.m3uEditor.triggered.connect(lambda: KotoriData.show_m3u_editor())

    KotoriData.exitAction = qaction(_("&Exit"), data)
    KotoriData.exitAction.setShortcut(kbd("app.quit"))
    KotoriData.exitAction.triggered.connect(lambda: KotoriData.app_quit())

    # Play

    KotoriData.playpause = qaction(_("&Play / Pause"), data)
    KotoriData.playpause.setShortcut(kbd("mpv_play"))
    KotoriData.playpause.triggered.connect(lambda: KotoriData.mpv_play())

    KotoriData.stop = qaction(_("&Stop"), data)
    KotoriData.stop.setShortcut(kbd("mpv_stop"))
    KotoriData.stop.triggered.connect(lambda: KotoriData.mpv_stop())

    KotoriData.secs = []
    sec_keys = [
        kbd("(lambda: mpv_seek(-10))"),
        kbd("(lambda: mpv_seek(10))"),
        kbd("(lambda: mpv_seek(-60))"),
        kbd("(lambda: mpv_seek(60))"),
        kbd("(lambda: mpv_seek(-600))"),
        kbd("(lambda: mpv_seek(600))"),
    ]
    sec_i18n = [
        lang1.ngettext("-%d second", "-%d seconds", 10) % 10,
        lang1.ngettext("+%d second", "+%d seconds", 10) % 10,
        lang1.ngettext("-%d minute", "-%d minutes", 1) % 1,
        lang1.ngettext("+%d minute", "+%d minutes", 1) % 1,
        lang1.ngettext("-%d minute", "-%d minutes", 10) % 10,
        lang1.ngettext("+%d minute", "+%d minutes", 10) % 10,
    ]
    sec_i = -1
    for i in ((10, "seconds", 10), (1, "minutes", 60), (10, "minutes", 600)):
        for k in ("-", "+"):
            sec_i += 1
            sec = qaction(sec_i18n[sec_i], data)
            sec.setShortcut(qkeysequence(sec_keys[sec_i]))
            sec.triggered.connect(
                partial(ast_mpv_seek, i[2] * -1 if k == "-" else i[2])
            )
            KotoriData.secs.append(sec)

    KotoriData.normalSpeed = qaction(_("&Normal speed"), data)
    KotoriData.normalSpeed.triggered.connect(partial(ast_mpv_speed, 1.00))
    KotoriData.normalSpeed.setShortcut(kbd("(lambda: set_playback_speed(1.00))"))

    KotoriData.spds = []

    for spd in (0.25, 0.5, 0.75, 1.25, 1.5, 1.75):
        spd_action = qaction(f"{spd}x", data)
        spd_action.triggered.connect(partial(ast_mpv_speed, spd))
        KotoriData.spds.append(spd_action)

    KotoriData.prevchannel = qaction(_("&Previous"), data)
    KotoriData.prevchannel.triggered.connect(lambda: KotoriData.prev_channel())
    KotoriData.prevchannel.setShortcut(kbd("prev_channel"))

    KotoriData.nextchannel = qaction(_("&Next"), data)
    KotoriData.nextchannel.triggered.connect(lambda: KotoriData.next_channel())
    KotoriData.nextchannel.setShortcut(kbd("next_channel"))

    # Video
    KotoriData.fullscreen = qaction(_("&Fullscreen"), data)
    KotoriData.fullscreen.triggered.connect(lambda: KotoriData.mpv_fullscreen())
    KotoriData.fullscreen.setShortcut(kbd("mpv_fullscreen"))

    KotoriData.compactmode = qaction(_("&Compact mode"), data)
    KotoriData.compactmode.triggered.connect(lambda: KotoriData.showhideeverything())
    KotoriData.compactmode.setShortcut(kbd("showhideeverything"))

    KotoriData.csforchannel = qaction(
        _("&Video settings") + KotoriData.str_offset, data
    )
    KotoriData.csforchannel.triggered.connect(
        lambda: KotoriData.main_channel_settings()
    )
    KotoriData.csforchannel.setShortcut(kbd("main_channel_settings"))

    KotoriData.screenshot = qaction(_("&Screenshot"), data)
    KotoriData.screenshot.triggered.connect(lambda: KotoriData.do_screenshot())
    KotoriData.screenshot.setShortcut(kbd("do_screenshot"))

    # Video filters
    KotoriData.vf_postproc = qaction(_("&Postprocessing"), data)
    KotoriData.vf_postproc.setCheckable(True)

    KotoriData.vf_deblock = qaction(_("&Deblock"), data)
    KotoriData.vf_deblock.setCheckable(True)

    KotoriData.vf_dering = qaction(_("De&ring"), data)
    KotoriData.vf_dering.setCheckable(True)

    KotoriData.vf_debanding = qaction(
        _("Debanding (&gradfun)") + KotoriData.str_offset, data
    )
    KotoriData.vf_debanding.setCheckable(True)

    KotoriData.vf_noise = qaction(_("Add n&oise"), data)
    KotoriData.vf_noise.setCheckable(True)

    KotoriData.vf_black = qaction(_("Add &black borders"), data)
    KotoriData.vf_black.setCheckable(True)

    KotoriData.vf_softscaling = qaction(_("Soft&ware scaling"), data)
    KotoriData.vf_softscaling.setCheckable(True)

    KotoriData.vf_phase = qaction(_("&Autodetect phase"), data)
    KotoriData.vf_phase.setCheckable(True)

    # Audio

    KotoriData.muteAction = qaction(_("&Mute audio"), data)
    KotoriData.muteAction.triggered.connect(lambda: KotoriData.mpv_mute())
    KotoriData.muteAction.setShortcut(kbd("mpv_mute"))

    KotoriData.volumeMinus = qaction(_("V&olume -"), data)
    KotoriData.volumeMinus.triggered.connect(
        lambda: KotoriData.my_down_binding_execute()
    )
    KotoriData.volumeMinus.setShortcut(kbd("my_down_binding_execute"))

    KotoriData.volumePlus = qaction(_("Vo&lume +"), data)
    KotoriData.volumePlus.triggered.connect(lambda: KotoriData.my_up_binding_execute())
    KotoriData.volumePlus.setShortcut(kbd("my_up_binding_execute"))

    # Audio filters

    KotoriData.af_extrastereo = qaction(_("&Extrastereo"), data)
    KotoriData.af_extrastereo.setCheckable(True)

    KotoriData.af_karaoke = qaction(_("&Karaoke"), data)
    KotoriData.af_karaoke.setCheckable(True)

    KotoriData.af_earvax = qaction(
        _("&Headphone optimization") + KotoriData.str_offset, data
    )
    KotoriData.af_earvax.setCheckable(True)

    KotoriData.af_volnorm = qaction(_("Volume &normalization"), data)
    KotoriData.af_volnorm.setCheckable(True)

    # View

    KotoriData.showhideplaylistAction = qaction(_("Show/hide playlist"), data)
    KotoriData.showhideplaylistAction.triggered.connect(
        lambda: KotoriData.showhideplaylist()
    )
    KotoriData.showhideplaylistAction.setShortcut(kbd("key_t"))

    KotoriData.showhidectrlpanelAction = qaction(_("Show/hide controls panel"), data)
    KotoriData.showhidectrlpanelAction.triggered.connect(
        lambda: KotoriData.lowpanel_ch_1()
    )
    KotoriData.showhidectrlpanelAction.setShortcut(kbd("lowpanel_ch_1"))

    KotoriData.alwaysontopAction = qaction(_("Window always on top"), data)
    KotoriData.alwaysontopAction.triggered.connect(alwaysontop_action)
    KotoriData.alwaysontopAction.setCheckable(True)
    KotoriData.alwaysontopAction.setShortcut(kbd("alwaysontop"))
    if qt_library == "PyQt6" or os.name == "nt":
        KotoriData.alwaysontopAction.setVisible(False)

    KotoriData.streaminformationAction = qaction(_("Stream Information"), data)
    KotoriData.streaminformationAction.triggered.connect(
        lambda: KotoriData.open_stream_info()
    )
    KotoriData.streaminformationAction.setShortcut(kbd("open_stream_info"))

    KotoriData.showepgAction = qaction(_("TV guide"), data)
    KotoriData.showepgAction.triggered.connect(lambda: KotoriData.show_tvguide_2())
    KotoriData.showepgAction.setShortcut(kbd("show_tvguide_2"))

    KotoriData.forceupdateepgAction = qaction(_("&Update TV guide"), data)
    KotoriData.forceupdateepgAction.triggered.connect(
        lambda: KotoriData.force_update_epg()
    )
    KotoriData.forceupdateepgAction.setShortcut(kbd("force_update_epg"))

    # Options

    KotoriData.sortAction = qaction(_("&Channel sort"), data)
    KotoriData.sortAction.triggered.connect(lambda: KotoriData.show_sort())
    KotoriData.sortAction.setShortcut(kbd("show_sort"))

    KotoriData.shortcutsAction = qaction("&" + _("Shortcuts"), data)
    KotoriData.shortcutsAction.triggered.connect(lambda: KotoriData.show_shortcuts())

    KotoriData.settingsAction = qaction(_("&Settings"), data)
    KotoriData.settingsAction.triggered.connect(lambda: KotoriData.show_settings())
    KotoriData.settingsAction.setShortcut(kbd("show_settings"))

    # Help

    KotoriData.aboutAction = qaction(_("&About kotori"), data)
    KotoriData.aboutAction.triggered.connect(lambda: KotoriData.show_help())

    # Empty (track list)
    KotoriData.empty_action = qaction("<{}>".format(_("empty")), data)
    KotoriData.empty_action.setEnabled(False)
    KotoriData.empty_action1 = qaction("<{}>".format(_("empty")), data)
    KotoriData.empty_action1.setEnabled(False)
    KotoriData.empty_action2 = qaction("<{}>".format(_("empty")), data)
    KotoriData.empty_action2.setEnabled(False)

    # Filters mapping
    KotoriData.filter_mapping = {
        "vf::::::::lavfi=[pp]": KotoriData.vf_postproc,
        "vf::::::::lavfi=[pp=vb/hb]": KotoriData.vf_deblock,
        "vf::::::::lavfi=[pp=dr]": KotoriData.vf_dering,
        "vf::::::::lavfi=[gradfun]": KotoriData.vf_debanding,
        "vf::::::::lavfi=[noise=alls=9:allf=t]": KotoriData.vf_noise,
        "vf::::::::__AST_VFBLACK__": KotoriData.vf_black,
        "vf::::::::__AST_SOFTSCALING__": KotoriData.vf_softscaling,
        "vf::::::::lavfi=[phase=A]": KotoriData.vf_phase,
        "af::::::::lavfi=[extrastereo]": KotoriData.af_extrastereo,
        "af::::::::lavfi=[stereotools=mlev=0.015625]": KotoriData.af_karaoke,
        "af::::::::lavfi=[earwax]": KotoriData.af_earvax,
        "af::::::::lavfi=[acompressor]": KotoriData.af_volnorm,
    }
    for vf_filter in KotoriData.filter_mapping:
        KotoriData.filter_mapping[vf_filter].triggered.connect(
            partial(apply_vf_filter, vf_filter, KotoriData.filter_mapping[vf_filter])
        )
    return KotoriData.alwaysontopAction


def populate_menubar(
    i, menubar, data, track_list=None, playing_chan=None, get_keybind=None
):
    # logger.info("populate_menubar called")
    # File

    if get_keybind:
        KotoriData.get_keybind = get_keybind

    aot_action = None

    if not KotoriData.menubar_ready:
        aot_action = init_menubar(data)
        KotoriData.menubar_ready = True

    file_menu = menubar.addMenu(_("&File"))
    file_menu.addAction(KotoriData.playlists)
    file_menu.addSeparator()
    file_menu.addAction(KotoriData.reloadPlaylist)
    file_menu.addAction(KotoriData.forceupdateepgAction)
    file_menu.addSeparator()
    file_menu.addAction(KotoriData.m3uEditor)
    file_menu.addAction(KotoriData.exitAction)

    # Play

    play_menu = menubar.addMenu(_("&Play"))
    play_menu.addAction(KotoriData.playpause)
    play_menu.addAction(KotoriData.stop)
    play_menu.addSeparator()
    for sec in KotoriData.secs:
        play_menu.addAction(sec)
    play_menu.addSeparator()

    speed_menu = play_menu.addMenu(_("Speed"))
    speed_menu.addAction(KotoriData.normalSpeed)
    for spd_action1 in KotoriData.spds:
        speed_menu.addAction(spd_action1)
    play_menu.addSeparator()
    play_menu.addAction(KotoriData.prevchannel)
    play_menu.addAction(KotoriData.nextchannel)

    # Video

    video_menu = menubar.addMenu(_("&Video"))
    video_track_menu = video_menu.addMenu(_("&Track"))
    video_track_menu.clear()
    video_menu.addAction(KotoriData.fullscreen)
    video_menu.addAction(KotoriData.compactmode)
    video_menu.addAction(KotoriData.csforchannel)
    KotoriData.video_menu_filters = video_menu.addMenu(_("F&ilters"))
    KotoriData.video_menu_filters.addAction(KotoriData.vf_postproc)
    KotoriData.video_menu_filters.addAction(KotoriData.vf_deblock)
    KotoriData.video_menu_filters.addAction(KotoriData.vf_dering)
    KotoriData.video_menu_filters.addAction(KotoriData.vf_debanding)
    KotoriData.video_menu_filters.addAction(KotoriData.vf_noise)
    KotoriData.video_menu_filters.addAction(KotoriData.vf_black)
    KotoriData.video_menu_filters.addAction(KotoriData.vf_softscaling)
    KotoriData.video_menu_filters.addAction(KotoriData.vf_phase)
    video_menu.addSeparator()
    video_menu.addAction(KotoriData.screenshot)

    # Audio

    audio_menu = menubar.addMenu(_("&Audio"))
    audio_track_menu = audio_menu.addMenu(_("&Track"))
    audio_track_menu.clear()
    KotoriData.audio_menu_filters = audio_menu.addMenu(_("F&ilters"))
    KotoriData.audio_menu_filters.addAction(KotoriData.af_extrastereo)
    KotoriData.audio_menu_filters.addAction(KotoriData.af_karaoke)
    KotoriData.audio_menu_filters.addAction(KotoriData.af_earvax)
    KotoriData.audio_menu_filters.addAction(KotoriData.af_volnorm)
    audio_menu.addSeparator()
    audio_menu.addAction(KotoriData.muteAction)
    audio_menu.addSeparator()
    audio_menu.addAction(KotoriData.volumeMinus)
    audio_menu.addAction(KotoriData.volumePlus)

    # Subtitles
    subtitles_menu = menubar.addMenu(_("&Subtitles"))
    sub_track_menu = subtitles_menu.addMenu(_("&Track"))
    sub_track_menu.clear()

    # View

    view_menu = menubar.addMenu(_("Vie&w"))
    view_menu.addAction(KotoriData.showhideplaylistAction)
    view_menu.addAction(KotoriData.showhidectrlpanelAction)
    view_menu.addAction(KotoriData.alwaysontopAction)
    view_menu.addAction(KotoriData.streaminformationAction)
    view_menu.addAction(KotoriData.showepgAction)

    # Options

    options_menu = menubar.addMenu(_("&Options"))
    options_menu.addAction(KotoriData.sortAction)
    options_menu.addSeparator()
    options_menu.addAction(KotoriData.shortcutsAction)
    options_menu.addAction(KotoriData.settingsAction)

    # Help

    help_menu = menubar.addMenu(_("&Help"))
    help_menu.addAction(KotoriData.aboutAction)

    KotoriData.menubars[i] = [video_track_menu, audio_track_menu, sub_track_menu]

    return aot_action


# Preventing memory leak
def clear_menu(menu):
    for mb_action in menu.actions():
        if mb_action.isSeparator():
            mb_action.deleteLater()
        # elif mb_action.menu():
        #    clear_menu(mb_action.menu())
        #    mb_action.menu().deleteLater()
        else:
            if mb_action.text() != "<{}>".format(_("empty")):
                mb_action.deleteLater()


def recursive_filter_setstate(state):
    for act in KotoriData.video_menu_filters.actions():
        if not act.isSeparator():  # or act.menu():
            act.setEnabled(state)
    for act1 in KotoriData.audio_menu_filters.actions():
        if not act1.isSeparator():  # or act1.menu():
            act1.setEnabled(state)


def get_first_run():
    return KotoriData.first_run


def update_menubar(track_list, playing_chan, m3u, aot_file):
    # Filters enable / disable
    if playing_chan:
        recursive_filter_setstate(True)
        # print(playing_chan + '::::::::::::::' + m3u)
        if not KotoriData.first_run:
            KotoriData.first_run = True
            logger.info("KotoriData.first_run")
            try:
                vf_filters_read = read_option("vf_filters")
                if vf_filters_read:
                    for dat in vf_filters_read:
                        if dat in KotoriData.filter_mapping:
                            KotoriData.filter_mapping[dat].setChecked(True)
                            apply_vf_filter(dat, KotoriData.filter_mapping[dat])
            except Exception:
                pass
    else:
        recursive_filter_setstate(False)
    # Always on top
    if not KotoriData.first_run1:
        KotoriData.first_run1 = True
        try:
            if os.path.isfile(aot_file):
                file_2 = open(aot_file, "r", encoding="utf-8")
                file_2_out = file_2.read()
                file_2.close()
                aot_state = json.loads(file_2_out)["alwaysontop"]
                if aot_state:
                    KotoriData.alwaysontopAction.setChecked(True)
                else:
                    KotoriData.alwaysontopAction.setChecked(False)
        except Exception:
            pass
    # Track list
    for i in KotoriData.menubars:
        clear_menu(KotoriData.menubars[i][0])
        clear_menu(KotoriData.menubars[i][1])
        clear_menu(KotoriData.menubars[i][2])
        KotoriData.menubars[i][0].clear()
        KotoriData.menubars[i][1].clear()
        KotoriData.menubars[i][2].clear()
        if track_list and playing_chan:
            if not [x for x in track_list if x["type"] == "video"]:
                KotoriData.menubars[i][0].addAction(KotoriData.empty_action)
            if not [x for x in track_list if x["type"] == "audio"]:
                KotoriData.menubars[i][1].addAction(KotoriData.empty_action1)
            # Subtitles off
            sub_off_action = qaction(_("None"), KotoriData.data)
            if KotoriData.player.sid == "no" or not KotoriData.player.sid:
                sub_off_action.setIcon(KotoriData.circle_icon)
            sub_off_action.triggered.connect(partial(kotori_trackset, "no", "sid"))
            KotoriData.menubars[i][2].addAction(sub_off_action)
            for track in track_list:
                if track["type"] == "video":
                    trk = qaction(str(track["id"]), KotoriData.data)
                    if track["id"] == KotoriData.player.vid:
                        trk.setIcon(KotoriData.circle_icon)
                    trk.triggered.connect(partial(kotori_trackset, track["id"], "vid"))
                    KotoriData.menubars[i][0].addAction(trk)
                if track["type"] == "audio":
                    if "lang" in track:
                        trk1 = qaction(
                            "{} ({})".format(track["id"], track["lang"]),
                            KotoriData.data,
                        )
                    else:
                        trk1 = qaction(str(track["id"]), KotoriData.data)
                    if track["id"] == KotoriData.player.aid:
                        trk1.setIcon(KotoriData.circle_icon)
                    trk1.triggered.connect(partial(kotori_trackset, track["id"], "aid"))
                    KotoriData.menubars[i][1].addAction(trk1)
                if track["type"] == "sub":
                    if "lang" in track:
                        trk2 = qaction(
                            "{} ({})".format(track["id"], track["lang"]),
                            KotoriData.data,
                        )
                    else:
                        trk2 = qaction(str(track["id"]), KotoriData.data)
                    if track["id"] == KotoriData.player.sid:
                        trk2.setIcon(KotoriData.circle_icon)
                    trk2.triggered.connect(partial(kotori_trackset, track["id"], "sid"))
                    KotoriData.menubars[i][2].addAction(trk2)
        else:
            KotoriData.menubars[i][0].addAction(KotoriData.empty_action)
            KotoriData.menubars[i][1].addAction(KotoriData.empty_action1)
            KotoriData.menubars[i][2].addAction(KotoriData.empty_action2)


def init_kotori_menubar(data, app, menubar):
    KotoriData.data = data


def init_menubar_player(
    player,
    mpv_play,
    mpv_stop,
    prev_channel,
    next_channel,
    mpv_fullscreen,
    showhideeverything,
    main_channel_settings,
    show_settings,
    show_help,
    do_screenshot,
    mpv_mute,
    showhideplaylist,
    lowpanel_ch_1,
    open_stream_info,
    app_quit,
    redraw_menubar,
    circle_icon,
    my_up_binding_execute,
    my_down_binding_execute,
    show_m3u_editor,
    show_playlists,
    show_sort,
    show_exception,
    get_curwindow_pos,
    force_update_epg,
    get_keybind,
    show_tvguide_2,
    enable_always_on_top,
    disable_always_on_top,
    reload_playlist,
    show_shortcuts,
    aot_file,
    kotori_track_set,
):
    for func in locals().items():
        setattr(KotoriData, func[0], func[1])

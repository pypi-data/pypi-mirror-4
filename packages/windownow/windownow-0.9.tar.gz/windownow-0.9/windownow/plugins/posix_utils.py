#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import tempfile

import windownow.plugins as plugins
modules = ['gtk', 'keybinder', 'wnck', 'wx', 'gtk.keysyms']
os_modules = ['python-gtk2', 'python-keybinder', 'python-wnck', 'python-wxgtk2.8']
for idx in xrange(len(modules)):
    module = modules[idx]
    mod_name = module.rsplit('.', 1)[-1]
    locals()[mod_name] = plugins.verbose_import(module, os_modules[idx],
        from_name='')

import windownow.common as common

logger = logging.getLogger(__name__)
DEBUG = 1

__author__ = 'xliiv <tymoteusz.jankowski@gmail.com>'

TIMESTAMP = 0
temp_icon = os.path.join(tempfile.gettempdir(), 'windowNow')

gtk_keys_names = {}
for key in dir(keysyms):
    value = getattr(keysyms, key)
    if type(key) == type('') and type(value) == type(3):
        gtk_keys_names[value] = key

gtk_mod_format = lambda key_name: '<%s>' % key_name


class UnknownKey(Exception):
    pass

gtk_keys_exceptions = {
    17: '<Ctrl>',
    18: '<Alt>',
    65505: '<Shift>',
    65506: '<Shift>',
    65507: '<Ctrl>',
    65508: '<Ctrl>',
    65513: '<Alt>',
#    '.': 'period',
#    "BACK":,
#    "TAB":,
#    "RETURN":,
#    "ESCAPE":,
#    "SPACE":,
#    "DELETE":,
#    "START":,
#    "LBUTTON":,
#    "RBUTTON":,
#    "CANCEL":,
#    "MBUTTON":,
#    "CLEAR":,
#    "MENU":,
#    "PAUSE":,
#    "CAPITAL":,
#    "END":,
#    "HOME":,
#    "LEFT":,
#    "UP":,
#    "RIGHT":,
#    "DOWN":,
#    "SELECT":,
#    "PRINT":,
#    "EXECUTE":,
#    "SNAPSHOT":,
#    "INSERT":,
#    "HELP":,
#    "NUMPAD0":,
#    "NUMPAD1":,
#    "NUMPAD2":,
#    "NUMPAD3":,
#    "NUMPAD4":,
#    "NUMPAD5":,
#    "NUMPAD6":,
#    "NUMPAD7":,
#    "NUMPAD8":,
#    "NUMPAD9":,
#    "MULTIPLY":,
#    "ADD":,
#    "SEPARATOR":,
#    "SUBTRACT":,
#    "DECIMAL":,
#    "DIVIDE":,
#    "F1":,
#    "F2":,
#    "F3":,
#    "F4":,
#    "F5":,
#    "F6":,
#    "F7":,
#    "F8":,
#    "F9":,
#    "F10":,
#    "F11":,
#    "F12":,
#    "F13":,
#    "F14":,
#    "F15":,
#    "F16":,
#    "F17":,
#    "F18":,
#    "F19":,
#    "F20":,
#    "F21":,
#    "F22":,
#    "F23":,
#    "F24":,
#    "NUMLOCK":,
#    "SCROLL":,
#    "PAGEUP": 'Page_Down',
#    "PAGEDOWN": 'Page_Up',
#    "NUMPAD_SPACE":,
#    "NUMPAD_TAB":,
#    "NUMPAD_ENTER":,
#    "NUMPAD_F1":,
#    "NUMPAD_F2":,
#    "NUMPAD_F3":,
#    "NUMPAD_F4":,
#    "NUMPAD_HOME":,
#    "NUMPAD_LEFT":,
#    "NUMPAD_UP":,
#    "NUMPAD_RIGHT":,
#    "NUMPAD_DOWN":,
#    "NUMPAD_PAGEUP":,
#    "NUMPAD_PAGEDOWN":,
#    "NUMPAD_END":,
#    "NUMPAD_BEGIN":,
#    "NUMPAD_INSERT":,
#    "NUMPAD_DELETE":,
#    "NUMPAD_EQUAL":,
#    "NUMPAD_MULTIPLY":,
#    "NUMPAD_ADD":,
#    "NUMPAD_SEPARATOR":,
#    "NUMPAD_SUBTRACT":,
#    "NUMPAD_DECIMAL":,
#    "NUMPAD_DIVIDE":,
#    "WINDOWS_LEFT":,
#    "WINDOWS_RIGHT":,
#    "WINDOWS_MENU":,
#    "COMMAND":,
#    "SPECIAL1":,
#    "SPECIAL2":,
#    "SPECIAL3":,
#    "SPECIAL4":,
#    "SPECIAL5":,
#    "SPECIAL6":,
#    "SPECIAL7":,
#    "SPECIAL8":,
#    "SPECIAL9":,
#    "SPECIAL10":,
#    "SPECIAL11":,
#    "SPECIAL12":,
#    "SPECIAL13":,
#    "SPECIAL14":,
#    "SPECIAL15":,
#    "SPECIAL16":,
#    "SPECIAL17":,
#    "SPECIAL18":,
#    "SPECIAL19":,
#    "SPECIAL2":,
}

def show_opened_wins():
    wins_data = get_window_data(mask='')
    logger.debug('desktop wins')
    for win_id, null, null, title in wins_data:
        logger.debug('{0:8} (Ox{1:8X}): "{2}")'.format(win_id, win_id,
            title))
    logger.debug('END desktop wins')


def win_id_by_title(title):
    """
    Get window obj by title
    """
    logger.debug('find win by title: "{0}"'.format(title))

    screen = wnck.screen_get_default()
    while gtk.events_pending():
        gtk.main_iteration(False)

    show_opened_wins()
    for win in screen.get_windows():
        if win.get_name() == title:
            win_id = win.get_xid()
            logger.debug('got win: title = "{0}", {1} (Ox{2:X})'.format(
                title, win_id, win_id))
            break
    else:
        win_id = None

    return win_id


def conv_GdkPixbuf2wxIcon(icon):
    """
    temporary function until got know how to convert
    GdkPixbuf to wxIcon|wxBitmap
    """
    #icon_pixels = icon.get_pixels()
    img_file = os.path.join(temp_icon)
    icon.save(img_file, 'png')
    icon_pixels = wx.Bitmap(img_file, wx.BITMAP_TYPE_PNG)
    return icon_pixels


def get_window_data(mask=''):
    """
    Returns: list of tuples
    [(win_id, icon_pixels, app_name, window_title_text), ..]
    [(1234567, '??', 'rhythmbox', 'shakira - loca'), ..]
    """
    screen = wnck.screen_get_default()

    while gtk.events_pending():
        gtk.main_iteration(False)

    wins_data = []
    for win in screen.get_windows():
        win_id = win.get_xid()
        icon = win.get_icon()
        icon_pixels = conv_GdkPixbuf2wxIcon(icon)
        #icon_pixels = 'icon_pixels' #mock
        app_name = win.get_application().get_name()
        window_title = win.get_name()
        if not (common.contains(app_name, mask) or
                common.contains(window_title, mask)):
            continue
        wins_data.append([win_id, icon_pixels, app_name, window_title])

    return wins_data


def raise_window(win_id):
    # : on linux window sometimes apprears as a flash
    # and repeated hide-show action make it top
    show_opened_wins()

    import time
    TIMESTAMP = long(time.time()) #, this doesn't raise window .o.
    win = wnck.window_get(win_id)
    logger.debug('raising, win: title, id = "{0}", {1}'.format(win.get_name(),
        win_id))
    active_workspace = wnck.screen_get_default().get_active_workspace()
    if not win.is_on_workspace(active_workspace):
        # change workspace
        logger.debug('workaspace changed')
        workspace = win.get_workspace()
        workspace.activate(TIMESTAMP)
    if win.is_minimized():
        logger.debug('uniminimized')
        win.unminimize(TIMESTAMP)

    if DEBUG:
        attrs = [
            'is_above', 'is_active', 'is_below', 'is_fullscreen',
            'is_in_viewport', 'is_maximized', 'is_maximized_horizontally',
            'is_maximized_vertically', 'is_minimized',
            'is_most_recently_activated', 'is_on_workspace', 'is_pinned',
            'is_shaded', 'is_skip_pager', 'is_skip_tasklist', 'is_sticky',
            'is_visible_on_workspace',
        ]
        for a in attrs:
            break
            state = getattr(win, a)
            try:
                logger.debug('attr {0}: {1}'.format(a, state()))
            except:
                try:
                    logger.debug('attr {0}: {1}'.format(a, state(win)))
                except:
                    workspace = win.get_workspace()
                    logger.debug('attr {0}: {1}'.format(a, state(workspace)))

    activate_windows(win)


def activate_windows(win):
    """
    {win}: is a win obj to activate like: win = wnck.window_get(win_id)
    """
    win.activate(TIMESTAMP)

#    import subprocess
#    subprocess.call('wmctrl -l'.format(win_id), shell=True)
#    cmd = 'wmctrl -a {0} -i'.format(win_id)
#    logger.debug('activate cmd: {0}'.format(cmd))
#    subprocess.call(cmd, shell=True)
#    logger.debug('activated, win: title, id = "{0}", {1}'.format(
#        win.get_name(), win.get_xid()))
#

def register_hotkey(hotkey, toggle_shown_func):
    """
    Register OSwide hotkey

    $hotkey: is like output from f. codes2hotkey()
    $toggle_shown_func: self-explaining.
    """
    import re
    hotkey = re.sub(r'\s\+\s', '', hotkey)
    #unbind(hotkey)
    logger.debug('hotkey registering: {0}'.format(hotkey))
    keybinder.bind(hotkey, toggle_shown_func)


def code2char_name(code, shift_down=False):
    """
    Change raw code to user-friendly name.
    E.g:
    65 to 'A'
    65507 '<ctrl>'
    """
    if ord('0') <= code <= ord('9'):
        # gtk.keysyms has defined numers, but its format is '_\d+',
        # thus gkt_keys_names can't be used and need something extra
        return chr(code)
    for dikt in [gtk_keys_exceptions, gtk_keys_names]:
        if code in dikt:
            return dikt.get(code)
    return u'Unknown'


def codes2hotkey(keys_codes):
    """
    Change list of key codes to user-friendly hotkey.
    E.g:
    return: <alt><ctrl>period
    """
    keys_names = []
    for code in keys_codes:
        keys_names.append(code2name(code))
    return keys_names


def valid_hotkey(modifiers, key, data=None):
    """
    Check if passed hotkey compound of $key and $modifiers is valid.
    """
    mods = [key]
    mods.extend([gtk_mod_format(m) for m in modifiers])
    hotkey = ''.join(mods)
    dummy_func = lambda x: x
    try:
        keybinder.bind(hotkey, dummy_func)
        logger.debug('binded succesfully: {0}, {1}'.format(mods, ''))
    except KeyError as e:
        logger.error(e)
        valid, msg = False, 'Already registered'
    else:
        unbind(hotkey)
        valid, msg = True, 'Correct hotkey.'
    return valid, msg

def unbind(hotkey):
    logger.debug('unbinding: {0}'.format(hotkey))
    try:
        keybinder.unbind(hotkey)
    except KeyError as e:
        logging.error('hotkey is not set: {0} ({1})'.format(hotkey, e))


if __name__ == '__main__':
    os.system('python windowNow.py')

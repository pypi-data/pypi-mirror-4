#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import win32api
import win32con
import win32gui
import win32process
import wx

import windowNow

__author__ = 'xliiv <tymoteusz.jankowski@gmail.com>'

# user-friendly key to windows-friendly key map
keyname2code = {
    'lbutton': 0x01, #Left mouse button
    'rbutton': 0x02, #Right mouse button
    'cancel': 0x03, #Control-break processing
    'mbutton': 0x04, #Middle mouse button (three-button mouse)
    'xbutton1': 0x05, #X1 mouse button
    'xbutton2': 0x06, #X2 mouse button
    'back': 0x08, #BACKSPACE key
    'tab': 0x09, #TAB key
    'clear': 0x0C, #CLEAR key
    'return': 0x0D, #ENTER key
    'shift': 0x10, #SHIFT key
    'control': 0x11, #CTRL key
    'menu': 0x12, #ALT key
    'pause': 0x13, #PAUSE key
    'capital': 0x14, #CAPS LOCK key
    'kana': 0x15, #IME Kana mode
    'hanguel': 0x15, #IME Hanguel mode (maintained for compatibility; use HANGUL)
    'hangul': 0x15, #IME Hangul mode
    'junja': 0x17, #IME Junja mode
    'final': 0x18, #IME final mode
    'hanja': 0x19, #IME Hanja mode
    'kanji': 0x19, #IME Kanji mode
    'escape': 0x1B, #ESC key
    'convert': 0x1C, #IME convert
    'nonconvert': 0x1D, #IME nonconvert
    'accept': 0x1E, #IME accept
    'modechange': 0x1F, #IME mode change request
    'space': 0x20, #SPACEBAR
    'prior': 0x21, #PAGE UP key
    'next': 0x22, #PAGE DOWN key
    'end': 0x23, #END key
    'home': 0x24, #HOME key
    'left': 0x25, #LEFT ARROW key
    'up': 0x26, #UP ARROW key
    'right': 0x27, #RIGHT ARROW key
    'down': 0x28, #DOWN ARROW key
    'select': 0x29, #SELECT key
    'print': 0x2A, #PRINT key
    'execute': 0x2B, #EXECUTE key
    'snapshot': 0x2C, #PRINT SCREEN key
    'insert': 0x2D, #INS key
    'delete': 0x2E, #DEL key
    'help': 0x2F, #HELP key
    '0': 0x30, # 0 key
    '1': 0x31, # 1 key
    '2': 0x32, # 2 key
    '3': 0x33, # 3 key
    '4': 0x34, # 4 key
    '5': 0x35, # 5 key
    '6': 0x36, # 6 key
    '7': 0x37, # 7 key
    '8': 0x38, # 8 key
    '9': 0x39, # 9 key
    'A': 0x41, # A key
    'B': 0x42, # B key
    'C': 0x43, # C key
    'D': 0x44, # D key
    'E': 0x45, # E key
    'F': 0x46, # F key
    'G': 0x47, # G key
    'H': 0x48, # H key
    'I': 0x49, # I key
    'J': 0x4a, # J key
    'K': 0x4b, # K key
    'L': 0x4c, # L key
    'M': 0x4d, # M key
    'N': 0x4e, # N key
    'O': 0x4f, # O key
    'P': 0x50, # P key
    'Q': 0x51, # Q key
    'R': 0x52, # R key
    'S': 0x53, # S key
    'T': 0x54, # T key
    'U': 0x55, # U key
    'V': 0x56, # V key
    'W': 0x57, # W key
    'X': 0x58, # X key
    'Y': 0x59, # Y key
    'Z': 0x5a, # Z key
    'lwin': 0x5B, #Left Windows key (Natural keyboard) 
    'rwin': 0x5C, #Right Windows key (Natural keyboard)
    'apps': 0x5D, #Applications key (Natural keyboard)
    'sleep': 0x5F, #Computer Sleep key
    'numpad0': 0x60, #Numeric keypad 0 key
    'numpad1': 0x61, #Numeric keypad 1 key
    'numpad2': 0x62, #Numeric keypad 2 key
    'numpad3': 0x63, #Numeric keypad 3 key
    'numpad4': 0x64, #Numeric keypad 4 key
    'numpad5': 0x65, #Numeric keypad 5 key
    'numpad6': 0x66, #Numeric keypad 6 key
    'numpad7': 0x67, #Numeric keypad 7 key
    'numpad8': 0x68, #Numeric keypad 8 key
    'numpad9': 0x69, #Numeric keypad 9 key
    'multiply': 0x6A, #Multiply key
    'add': 0x6B, #Add key
    'separator': 0x6C, #Separator key
    'subtract': 0x6D, #Subtract key
    'decimal': 0x6E, #Decimal key
    'divide': 0x6F, #Divide key
    'f1': 0x70, #F1 key
    'f2': 0x71, #F2 key
    'f3': 0x72, #F3 key
    'f4': 0x73, #F4 key
    'f5': 0x74, #F5 key
    'f6': 0x75, #F6 key
    'f7': 0x76, #F7 key
    'f8': 0x77, #F8 key
    'f9': 0x78, #F9 key
    'f10': 0x79, #F10 key
    'f11': 0x7A, #F11 key
    'f12': 0x7B, #F12 key
    'f13': 0x7C, #F13 key
    'f14': 0x7D, #F14 key
    'f15': 0x7E, #F15 key
    'f16': 0x7F, #F16 key
    'f17': 0x80, #F17 key
    'f18': 0x81, #F18 key
    'f19': 0x82, #F19 key
    'f20': 0x83, #F20 key
    'f21': 0x84, #F21 key
    'f22': 0x85, #F22 key
    'f23': 0x86, #F23 key
    'f24': 0x87, #F24 key
    'numlock': 0x90, #NUM LOCK key
    'scroll': 0x91, #SCROLL LOCK key
    'lshift': '0xa0', #Left SHIFT key
    'rshift': 0xA1, #Right SHIFT key
    'lcontrol': 0xA2, #Left CONTROL key
    'rcontrol': 0xA3, #Right CONTROL key
    'lmenu': 0xA4, #Left MENU key
    'rmenu': 0xA5, #Right MENU key
    'browser_back': 0xA6, #Browser Back key
    'browser_forward': 0xA7, #Browser Forward key
    'browser_refresh': 0xA8, #Browser Refresh key
    'browser_stop': 0xA9, #Browser Stop key
    'browser_search': 0xAA, #Browser Search key 
    'browser_favorites': 0xAB, #Browser Favorites key
    'browser_home': 0xAC, #Browser Start and Home key
    'volume_mute': 0xAD, #Volume Mute key
    'volume_down': 0xAE, #Volume Down key
    'volume_up': 0xAF, #Volume Up key
    'media_next_track': 0xB0, #Next Track key
    'media_prev_track': 0xB1, #Previous Track key
    'media_stop': 0xB2, #Stop Media key
    'media_play_pause': 0xB3, #Play/Pause Media key
    'launch_mail': 0xB4, #Start Mail key
    'launch_media_select': 0xB5, #Select Media key
    'launch_app1': 0xB6, #Start Application 1 key
    'launch_app2': 0xB7, #Start Application 2 key
    'oem_1': 0xBA, #Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the ';:' key 
    'oem_plus': 0xBB, #For any country/region, the '+' key
    'oem_comma': 0xBC, #For any country/region, the ',' key
    'oem_minus': 0xBD, #For any country/region, the '-' key
    'oem_period': 0xBE, #For any country/region, the '.' key
    'oem_2': 0xBF, #Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the '/?' key 
    'oem_3': 0xC0, #Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the '`~' key 
    'oem_4': 0xDB, #Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the '[{' key
    'oem_5': 0xDC, #Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the '\|' key
    'oem_6': 0xDD, #Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the ']}' key
    'oem_7': 0xDE, #Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the 'single-quote/double-quote' key
    'oem_8': 0xDF, #Used for miscellaneous characters; it can vary by keyboard.
    'oem_102': 0xE2, #Either the angle bracket key or the backslash key on the RT 102-key keyboard
    'processkey': 0xE5, #IME PROCESS key
    'attn': 0xF6, #Attn key
    'crsel': 0xF7, #CrSel key
    'exsel': 0xF8, #ExSel key
    'ereof': 0xF9, #Erase EOF key
    'play': 0xFA, #Play key
    'zoom': 0xFB, #Zoom key
    'pa1': 0xFD, #PA1 key
    'oem_clear': 0xFE, #Clear key
    #'control': win32con.MOD_CONTROL,
    #'alt': win32con.MOD_ALT,
}

code2keyname = dict([(v, k) for k, v in keyname2code.items()])

def get_app_name(exe_path):
    """
    Returns app_name from path to .exe
    """

    return os.path.splitext(os.path.basename(exe_path))[0]

def get_exe_path(hwnd):
    """
    Get exe path for window handler
    """
    pid = win32process.GetWindowThreadProcessId(hwnd)
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid[1])
    return win32process.GetModuleFileNameEx(handle, 0)

def get_windows_hwnds():
    """
    Get list of handlers for visible windows
    """
    def collect_hwnds(hwnd, memory):
        if win32gui.IsWindowVisible(hwnd):
            exe_path = get_exe_path(hwnd)
            memory.append(hwnd)
    memory = []
    win32gui.EnumWindows(collect_hwnds, memory)
    return memory

def get_window_title(hwnd):
    """
    Get window title
    return: string 'interia.pl : Opera'
    """
    return win32gui.GetWindowText(hwnd)

def get_window_data(mask):
    """
    win_id, icon, app_name, app_title
    """
    icons_titles = []
    hwnds = get_windows_hwnds()
    for hwnd in hwnds:
        window_title = get_window_title(hwnd)
        app_name = get_app_name(get_exe_path(hwnd))

        if not (windowNow.contains(app_name, mask) or
                windowNow.contains(window_title, mask)):
            continue

        icon_path = get_exe_path(hwnd)
        icon = get_icon_somehow(icon_path)
        icons_titles.append([hwnd, icon, app_name, window_title])
    return icons_titles

def get_icon_somehow(icon_path):
    """
    ugly and tmp, until i not read more about images
    """
    # if exe has no icon then dialog appears..
    # redirect log message then no dialog
    log = wx.LogNull()
    icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
    bmp = wx.EmptyBitmap(32, 32)
    if icon.IsOk():
        bmp.CopyFromIcon(icon)
    return bmp

def raise_window(hwnd):
    """
    Raise window by hwnd
    """
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

def code2char_name(code, shift_down=None):
    """
    Change raw code to user-friendly name.
    E.g:
    65 to 'A'
    """
    #TODO: simplify by reduction of dicts
    #TODO: on <tab> panel lose focus
    mods_codes2names = {
        16: '<Shift>',
        17: '<Control>',
        91: '<Windows>',
        18: '<Alt>',
        93: '<Menu>',
    }
    nonalpha_codes = [192, 49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 189, 187, 8, 219,
                221, 220, 186, 222, 188, 190, 191]
    nonalpha_chars = zip('`1234567890-=[]\\;\',./', '~!@#$%^&*()_+{}|:"<>?')
    codes2chars = dict(zip(nonalpha_codes, nonalpha_chars))

    if code in mods_codes2names:
        name = mods_codes2names[code]
    elif code in codes2chars:
        # nonalpha
        name = codes2chars[code][shift_down]
    elif ord('A') <= code <= ord('Z'):
        # only alpha
        name = chr(code)
        if not shift_down:
            # make it lower
            name = chr(code).lower()
    elif code in code2keyname:
        name = code2keyname[code]
    else:
        name = u'Unknown'
    return name


def codes2hotkey(keys_codes):
    """
    Change list of key codes to user-friendly hotkey.
    E.g:
    return: <alt><ctrl>period
    """
    keys_names = []
    for code in keys_codes:
        keys_names.append(code2char_name(code))
    return keys_names


def valid_hotkey(modifiers, key, data=None):
    """
    Check if passed hotkey compound of $key and $modifiers is valid.
    """
    if 'main_window_obj' in data:
        main_window_obj = data['main_window_obj']
    mods = [keyname2code.get(m) for m in modifiers]
    main_window_obj.hotkey_id = 100
    if main_window_obj.RegisterHotKey(main_window_obj.hotkey_id, mods,
            keyname2code.get(key)):
        main_window_obj.UnregisterHotKey(main_window_obj.hotkey_id)
        valid, msg = True, 'Correct hotkey.'
    else:
        valid, msg = False, 'Already registered'
    return valid, msg

def mods_and_key(hotkey):
    """
    Seperates modifiers (alt, control, ..) and key ('a', '9', '.', ..).
    """
    known_mods = 'alt control'.split()
    mods = []
    for k in keys:
        if key in known_mods:
            mods.append(k)
        else:
            key = k
    return mods, key

def register_hotkey(hotkey, toggle_shown_func):
    """
    Register OSwide hotkey

    $hotkey: is like output from f. codes2hotkey() eg.: "<ctrl> + <alt> + p"
    $toggle_shown_func: self-explaining.
    """
    # extract keys
    import re
    keys = re.sub(r'\w+', hotkey)
    mods, key = mods_and_key(hotkey)
    
    self.hotkey_id = 100
    self.RegisterHotKey(
        self.hotkey_id,
        mods,
        key,
    )
    self.Bind(wx.EVT_HOTKEY, toggle_shown_func, id=self.hotkey_id)

if __name__ == '__main__':
    os.system('windownow.py')

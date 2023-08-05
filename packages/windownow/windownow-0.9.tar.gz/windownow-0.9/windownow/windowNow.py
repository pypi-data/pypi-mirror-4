#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'xliiv <tymoteusz.jankowski@gmail.com>'

"""
Simple wx app that let you switch among desktop windows
"""

import ConfigParser
import sys
import wx

from windownow import *
from KeyReader import KeyReader

logger = logging.getLogger(__name__)


class InvalidKey(Exception):
    pass


class WrongDirectionParam(Exception):
    pass



def f(name, obj):
    """
    Debug function. It makes introspection easier
    """
    print [i for i in dir(obj) if name in i.lower()]



def ctrl_plus(char):
    char = char.lower()
    code = ord(char) - ord('a') + 1
    return code


def get_hotkey():
    """
    Read hotkey from config file.
    """
    user_conf = ConfigParser.ConfigParser()
    try:
        config_file = open(CONFIG_PATH)
    except IOError as e:
        print u'Config file not exists: %s' % CONFIG_PATH
        hotkey = None
    else:
        user_conf.readfp(config_file)
        try:
            section_name = 'Hotkeys'
            hotkey = user_conf.get(section_name, 'toggle_shown')
        except Exception as e:
            print unicode(e)
            hotkey = None
    return hotkey


class WindowLister(wx.ListCtrl):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT |
                             wx.LC_SORT_ASCENDING | wx.LC_SINGLE_SEL)
        self.frame = parent
        self.typed = []

        # images
        self.image_list = wx.ImageList(ICON_SIZE, ICON_SIZE)

        self.refresh_windows_list()
        self.SetFocus()

        self.Bind(wx.EVT_CHAR, self.OnKeyPressed)

    def fill_table(self, rows):
        "Fill table from f:create_table with data"
        #"Prepare table model like how many columns etc."
        # but since we want images on the column header we have to do it the
        # hard way:
        self.ClearAll()
        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE \
            | wx.LIST_MASK_FORMAT
        info.m_format = 0
        info.m_text = "Window id"
        self.InsertColumnInfo(0, info)

        info.m_format = 0
        info.m_text = "app name"
        self.InsertColumnInfo(1, info)

        info.m_format = 0
        info.m_text = "Window title"
        self.InsertColumnInfo(2, info)

        for idx, row in enumerate(rows):
            index = self.InsertImageStringItem(sys.maxint, str(row[0]), row[1])
            self.SetStringItem(index, 1, row[2])
            self.SetStringItem(index, 2, row[3])
            self.SetItemData(index, idx + 1)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

    def load_images(self, data, img_pos):
        """
        data - a list with path to image within
        img_pos - idx in $data where path to image is located

        eg.
        data = [
            ['0', 'path_to_image1', '2', '3'],
            ['0', 'path_to_image2', '2', '3'],
            ['0', 'path_to_image3', '2', '3'],
        ]
        load_images(data, 1):
        """
        for data_list in data:
            self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)
            data_list[img_pos] = self.image_list.Add(data_list[img_pos])
        return data

    def refresh_windows_list(self):
        self.frame.Centre()
        if not self.typed:
            self.frame.SetStatusText("Type app name")

        self.generate_list()

    def generate_list(self):
        #wins_data is tuple: win_id, icon_idx, app_name, app_title
        wins_data = utils.get_window_data(''.join(self.typed))
        wins_data = self.load_images(wins_data, 1)
        self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)
        self.fill_table(wins_data)

    def OnKeyPressed(self, evt):
        #TODO: rethink it
        # match to filter
        #self.refresh_windows_list()

        keycode = evt.GetKeyCode()
        if keycode == ctrl_plus('q'):
            self.frame.Close()
        if keycode == ctrl_plus('u'):
            if self.typed:
                self.typed = []

        if self.GetItemCount() > 1 and \
            (keycode == ctrl_plus('p') or keycode == ctrl_plus('n')):

            # wraping selecting items
            if keycode == ctrl_plus('p'):
                self.select_item('prev')
            if keycode == ctrl_plus('n'):
                self.select_item('next')
            return True

        if keycode == wx.WXK_RETURN:
            selected = self.GetFirstSelected()
            if selected != -1:
                # item is selected
                win_id = long(self.GetItem(selected, 0).GetText())
                self.typed = []
                self.frame.Hide()
                utils.raise_window(win_id)
                logger.debug('END ses'.format(vars))

        if keycode == wx.WXK_ESCAPE:
            if self.typed:
                self.typed = []
            else:
                self.frame.Hide()
        elif keycode == wx.WXK_BACK:
            self.typed = self.typed[:-1]
        elif keycode in VALID_CHAR_CODES:
            self.typed.append(chr(keycode))

        status_bar = self.frame.GetStatusBar()
        status_bar.SetStatusText(''.join(self.typed))
        self.refresh_windows_list()
        self.Select(0)

        evt.Skip()

    def get_last_item(self):
        return self.GetItemCount() - 1

    def select_item(self, direction):
        selected_idx = self.GetFirstSelected() or 0

        if direction == 'prev':
            new_idx = selected_idx - 1
            if new_idx == -1:
                new_idx = self.get_last_item()
        elif direction == 'next':
            new_idx = selected_idx + 1
            if new_idx > self.get_last_item():
                new_idx = 0
        else:
            msg = "Unknown value for $direction passed" + direction
            raise WrongDirectionParam(msg)
        self.Select(new_idx)
        self.EnsureVisible(new_idx)


class MyTaskBarIcon(wx.TaskBarIcon):

    def __init__(self, icon, frame):
        wx.TaskBarIcon.__init__(self)
        self.SetIcon(icon, APP_NAME)

        self.frame = frame
        #add taskbar icon event
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left)
        self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.OnTaskBarRight)

    def OnTaskBarRight(self, event):
        # popup menu
        self.menu = wx.Menu()

        #menu item
        item_id = wx.NewId()
        self.menu.Append(item_id, "&quit")
        self.Bind(wx.EVT_MENU, self.quit, id=item_id)

        self.PopupMenu(self.menu)

    def quit(self, evt):
        sys.exit(0)

    def on_left(self, evt):
        self.frame.toggle_shown()


class WindowNow(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self.Centre()

        # setup taskbar icon
        icon = wx.Icon(APP_ICON_PATH, wx.BITMAP_TYPE_PNG)
        #MyTaskBarIcon(icon, self)
        self.SetIcon(icon)

        sb = wx.StatusBar(self)
        self.SetStatusBar(sb)

        self.hotkey = get_hotkey()
        #TODO: split hotkey to mods and key, then pass it in 2 vars (mods, key)
        # nt_utils.mods_and_key(..) does it
        if not self.hotkey:
            self.SetTitle(u'WindowNow - Set hotkey')
            self.panel = KeyReader(self)
            self.Show()
        else:
            self.build_win_lister()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)

    def on_activate(self, event):
        if hasattr(self, 'listctrl'):
            if event.GetActive():
                # window is activated
                #useless? self.listctrl.refresh_windows_list()
                self.listctrl.SetFocus()
            event.Skip()
        if hasattr(self, 'panel'):
            # panel reads keys, so give focus to panel
            self.panel.SetFocusIgnoringChildren()

    def on_close(self, event):
        self.Destroy()
        sys.exit()

    def toggle_shown(self, event=None):
        # event is None for linux
        logger.debug('START ses')
        logger.debug('toggling shown windowNow..')
        if self.IsShown():
            logger.debug('shown')
            if self.IsActive():
                logger.debug('active')
                #XXX: linux bug by keybinder, this works perfectly if
                # triggered from on_left()
                self.Hide()
            else:
                logger.debug('not active')
                self.raise_self()
        else:
            logger.debug('not shown')
            self.Show()
            self.raise_self()
        logger.debug('END toggling shown windowNow..\n')

    def build_win_lister(self):
        logger.debug('building hotkey listener..')
        self.SetTitle(APP_NAME)
        try:
            utils.register_hotkey(self.hotkey, self.toggle_shown)
        except Exception as e:
            print unicode(e)
            self.Destroy()
            sys.exit(1)
        else:
            self.listctrl = WindowLister(self)

    def toggle_panels(self):
        self.panel.Destroy()
        self.SendSizeEvent()
        self.build_win_lister()


    def raise_self(self):
        "raise app window and make it activated"
        ## simple solution is:
        #self.Raise()
        if DEBUG:
            attrs = [ 'IsActive', 'IsAlwaysMaximized', 'IsBeingDeleted',
                    'IsDoubleBuffered', 'IsEnabled', 'IsExposed',
                    'IsExposedPoint', 'IsExposedRect', 'IsFrozen', 'IsFullScreen',
                    'IsIconized', 'IsMaximized', 'IsRetained', 'IsSameAs',
                    'IsShown', 'IsShownOnScreen', 'IsTopLevel',
            ]
            for a in attrs:
                break
                state = getattr(self, a)
                try:
                    logger.debug('attr {0}: {1}'.format(a, state()))
                except Exception as e:
                    logger.error(e)

            #logger.debug('fosus: {0}'.format(self.HasFocus()))
            #self.SetFocus()
            #logger.debug('fosus: {0}'.format(self.HasFocus()))

        ## but there is a bug:
        ## http://stackoverflow.com/questions/6398417/why-wxframe-isnt-raised-from-a-function-called-with-global-gtk-binder
        ## so:
        win_id = utils.win_id_by_title(APP_NAME)
        if win_id:
            self.win_id = utils.win_id_by_title(APP_NAME)
        logger.debug('self.win_id, win_id = {0}, {1}'.format(self.win_id,
            win_id))
        utils.raise_window(self.win_id)

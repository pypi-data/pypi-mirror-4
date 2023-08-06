import ConfigParser
import logging
import wx

import common
from windownow import *
from windownow import utils

class KeyReader(wx.Panel):
    """
    Class reads hotkey from user.
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.mods = []  # shift control alt etc.
        self.key = None

        self.notice = wx.StaticText(self, wx.ID_ANY, u'Type hotkey.')
        self.hotkey_viewer = wx.StaticText(self, wx.ID_ANY)
        self.accept_btn = wx.Button(self, wx.ID_APPLY)
        self.accept_btn.Disable()

        ## lay by sizer
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.AddStretchSpacer()

        self.box.Add(self.notice, 0, flag=wx.ALIGN_CENTER)
        self.box.Add(self.hotkey_viewer, 0, flag=wx.ALL | wx.ALIGN_CENTER,
                border=10)
        self.box.Add(self.accept_btn, 0, flag=wx.ALIGN_CENTER)

        self.box.AddStretchSpacer()
        self.SetSizer(self.box)

        self.Bind(wx.EVT_SET_FOCUS, self.on_set_focus)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_PAINT, self.repaint)
        self.accept_btn.Bind(wx.EVT_BUTTON, self.accept_hotkey)

    def repaint(self, evt):
        logging.debug('repaint')
        self.box.Layout()
        # http://www.wxpython.org/docs/api/wx.PaintDC-class.html
        # 'If you have an EVT_PAINT handler, you must create a wx.PaintDC
        # object
        # .. within it even if you don't actually use it.'
        dc = wx.PaintDC(self)
        # this because <tab> remove focus from panel and keys can't be read
        # more
        self.SetFocusIgnoringChildren()

    def on_set_focus(self, evt):
        self.notice.SetLabel(
            u'Press keys to set hotkey for calling {0}'.format(APP_NAME))


    def get_modifiers(self, key_pressed_event, mod_code):
        '''
        Recognize if modifiers pressed.
        Modifiers are defined as class property.
        '''
        logging.debug('mod_code: {0}'.format(mod_code.items()))
        mods_down = set()
        for name, code in mod_code.items():
            func_name = name + 'Down'  # e.g: AltDown, ShiftDown
            mod_down = getattr(key_pressed_event, func_name)
            if mod_down():
                logging.debug('mod append: {0}'.format(name))
                mods_down.add(code)
        return list(mods_down)


    def on_key_down(self, event):
        self.mods = self.get_modifiers(event, utils.MOD_CODE)
        self.key = event.GetRawKeyCode()
        logging.debug('mods, key = {0}, {1}'.format(self.mods, self.key))
        hotkey = self.name_from_keycodes()
        self.hotkey_viewer.SetLabel(hotkey)


    def name_from_keycodes(self):
        '''
        Generates user-friendly text describing pressed keys.
        '''
        together = []
        for code in self.mods:
            together.append(utils.code2char_name(code))
        #if self.key not in together:
        #    together.append(self.key)
        together.append(utils.code2char_name(self.key))
        result = KEY_SEPARATOR.join(together)
        return result


    def on_key_up(self, event):
        # validate
        valid, msg = self.validate_hotkey(self.mods, self.key)
        self.notice.SetLabel(msg)
        if not valid:
            self.mods = []
            self.key = None
            self.hotkey_viewer.SetLabel('')
            self.accept_btn.Disable()
        else:
            self.accept_btn.Enable()


    def validate_hotkey(self, mods, key):
        """
        Validate if typed hotkey is valid.
        E.g.:
        Check if typed hotkey is understand by utils module.
        """
        valid, msg = (False,
            u'Required one of special keys like: {0}'.format(
                ' '.join(SPECIAL_KEYS)))
        if mods and key:
            valid, msg = utils.valid_hotkey(self.mods, self.key,
                {'keyreader_win': self})
        return valid, msg


    def accept_hotkey(self, evt):
        frame = self.GetParent()
        frame.set_hotkey(self.mods, self.key)
        common.save_hotkey(frame.hotkey)
        frame.toggle_panels()
        return True

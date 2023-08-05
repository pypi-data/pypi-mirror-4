import ConfigParser
import logging
import wx

from windownow import *
from windownow import utils


def save_hotkey(hotkey):
    """
    Save hotkey to config file.
    """
    section_name = 'Hotkeys'
    user_conf = ConfigParser.ConfigParser()
    try:
        config_file = open(CONFIG_PATH, 'ab')
    except IOError as e:
        print u'Config file not exists: %s' % CONFIG_PATH
    else:
        user_conf.add_section(section_name)
    finally:
        user_conf.set(section_name, 'toggle_shown', hotkey)
        user_conf.write(config_file)
        config_file.close()


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
        self.hotkey_viewer.Disable()
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

    def on_key_down(self, event):
        self.mods = self.get_modifiers(event)
        code = event.GetRawKeyCode()
        self.key = utils.code2char_name(code, event.ShiftDown())
        hotkey = self.name_from_pressed_keys()
        self.hotkey_viewer.SetLabel(hotkey)

    def get_modifiers(self, key_pressed_event):
        '''
        Recognize if modifiers pressed.
        Modifiers are defined as class property.
        '''
        mod_code = {
            'Control': 17,
            'Alt': 18,
        }
        mods_down = []
        for name, code in mod_code.items():
            func_name = name + 'Down'  # e.g: AltDown, ShiftDown
            mod_down = getattr(key_pressed_event, func_name)
            if mod_down():
                mods_down.append(code)
        return mods_down

    def name_from_pressed_keys(self):
        '''
        Generates user-friendly text describing pressed keys.
        '''
        together = []
        for code in self.mods:
            together.append(utils.code2char_name(code))
        if self.key not in together:
            together.append(self.key)
        result = ' + '.join(together)
        return result

    def on_key_up(self, event):
        # validate
        valid, msg = self.validate_hotkey(self.mods, self.key)
        self.notice.SetLabel(msg)
        if not valid:
            self.mods = []
            self.key = None
            self.hotkey_viewer.SetLabel('')
            self.hotkey_viewer.Disable()
            self.accept_btn.Disable()
        else:
            self.hotkey_viewer.Enable()
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
            valid, msg = utils.valid_hotkey(self.mods, self.key, {'self':
                self})
        return valid, msg

    def accept_hotkey(self, evt):
        # save to config
        frame = self.GetParent()
        frame.hotkey = self.hotkey_viewer.GetLabel()
        save_hotkey(frame.hotkey)
        frame.toggle_panels()
        return True

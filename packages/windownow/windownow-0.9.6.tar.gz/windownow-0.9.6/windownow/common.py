import ConfigParser
import json
import logging
import re

from windownow import *

logger = logging.getLogger(__name__)

def contains(string, substring=None):
    """
    Check if $typed in $text

    check_matching('du', 'adfDU'): True
    check_matching('fda', 'fdbadafa'): False
    """
    res = re.search(substring, string, re.I)
    return True if res else False


def track_vals(fn):
    def new_fn(*args, **kwargs):
        logging.debug('fn: {0}'.format(fn.__name__))
        logging.debug('args: {0}'.format(args))
        logging.debug('kwargs: {0}'.format(kwargs))
        res = fn(*args, **kwargs)
        logging.debug('res: {0}'.format(res))
        return res
    return new_fn


def get_hotkey():
    """
    Read hotkey from config file.
    """
    hotkey = None
    user_conf = ConfigParser.ConfigParser()
    try:
        config_file = open(CONFIG_PATH)
    except IOError as e:
        logging.error(u'Config file not exists: {0}'.format(CONFIG_PATH))
    else:
        user_conf.readfp(config_file)
        try:
            section_name = 'Hotkeys'
            hotkey = {
                'mods': json.loads(user_conf.get(section_name, 'mods')),
                'key': json.loads(user_conf.get(section_name, 'key')),
            }
        except Exception as e:
            logging.error(e)
    return hotkey


def save_hotkey(hotkey):
    """
    Save hotkey to config file.
    """
    section_name = 'Hotkeys'
    user_conf = ConfigParser.ConfigParser()
    try:
        config_file = open(CONFIG_PATH, 'ab')
    except IOError as e:
        logging.error(u'Config file not exists: {0}'.format(CONFIG_PATH))
    else:
        user_conf.add_section(section_name)
        user_conf.set(section_name, 'mods', json.dumps(hotkey['mods']))
        user_conf.set(section_name, 'key', json.dumps(hotkey['key']))
        user_conf.write(config_file)
        config_file.close()

import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

DEBUG = 1

APP_NAME = 'windowNow'
APP_DIR = os.path.dirname(__file__)
HOME_DIR = os.path.expanduser('~')
CONFIG_NAME = ''.join(['.', APP_NAME, '.ini'])
CONFIG_PATH = os.path.join(HOME_DIR, CONFIG_NAME)
LOG_PATH = os.path.join(APP_DIR, APP_NAME + '.log')

ICON_SIZE = 32
ICONS_DIR = 'icons'
DEFAULT_ICON_NAME = "default"
DEFAULT_ICON_PATH = os.path.join(ICONS_DIR, DEFAULT_ICON_NAME)
ICONS_DIR_PATH = os.path.join(APP_DIR, ICONS_DIR)
APP_ICON_NAME = '.'.join([APP_NAME, 'png'])
APP_ICON_PATH = os.path.join(ICONS_DIR_PATH, APP_ICON_NAME)

VALID_CHAR_CODES = range(32, 127)
chr(VALID_CHAR_CODES.pop(15)) #remove '/' which is not file name char


PLUGINS_DIR_NAME = 'plugins'
PLUGINS_DIR_PATH = os.path.join(APP_DIR, PLUGINS_DIR_NAME)
PLUGINS_PATH = '.'.join([APP_NAME.lower(), PLUGINS_DIR_NAME])
OS_SPEC_MOD_NAME = '%s_utils' % os.name
OS_SPEC_MOD_PATH = '.'.join([APP_NAME.lower(), PLUGINS_DIR_NAME,
    OS_SPEC_MOD_NAME])

SPECIAL_KEYS = 'Alt,Control,Shift'.split()
KEY_SEPARATOR = ' '



def dynamic_import(module_path, from_name=None):
    '''
    import module {module_path} as "import {module_path}"
    or
    import module {from_name} as "from {module_path} from {from_name}"

    {module_path}: path to module, like 'os' or 'os.path'
    {from_name}: name of module from 'from {module_path} import {from_name}'
    import

    '''
    logging.debug('module_path, from_name = {0}, {1}'.format(module_path,
        from_name))
    fromlist = [from_name] if from_name else []
    module = __import__(module_path, globals=globals(), locals=locals(),
        fromlist=fromlist)
    if from_name:
        logger.debug('imported module is: {0}'.format(module))
        module = getattr(module, from_name)
    logger.debug('imported module is: {0}'.format(module))
    return module


try:
    utils = dynamic_import(PLUGINS_PATH, OS_SPEC_MOD_NAME)
except Exception as e:
    logger.error("Failed loading module {0}: ({1})".format(OS_SPEC_MOD_NAME,
        e))
    sys.exit(0)

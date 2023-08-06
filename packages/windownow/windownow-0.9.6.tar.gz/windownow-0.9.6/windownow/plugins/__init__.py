import logging
import sys

import windownow

logger = logging.getLogger(__name__)


MOD_CODE = {
    'Control': 17,
    'Alt': 18,
}


def verbose_import(module, from_name, info_msg):
    '''
    {module}: name of module
    {from_name}: name typed in syntax "from module import {from_name}"
    {info_msg}: msg for user about instaling missing module
    '''
    try:
        module = windownow.dynamic_import(module, from_name)
    except Exception as e:
        logging.error('cannot import module: "{0}" ({1})'.format(module, e))
        if info_msg:
            logging.info(info_msg)
        sys.exit(0)
    return module

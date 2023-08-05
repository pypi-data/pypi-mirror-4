import logging
import sys

import windownow

logger = logging.getLogger(__name__)

def verbose_import(module, os_package_name, from_name):
    try:
        module = windownow.dynamic_import(module, from_name)
    except Exception as e:
        msg = '\n'.join([
            'cannot import module: "{0}" ({1})',
            'install module "{0}" by your OS utils.'
        ]).format(module, e, os_package_name)
        logging.error(msg)
        if os_package_name:
            logging.info('for example: "sudo aptitude install {0}"'.format(
                os_package_name))
        sys.exit(0)
    return module




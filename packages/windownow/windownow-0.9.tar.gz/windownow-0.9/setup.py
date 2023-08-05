#!/usr/bin/env python

from distutils.core import setup

import os


PROJECT = 'windownow'
VERSION = '0.9'
URL = 'http://pypi.python.org/pypi/windownow/'
AUTHOR = 'xliiv'
AUTHOR_EMAIL = 'tymoteusz.jankowski@gmail.com'
DESC = "Switch desktop's windows by typing their titles, name, etc."


def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    packages=[
        'windownow',
        'windownow/plugins',
    ],
    include_package_data = True,
    #package_data = {
    #    '': [
    #        'icons/*',
    #    ]
    #},
    scripts = [
        'bin/windownow',
    ],
    install_requires=[
        # -*- Requirements -*-
        #'wxPython',
        #'PyGTK>=2.0',

    ],
    keywords = ['desktop', 'windows', 'switcher'
    ],
    classifiers=[
        # see http://pypi.python.org/pypi?:action=list_classifiers
        # -*- Classifiers -*- 
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Gnome",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        'License :: OSI Approved',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        "Programming Language :: Python",
        "Topic :: Desktop Environment :: Window Managers",
        "Topic :: Utilities",
    ],
)

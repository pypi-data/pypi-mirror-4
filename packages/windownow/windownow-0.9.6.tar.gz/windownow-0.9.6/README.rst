=========
Windownow
=========

About
-----

Switch desktop's windows by typing text from their title, application name,
etc.

Now experimentally works on Microsoft Windows.

Installation & running
----------------------

    pip install windownow

    $ windownow


Keyboard
--------
    * control+p: highlight previous item
    * control+n: highlight next item
    * enter | return: hide windownow and raise highlighted window
    * esc:
        * if typed any filter letter:
            reset filter

        * if no filter string typed:
            hide windownow

Requirements
------------
System enviroment should have installed this packages:

    * python-gtk2 (or higher)
    * python-keybinder
    * python-wnck
    * python-wxgtk2.8 (or higher)

Check for above packages with your linux distribution package manager, like::

    aptitude install python-gtk2

or (if package not found)::

    aptitude search python-gtk2

in Ubuntu | Debian



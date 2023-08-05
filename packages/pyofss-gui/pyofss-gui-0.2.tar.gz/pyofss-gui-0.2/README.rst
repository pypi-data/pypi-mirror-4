
Pyofss-gui: A PyQt-based graphical user interface for pyofss
============================================================

The pyofss GUI uses a drag-and-drop approach to adding optical modules to form a system to simulate.
Parameters for each optical module can be viewed and modified before the system simulation is run.
Outputs from each optical module can be visualised using the plot interface.

Installation
------------

Pyofss-gui is available on PyPI and can be retrieved using the pip program:

.. code-block:: bash

    sudo aptitude install python-pip
    pip install pyofss-gui

Dependencies
------------

Pyofss-gui depends on pyofss and PyQt.
They can be installed using:

.. code-block:: bash

    sudo aptitude install python-qt4
    pip install pyofss

Appearance
----------

Some themes do not show icons in menus and on buttons.
The following two commands can often fix this issue:

.. code-block:: bash

    gconftool-2 --type boolean --set /desktop/gnome/interface/buttons_have_icons true
    gconftool-2 --type boolean --set /desktop/gnome/interface/menus_have_icons true

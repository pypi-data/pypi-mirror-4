
"""
    Copyright (C) 2012 David Bolt

    This file is part of pyofss-gui.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt4 import QtGui


class GuiGroup(QtGui.QTabWidget):
    """ Group modules together in a tabbed browser. """
    def __init__(self):
        super(GuiGroup, self).__init__()

        self.setMovable(True)
        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)

        self.tabCloseRequested.connect(self.removeTab)

    def add_module(self, module_id, data=None):
        """ Construct a module (module_id), then fill widget data. """
        if module_id in ("Gaussian", "Sech", "Fibre"):
            # Module name is of the form: GuiFibre
            module = "".join(["Gui", module_id])
            # Package name is of the form: gui_fibre
            package = "_".join(["gui", module_id.lower()])
            # Dynamically import module from package:
            _temp = __import__(package, globals(), locals(), [module], -1)
            # Get a reference to the corresponding class:
            constructor = getattr(_temp, module)
            print "Constructing %s... " % module,
            # Call the constructor reference
            widget = constructor()
            print "done."

            if data is not None:
                widget.set_data(data)

            # If icon available, use: addTab(optical_module, icon, text)
            self.addTab(widget, module_id)
        else:
            print "Unknown module type"


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

from PyQt4 import QtGui, QtCore

from pyofss.modules.plotter \
    import single_plot, map_plot, waterfall_plot, animated_plot
from pyofss.field import temporal_power, spectral_power


class GuiPlotter(QtGui.QDialog):
    """ Wrapper for pyofss.modules.plotter. """
    def __init__(self, system=None):
        super(GuiPlotter, self).__init__()

        self.system = system

        self.setWindowTitle("Field Plotter")

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)

        self.module_outputs = QtGui.QComboBox()
        if system is not None:
            for label in system.fields:
                self.module_outputs.addItem(label)

        self.plot_types = QtGui.QComboBox()
        self.plot_types.addItems(
            QtCore.QStringList(["Single plot", "Map plot",
                                "Waterfall plot", "Animated plot"]))
        self.select_domain = QtGui.QComboBox()
        self.select_domain.addItems(
            QtCore.QStringList(["Temporal", "Spectral"]))

        layout.addRow("Select module output:", self.module_outputs)
        layout.addRow("Select plot type:", self.plot_types)
        layout.addRow("Select domain:", self.select_domain)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self.generate_plot)
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self.close_dialog)
        layout.addRow(buttons)

        self.setLayout(layout)

    def generate_plot(self):
        """ Generate the appropriate plot. """
        if self.system is None:
            print "System has not been run!"
            return

        selected_module = self.module_outputs.currentText()
        selected_plot = self.plot_types.currentText()
        selected_domain = self.select_domain.currentText()

        if selected_plot == "Single plot":
            if selected_domain == "Temporal":
                x = self.system.domain.t
                y = temporal_power(self.system.fields[selected_module])
            else:
                x = self.system.domain.nu
                y = spectral_power(self.system.field, True)

            single_plot(x, y)
        else:
            if hasattr(self.system[selected_module], "stepper"):
                storage = self.system['fibre'].stepper.storage
            else:
                print "Unable to plot: Module does not have any traces stored!"
                return

            if selected_domain == "Temporal":
                (x, y, z) = storage.get_plot_data(is_temporal=True)
            else:
                (x, y, z) = storage.get_plot_data(is_temporal=False,
                                                  normalised=True)

            if selected_plot == "Map plot":
                map_plot(x, y, z)
            elif selected_plot == "Waterfall plot":
                waterfall_plot(x, y, z)
            elif selected_plot == "Animated plot":
                animated_plot(x, y, z)

    def close_dialog(self):
        """ Close this dialog. """
        self.close()

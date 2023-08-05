
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
from helpers import set_spinbox_data

from pyofss.modules.plotter \
    import single_plot, map_plot, waterfall_plot, animated_plot
from pyofss.field import temporal_power, spectral_power


class GuiPlotter(QtGui.QDialog):
    """ Wrapper for pyofss.modules.plotter. """
    def __init__(self, system=None):
        super(GuiPlotter, self).__init__()

        self.system = system

        self.setWindowTitle("Field Plotter")

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

        self.filename = QtGui.QLineEdit()

        self.x_label = QtGui.QLineEdit()
        self.y_label = QtGui.QLineEdit()
        self.z_label = QtGui.QLineEdit()

        self.x_minimum = QtGui.QDoubleSpinBox()
        self.x_maximum = QtGui.QDoubleSpinBox()
        self.y_minimum = QtGui.QDoubleSpinBox()
        self.y_maximum = QtGui.QDoubleSpinBox()

        self.use_fill = QtGui.QCheckBox()
        self.use_fill.setChecked(True)
        self.fill_colour = QtGui.QLineEdit("blue")
        self.alpha = QtGui.QDoubleSpinBox()
        self.style = QtGui.QLineEdit("b-")

        self.use_colour = QtGui.QCheckBox()
        self.use_colour.setChecked(True)
        self.interpolation = QtGui.QComboBox()
        self.interpolation.addItem("lanczos")

        self.fps = QtGui.QSpinBox()
        self.clear_temp = QtGui.QCheckBox()
        self.clear_temp.setChecked(True)
        self.frame_prefix = QtGui.QLineEdit("_tmp")

        set_spinbox_data(self.x_minimum, value=None, minimum=-1.0e3,
                         maximum=1.0e3, single_step=0.1, decimals=3)
        set_spinbox_data(self.x_maximum, value=None, minimum=-1.0e3,
                         maximum=1.0e3, single_step=0.1, decimals=3)
        set_spinbox_data(self.alpha, value=0.2, minimum=0.0,
                         maximum=1.0, single_step=0.1, decimals=2)
        set_spinbox_data(self.y_minimum, value=None, minimum=-1.0e3,
                         maximum=1.0e3, single_step=0.005, decimals=4)
        set_spinbox_data(self.y_maximum, value=None, minimum=-1.0e3,
                         maximum=1.0e3, single_step=0.005, decimals=4)
        # Note default value of 10 (not 5 as in plotter.animated_plot):
        set_spinbox_data(self.fps, value=10, minimum=1,
                         maximum=100, single_step=1, decimals=None)

        general_layout = QtGui.QFormLayout()
        general_layout.setFieldGrowthPolicy(
            QtGui.QFormLayout.FieldsStayAtSizeHint)

        general_layout.addRow("Select module output:", self.module_outputs)
        general_layout.addRow("Select plot type:", self.plot_types)
        general_layout.addRow("Select domain:", self.select_domain)
        general_layout.addRow("Filename to save as:", self.filename)
        general_layout.addRow("Label for x-axis:", self.x_label)
        general_layout.addRow("Label for y-axis:", self.y_label)
        general_layout.addRow("Label for z-axis:", self.z_label)
        general_layout.addRow("Minimum for x-axis:", self.x_minimum)
        general_layout.addRow("Maximum for x-axis:", self.x_maximum)
        general_layout.addRow("Minimum for y-axis:", self.y_minimum)
        general_layout.addRow("Maximum for y-axis:", self.y_maximum)

        general_tab = QtGui.QWidget()
        general_tab.setLayout(general_layout)

        extras_layout = QtGui.QFormLayout()
        extras_layout.setFieldGrowthPolicy(
            QtGui.QFormLayout.FieldsStayAtSizeHint)

        extras_layout.addRow("Use fill for plots:", self.use_fill)
        extras_layout.addRow("Colour to use for fill:", self.fill_colour)
        extras_layout.addRow("Set transparency for fill:", self.alpha)
        extras_layout.addRow("Line style (colour and type):", self.style)
        extras_layout.addRow("Use colour in map plot:", self.use_colour)
        extras_layout.addRow("Interpolation method for map plot:",
                             self.interpolation)
        extras_layout.addRow("Frames per second for animation:", self.fps)
        extras_layout.addRow("Clear temporary files \nafter saving animation:",
                             self.clear_temp)
        extras_layout.addRow("Prefix for animation frames:", self.frame_prefix)

        extras_tab = QtGui.QWidget()
        extras_tab.setLayout(extras_layout)

        plot_option_tabs = QtGui.QTabWidget()
        plot_option_tabs.addTab(general_tab, "General options")
        plot_option_tabs.addTab(extras_tab, "Extra options")

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self.generate_plot)
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self.close_dialog)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(plot_option_tabs)
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)

    def generate_plot(self):
        """ Generate the appropriate plot. """
        if self.system is None:
            print "System has not been run!"
            return

        selected_module = self.module_outputs.currentText()
        selected_plot = self.plot_types.currentText()
        selected_domain = self.select_domain.currentText()

        label_data = {"x_label": str(self.x_label.text()),
                      "y_label": str(self.y_label.text()),
                      "z_label": str(self.z_label.text())}

        x_range = (self.x_minimum.value(), self.x_maximum.value())
        y_range = (self.y_minimum.value(), self.y_maximum.value())

        # If range is invalid (or the default), then set to None:
        if(x_range[0] == x_range[1]):
            x_range = None
        if(y_range[0] == y_range[1]):
            y_range = None

        if selected_plot == "Single plot":
            # Single plot uses "label", so change key name in label_data:
            label_data["label"] = label_data["z_label"]
            del label_data["z_label"]

            extra_options = {"use_fill": self.use_fill.isChecked(),
                             "fill_colour": str(self.fill_colour.text()),
                             "alpha": self.alpha.value(),
                             "style": str(self.style.text()),
                             "x_range": x_range,
                             "y_range": y_range}
            # Improve on default: set the minimum for the y-axis to zero:
            if(y_range is None):
                extra_options["y_range"] = 0.0

            extra_options.update(label_data)

            if selected_domain == "Temporal":
                data = (self.system.domain.t,
                        temporal_power(self.system.fields[selected_module]))
            else:
                data = (self.system.domain.nu,
                        spectral_power(self.system.field, True))

            single_plot(*data, **extra_options)
        else:
            if hasattr(self.system[selected_module], "stepper"):
                storage = self.system[selected_module].stepper.storage
            else:
                print "Unable to plot: No traces stored by this module!"
                return

            extra_options = {"filename": str(self.filename.text()),
                             "y_range": y_range}
            extra_options.update(label_data)

            if selected_domain == "Temporal":
                data = storage.get_plot_data(
                    is_temporal=True, reduced_range=x_range)
            else:
                data = storage.get_plot_data(
                    is_temporal=False, normalised=True, reduced_range=x_range)

            if selected_plot == "Map plot":
                extra_options["use_colour"] = self.use_colour.isChecked()
                extra_options["interpolation"] = \
                    str(self.interpolation.currentText())
                map_plot(*data, **extra_options)
            elif selected_plot == "Waterfall plot":
                extra_options["use_poly"] = self.use_fill.isChecked()
                waterfall_plot(*data, **extra_options)
            elif selected_plot == "Animated plot":
                extra_options["alpha"] = self.alpha.value()
                extra_options["fps"] = self.fps.value() * 1.0
                print extra_options["fps"]
                extra_options["clear_temp"] = self.clear_temp.isChecked()
                extra_options["frame_prefix"] = \
                    str(self.frame_prefix.text())
                # Improve on default: set the minimum for the y-axis to zero:
                if(y_range is None):
                    extra_options["y_range"] = 0.0
                animated_plot(*data, **extra_options)

    def close_dialog(self):
        """ Close this dialog. """
        self.close()

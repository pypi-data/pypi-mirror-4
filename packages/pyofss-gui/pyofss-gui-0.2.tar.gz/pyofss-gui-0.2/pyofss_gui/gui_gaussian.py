
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

import numpy as np
from pyofss.modules.gaussian import Gaussian


class GuiGaussian(QtGui.QWidget):
    """ Wrapper for pyofss.modules.gaussian. """
    def __init__(self):
        super(GuiGaussian, self).__init__()

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)

        self.name = QtGui.QLineEdit("gaussian")
        self.position = QtGui.QDoubleSpinBox()
        self.width = QtGui.QDoubleSpinBox()
        self.peak_power = QtGui.QDoubleSpinBox()
        self.offset_nu = QtGui.QDoubleSpinBox()
        self.order = QtGui.QSpinBox()
        self.chirp = QtGui.QDoubleSpinBox()
        self.initial_phase = QtGui.QDoubleSpinBox()
        self.channel = QtGui.QSpinBox()
        self.using_fwhm = QtGui.QCheckBox()

        set_spinbox_data(self.position, value=0.5, minimum=0.0,
                         maximum=1.0, single_step=0.01, decimals=2)
        set_spinbox_data(self.width, value=10.0, minimum=1.0e-3,
                         maximum=1.0e3, single_step=0.1, decimals=3)
        set_spinbox_data(self.peak_power, value=1.0e-3, minimum=0.0,
                         maximum=1.0e9, single_step=0.05, decimals=4)
        set_spinbox_data(self.offset_nu, value=0.0, minimum=-100.0,
                         maximum=100.0, single_step=0.001, decimals=3)
        set_spinbox_data(self.order, value=1, minimum=1, maximum=50,
                         single_step=1, decimals=None)
        set_spinbox_data(self.chirp, value=0.0, minimum=-1.0e3,
                         maximum=1.0e3, single_step=0.2, decimals=None)
        set_spinbox_data(self.initial_phase, value=0.0, minimum=0.0,
                         maximum=2.0 * np.pi, single_step=0.01, decimals=2)
        set_spinbox_data(self.channel, value=0, minimum=0,
                         maximum=1, single_step=1, decimals=None)

        layout.addRow("Name:", self.name)
        layout.addRow("Position:", self.position)
        layout.addRow("Width:", self.width)
        layout.addRow("Peak power:", self.peak_power)
        layout.addRow("Offset frequency:", self.offset_nu)
        layout.addRow("Gaussian order:", self.order)
        layout.addRow("Chirp parameter:", self.chirp)
        layout.addRow("Initial phase:", self.initial_phase)
        layout.addRow("Channel:", self.channel)
        layout.addRow("Use FWHM measure:", self.using_fwhm)

        self.setLayout(layout)

    def get_data(self):
        """ Retrieve data from widgets. """
        name = self.name.text()
        position = self.position.value()
        width = self.width.value()
        peak_power = self.peak_power.value()
        offset_nu = self.offset_nu.value()
        order = self.order.value()
        chirp = self.chirp.value()
        initial_phase = self.initial_phase.value()
        channel = self.channel.value()
        using_fwhm = self.using_fwhm.isChecked()

        data = {"name": name, "position": position, "width": width,
                "peak_power": peak_power, "offset_nu": offset_nu,
                "m": order, "C": chirp, "initial_phase": initial_phase,
                "channel": channel, "using_fwhm": using_fwhm}

        data["id"] = "Gaussian"
        return data

    def set_data(self, data):
        """ Set widget data. """
        self.name.setText(data["name"])
        self.position.setValue(data["position"])
        self.width.setValue(data["width"])
        self.peak_power.setValue(data["peak_power"])
        self.offset_nu.setValue(data["offset_nu"])
        self.order.setValue(data["m"])
        self.chirp.setValue(data["C"])
        self.initial_phase.setValue(data["initial_phase"])
        self.channel.setValue(data["channel"])
        self.using_fwhm.setChecked(data["using_fwhm"])

    def __call__(self):
        data = self.get_data()
        del data["id"]
        return Gaussian(**data)

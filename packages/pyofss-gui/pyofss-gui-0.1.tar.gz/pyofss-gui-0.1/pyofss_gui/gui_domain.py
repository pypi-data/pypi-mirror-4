
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

from pyofss.domain import Domain


class GuiDomain(QtGui.QDialog):
    """ Wrapper for pyofss.domain. """
    def __init__(self):
        super(GuiDomain, self).__init__()

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)

        self.total_bits = QtGui.QSpinBox()
        self.samples_per_bit = QtGui.QSpinBox()
        self.bit_width = QtGui.QDoubleSpinBox()
        self.centre_nu = QtGui.QDoubleSpinBox()
        self.channels = QtGui.QSpinBox()

        set_spinbox_data(self.total_bits, value=1, minimum=1,
                         maximum=4096, single_step=1, decimals=None)
        set_spinbox_data(self.samples_per_bit, value=512, minimum=0,
                         maximum=262144, single_step=1, decimals=None)
        set_spinbox_data(self.bit_width, value=100.0, minimum=0.01,
                         maximum=1.0e4, single_step=1.0, decimals=2)
        set_spinbox_data(self.centre_nu, value=193.1, minimum=185.0,
                         maximum=400.0, single_step=0.001, decimals=3)
        set_spinbox_data(self.channels, value=1, minimum=1,
                         maximum=2, single_step=1, decimals=None)

        layout.addRow("Total bits to generate:", self.total_bits)
        layout.addRow("Number of samples per bit:", self.samples_per_bit)
        layout.addRow("Temporal with per bit:", self.bit_width)
        layout.addRow("Frequency of first channel:", self.centre_nu)
        layout.addRow("Number of channels to simulate:", self.channels)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self.close_dialog)
        layout.addRow(buttons)

        self.setLayout(layout)

        self.data = None

    def close_dialog(self):
        """ Close this dialog. """
        self.close()

    def update_data(self):
        """ Retrieve data from widgets. """
        total_bits = self.total_bits.value()
        samples_per_bit = self.samples_per_bit.value()
        bit_width = self.bit_width.value()
        centre_nu = self.centre_nu.value()
        channels = self.channels.value()

        self.data = {
            "total_bits": total_bits, "samples_per_bit": samples_per_bit,
            "bit_width": bit_width, "centre_nu": centre_nu,
            "channels": channels}

    def __call__(self):
        self.update_data()
        return Domain(**self.data)

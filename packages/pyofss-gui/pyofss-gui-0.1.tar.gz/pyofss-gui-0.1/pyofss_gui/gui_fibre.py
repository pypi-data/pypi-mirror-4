
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
from helpers import set_spinbox_data

from pyofss.modules.fibre import Fibre


class GuiFibre(QtGui.QWidget):
    """ Wrapper for pyofss.modules.fibre. """
    def __init__(self):
        super(GuiFibre, self).__init__()

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)

        self.name = QtGui.QLineEdit("fibre")
        self.length = QtGui.QDoubleSpinBox()
        self.alpha = QtGui.QDoubleSpinBox()
        self.beta_2 = QtGui.QDoubleSpinBox()
        self.beta_3 = QtGui.QDoubleSpinBox()
        self.gamma = QtGui.QDoubleSpinBox()
        self.traces = QtGui.QSpinBox()
        self.total_steps = QtGui.QSpinBox()

        set_spinbox_data(self.length, value=1.0, minimum=0.0,
                         maximum=100.0, single_step=1.0e-3, decimals=5)
        set_spinbox_data(self.alpha, value=0.0, minimum=0.0,
                         maximum=5.0, single_step=0.01, decimals=4)
        set_spinbox_data(self.beta_2, value=0.0, minimum=-50.0,
                         maximum=50.0, single_step=0.01, decimals=4)
        set_spinbox_data(self.beta_3, value=0.0, minimum=-50.0,
                         maximum=50.0, single_step=0.01, decimals=4)
        set_spinbox_data(self.gamma, value=0.0, minimum=0.0,
                         maximum=1.0e3, single_step=0.01, decimals=4)
        set_spinbox_data(self.traces, value=1, minimum=0,
                         maximum=1000, single_step=1, decimals=None)
        set_spinbox_data(self.total_steps, value=100, minimum=1,
                         maximum=65536, single_step=1, decimals=None)

        layout.addRow("Name:", self.name)
        layout.addRow("Length:", self.length)
        layout.addRow("Attenuation:", self.alpha)
        layout.addRow("Second order dispersion:", self.beta_2)
        layout.addRow("Third order dispersion:", self.beta_3)
        layout.addRow("Nonlinearity:", self.gamma)
        layout.addRow("Number of traces:", self.traces)
        layout.addRow("Number of steps:", self.total_steps)

        self.setLayout(layout)

        self.data = None

    def update_data(self):
        """ Retrieve data from widgets. """
        name = self.name.text()
        length = self.length.value()
        from pyofss.modules.linearity import convert_alpha_to_linear
        alpha = convert_alpha_to_linear( self.alpha.value() )
        beta_2 = self.beta_2.value()
        beta_3 = self.beta_3.value()
        gamma = self.gamma.value()
        traces = self.traces.value()
        total_steps = self.total_steps.value()

        self.data = {
            "name": name, "length": length, "alpha": alpha,
            "beta": [0.0, 0.0, beta_2, beta_3], "gamma": gamma,
            "traces": traces, "total_steps": total_steps}

    def __call__(self):
        self.update_data()
        return Fibre(**self.data)

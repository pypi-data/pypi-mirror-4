
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


def set_spinbox_data(widget, value=None, minimum=None, maximum=None,
                     single_step=None, decimals=None):
    """ Set data for spinbox. """
    # Set decimals first, otherwise quantities rounded to two decimal places.
    if decimals is not None:
        widget.setDecimals(decimals)
    if minimum is not None:
        widget.setMinimum(minimum)
    if maximum is not None:
        widget.setMaximum(maximum)
    # Set value after minimum and maximum, otherwise it will be overwritten.
    if value is not None:
        widget.setValue(value)
    if single_step is not None:
        widget.setSingleStep(single_step)

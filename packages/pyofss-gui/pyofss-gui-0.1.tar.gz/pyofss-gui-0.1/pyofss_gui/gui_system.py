
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

import sys
import time
import functools
from PyQt4 import QtGui, QtCore

from gui_domain import GuiDomain
from gui_gaussian import GuiGaussian
from gui_sech import GuiSech
from gui_fibre import GuiFibre
from gui_plotter import GuiPlotter

from pyofss.system import System


class GuiSystem(QtGui.QMainWindow):
    """ Wrapper for pyofss.system. """
    def __init__(self):
        super(GuiSystem, self).__init__()

        self.setWindowTitle("Pyofss-gui")

        self.init_menubar_and_toolbar()
        self.statusBar()

        self.init_module_toolbar()
        self.init_module_browser()

        self.gui_domain = GuiDomain()

        self.system = None

    def init_menubar_and_toolbar(self):
        """ Generate actions and use to initialise a menubar and toolbar. """
        file_new_action = self.make_action(
            "&New", shortcut="Ctrl+N", icon="document-new",
            tip="Create a new parameter file", slot=self.new_file)

        file_open_action = self.make_action(
            "&Open", shortcut="Ctrl+O", icon="document-open",
            tip="Open a parameter file", slot=self.open_file)

        file_save_action = self.make_action(
            "&Save", shortcut="Ctrl+S", icon="document-save",
            tip="Save system to parameter file", slot=self.save_file)

        file_save_as_action = self.make_action(
            "Save &As", icon="document-save-as",
            tip="Select file name for save", slot=self.save_file_as)

        file_quit_action = self.make_action(
            "&Quit", shortcut="Ctrl+Q", icon="application-exit",
            tip="Quit the program", slot=self.quit_program)

        tools_domain_action = self.make_action(
            "&Domain", icon="document-properties",
            tip="Configure domain settings", slot=self.configure_domain)

        tools_simulate_action = self.make_action(
            "&Simulate", icon="system-run",
            tip="Start simulation", slot=self.simulate)

        tools_plot_action = self.make_action(
            "&Plot", icon="document-page-setup",
            tip="Generate plots", slot=self.plot)

        help_about_action = self.make_action(
            "&About", icon="help-about",
            tip="About this program...", slot=self.about)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        tools_menu = menubar.addMenu("&Tools")
        help_menu = menubar.addMenu("&Help")

        self.add_actions(
            file_menu, [file_new_action, file_open_action, file_save_action,
                        file_save_as_action, None, file_quit_action])
        self.add_actions(
            tools_menu, [tools_domain_action,
                         tools_simulate_action, tools_plot_action])
        help_menu.addAction(help_about_action)

        toolbar = QtGui.QToolBar()
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.add_actions(
            toolbar, [file_new_action, file_open_action, file_save_action,
                      None, tools_domain_action, tools_simulate_action,
                      tools_plot_action, None, file_quit_action])
        self.addToolBar(toolbar)

    def init_module_toolbar(self):
        """ Generate toolbar with buttons representing optical modules. """
        module_toolbar = QtGui.QToolBar()

        gaussian_action = self.make_action(
            "Gaussian", slot=functools.partial(self.add_module, GuiGaussian))
        sech_action = self.make_action(
            "Sech", slot=functools.partial(self.add_module, GuiSech))
        fibre_action = self.make_action(
            "Fibre", slot=functools.partial(self.add_module, GuiFibre))

        self.add_actions(
            module_toolbar, [gaussian_action, sech_action, fibre_action])
        self.addToolBar(QtCore.Qt.LeftToolBarArea, module_toolbar)

    def init_module_browser(self):
        """ Generate a tabbed browser representing an optical system. """
        module_browser = QtGui.QTabWidget()
        module_browser.setMovable(True)
        module_browser.setTabsClosable(True)
        module_browser.setUsesScrollButtons(True)

        self.setCentralWidget(module_browser)

    def make_action(self, text, shortcut=None, icon=None, tip=None,
                    slot=None, signal="triggered()"):
        """ Helper function to make actions for menu and toolbar. """
        action = QtGui.QAction(text, self)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if icon is not None:
            action.setIcon(QtGui.QIcon.fromTheme(icon))
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        return action

    @staticmethod
    def add_actions(target, actions):
        """ Helper function to add a list of actions to target. """
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def add_module(self, module):
        """ Generate module and add to module viewer. """
        module_label = self.sender().text()
        module_viewer = self.centralWidget()
        # If icon available, use: addTab(optical_module, icon, text)
        module_viewer.addTab(module(), module_label)

    def new_file(self):
        """ Create a new simulation. """
        pass

    def open_file(self):
        """ Open an existing simulation. """
        pass

    def save_file(self):
        """ Save current simulation. """
        pass

    def save_file_as(self):
        """ Set location for saving current simulation. """
        pass

    @staticmethod
    def quit_program():
        """ Exit pyofss-gui. """
        QtGui.qApp.quit()

    def configure_domain(self):
        """ Configure domain settings for the simulation. """
        self.gui_domain.exec_()

    def simulate(self):
        """ Start a simulation. """
        self.system = System(self.gui_domain())

        module_viewer = self.centralWidget()
        for tab in range(module_viewer.count()):
            module = module_viewer.widget(tab)
            self.system.add(module())

        # Set minimum and maximum to zero, progress bar shows a busy indicator:
        progress = QtGui.QProgressDialog(
            "Running simulation...", "OK", 0, 0, self)
        progress.setWindowTitle("Simulation progress")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setAutoReset(False)
        progress.setAutoClose(False)
        progress.show()

        # Change to busy cursor to indicate waiting:
        QtGui.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.WaitCursor))
        QtGui.qApp.processEvents()

        time.sleep(0.5)

        self.system.run()

        # Set progress bar to maximum (deactivates busy indicator):
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setValue(100)
        progress.setLabelText("Simulation complete.")

        QtGui.QApplication.restoreOverrideCursor()

    def plot(self):
        """ Open a plotting dialog. """
        gui_plotter = GuiPlotter(self.system)
        gui_plotter.exec_()

    def about(self):
        """ Open an about dialog. """
        pass


def main():
    """ Generate application. """
    # Uncomment the following two lines to force the "Cleanlooks" style:
    #~style = QtGui.QStyleFactory.create('Cleanlooks')
    #~QtGui.QApplication.setStyle(style)

    app = QtGui.QApplication(sys.argv)
    gui_system = GuiSystem()
    gui_system.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

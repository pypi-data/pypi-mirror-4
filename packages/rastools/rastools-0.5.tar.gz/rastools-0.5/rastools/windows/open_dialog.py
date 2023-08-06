# vim: set et sw=4 sts=4:

# Copyright 2012 Dave Hughes.
#
# This file is part of rastools.
#
# rastools is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# rastools is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# rastools.  If not, see <http://www.gnu.org/licenses/>.

"""Module implementing the file open dialog"""

from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )

import os

import pkg_resources
from PyQt4 import QtCore, QtGui, uic

from rastools.windows import get_ui_file


class OpenDialog(QtGui.QDialog):
    "Implements the file/open dialog"

    def __init__(self, parent=None):
        super(OpenDialog, self).__init__(parent)
        self.ui = uic.loadUi(get_ui_file('open_dialog.ui'), self)
        # Read the last-used lists
        self.settings = self.parent().settings
        self.settings.beginGroup('last_used')
        try:
            count = self.settings.beginReadArray('data_files')
            try:
                for i in range(count):
                    self.settings.setArrayIndex(i)
                    self.ui.data_file_combo.addItem(
                        self.settings.value('path'))
            finally:
                self.settings.endArray()
            self.ui.data_file_combo.setEditText(
                self.settings.value('data_file', ''))
            count = self.settings.beginReadArray('channel_files')
            try:
                for i in range(count):
                    self.settings.setArrayIndex(i)
                    self.ui.channel_file_combo.addItem(
                        self.settings.value('path'))
            finally:
                self.settings.endArray()
            self.ui.channel_file_combo.setEditText(
                self.settings.value('channel_file', ''))
        finally:
            self.settings.endGroup()
        # Connect up signals
        self.ui.data_file_combo.editTextChanged.connect(self.data_file_changed)
        self.ui.data_file_button.clicked.connect(self.data_file_select)
        self.ui.channel_file_button.clicked.connect(self.channel_file_select)
        self.data_file_changed()

    def accept(self):
        "Called when the user closes the dialog to open a file"
        super(OpenDialog, self).accept()
        # When the dialog is accepted insert the current filenames at the top
        # of the combos or, if the entry already exists, move it to the top of
        # the combo list
        i = self.ui.data_file_combo.findText(
            self.ui.data_file_combo.currentText())
        if i == -1:
            self.ui.data_file_combo.addItem(
                self.ui.data_file_combo.currentText())
        else:
            self.ui.data_file_combo.insertItem(
                0, self.ui.data_file_combo.currentText())
            self.ui.data_file_combo.setCurrentIndex(0)
            self.ui.data_file_combo.removeItem(i + 1)
        if str(self.ui.channel_file_combo.currentText()) != '':
            i = self.ui.channel_file_combo.findText(
                self.ui.channel_file_combo.currentText())
            if i == -1:
                self.ui.channel_file_combo.addItem(
                    self.ui.channel_file_combo.currentText())
            else:
                self.ui.channel_file_combo.insertItem(
                    0, self.ui.channel_file_combo.currentText())
                self.ui.channel_file_combo.setCurrentIndex(0)
                self.ui.channel_file_combo.removeItem(i + 1)
        # Keep the drop-downs to a reasonable size
        while self.ui.data_file_combo.count() > self.ui.data_file_combo.maxCount():
            self.ui.data_file_combo.removeItem(
                self.ui.data_file_combo.count() - 1)
        while self.ui.channel_file_combo.count() > self.ui.channel_file_combo.maxCount():
            self.ui.channel_file_combo.removeItem(
                self.ui.channel_file_combo.count() - 1)
        # Only write the last-used lists when the dialog is accepted (not when
        # cancelled or just closed)
        self.settings.beginGroup('last_used')
        try:
            self.settings.beginWriteArray(
                'data_files', self.ui.data_file_combo.count())
            try:
                for i in range(self.ui.data_file_combo.count()):
                    self.settings.setArrayIndex(i)
                    self.settings.setValue(
                        'path', self.ui.data_file_combo.itemText(i))
            finally:
                self.settings.endArray()
            self.settings.setValue(
                'data_file', self.ui.data_file_combo.currentText())
            self.settings.beginWriteArray(
                'channel_files', self.ui.channel_file_combo.count())
            try:
                for i in range(self.ui.channel_file_combo.count()):
                    self.settings.setArrayIndex(i)
                    self.settings.setValue(
                        'path', self.ui.channel_file_combo.itemText(i))
            finally:
                self.settings.endArray()
            self.settings.setValue(
                'channel_file', self.ui.channel_file_combo.currentText())
        finally:
            self.settings.endGroup()

    @property
    def data_file(self):
        "Returns the current content of the data_file combo"
        result = str(self.ui.data_file_combo.currentText())
        if result:
            return result
        else:
            return None

    @property
    def channel_file(self):
        "Returns the current content of the channel_file combo"
        result = str(self.ui.channel_file_combo.currentText())
        if result:
            return result
        else:
            return None

    @property
    def multi_layer(self):
        "Returns True if the multi-layer open-mode is selected"
        return self.ui.multi_layer_radio.isChecked()

    def data_file_changed(self, value=None):
        "Called to update the dialog buttons when the data_file changes"
        if value is None:
            value = self.ui.data_file_combo.currentText()
        self.ui.button_box.button(
            QtGui.QDialogButtonBox.Ok).setEnabled(value != '')

    def data_file_select(self):
        "Called when the user clicks on Browse... next to Data file"
        QtGui.QApplication.instance().setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            from rastools.data_parsers import DATA_PARSERS
        finally:
            QtGui.QApplication.instance().restoreOverrideCursor()
        filter_map = dict(
            ('{name} ({exts})'.format(
                    name=self.tr(label),
                    exts=' '.join('*' + ext for ext in exts)),
                exts[0])
            for (_, exts, label) in DATA_PARSERS
        )
        filters = ';;'.join(
            [
                str(self.tr('All data files (%s)')) % ' '.join(
                    '*' + ext
                    for (_, exts, _) in DATA_PARSERS
                    for ext in exts
                )
            ] + sorted(filter_map.keys())
        )
        filename = QtGui.QFileDialog.getOpenFileName(
            self, self.tr('Select data file'), os.getcwd(), filters)
        if filename:
            os.chdir(os.path.dirname(str(filename)))
            self.ui.data_file_combo.setEditText(filename)

    def channel_file_select(self):
        "Called when the user clicks on Browse... next to Channel file"
        filename = QtGui.QFileDialog.getOpenFileName(
            self, self.tr('Select channel file'), os.getcwd(),
            self.tr('Text files (*.txt *.TXT);;All files (*)'))
        if filename:
            os.chdir(os.path.dirname(str(filename)))
            self.ui.channel_file_combo.setEditText(filename)


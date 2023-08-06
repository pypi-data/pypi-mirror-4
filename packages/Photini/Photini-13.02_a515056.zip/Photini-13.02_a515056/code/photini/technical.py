# -*- coding: utf-8 -*-
##  Photini - a simple photo metadata editor.
##  http://github.com/jim-easterbrook/Photini
##  Copyright (C) 2012-13  Jim Easterbrook  jim@jim-easterbrook.me.uk
##
##  This program is free software: you can redistribute it and/or
##  modify it under the terms of the GNU General Public License as
##  published by the Free Software Foundation, either version 3 of the
##  License, or (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see
##  <http://www.gnu.org/licenses/>.

from datetime import datetime

from PyQt4 import QtGui, QtCore

class DateAndTimeWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        # date
        self.date = QtGui.QDateEdit()
        self.date.setDisplayFormat(' yyyy-MM-dd')
        self.date.setCalendarPopup(True)
        self.date.setSpecialValueText(' ')
        self.date.editingFinished.connect(self.new_date_time)
        layout.addWidget(self.date)
        # time
        self.time = QtGui.QTimeEdit()
        self.time.setDisplayFormat(' hh:mm:ss')
        self.time.setSpecialValueText(' ')
        self.time.editingFinished.connect(self.new_date_time)
        layout.addWidget(self.time)
        # clear button
        clear_button = QtGui.QPushButton('clear')
        clear_button.clicked.connect(self.clear)
        layout.addWidget(clear_button)
        # set button
        set_button = QtGui.QPushButton('set')
        set_button.clicked.connect(self.set_default)
        layout.addWidget(set_button)

    datetime_changed = QtCore.pyqtSignal(datetime)
    def new_date_time(self):
        date = self.date.date()
        time = self.time.time()
        print date, time
##        if date != self.date.minimumDate() and time != self.time.minimumTime():
##            self.datetime_changed.emit(
##                QtCore.QDateTime(date, time).toPyDateTime())
##        if date == self.date.minimumDate() and time == self.time.minimumTime():
##            self.datetime_changed.emit(datetime.min)

    def set_default(self):
        now = datetime.now()
        self.setDate(now.date())
        self.setTime(now.time())

    def clear(self):
        self.clearDate()
        self.clearTime()

    def clearDate(self):
        self.date.setSpecialValueText(' ')
        self.date.setDate(self.date.minimumDate())
        self.date.setReadOnly(True)

    def clearTime(self):
        self.time.setSpecialValueText(' ')
        self.time.setTime(self.time.minimumTime())
        self.time.setReadOnly(True)

    def setMultipleDate(self):
        self.date.setSpecialValueText('<multiple>')
        self.date.setDate(self.date.minimumDate())
        self.date.setReadOnly(True)

    def setMultipleTime(self):
        self.time.setSpecialValueText('<multiple>')
        self.time.setTime(self.time.minimumTime())
        self.time.setReadOnly(True)

    def setDate(self, value):
        self.date.setDate(value)
        self.date.setReadOnly(False)

    def setTime(self, value):
        self.time.setTime(value)
        self.time.setReadOnly(False)

class Technical(QtGui.QWidget):
    def __init__(self, config_store, image_list, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.config_store = config_store
        self.image_list = image_list
        self.setLayout(QtGui.QGridLayout())
        self.widgets = dict()
        # date and time
        date_group = QtGui.QGroupBox('Date and time')
        date_group.setLayout(QtGui.QFormLayout())
        # taken
        self.widgets['taken'] = DateAndTimeWidget()
        self.widgets['taken'].datetime_changed.connect(self.new_taken)
        date_group.layout().addRow('Taken', self.widgets['taken'])
        # digitised
        self.widgets['digitised'] = DateAndTimeWidget()
        self.widgets['digitised'].datetime_changed.connect(self.new_digitised)
        date_group.layout().addRow('Digitised', self.widgets['digitised'])
        # modified
        self.widgets['modified'] = DateAndTimeWidget()
        self.widgets['modified'].datetime_changed.connect(self.new_modified)
        date_group.layout().addRow('Modified', self.widgets['modified'])
        self.layout().addWidget(date_group, 0, 0)
        # other
        other_group = QtGui.QGroupBox('Other')
        other_group.setLayout(QtGui.QFormLayout())
        # orientation
        self.orientation = QtGui.QComboBox()
        self.orientation.addItem('normal', 1)
        self.orientation.addItem('rotate -90', 6)
        self.orientation.addItem('rotate +90', 8)
        self.orientation.addItem('rotate 180', 3)
        self.orientation.addItem('reflect left-right', 2)
        self.orientation.addItem('reflect top-bottom', 4)
        self.orientation.addItem('reflect tr-bl', 5)
        self.orientation.addItem('reflect tl-br', 7)
        self.orientation.addItem('multiple', -1)
        self.orientation.currentIndexChanged.connect(self.new_orientation)
        other_group.layout().addRow('Orientation', self.orientation)
        self.layout().addWidget(other_group, 0, 1)
        # disable until an image is selected
        for key in self.widgets:
            self.widgets[key].setEnabled(False)
        self.orientation.setEnabled(False)

    def refresh(self):
        pass

    def new_taken(self, value):
        self._new_value('taken', value)

    def new_digitised(self, value):
        self._new_value('digitised', value)

    def new_modified(self, value):
        self._new_value('modified', value)

    @QtCore.pyqtSlot(int)
    def new_orientation(self, index):
        value, OK = self.orientation.itemData(index).toInt()
        if value < 1 or not OK:
            self._update_orientation()
            return
        for image in self.image_list.get_selected_images():
            image.metadata.set_item('orientation', value)
            image.pixmap = None
            image.load_thumbnail()

    def _new_value(self, key, value):
        if value == datetime.min:
            value = None
        for image in self.image_list.get_selected_images():
            image.metadata.set_item('date_%s' % key, value)
        self._update_date(key)
        self._update_time(key)

    def _update_date(self, key):
        value = None
        for image in self.image_list.get_selected_images():
            new_value = image.metadata.get_item('date_%s' % key).date()
            if value and new_value != value:
                self.widgets[key].setMultipleDate()
                return
            value = new_value
        if value:
            self.widgets[key].setDate(value)
        else:
            self.widgets[key].clearDate()

    def _update_time(self, key):
        value = None
        for image in self.image_list.get_selected_images():
            new_value = image.metadata.get_item('date_%s' % key).time()
            if value and new_value != value:
                self.widgets[key].setMultipleTime()
                return
            value = new_value
        if value:
            self.widgets[key].setTime(value)
        else:
            self.widgets[key].clearTime()

    def _update_orientation(self):
        value = None
        for image in self.image_list.get_selected_images():
            new_value = image.metadata.get_item('orientation')
            if value and new_value != value:
                value = -1
                break
            value = new_value
        if not value:
            value = 1
        self.orientation.setCurrentIndex(self.orientation.findData(value))

    @QtCore.pyqtSlot(list)
    def new_selection(self, selection):
        if not selection:
            for key in self.widgets:
                self.widgets[key].clear()
                self.widgets[key].setEnabled(False)
            self.orientation.setCurrentIndex(self.orientation.findData(1))
            self.orientation.setEnabled(False)
            return
        for key in self.widgets:
            self.widgets[key].setEnabled(True)
            self._update_date(key)
            self._update_time(key)
        self.orientation.setEnabled(True)
        self._update_orientation()

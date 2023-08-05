# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
The PBDateEdit provides a date input box with more flexible entry.

It also supports null dates which is something QDateEdit does not.
"""

from PySide import QtCore, QtGui
from button_edit import PBButtonEdit, Property
import datetime

import fuzzyparsers

from qtalchemy import fromQType, toQType

class DateValidator(QtGui.QValidator):
    def __init__(self,parent=None):
        QtGui.QValidator.__init__(self,parent)

    def fixup(self,input):
        if input == "":
            return ""
        try:
            date = fuzzyparsers.parse_date(input)
        except:
            return ""
        #input.replace(0,input.length(),date.strftime("%x"))
        print date.strftime("%x")
        return date.strftime("%x")

    def validate(self,input,pos):
        try:
            date = fuzzyparsers.parse_date(input)
            return QtGui.QValidator.Acceptable,input,pos
        except Exception,e:
            return QtGui.QValidator.Intermediate,input,pos
    

class PBDateEdit(PBButtonEdit):
    """
    PBDateEdit is a QLineEdit derivative that parses input strings into dates 
    with the fuzzyparsers python package.  A QCalendarWidget is available 
    by clicking a button to the right of the edit or pressing F4.
    """
    def __init__(self,parent=None):
        PBButtonEdit.__init__(self,parent)
        self.setValidator(DateValidator())
        self.button.setIcon(QtGui.QIcon(':/qtalchemy/widgets/view-calendar.ico'))
        self.editingFinished.connect(self.transform)
        x = self.sizePolicy()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,x.verticalPolicy())

    def minimumSizeHint(self):
        buttonWidth = self.style().pixelMetric(QtGui.QStyle.PM_ScrollBarExtent)
        x = PBButtonEdit.minimumSizeHint(self)
        x.setWidth(len(datetime.date.today().strftime("%x"))*9+buttonWidth)
        return x

    def sizeHint(self):
        buttonWidth = self.style().pixelMetric(QtGui.QStyle.PM_ScrollBarExtent)
        x = PBButtonEdit.sizeHint(self)
        x.setWidth(len(datetime.date.today().strftime("%x"))*9+buttonWidth)
        return x

    def date(self):
        x = self.text()
        if x == "":
            return None
        else:
            return toQType(fuzzyparsers.parse_date(x))

    def setDate(self,v):
        v = fromQType(v)
        if v is None:
            self.setText("")
        else:
            self.setText(v.strftime("%x"))

    date = Property("QDate", date, setDate)

    def transform(self):
        x = self.text()
        if x != "":
            self.setDate(toQType(fuzzyparsers.parse_date(x)))

    def date_selected(self,date):
        self.setDate(date)
        self.calendar.close()
        #self.calendar = None

    def buttonPress(self):
        PBButtonEdit.buttonPress(self)
        self.calendar = QtGui.QCalendarWidget()
        self.calendar.setWindowFlags(QtCore.Qt.Popup)
        if self.date is not None:
            self.calendar.setSelectedDate(self.date)
        self.calendar.activated.connect(self.date_selected)
        self.calendar.clicked.connect(self.date_selected)
        self.calendar.move(self.mapToGlobal(self.rect().bottomLeft()))
        self.calendar.show()
        self.calendar.setFocus(QtCore.Qt.PopupFocusReason)

# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
The search dialog is a very high level GUI element of the qtalchemy library.  It
utilizes the DomainEntity to provide descriptive details of the objects to query
in these search dialogs. 
"""

from qtalchemy import *
from sqlalchemy.orm import mapper, create_session, relation, object_session
import sqlalchemy.sql.expression as expr
from PySide import QtGui, QtCore, QtDeclarative

class QuickList(QtGui.QWidget):
    """
    This base class gathers a search edit and table together in a single dialog.
    """
    def __init__(self, qml, ssrc, entityCls, parent=None, extensionId=None):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.Dialog)

        self.setProperty("ExtensionId", extensionId)

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        searchLayout = QtGui.QHBoxLayout()
        vbox.addLayout(searchLayout)
        searchLabel = QtGui.QLabel("&Search: ")
        searchLayout.addWidget(searchLabel)
        self.searchEdit = QtGui.QLineEdit()
        self.searchEdit.returnPressed.connect(self.resetSearch)
        searchLabel.setBuddy(self.searchEdit)
        searchLayout.addWidget(self.searchEdit)
        self.searchGo = QtGui.QPushButton("&Refresh")
        searchLayout.addWidget(self.searchGo)
        self.searchGo.clicked.connect(self.resetSearch)

        self.ssrc = ssrc
        self.entity = entityCls(ssrc, self)
        self.base_query, converter = self.entity.list_query_converter()

        self.model = QueryTableModel(self.base_query, ssrc=ssrc, objectConverter=converter)
        
        self.view = LayoutWidget(vbox,QtDeclarative.QDeclarativeView())
        context = self.view.rootContext()
        context.setContextProperty("myModel", self.model)
        self.view.setSource(QtCore.QUrl.fromLocalFile(qml))
        
        self.setFocusProxy(self.searchEdit)

    def resetSearch(self):
        if self.searchEdit.text() != "":
            like_str = "%%%s%%"%(self.searchEdit.text(),)
            filter_cols = [c.ilike(like_str) for c in self.entity.list_search_columns]

            self.model.query = self.base_query.filter(expr.or_(*tuple(filter_cols)))
        else:
            self.model.query = self.base_query

        self.model.reset_content_from_session()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Down:
            self.view.setFocus(QtCore.Qt.TabFocusReason)
            e.accept()
        else:
            QtGui.QDialog.keyPressEvent(self, e)

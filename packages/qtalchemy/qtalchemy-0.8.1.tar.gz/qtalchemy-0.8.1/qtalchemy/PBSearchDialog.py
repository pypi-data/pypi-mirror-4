# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
The search dialog is a very high level GUI element of the qtalchemy library.  It utilizes 
the DomainEntity to provide descriptive details of the objects to query in these search dialogs.
"""

from PyQtHelpers import *
from sqlalchemy.orm import mapper, create_session, relation, object_session
import sqlalchemy.sql.expression as expr
from sqlalchemy_helper import *
import sqlalchemy
from qtalchemy.widgets import TableView
from PyQtModels import *

from commands import Command, BoundCommandMenu

class PBSearchableListDialog(QtGui.QDialog):
    """
    This base class gathers a search edit and table together in a single dialog.
    
    This class is now deprecated in favor of :class:`qtalchemy.ext.QueryDataView`.
    """
    def __init__(self, parent=None, extensionId=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Dialog)

        self.setObjectName(extensionId)

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
 
        self.table = TableView()
        vbox.addWidget(self.table)
        
        self.setFocusProxy(self.searchEdit)

    def resetSearch(self):
        if self.searchEdit.text() != "":
            like_str = "%%%s%%"%(self.searchEdit.text(),)
            filter_cols = [c.ilike(like_str) for c in self.entity.list_search_columns]

            self.table.model().query = self.base_query.filter(expr.or_(*tuple(filter_cols)))
        else:
            self.table.model().query = self.base_query

        self.table.model().reset_content_from_session()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Down:
            self.table.setFocus(QtCore.Qt.TabFocusReason)
            e.accept()
        else:
            QtGui.QDialog.keyPressEvent(self, e)

class PBSearchDialog(PBSearchableListDialog):
    """
    This class is intended to be used principally by the PBKeyEdit to provide a
    graphical search dialog which is a little more featureful than can be
    packed into a basic combo box.

    This class is now deprecated in favor of
    :class:`qtalchemy.ext.QueryDataView`.
    """
    def __init__(self, ssrc, entityCls, parent=None):
        extensionId = "%s/Search" % (entityCls.__name__, )

        PBSearchableListDialog.__init__(self, parent, extensionId=extensionId)
        self.setWindowTitle("Search")

        self.ssrc = ssrc
        self.entity = entityCls(ssrc, self)
        self.base_query, converter = self.entity.list_query_converter()

        self.table.setModel(QueryTableModel(self.base_query, ssrc=ssrc, objectConverter=converter), 
                            extensionId=suffixExtId(self, "Table"))

        self.toolbar = LayoutWidget(self.layout(), QtGui.QToolBar(self))
        buttonbox = LayoutWidget(self.layout(),QtGui.QDialogButtonBox())

        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=False)
        self.bindings.fillToolbar(self.toolbar)

        # We might prefer AcceptRole for the 'select button', but that caused
        # default button grief.  In particular, it made 'Select' a default
        # button, but that caused 'enter' on the search edit to also select in
        # addition to refreshing the search.
        select = buttonbox.addButton("Selec&t", QtGui.QDialogButtonBox.ActionRole)
        buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)

        select.clicked.connect(self.selectCurrent)
        buttonbox.rejected.connect(self.close)
        self.table.activated.connect(self.select)

        self.table.model().reset_content_from_session()
        
        self.geo = WindowGeometry(self, position=False)

    def select(self, index):
        self.selected_id = self.table.model().objectConverter(index.internalPointer())
        self.close()

    def selectedItem(self, class_, session):
        if hasattr(self,"selected_id"):
            return session.query(class_).filter(self.entity.key_column==self.selected_id).one()

    def selectCurrent(self):
        self.select(self.table.selectedIndexes()[0])

class PBMdiTableView(PBSearchableListDialog):
    """
    This class is now deprecated in favor of :class:`qtalchemy.ext.QueryDataView`.
    """
    def __init__(self, ssrc, entityCls):
        extensionId = "%s/MDISearch" % (entityCls.__name__, )

        PBSearchableListDialog.__init__(self, extensionId=extensionId)

        self.ssrc = ssrc
        self.entity = entityCls(ssrc, self)
        self.base_query, converter = self.entity.list_query_converter()
        self.table.setModel(QueryTableModel(self.base_query, ssrc=ssrc,objectConverter=converter),
                            extensionId=suffixExtId(self, "Table"))
        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=True)

        self.table.model().reset_content_from_session()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            e.ignore()
        else:
            PBSearchableListDialog.keyPressEvent(self, e)

def colAttr(col):
    return col.property.columns[0].name

class PBTableTab(QtGui.QWidget):
    """
    This class is now deprecated in favor of :class:`qtalchemy.ext.QueryDataView`.
    """
    def __init__(self, parent, ssrc, entityCls, filters=None, query=None, extensionId=None, objectConverter=None):
        QtGui.QWidget.__init__(self, parent)

        self.ssrc = ssrc
        self.entity = entityCls(ssrc, parent)
        if query is None:
            self.query, self.objectConverter = self.entity.list_query_converter()
        else:
            self.query = query
            self.objectConverter = objectConverter
        self.filters = filters

        if extensionId is None:
            extensionId = suffixExtId(parent, entityCls.__name__)
        if extensionId is not None:
            self.setProperty("ExtensionId", extensionId)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.toolbar = LayoutWidget(layout, QtGui.QToolBar(self))
        # build the table and attach a model
        self.table = LayoutWidget(layout,TableView(extensionId=suffixExtId(self, "Table")))
        self.table.setModel(QueryTableModel(self.query, ssrc=ssrc, objectConverter=self.objectConverter), 
                            extensionId=suffixExtId(self, "Table"))

        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=True)
        self.bindings.fillToolbar(self.toolbar)

        dataContextNeeded = False
        if self.filters is not None:
            for col, value in self.filters:
                if callable(value):
                    dataContextNeeded = True

        if not dataContextNeeded:
            self.refresh()

    def refresh(self, dataContext=None):
        q=self.query
        if self.filters is not None:
            for col, value in self.filters:
                if callable(value):
                    value = value(dataContext)
                q = q.filter(col==value)
                self.entity.info[colAttr(col)] = value
        self.table.model().query = q

        self.table.model().reset_content_from_session()

# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from PySide import QtCore, QtGui
from qtalchemy import fromQType, modelMimeRectangle, writeTableColumnGeo, readTableColumnGeo
from viewbase import ViewBase

class TreeView(QtGui.QTreeView, ViewBase):
    """
    The TreeView provides a QTreeView override with support for the following elements:

    - row deletion with ctrl+delete for editable models
    - tab skipping read-only columns for editable models
    - clipboard copy of the selected blocks
    - load & save column geometry from user settings

    :param parent:  Qt parent widget for this table
    :param extensionId:  settings location for saving column geometry
    
    Note:  You are encouraged to use the extensionId parameter 
    in setModel rather than this one.  The setModel function determines 
    the available columns so that is a better point to specify the 
    related concern of saving column geometry.
    """
    def __init__(self, parent=None, extensionId=None):
        QtGui.QTreeView.__init__(self,parent)
        self.use_edit_tab_semantics = False
        self.setProperty("ExtensionId", extensionId)
        self.preservedRowState = None

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)

        # Ctrl+Delete should delete the row.
        self.del_key = QtGui.QShortcut(self)
        self.del_key.setKey(QtCore.Qt.CTRL + QtCore.Qt.Key_Delete)
        self.del_key.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.del_key.activated.connect(self.delKeyPressed)

        # hook up header events to save section widths
        header = self.header()
        header.sectionResized.connect(lambda x,y,z: self.saveSections())
        header.sectionAutoResize.connect(lambda x,y: self.saveSections())

    def setModel(self, model, extensionId=None):
        """
        :param model:  Qt model to connect to this table
        :param extensionId:  settings location for saving column geometry
        """
        if extensionId is not None:
            # clobber the parameter to __init__ if specified non-None here
            self.setProperty("ExtensionId", extensionId)

        QtGui.QTreeView.setModel(self, model)
        # hook up model resets to preserve selection across reloads
        self.model().modelAboutToBeReset.connect(self.preReset)
        self.model().modelReset.connect(self.postReset)
        if self.property("ExtensionId") is not None:
            readTableColumnGeo(self, self.property("ExtensionId"))

    def keyPressEvent(self, event):
        """
        Copy key copies selection 
        """
        if event.matches(QtGui.QKeySequence.Copy):
            cb = QtGui.QApplication.instance().clipboard()
            cb.setMimeData(modelMimeRectangle(self.model(), self.selectedIndexes()))
        else:
            QtGui.QTreeView.keyPressEvent(self,event)

    def edit(self, index, trigger, event):
        # At this point this method is overridden strictly as a place to set the flag to initiate the 
        # semantics of moveCursor to skip read-only cells in tabbing.
        inherited = QtGui.QTreeView.edit(self, index, trigger, event)
        if inherited:
            self.use_edit_tab_semantics = True
        return inherited

    def moveCursor(self, cursorAction, modifiers):
        if self.use_edit_tab_semantics == True:
            # Skip read-only cells.
            # We max out at iterating through the equivalent of 3 full rows 
            # because that probably indicates an unexpected situation.
            cell_max = self.model().columnCount(None) * 3
            iterations = 0
            if cursorAction == QtGui.QAbstractItemView.MoveNext:
                index = self.currentIndex()
                model = self.model()
                while True and iterations < cell_max:
                    iterations += 1
                    candidate = self.nextIndex(index)
                    if (model.flags(candidate) & QtCore.Qt.ItemIsEditable) == QtCore.Qt.ItemIsEditable:
                        return candidate
                    index = candidate
            elif cursorAction == QtGui.QAbstractItemView.MovePrevious:
                index = self.currentIndex()
                model = self.model()
                while True and iterations < cell_max:
                    iterations += 1
                    candidate = self.prevIndex(index)
                    if (model.flags(candidate) & QtCore.Qt.ItemIsEditable) == QtCore.Qt.ItemIsEditable:
                        return candidate
                    index = candidate
        return QtGui.QTreeView.moveCursor(self,cursorAction,modifiers)

    def columnIndices(self, index):
        m = self.model()
        return [m.index(i, 0, index) for i in range(m.rowCount(index))]

    def saveRowState(self, index):
        for cIndex in self.columnIndices(index):
            if self.isExpanded(cIndex):
                self.preservedRowState.expanded.append(self.model().objectConverter(cIndex.internalPointer()))
                self.saveRowState(cIndex)

    def preReset(self):
        self.preservedRowState = RowState()
        index = self.selectionModel().currentIndex()
        if index is not None and index.isValid():
            oc = self.model().objectConverter
            self.preservedRowState.current = oc(index.internalPointer())
        self.saveRowState(QtCore.QModelIndex())

    def loadRowState(self, index):
        oc = self.model().objectConverter
        for cIndex in self.columnIndices(index):
            id_ = oc(cIndex.internalPointer())
            if self.preservedRowState.isExpanded(id_):
                self.expand(cIndex)
                self.loadRowState(cIndex)
            if id_ == self.preservedRowState.current:
                self.setCurrentIndex(cIndex)

    def postReset(self):
        if self.preservedRowState is not None:
            # the current index is reset with-in the recursive loadRowState
            # there is a possibility that the parent of the selected index has been reset in some way and the current index wouldn't be found.
            self.loadRowState(QtCore.QModelIndex())


class RowState:
    def __init__(self):
        self.current = None
        self.expanded = []

    def isExpanded(self, id):
        return id in self.expanded

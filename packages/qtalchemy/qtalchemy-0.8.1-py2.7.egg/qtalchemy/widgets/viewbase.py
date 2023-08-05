# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from qtalchemy import writeTableColumnGeo

class ViewBase(object):
    """
    This handles functions common to TreeView and TableView.  At this 
    point, it's innards are not well encapsulated, but at least the 
    code is not duplicated.
    """
    def nextIndex(self,index):
        model = self.model()
        if index.column()+1 < model.columnCount(index.parent()):
            return model.index(index.row(),index.column()+1,index.parent())
        elif index.row()+1 < model.rowCount(index.parent()):
            return model.index(index.row()+1,0,index.parent())
        else:
            return model.index(0,0,index.parent())

    def prevIndex(self,index):
        model = self.model()
        if index.column() > 0:
            return model.index(index.row(),index.column()-1,index.parent())
        elif index.row() > 0:
            return model.index(index.row()-1,model.columnCount(index.parent())-1,index.parent())
        else:
            return model.index(model.rowCount(index.parent())-1,model.columnCount(index.parent())-1,index.parent())

    def delKeyPressed(self):
        #print "deleting"
        model = self.model()
        index = self.currentIndex()
        
        # We'll just call removeRows.  If the model doesn't support it, it returns False
        model.removeRows(index.row(),1,index.parent())

    def saveSections(self):
        if self.property("ExtensionId") is not None and self.model() is not None:
            writeTableColumnGeo(self, self.property("ExtensionId"))


# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from qtalchemy import *
from qtalchemy.widgets import *
from PySide import QtCore, QtGui
from sqlalchemy.orm import Query
import sqlalchemy.sql.expression as expr

class QueryManager(ModelObject):
    """
    Abstract base class for QueryManager classes.
    """
    def objectConverter(self, obj):
        """
        Return the key value from the passed obj.  This function is passed as
        the callable to the :class:`qtalchemy.QueryTableModel` which is in the
        :class:`QueryDataView`.
        """
        pass

    def fillQueryLayout(self, layout):
        """
        This function is called to give the manager a chance to create the
        widgets which let the user input query selections.
        
        :param layout:  a QLayout object to receive the input elements.
        
        The helper functions :func:`qtalchemy.LayoutLayout` and
        :func:`qtalchemy.LayoutWidget` are often helpful here.
        
        The return value is the widget that should be the focus proxy for the
        enclosing :class:`QueryDataView`.
        """
        pass

    def requery(self):
        """
        This function uses the input objects in constructed in
        :func:`fillQueryLayout` to construct a sqlalchemy.orm.Query object
        which will be associated with a session and queried by the
        :class:`QueryDataView`.
        """
        pass



class BasicQueryManager(QueryManager):
    """
    This is the most basic useful override of :class:`QueryManager` possible.
    It returns a query with the cols specified in the list of column names
    cols.
    
    :param cls: a sqlalchemy mapped class
    :param keyAttr: the primary key attribute name for cls
    :param cols: a list of attribute names desired in the view
    """
    def __init__(self, cls, keyAttr, cols):
        self.cls = cls
        self.keyAttr = keyAttr
        self.cols = cols
        self.sort_col = None
        self.sort_order = QtCore.Qt.AscendingOrder
    
    def objectConverter(self, obj):
        return getattr(obj, self.keyAttr)

    def sortChange(self, colIndex, order):
        self.sort_col = self.cols[colIndex]
        self.sort_order = order

    def sortOrder(self):
        try:
            return self.cols.index(self.sort_col), self.sort_order
        except:
            return -1, self.sort_order

    def fillQueryLayout(self, layout):
        # no query options at all
        return None

    def requery(self):
        cols = [getattr(self.cls, c) for c in [self.keyAttr]+self.cols]
        q = Query(cols)
        if self.sort_col is not None:
            sorts = {QtCore.Qt.DescendingOrder: expr.desc, QtCore.Qt.AscendingOrder: expr.asc}
            f = sorts[self.sort_order]
            q = q.order_by(f(getattr(self.cls, self.sort_col)))
        return q

class QueryDataView(QtGui.QWidget):
    """
    A QueryDataView displays a flexible interface element showing items in a
    tabular view.  The main flexibility of QueryDataView arises from queryMgr
    which is an instance of :class:`QueryManager`.  This object queryMgr can
    add an arbitrary collection of input widgets for user query parameters.
    The queryMgr is responsible for returning a sqlalchemy Query object back to
    the QueryDataView to display.
    
    :param parent:  a parent window (optionally pass as None)
    :param Session:  a session creator
    :param entityCls:  a command holding class from which the attributes in
            commandSets are taken
    :param commandSets:  a list of :class:`qtalchemy.CommandMenu` attributes in
        the entityCls
    :param queryMgr:  an instance of a :class:`QueryManager` class.

    >>> from sqlalchemy import Table, Column, String, Integer, MetaData, create_engine
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> 
    >>> from qtalchemy import *
    >>> from qtalchemy.ext.dataviews import *
    >>> from PySide import QtCore, QtGui
    >>> 
    >>> metadata = MetaData()
    >>> Base = declarative_base(metadata=metadata, cls=ModelObject)
    >>> 
    >>> class People(Base):
    ...     __table__ = Table('people', metadata,
    ...                     Column('id', Integer, primary_key=True),
    ...                     Column('f_name', String(50), info={"label": "First Name"}),
    ...                     Column('l_name', String(50), info={"label": "Last Name"}),
    ...                     Column('title', String(10), info={"label": "Title"}))
    ... 
    >>> class PeopleCommands(object):
    ...     def __init__(self, Session, parent):
    ...         pass
    ...
    >>> engine = create_engine("sqlite://")
    >>> metadata.bind = engine
    >>> metadata.create_all()
    >>> Session = PBSessionMaker(bind=engine)
    >>> 
    >>> app = qtapp()
    >>> view = QueryDataView(None, Session, PeopleCommands, [],
    ...                 BasicQueryManager(People, "id",
    ...                        "f_name l_name title".split(' ')))
    """
    def __init__(self, parent, Session, entityCls, commandSets, queryMgr):
        QtGui.QWidget.__init__(self, parent)

        self.Session = Session
        self.entity = entityCls(Session, parent)
        self.queryManager = queryMgr

        self.setObjectName("{0}_{1}".format(self.entity.__class__.__name__, self.queryManager.__class__.__name__))

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.toolbar = LayoutWidget(layout, QtGui.QToolBar(self))
        self.toolbar.setFocusPolicy(QtCore.Qt.NoFocus)
        x = LayoutLayout(layout, QtGui.QHBoxLayout())
        self.setFocusProxy(self.queryManager.fillQueryLayout(x))
        self.refreshBtn = LayoutWidget(x, QtGui.QPushButton("Refresh"))
        self.table = LayoutWidget(layout, TableView())
        if hasattr(self.queryManager, "sortChange"):
            self.table.setSortingEnabled(True)
            self.table.horizontalHeader().setSortIndicatorShown(True)
            self.table.horizontalHeader().sortIndicatorChanged.connect(self.queryManager.sortChange)
            self.table.horizontalHeader().sortIndicatorChanged.connect(lambda col, order: self.refresh())
            self.table.horizontalHeader().setSortIndicator(*self.queryManager.sortOrder())

        self.table.setModel(QueryTableModel(self.queryManager.requery(),
                ssrc=self.Session,
                objectConverter=self.queryManager.objectConverter),
                extensionId=suffixExtId(self, "Table"))

        self.refreshBtn.clicked.connect(self.refresh)

        self.bindings = [getattr(self.entity, c) for c in commandSets]
        self.bindings = [b.withView(self.table, bindDefault=True) for b in self.bindings]

        for i in range(len(self.bindings)):
            if i > 0:
                self.toolbar.addSeparator()
            self.bindings[i].fillToolbar(self.toolbar)
            self.bindings[i].preCommand.connect(self.preCommand)
            self.bindings[i].refresh.connect(self.refresh)

        self.refresh()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Return or e.key() == QtCore.Qt.Key_Enter:
            self.refresh()
            e.accept()
        elif e.key() == QtCore.Qt.Key_Down:
            self.table.setFocus(QtCore.Qt.TabFocusReason)
            e.accept()
        else:
            QtGui.QWidget.keyPressEvent(self, e)

    def preCommand(self):
        pass
        #print "in preCommand"

    def refresh(self):
        if self.table.model() is not None:
            self.table.model().query = self.queryManager.requery()
            self.table.model().reset_content_from_session()

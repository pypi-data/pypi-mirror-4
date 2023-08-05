# -*- coding: utf-8 -*-

from qtalchemy import MapperMixin, user_message, LayoutLayout, LayoutWidget, Message, CommandEvent
from PySide import QtCore, QtGui
from sqlalchemy.orm import mapper, create_session, relation, object_session, Query
import traceback
import sys

def MessageButtonsToQt(flags):
    result = QtGui.QMessageBox.NoButton
    for x in "Ok Cancel Yes No".split(' '):
        if flags & getattr(Message, x):
            result |= getattr(QtGui.QMessageBox, x)
    return result

def QtToMessageButtons(flags):
    result = 0
    for x in "Ok Cancel Yes No".split(' '):
        if flags & getattr(QtGui.QMessageBox, x):
            result |= getattr(Message, x)
    return result

def appMessage(parent, flags, msg):
    """
    Display a Qt message box.
    """
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    try:
        msgBox = QtGui.QMessageBox(parent)
        msgBox.setWindowTitle(QtGui.QApplication.applicationName())
        #if icon is not None:
        #    msgBox.setIcon( icon )
        msgBox.setText( msg )
        
        msgBox.setStandardButtons(MessageButtonsToQt(flags))
        return QtToMessageButtons(msgBox.exec_())
    finally:
        QtGui.QApplication.restoreOverrideCursor()

class SessionMessageBox(object):
    """
    This class is a callable to hook to a session message handler to display 
    messages for this session.
    """
    def __init__(self, parent=None):
        self.parent = parent

    def __call__(self, session, instance, flags, msg):
        # TODO:  pass icon
        # TODO:  pass exception info
        # TODO:  pass additional buttons
        # TODO:  allow data entry on instance (??) -- augment the message box with a bound data form
        msgBox = QtGui.QMessageBox(self.parent)
        msgBox.setWindowTitle(QtGui.QApplication.applicationName())
        #if icon is not None:
        #    msgBox.setIcon( icon )
        msgBox.setText( msg )
        
        msgBox.setStandardButtons(MessageButtonsToQt(flags))
        return QtToMessageButtons(msgBox.exec_())

def exception_message_box(e,text,parent=None,icon=None):
    """
    Extract exception information and display a message box with exception details in 
    a details extension of the message.
    """
    msg = QtGui.QMessageBox(parent)
    msg.setWindowTitle(QtGui.QApplication.applicationName())
    if icon is not None:
        msg.setIcon( icon )
    msg.setText( text )
    msg.setInformativeText( user_message(e) )
    exc_type, exc_value, exc_traceback = sys.exc_info()
    msg.setDetailedText( ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)) )
    msg.setStandardButtons( QtGui.QMessageBox.Ok )
    return msg.exec_()

def messaged_commit(session, parent):
    """
    This helper function displays a message to the user if the commit on the session fails.
    
    The message text is given by the user_message function.
    """
    try:
        session.commit()
    except Exception, e:
        exception_message_box(e,"There was an error saving the data.",parent=parent,icon=QtGui.QMessageBox.Warning)

class MapperDialog(QtGui.QDialog, MapperMixin):
    def __init__(self,parent):
        QtGui.QDialog.__init__(self,parent)

    def accept(self):
        self.submit()
        QtGui.QDialog.accept(self)

class BoundDialog(MapperDialog):
    """
    The BoundDialog class pulls together the :class:`MapperMixin` and 
    sqlalchemy session management.  There are functions to load and save a 
    data form.
    
    The typical set-up code for a BoundDialog object has the following in 
    __init__:

      - a call to setDataReader giving the table and key information to get a 
        record to display on screen
      - code setting up the widgets on the screen (particularly with calls to 
        the inherited :func:`MapperMixin.mapClass`)
      - a final call to self.readData with the initial record to display

    An application utilizing methods :func:`preCommandSave`, :func:`refresh`, 
    and :func:`readData` may re-implement :func:`load`, but it is recommended 
    to call add screen loaders with :func:`addLoader`.
    """
    def __init__(self, parent, session=None, flush=True):
        MapperDialog.__init__(self,parent)
        self.flush_on_close = flush
        self.session = session
        self.loaders = []

    def setDataReader(self, Session, tableClass, keyAttr):
        """
        :param Session:  Session class returned from sqlalchemy sessionmaker
        :param tableClass:  sqlalchemy mapped class with the root of the 
            data shown on this form
        :param keyAttr:  attribute of primary key in tableClass
        """
        self.Session = Session
        self.tableClass = tableClass
        self.keyAttr = keyAttr
        if self.tableClass is not None and self.keyAttr is not None:
            self.keyColumn = getattr(self.tableClass, self.keyAttr)

    def readData(self, row=None, rowKey=None, load=True):
        """
        If row is specified then row is expected to be an instance of
        self.tableClass.  If neither is specified, then no data is loaded and a
        new class of type self.tableType is created.  One can use either
        parameter for flexibility to specify the data to load by object or by
        primary key.

        :param row: row instance to map from the bound tableClass
        :param rowKey:  primary key value which will be loaded from the database 
            for display
        """
        if row is not None:
            self.main_row = row
            self.session = object_session(row)
        else:
            self.session = self.Session()
            if rowKey is None:
                self.main_row = self.tableClass()
                self.session.add(self.main_row)
            else:
                self.main_row = self.session.query(self.tableClass).filter(self.keyColumn==rowKey).one()

        if load:
            self._load()

    def addLoader(self, callable):
        """
        Add a collable taking the main row and which loads the data from this
        main row displaying it on the screen.
        
        :param callable:  callable taking self.main_row
        """
        self.loaders.append(callable)

    def _load(self):
        for l in self.loaders:
            l(self.main_row)
        self.load()

    def load(self):
        """
        This load method should connect mappers with
        :func:`WidgetAttributeMapper.connect_instance` and connect models with
        :func:`PBTableModel.reset_content_from_list`.  The default
        implementation of load does nothing.
        """
        pass

    def preCommandSave(self, event):
        """
        This function is a recommended slot for the preCommandSave signal of 
        :class:`BoundCommandMenu`.

        Application developers may call this function in tandem with 
        :func:`refresh` in the following way.
        
            >>> event = CommandEvent()
            >>> self.preCommandSave(event)        #doctest: +SKIP
            >>> if not event.aborted:             #doctest: +SKIP
            ...     # take some action with the persisted data
            ...     self.refresh(event)
        """
        try:
            event.savedDataContext = self.main_row
            MapperDialog.submit(self)
            if self.flush_on_close:
                self.flush()
                self.session.close()
        except Exception, e:
            self.session.rollback()
            exception_message_box(e,"There was an error saving data.",icon=QtGui.QMessageBox.Warning,parent=self)
            event.abort()

    def refresh(self, event):
        """
        This function is a recommended slot for the refresh signal of 
        :class:`BoundCommandMenu`.
        
        Note that it calls self.load which the application is expected to 
        provide (there is no default implementation).
        """
        self.readData(rowKey = getattr(event.savedDataContext, self.keyAttr), load=True)

    def commitAndRefresh(self):
        event  = CommandEvent()
        self.preCommandSave(event)
        if not event.aborted:
            self.refresh(event)

    def accept(self):
        event  = CommandEvent()
        self.preCommandSave(event)
        if not event.aborted:
            QtGui.QDialog.accept(self)

    def reject(self):
        MapperDialog.reject(self)
        if self.flush_on_close and self.session is not None:
            self.session.close()

    def flush(self):
        assert self.session is not None, "If flushing changes, we must have a session"
        self.session.commit()

def BoundDialogObject(parent,row):
    b = BoundDialog(parent)
    b.setDataReader(object_session(row), None, None)
    b.setWindowTitle(row.DialogTitle)

    main = QtGui.QVBoxLayout()
    b.setLayout(main)
    grid = LayoutLayout(main,QtGui.QFormLayout())

    m = b.mapClass(type(row))
    for col in row.DialogVisualElements:
        m.addBoundField(grid,col)
    m.connect_instance(row)

    buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox())
    buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
    buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
    buttonbox.accepted.connect(b.accept)
    buttonbox.rejected.connect(b.reject)

    b.show()
    b.exec_()

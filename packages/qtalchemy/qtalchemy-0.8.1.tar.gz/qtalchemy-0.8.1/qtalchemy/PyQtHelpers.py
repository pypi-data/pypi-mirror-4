# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
This module contains convenience functions used elsewhere in the qtalchemy library.

qtalchemy using API2 of PyQt so we need to enable that before importing PyQt4.  We 
do this here as an example and to prepare for the doc-tests.  Note that it is not
illegal to call sip.setapi twice, but the second call must agree in api version with
the first.

    >>> if qt_bindings == 'PyQt4':
    ...     import sip
    ...     sip.setapi('QString', 2)
    ...     sip.setapi('QVariant', 2)
"""

qt_bindings = 'PySide'
if qt_bindings == 'PyQt4':
    # we wish to only touch sip if we're PyQt4 based (otherwise sip is unnecessary)
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
from PySide import QtGui,QtCore
import datetime
import decimal
import re

# with this conditional, we abstract away this difference between pyqt and pyside
if QtCore.__name__.startswith("PySide"):
    Slot = QtCore.Slot
    Signal = QtCore.Signal
    Property = QtCore.Property
else:
    Slot = QtCore.pyqtSlot
    Signal = QtCore.pyqtSignal
    Property = QtCore.pyqtProperty

def fromQType(v, suggested=None):
    """
    This function takes a PyQt/PySide type and returns the most faithful representative of the item 
    in a native python type.
    
    (Basic) Examples:
    >>> type(fromQType(toQType(45)))
    <type 'int'>
    >>> fromQType(toQType(datetime.date.today()))==datetime.date.today()
    True
    """
    if hasattr(v, "toPyObject"):  # PyQt QVariant
        if v.isNull():
            return None
        v = v.toPyObject()
    elif hasattr(v, "toPyDateTime"):  # PyQt QDateTime
        if v.isNull():
            return None
        v = v.toPyDateTime()
    elif hasattr(v, "toPyDate"):  # PyQt QDate
        if v.isNull():
            return None
        v = v.toPyDate()
    elif hasattr(v, "toPyTime"):  # PyQt QTime
        if v.isNull():
            return None
        v = v.toPyTime()
    elif hasattr(v, "toPython"):  # PySide object
        if v.isNull():
            return None
        v = v.toPython()

    if suggested in (int, float, decimal.Decimal) and v=="":
        if suggested is decimal.Decimal:
            v = decimal.Decimal('0')
        else:
            v = suggested(0)
    elif suggested is datetime.date and isinstance(v,datetime.datetime):
        # TODO:  dangerous down-cast
        v = datetime.date(v.year,v.month,v.day)
    elif suggested is not None:
        try:
            is_ = isinstance(v,suggested)
        except TypeError as e:
            is_ = False

        if not is_:
            v = suggested(v)

    return v

def toQType(v, suggested=None, empty_zero=False):
    """
    This function takes a native python object and returns it in the most
    faithful way as a PyQt/PySide type.  For API 2, this means that basic types
    like str and int are returned unchanged.
    
    One notable caveat is that Qt does not have a decimal type so objects of
    type decimal.Decimal are returned as strings.  The rationale for this is
    that maintaining decimal exactness of decimals is almost always the right
    thing.
    
    Examples:
    >>> type(toQType(12))
    <type 'int'>
    >>> type(toQType("A string"))
    <type 'str'>
    >>> toQType(decimal.Decimal("12.34"))
    '12.34'
    >>> type(toQType(datetime.date(1979,1,9))) is QtCore.QDate
    True

    When the value `v` is None, we return a blank version of the suggested
    type.

    >>> toQType(None,suggested=str)
    ''
    >>> toQType(None,suggested=int)
    0
    """
    if isinstance(v, datetime.date):
        v = QtCore.QDate(v.year,v.month,v.day)
    elif isinstance(v, decimal.Decimal):
        if empty_zero and v == 0: 
            v = ""
        else:
            v = str(v)

    if v is None and suggested is not None:
        if suggested == datetime.date:
            v = QtCore.QDate()
        else:
            # I'm baffled, suggested appears to be passed as a python type
            # but the whole point here is to return Qt type!
            v = suggested()

    if type(v) in [int, float] and empty_zero and v == 0:
        return ""

    return v

def ButtonBoxButton(bb,b,role=None):
    """
    :func:`.ButtonBoxButton` is a convenience function which enables button
    construction and assignment on one line of application code.
    """
    #TODO:  The return from this function can be a button or Role constant ... positively bizzarre
    if role is None:
        bb.addButton(b)
    else:
        bb.addButton(b,role)
    return b

def FormRow(form,label,widget):
    """
    :func:`.FormRow` is a convenience function which enables widget
    construction and assignment on one line of application code.
    """
    form.addRow(label,widget)
    return widget

def LayoutLayout(host,inner):
    """
    :func:`.LayoutLayout` is a convenience function which enable layout
    construction and assignment on one line of application code.
    
    See also :func:`.LayoutWidget` :func:`.FormRow` :func:`.ButtonBoxButton`

        >>> app = qtapp()
        >>> class Item(QtGui.QDialog):
        ...     def __init__(self,parent=None):
        ...         QtGui.QDialog.__init__(self,parent)
        ...         vbox = QtGui.QVBoxLayout(self)
        ... 
        ...         form = LayoutLayout(vbox,QtGui.QFormLayout())
        ...         self.book_edit = FormRow(form,"&Book Title",QtGui.QLineEdit())
        ...         self.author_edit = FormRow(form,"&Author",QtGui.QLineEdit())
        ... 
        ...         self.buttons = LayoutWidget(vbox,QtGui.QDialogButtonBox())
        ...         self.ok = ButtonBoxButton(self.buttons,QtGui.QDialogButtonBox.Save)
        ...         self.cancel = ButtonBoxButton(self.buttons,QtGui.QDialogButtonBox.Cancel)
        >>> d = Item()
        >>> d.exec_()  #doctest: +SKIP
        0
    """
    host.addLayout(inner)
    return inner

def LayoutWidget(layout,widget):
    """
    :func:`.LayoutWidget` is a convenience function which enable widget
    construction and assignment on one line of application code.
    """
    layout.addWidget(widget)
    return widget

def writeTableColumnGeo(table,name):
    settings = QtCore.QSettings()
    settings.beginGroup(name)
    for i in range(table.model().columnCount(None)):
        settings.setValue("Column%02i"%i,table.columnWidth(i))
    settings.endGroup()

def readTableColumnGeo(table,name):
    settings = QtCore.QSettings()
    settings.beginGroup(name)
    ei = table.property("ExtensionId")
    table.setProperty("ExtensionId", None)
    total = sum([table.columnWidth(i) for i in range(table.model().columnCount(None))])
    defaults = None
    defaultTotal = None
    if hasattr(table.model(), "columnWidthRatios"):
        defaults = table.model().columnWidthRatios()
        defaults = [defaults[i] for i in range(table.model().columnCount(None))]
        if None not in defaults:
            defaultTotal = sum(defaults)
    for i in range(table.model().columnCount(None)):
        if settings.value("Column%02i"%i,-1) != -1:
            table.setColumnWidth(i,int(settings.value("Column%02i"%i,-1)))
        else:
            if defaults is not None and defaults[i] is not None:
                table.setColumnWidth(i, int(float(defaults[i]) * total / defaultTotal))
    table.setProperty("ExtensionId", ei)
    settings.endGroup()

def suffixExtId(parent, ext):
    id = parent.property("ExtensionId")
    if id is None:
        id = parent.objectName()
    if id is None:
        return ext
    else:
        return id+"/"+ext

class TabMenuHolder:
    def __init__(self, tab):
        self.tab = tab

        self.actSaveLast = QtGui.QAction("&Reopen to last viewed tab", self.tab)
        self.actSaveLast.setCheckable(True)
        self.actSaveThis = QtGui.QAction("&Reopen to current tab", self.tab)
        self.actSaveThis.setCheckable(True)

        self.tab.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tab.customContextMenuRequested.connect(self.contextMenu)

    def contextMenu(self, pnt):
        tb = self.tab.tabBar()
        if tb.tabAt(pnt) == self.tab.currentIndex():
            self.menu = QtGui.QMenu()
            self.menu.addAction(self.actSaveLast)
            self.menu.addAction(self.actSaveThis)
            self.menu.popup(self.tab.mapToGlobal(pnt))

    def setChecks(self, status):
        self.actSaveLast.setChecked(status == WindowGeometry.TAB_REOPEN_LAST)
        self.actSaveThis.setChecked(status == WindowGeometry.TAB_REOPEN_SPECIFIED)

class WindowGeometry(QtCore.QObject):
    """
    This class saves and restores the size and other geometry artifacts about 
    the passed QWidget.  It hooks the closeEvent by attaching itself as an 
    eventFilter to the passed QWidget.

    Table header geometry should be saved by passing an extensionId to 
    :func:`TableView.setModel` at this point.  This may change in the future.

    The geometry is persisted with QSettings under a name that is determined 
    by one of the following (with first items taking precedence).  This name 
    is determined in __init__ and saved for writing the settings later under 
    the same name.
    
    * name parameter
    * widget.property("ExtensionId")
    * widget.objectName()  (recommended)

    The QTabWidgets in the `tabs` list will have a context menu added on them 
    with options about how the tab selection should be recalled on reload.  They 
    can reopen the last opened, always reopen to a specific tab, or let it as 
    default (probably meaning the first tab is shown).

    :param widget: the QWidget for which to save & restore state
    :param name: optional identifier to associate this in the persistent state
    :param size: save & restore window size (default True)
    :param position: save & restore window position (default True)
    :param splitters: list of splitters to save position
    :param tabs: list of QTabWidgets whose tab selection should be managed/remembered
    """
    TAB_REOPEN_DEFAULT = 0
    TAB_REOPEN_LAST = 1
    TAB_REOPEN_SPECIFIED = 2

    def __init__(self, widget, name=None, size=True, position=True, splitters=None, tabs=None):
        QtCore.QObject.__init__(self, widget)

        self.widget = widget
        self.size = size
        self.position = position
        self.name = name
        if self.name is None:
            self.name = widget.property("ExtensionId")
        if self.name is None:
            self.name = widget.objectName()
        self.splitters = splitters if splitters else []
        self.tabs = tabs if tabs else []
        self.tabs = [TabMenuHolder(t) for t in self.tabs]

        for s_index in range(len(self.splitters)):
            self.splitters[s_index].splitterMoved.connect(lambda pos,index,x=s_index: self.updateSplitter(x,pos,index))

        self.tabActions = []
        for t_index in range(len(self.tabs)):
            self.tabs[t_index].tab.currentChanged.connect(lambda newSel,x = t_index: self.updateTab(x,newSel))
            self.tabs[t_index].actSaveLast.triggered.connect(lambda checked, kind=self.TAB_REOPEN_LAST, x=t_index: self.updateTabLastSave(x, checked, kind))
            self.tabs[t_index].actSaveThis.triggered.connect(lambda checked, kind=self.TAB_REOPEN_SPECIFIED, x=t_index: self.updateTabLastSave(x, checked, kind))

        self.restoreState()

        if hasattr(self.widget, "finished"):
            self.widget.finished.connect(self.finished)
        else:
            self.widget.installEventFilter(self)

    def finished(self, i):
        self.saveState(splitters=False, tabs=False)

    def eventFilter(self, obj, event):
        if obj is self.widget and event.type() == QtCore.QEvent.Close:
            self.saveState(splitters=False, tabs=False)
        return QtCore.QObject.eventFilter(self, obj, event)

    def saveState(self, splitters=True, tabs=True):
        """
        This saves the state of all controlled elements.  Some elements are 
        saved immediately when modified (such as splitters).  Thus we suppress 
        the state saving on close for these elements.

        :param splitters:  pass False to suppress the saving of the splitter 
            state for splitters passed in __init__
        :param tabs:  pass False to suppress the saving of the tab 
            state for tabs passed in __init__
        """
        settings = QtCore.QSettings()
        settings.beginGroup(self.name)
        if self.size and self.position:
            settings.setValue("geometry", self.widget.saveGeometry())
        elif self.size:
            settings.setValue("size", self.widget.size())
        elif self.position:
            settings.setValue("pos", self.widget.pos())
        
        if hasattr(self.widget, "saveState"):
            # I'm probably a QMainWindow
            settings.setValue("windowState", self.widget.saveState())

        if splitters:
            for splitter_index in range(len(self.splitters)):
                settings.setValue(self.splitter_persist_location(splitter_index),self.splitters[splitter_index].saveState())

        if tabs:
            for tab_index in range(len(self.tabs)):
                settings.setValue(self.tab_persist_location(tab_index, "to-reopen"), self.tabs[tab_index].tab.currentIndex())

        settings.endGroup()

    def restoreState(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.name)
        if self.size and self.position:
            if settings.value("geometry") is not None:
                self.widget.restoreGeometry(settings.value("geometry"))
        elif self.size:
            if settings.value("size") is not None:
                self.widget.resize(settings.value("size"))
        elif self.position:
            if settings.value("pos") is not None:
                self.widget.move(settings.value("pos"))
        
        if hasattr(self.widget, "saveState"):
            # I'm probably a QMainWindow
            if settings.value("windowState") is not None:
                self.widget.restoreState(settings.value("windowState"))
        
        for splitter_index in range(len(self.splitters)):
            state = settings.value(self.splitter_persist_location(splitter_index))
            if state is not None:
                self.splitters[splitter_index].restoreState(state)

        for tab_index in range(len(self.tabs)):
            reopen = int(settings.value(self.tab_persist_location(tab_index, "reopen-status"), self.TAB_REOPEN_LAST))
            self.tabs[tab_index].setChecks(reopen)
            state = settings.value(self.tab_persist_location(tab_index, "to-reopen"))
            if state is not None and reopen != self.TAB_REOPEN_DEFAULT:
                self.tabs[tab_index].tab.setCurrentIndex(int(state))
        settings.endGroup()

    def splitter_persist_location(self, splitter_index):
        splitter_name = self.splitters[splitter_index].objectName()
        if splitter_name in [None, ""]:
            splitter_name = str(splitter_index)
        return "splitter/{0}".format(splitter_name)

    def updateSplitter(self, splitter_index, pos, index):
        settings = QtCore.QSettings()
        settings.beginGroup(self.name)
        settings.setValue(self.splitter_persist_location(splitter_index),self.splitters[splitter_index].saveState())
        settings.endGroup()

    def tab_persist_location(self, tab_index, v):
        tab_name = self.tabs[tab_index].tab.objectName()
        if tab_name in [None, ""]:
            tab_name = str(tab_index)
        return "tab/{0}/{1}".format(tab_name, v)

    def updateTabLastSave(self, tab_index, checked, how):
        reopen = None
        tab_to_reopen = None
        if checked:
            reopen = how
            tab_to_reopen = self.tabs[tab_index].tab.currentIndex()
        else:
            reopen = self.TAB_REOPEN_DEFAULT

        if reopen is not None:
            self.tabs[tab_index].setChecks(reopen)

            settings = QtCore.QSettings()
            settings.beginGroup(self.name)
            settings.setValue(self.tab_persist_location(tab_index, "reopen-status"), reopen)
            if tab_to_reopen is not None:
                settings.setValue(self.tab_persist_location(tab_index, "to-repen"), tab_to_reopen)
            settings.endGroup()

    def updateTab(self, tab_index, newSel):
        settings = QtCore.QSettings()
        settings.beginGroup(self.name)
        if int(settings.value(self.tab_persist_location(tab_index, "reopen-status"), self.TAB_REOPEN_LAST)) == self.TAB_REOPEN_LAST:
            settings.setValue(self.tab_persist_location(tab_index, "to-reopen"), self.tabs[tab_index].tab.currentIndex())
        settings.endGroup()


class OnlineHelp(QtCore.QObject):
    """
    Install help buttons and an F1 event filter both of which direct to a web 
    url with appropriate anchor points (for context specific help).
    
    For context sensitive help, the F1 key is linked to the same URL with an 
    anchor suffix.  The suffix comes from the active control BoundFieldClass 
    property.  This property is set for controls bound by an :class:`InputYoke`.
    
    :param parent: the parent window to which help applies
    :param url: the URL to direct the user to when help is needed
    :param buttonBox:  optional QDialogButtonBox object to receive the help button
    :param button:  optional button to bind directly to the help URL
    :param contextHelp:  flag to determine whether the F1 key is bound for fields 
        with the BoundFieldClass property (default True)
    """
    def __init__(self, parent, url=None, buttonBox=None, button=None, contextHelp=True):
        QtCore.QObject.__init__(self, parent)
        self.parent = parent
        if url is None:
            url = "{0}_Screen.html".format(parent.objectName())
        self.url = url

        if buttonBox is not None:
            self.add_button(buttonBox)
        else:
            self.button = button
            self.button.clicked.connect(self.global_help)

        if contextHelp:
            self.parent.installEventFilter(self)

    def add_button(self, buttonBox):
        self.button = QtGui.QPushButton("Help", self.parent)
        self.button.clicked.connect(self.global_help)
        buttonBox.addButton(self.button, QtGui.QDialogButtonBox.HelpRole)

    def global_help(self):
        from qtalchemy import xplatform
        xplatform.xdg_open(self.url)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_F1:
            # iterate from the current focus up the parent chain looking for a 
            # qtalchemy yoke bound control with the BoundClassField property.
            prop = None
            focus = QtGui.QApplication.focusWidget()
            while focus is not None and focus is not self.parent:
                prop = focus.property("BoundClassField")
                if prop is None:
                    focus = focus.parentWidget()
                else:
                    break
            if prop is not None:
                self.context_help(prop)

        return QtCore.QObject.eventFilter(self, obj, event)

    def context_help(self, anchor):
        # reStructuredText anchors are sanitized rather harshly -- we must do likewise here
        anchor = re.sub('[._]', '-', anchor.lower())
        anchored = "{0}#{1}".format(self.url, anchor)
        from qtalchemy import xplatform
        xplatform.xdg_open(anchored)


def message_excepthook(type, value, tb):
    """
    Replace sys.excepthook with this function to display errors more gracefully 
    for an application which is not associated with a console.
    
    Refer to qtalchemy.xplatform.guiexcepthook for a lighter weight version of this.
    
    >>> import sys
    >>> from qtalchemy import *
    >>> sys.excepthook = message_excepthook
    """
    try:
        import traceback
        import qtalchemy.xplatform as xp

        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle(QtGui.QApplication.applicationName())
        msgBox.setIcon(QtGui.QMessageBox.Critical)
        
        if xp.is_windows():
            body = "An unhandled error was encountered.  Consider copying this entire message to an email to the program author by pressing Ctrl+C on this message.  Include a brief description of the actions leading to this error.\n\n{0}"
        else:
            body = "An unhandled error was encountered. Consider copying this entire message to an email to the program author.  Include a brief description of the actions leading to this error.\n\n{0}"

        tb2 = body.format(''.join(traceback.format_exception(type, value, tb, limit=3)))
        
        msgBox.setText( tb2 )
        
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.exec_()
    except:
        #raise
        import sys
        traceback.print_exception(type, value, tb, limit=None, file=sys.stderr)


_test_app = None

def qtapp():
    """
    A QApplication creator for test cases.  QApplication is a single-ton and 
    this provides a safe construction wrapper.
    
    >>> app=qtapp()
    >>> # put test code here
    """
    global _test_app
    _test_app = QtGui.QApplication.instance()
    if _test_app is None:
        _test_app = QtGui.QApplication([])
    return _test_app

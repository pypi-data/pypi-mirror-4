# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
Attach command descriptions and short-cut keys to python functions.  These 
command sets can be converted into QMenu and QToolbar objects.  Additionally, 
one can fill QDialogButtonBox classes.  Facilities are included for classifying 
and sorting the commands for global application consistency.
"""

import weakref
import inspect
from PyQtHelpers import *
from PySide import QtCore, QtGui

DROP_ACTION_TYPE="drop-action"

class Command(object):
    """
    This is a decorator for entity methods to mark them as methods that should be included 
    in the GUI command set in places with this entity.  This enables automatic generation of 
    button boxes and tool-bars.

    See :class:`BoundCommandMenu` for more details.
    """
    def __init__(self, descr, default=False, viewRelated=False, requireSelection=True, needs_reload=True, key=None, statusTip=None, iconFile=None, type="action", sort=500, mimeType=None):
        """
        :param descr: Text description of command for menu items
        :param default: Default command for item activation.
        :param viewRelated: True if this command must be activated in the presence of a view
        :param requireSelection: Set to false if the command function makes sense with-out a current object
        :param needs_reload: Set to false if the command does not modify the database in a way that would require refreshing the screen.
        :param key: shortcut key as given by QtCore.Qt.Key enumeration
        :param type: classifies the command for menu structure - new/view/action/delete are common options with special meanings to the sort algorithm
        """
        self.descr = descr
        self.viewRelated = viewRelated
        self.requireSelection = requireSelection
        self.default = default
        self.needs_reload = needs_reload
        self.iconFile = iconFile
        self.key = key
        self.statusTip = statusTip
        self.command_type = type
        self.sort = sort
        self.func = None

    def __call__(self, func):
        func._command_me = self
        func.descr = self.descr
        self.func = func
        return func

    def name(self):
        return self.func.func_name

    def action(self, parent):
        # drag & drop operations are not prompted by QAction gui events (and they must come with mime data)
        if self.command_type == DROP_ACTION_TYPE:
            return None

        action = QtGui.QAction(self.descr, parent)
        if self.key is not None:
            # type promotion to get around
            # https://bugreports.qt-project.org/browse/PYSIDE-19
            if isinstance(self.key, QtCore.Qt.Key):
                self.key = QtGui.QKeySequence(self.key)
            action.setShortcut(self.key)
        if self.statusTip is not None:
            action.setStatusTip(parent.tr(self.statusTip))
        if self.iconFile is not None:
            action.setIcon(QtGui.QIcon(self.iconFile))
        return action

    def sort_key(self):
        assert 0<=self.sort<1000, "We expect you to sort between 0 and 999 inclusive"
        action_map = {"new": 2, "view": 4, "action": 6, "delete": 8}
        try:
            actInt = action_map[self.command_type]
        except KeyError, e:
            actInt = 5
        return "{0:01f}{1:03f}".format(actInt, self.sort)

class CommandMenu(object):
    """
    The CommandMenu class defines a list of menu commands which can be incorporated 
    into menus or toolbars associated with some UI object.  Multiple CommandMenu 
    objects can be associated with a single class.  This enables modularity in 
    the menu structure.
    
    The principle interaction with CommandMenu is a method decorator 
    :func:`command` to add a command to the menu.  Additional decorators 
    are :func:`itemNew`, :func:`itemAction` and :func:`itemDelete` which 
    are useful with the :func:`BoundCommandMenu.withView`.
    """
    def __init__(self, name):
        self.commands = []
        self.name = name

    def command(self, descr, key=None, statusTip=None, type="action", iconFile=None, sort=500, default=False, requireSelection=False, viewRelated=False, needs_reload=True):
        """
        :param descr:  string that appears in the menu (or other UI element)
        :param key: short-cut key to apply to this command
        :param type:  a string value typically chosen from "new", "action", "delete"; 
            This is used to sort the menu.
        :param sort:  integer from 0 to 1000 used to fine-tune the sort after the 'type'

        A function decorated with itemNew must have one parameter:
        
        #.  command object (probably self)
        """
        def decorator(f):
            x = Command(descr, 
                key=key, 
                type=type, 
                statusTip=statusTip, 
                iconFile=iconFile, 
                sort=sort, 
                default=default, 
                viewRelated=viewRelated, 
                requireSelection=requireSelection, 
                needs_reload=needs_reload)
            x.func = f
            self.commands.append(x)
            self.commands.sort(key=lambda x:x.sort_key())
            return f
        return decorator

    def itemNew(self, **kwargs):
        """
        A function decorator similar to :func:`command` but with parameters 
        defaulted appropriate for adding an item to an adjacent view.
        
        A function decorated with itemNew must have two parameters:
        
        #.  command object (probably self)
        #.  identifier or object acted on.  This should have a default of 
            None if requireSelection is not specified in itemNew.
        """
        if not kwargs.has_key("descr"):
            kwargs["descr"] = "&New..."
        if not kwargs.has_key("iconFile"):
            kwargs["iconFile"] = ":/qtalchemy/default-new.ico"
        if not kwargs.has_key("requireSelection"):
            kwargs["requireSelection"] = False
        if not kwargs.has_key("viewRelated"):
            kwargs["viewRelated"] = True
        kwargs["type"] = "new"
        return self.command(**kwargs)

    def itemDelete(self, **kwargs):
        """
        A function decorator similar to :func:`command` but with parameters 
        defaulted appropriate for deleting an item in an adjacent view.
        
        A function decorated with itemNew must have two parameters:
        
        #.  command object (probably self)
        #.  identifier or object acted on.  This should have a default of 
            None if requireSelection is not specified in itemNew.
        """
        if not kwargs.has_key("descr"):
            kwargs["descr"] = "&Delete..."
        if not kwargs.has_key("requireSelection"):
            kwargs["requireSelection"] = True
        if not kwargs.has_key("viewRelated"):
            kwargs["viewRelated"] = True
        if not kwargs.has_key("iconFile"):
            kwargs["iconFile"] = ":/qtalchemy/default-delete.ico"
        kwargs["type"] = "delete"
        return self.command(**kwargs)

    def itemAction(self, descr, **kwargs):
        """
        A function decorator similar to :func:`command` but with parameters 
        defaulted appropriate for deleting an item in an adjacent view.
        
        A function decorated with itemNew must have two parameters:
        
        #.  command object (probably self)
        #.  identifier or object acted on.  This should have a default of 
            None if requireSelection is not specified in itemNew.
        """
        if not kwargs.has_key("requireSelection"):
            kwargs["requireSelection"] = True
        if not kwargs.has_key("viewRelated"):
            kwargs["viewRelated"] = True
        kwargs["type"] = "action"
        return self.command(descr, **kwargs)

    def dropCommand(self, mimeType, **kwargs):
        """
        A command function for when a bit of mime-data is dropped on 
        to the row.  This is typically used with-in the context of a 
        QAbstractItemView derived widget.
        """
        if not kwargs.has_key("requireSelection"):
            kwargs["requireSelection"] = True
        kwargs["viewRelated"] = True
        kwargs["type"] = DROP_ACTION_TYPE
        return self.command(mimeType, **kwargs)

    def __get__(self, instance, owner):
        try:
            return getattr(instance, self.name)
        except AttributeError as e:
            setattr(instance, self.name, BoundCommandMenu(instance, self))
            return getattr(instance, self.name)

class DomainEntity(CommandMenu):
    """
    DomainEntity is deprecated, but still used by the ForeignKey lookup stuff

    The DomainEntity object defines how an object appears and can be manipulated by the user.  This has 
    several components::
    
    * Defining database queries to provide user view of lists of these domain entities.
    * Key field information to map back to individual tables.
    * Commands acting on a record in the principle table (identified by primary key).
    
    QtAlchemy takes the view that rows of database queries do not map well to typical object oriented 
    design methods.  The DomainEntity provides a more abstract view of commands associated to an entity which 
    can be bound to arbitrary database queries with-in the code.  Thus a joined query can actually offer user 
    commands associated with any of the tables in the query.
    """

    def __init__(self, info=None):
        """
        The following assignments are a common proto-type associating this DomainEntity with a 
        explicit table.  We do not yet define the sql joins clearly.
        """
        CommandMenu.__init__(self,"base_menu")
        self.key_column = None
        self.list_display_columns = None
        self.list_search_columns = None
        self.info = {} if info is None else info

    def list_query_converter(self):
        from sqlalchemy.orm import Query
        queryCols = tuple([self.key_column.label("_hidden_id")] + self.list_display_columns)
        return (Query(queryCols).order_by(self.list_display_columns[0], self.key_column), lambda x: x._hidden_id)


class CommandEvent(object):
    """
    This class is passed with the `preCommand` signal, optionally to the command 
    function, and to the `refresh` signal after the command function is executed.  
    The command functions, decorated by members of :class:`CommandMenu`, are 
    expected to indicate refresh context in a semi-standard way which isn't 
    entirely known yet.
    
    Recipients of the `preCommand` signal can :func:`abort` the command if they 
    wish; this is useful if the ambient screen could not save its data for 
    some reason.  The CommandEvent class passed could be pre-loaded with settings 
    which might be useful with-in the command function.
    
    Recipients of the `refresh` signal may possibly desire to reload from 
    context clues put into the passed CommandEvent instance by the command 
    function.
    
    Note that the free-form nature of screen context can create a tight coupling 
    between the screens using the associate :class:`CommandMenu` and the the 
    command functions themselves.
    
    This class works can work in tight conjunction with :class:`qtalchemy.dialogs.BoundDialog`.  
    In this context, the preCommandSave function will set a member savedDataContext
    with the current main_row object bound to the BoundDialog.
    """
    def __init__(self, cmd=None):
        self.cmd = cmd
        self.aborted = False
    
    def abort(self):
        """
        Call this method of the event parameter to the preCommand signal to 
        stop the command function from being fired.  If aborted, the refresh 
        signal will not be emitted.
        """
        self.aborted = True

class BoundCommandMenuItem(object):
    """
    The class :class:`BoundCommandMenu` is responsible for creating and managing instances of this class.
    
    This class binds comamnds from an entity to a PyQt/PySide view where each row represents an 
    entity to the entity class.  The proxy slots 'activatedProxy' and 'triggeredProxy' redirect 
    to the specified function of the entity instance.
    """
    def __init__(self, cmd, action, objectConverter, binding):
        """
        :param cmd:  a :class:`Command` object
        :param action:  A QAction or QPushButton
        :param objectConverter:  A callable taking row objects (QModelIndex.internalPointer()) to id's for the entity functions.
            If objectConverter is None, then use the default model objectConverter.
        """
        self.cmd = cmd
        self.action = action
        self.objectConverter = objectConverter
        self.binding = binding
        self.model = None

        if binding.view is not None:
            self.model = binding.view.model()
            self.item_sel = binding.view.selectionModel()

            # hook to QItemSelectionModel::selectionChanged signal for enabling/disabling
            # hook to QAbstractItemModel::modelReset signal for enabling/disabling
            self.item_sel.selectionChanged.connect(self.enable_buttons)
            self.model.modelReset.connect(self.enable_buttons)

            if self.cmd.command_type == DROP_ACTION_TYPE:
                self.model.dropCallable[self.cmd.descr] = self.dropAction

        if isinstance(self.action, QtGui.QPushButton):
            self.action.clicked.connect(self.triggeredProxy)
        elif isinstance(self.action, QtGui.QAction):
            self.action.triggered.connect(self.triggeredProxy)

    def enable_buttons(self, sel=None, desel=None):
        # setEnabled is sufficient for both QPushButton and QAction
        if self.cmd.requireSelection and self.action is not None:
            indexes = self.binding.view.selectedIndexes()
            self.action.setEnabled(len(indexes)>0)

    def dropAction(self, data, action, row, column, parent):
        event = CommandEvent(self.cmd)
        self.binding.preCommand.emit(event)
        if event.aborted:
            return
        
        # this is a bit of a hack to preCommand first:
        # it is presumed that preCommand saves the data so that the database keys are up-to-date
        handle = parent.internalPointer()
        if handle is not None:
            handle = self.model.objectConverter(handle)
        args = inspect.getargspec(self.cmd.func).args
        d = {}
        if 'event' in args:
            d['event'] = event
        self.cmd.func(self.binding.target, handle, str(data.data(self.cmd.descr)), **d)
        self.binding.refresh.emit(event)
        if self.cmd.needs_reload:
            if self.binding.view:
                self.model.reset_content_from_session()
        return not event.aborted

    def objectActivatedProxy(self, obj=None, objectConverter=None):
        # self.objectConverter takes precedence!
        objectConverter = objectConverter if self.objectConverter is None else self.objectConverter
        event = CommandEvent(self.cmd)
        self.binding.preCommand.emit(event)
        if event.aborted:
            return
        
        # this is a bit of a hack to preCommand first:
        # it is presumed that preCommand saves the data so that the database keys are up-to-date
        handle = obj
        if handle is not None:
            handle = objectConverter(handle)
        args = inspect.getargspec(self.cmd.func).args
        d = {}
        if 'event' in args:
            d['event'] = event
        self.cmd.func(self.binding.target, handle, **d)
        self.binding.refresh.emit(event)
        if self.cmd.needs_reload:
            if self.binding.view:
                self.model.reset_content_from_session()

    def activatedProxy(self, index):
        if self.cmd.requireSelection and index is None:
            import warnings
            warnings.warn("No selected view index for {0}".format(self.cmd.name))
        else:
            if self.cmd.viewRelated and self.model is not None:
                handle = index
                if handle is not None:
                    handle = handle.internalPointer()
                self.objectActivatedProxy(handle, self.model.objectConverter)
            else:
                event = CommandEvent(self.cmd)
                self.binding.preCommand.emit(event)
                if event.aborted:
                    return
                try:
                    args = inspect.getargspec(self.cmd.func).args
                except Exception as e:
                    args = ()
                d = {}
                if 'event' in args:
                    d['event'] = event
                self.cmd.func(self.binding.target, **d)
                self.binding.refresh.emit(event)

    def triggeredProxy(self, checked=False):
        if self.binding.obj is not None:
            obj = self.binding.obj
            self.objectActivatedProxy(obj)
        elif self.binding.mapper is not None:
            self.objectActivatedProxy(self.binding.mapper.obj, self.binding.mapper.objectConverter)
        elif self.binding.view is not None:
            indexes = self.binding.view.selectedIndexes()
            index = None if len(indexes)==0 else indexes[0]
            self.activatedProxy(index)
        else:
            self.activatedProxy(None)

class BoundCommandMenu(QtCore.QObject):
    """
    This class holds the :class:`BoundCommandMenuItem` objects binding an entity to a view.  This is 
    the main class for tying :class:`CommandMenu` instances to PyQt/PySide views.
    
    Primarily the work of this class is carried out in the :class:`BoundCommandMenuItem` objects which holds 
    slots connected to signals from the view.  This class also attaches the actions to the view.
    
    Note that if the view is a :class:`qtalchemy.widgets.TableView`, the 
    default context menu policy of :class:`qtalchemy.widgets.TableView` is 
    QtCore.Qt.ActionsContextMenu.
    """
    preCommand = Signal(object, name='preCommand')
    refresh = Signal(object, name='refresh')

    def __init__(self, target, menu, view=None, mapper=None, obj=None, webView=None, javaScriptName=None, buttonBox=None, bindDefault=False, objectConverter=None):
        QtCore.QObject.__init__(self)
        self.target = target
        self.menu = menu
        self.view = view
        self.mapper = mapper
        self.obj = obj
        self.webView = webView
        self.javaScriptName = javaScriptName
        self.buttonBox = buttonBox
        self.bindDefault = bindDefault
        self.objectConverter = objectConverter
        
        if self.webView:
            # Is loadFinished soon enough?  What if the user is clicking 
            # links and icons before the load is finished?
            # Note that loadStarted was too soon and the frame was overwritten.
            self.webView.loadFinished.connect(lambda x: self.addJavascriptObjects())
        
        if self.view:
            # we need to hook up to the context menu immediately
            self.resetActions()

    def withView(self, view, buttonBox=None, bindDefault=False, objectConverter=None):
        """
        Return a duplicate of this BoundMenuCommand augmented with a view.  The 
        QAction objects will enable and disable as appropriate for the connected view.
        
        :param view: a QAbstractItemView attached to a QAbstractItemModel
        :param bindDefault: bindDefault can take several values - True, "double", "activated", False (True maps to "activated")
        """
        return BoundCommandMenu(self.target, self.menu, view=view, buttonBox=buttonBox, bindDefault=bindDefault, objectConverter=objectConverter)

    def withMapper(self, mapper, buttonBox=None, bindDefault=False, objectConverter=None):
        """
        Return a duplicate of this BoundMenuCommand augmented with a view.  The 
        QAction objects will enable and disable as appropriate for the connected view.
        
        :param view: a QAbstractItemView attached to a QAbstractItemModel
        """
        return BoundCommandMenu(self.target, self.menu, mapper=mapper, buttonBox=buttonBox, bindDefault=bindDefault, objectConverter=objectConverter)

    def withWebView(self, webView, javaScriptName=None, objectConverter=None):
        """
        Return a duplicate of this BoundMenuCommand augmented with a QWebView.  
        The methods :func:`htmlJavascript`, :func:`htmlIcons` and :func:`htmlButtons` can 
        be used to construct html which calls back to this view.
        
        The loadFinished signal of the passed QWebView is connected and the 
        QWebFrame method addToJavaScriptWindowObject is called to associated 
        this object with name in the javascript name space.
        
        :param webView:  the webview which is associated with the returned object
        :param javaScriptName:  a name for the returned object in the 
            javascript namespace.  If None, a unique name is auto-generated.
        """
        if javaScriptName is None:
            import uuid
            javaScriptName = "bound_command_{0}".format(uuid.uuid1().hex)
        return BoundCommandMenu(self.target, self.menu, webView=webView, javaScriptName=javaScriptName, objectConverter=objectConverter)

    def withObject(self, obj, buttonBox=None, objectConverter=None):
        """
        Return a duplicate of this BoundMenuCommand augmented with a view.  The 
        QAction objects will enable and disable as appropriate for the connected view.
        
        :param view: a QAbstractItemView attached to a QAbstractItemModel
        """
        return BoundCommandMenu(self.target, self.menu, obj=obj, buttonBox=buttonBox, objectConverter=objectConverter)

    def resetActions(self):
        """
        Regenerate QAction objects from self.target
        """
        self.action_bindings = [] # this is annoying -- I need to hold a reference explicitly
        self.button_bindings = []
        self.default_binding = None

        actionParent = self.view
        if actionParent is None and isinstance(self.target, QtGui.QWidget):
            actionParent = self.target
        if actionParent is None:
            actionParent = self.target.parent

        for cmd in self.menu.commands:
            action = cmd.action(actionParent)
            current = BoundCommandMenuItem(cmd, action, objectConverter = self.objectConverter, binding = weakref.proxy(self))
            self.action_bindings.append(current)
            if action is None:
                continue
            if cmd.default:
                self.default_binding = current

            if self.buttonBox is not None:
                #TODO:  map Command.type to QtGui.QDialogButtonBox.*Role items
                button = self.buttonBox.addButton(cmd.descr, QtGui.QDialogButtonBox.ActionRole)
                self.button_bindings.append(BoundCommandMenuItem(cmd, button, objectConverter = self.objectConverter, binding = weakref.proxy(self)))

        if self.default_binding:
            if self.bindDefault is True or self.bindDefault == "activate":
                self.view.activated.connect(self.default_binding.activatedProxy)
            elif self.bindDefault == "double":
                self.view.doubleClicked.connect(self.default_binding.activatedProxy)

        if self.view is not None:
            for cb in self.action_bindings:
                if cb.cmd.viewRelated and cb.action is not None:
                    self.view.addAction(cb.action)

    def fillMenu(self, menu):
        """
        Take the actions in the list and attach them to a menu.
        """
        if not hasattr(self, "action_bindings"):
            self.resetActions()
        for command in self.action_bindings:
            menu.addAction(command.action)

    def fillToolbar(self, toolbar):
        """
        Take the actions in the list and attach them to a toolbar.
        """
        if not hasattr(self, "action_bindings"):
            self.resetActions()
        for command in self.action_bindings:
            toolbar.addAction(command.action)

    def htmlButtons(self, obj):
        """
        Return a string with html button definitions which call the trigger slot.
        
        :param javaScriptName:  the name given when passing this binding object to addToJavaScriptWindowObject.
        """
        if not hasattr(self, "action_bindings"):
            self.resetActions()
        fstring = """<input type="button" id="evalbutton" value="{descr}" onclick="{callback}" />"""
        btns = [fstring.format(descr=binding.cmd.descr, callback=self.htmlJavascript(binding.cmd.name(), obj)) for binding in self.action_bindings]
        return ' '.join(btns)

    def htmlIcons(self, obj):
        """
        Return a string with html image definitions which call the trigger slot.
        
        :param javaScriptName:  the name given when passing this binding object to addToJavaScriptWindowObject.
        """
        if not hasattr(self, "action_bindings"):
            self.resetActions()
        fstring = """<img src="{icon}" alt="{descr}" onclick="{callback}" />"""
        btns = [fstring.format(descr=binding.cmd.descr, icon=binding.cmd.iconFile, callback=self.htmlJavascript(binding.cmd.name(), obj)) for binding in self.action_bindings]
        return ' '.join(btns)

    def htmlJavascript(self, cmd, obj):
        return "{jsn}.objectActivated('{name}', '{id}')".format(jsn=self.javaScriptName, name=cmd, id=obj)

    def addJavascriptObjects(self):
        self.webView.page().currentFrame().addToJavaScriptWindowObject(self.javaScriptName, self)

    @Slot(str, str)
    def objectActivated(self, cmd, obj):
        if not hasattr(self, "action_bindings"):
            self.resetActions()
        for binding in self.action_bindings:
            if binding.cmd.name() == cmd:
                binding.objectActivatedProxy(obj, self.objectConverter)

    @Slot(str)
    def trigger(self, cmd):
        if not hasattr(self, "action_bindings"):
            self.resetActions()
        for binding in self.action_bindings:
            if binding.cmd.name() == cmd:
                binding.triggeredProxy()

    def __len__(self):
        return len(self.menu.commands)

    def __getitem__(self, index):
        return self.menu.commands[index]

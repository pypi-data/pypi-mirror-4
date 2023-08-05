# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm.interfaces import AttributeExtension, MapperExtension, InstrumentationManager
from sqlalchemy.orm import object_session, EXT_STOP, EXT_CONTINUE, sessionmaker, session
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.dialects.postgresql import UUID as pg_UUID
import uuid
import inspect

class UUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    "Backend-agnostic GUID Type" from http://www.sqlalchemy.org/docs/core/types.html
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(pg_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

def sessionExtension(**kwargs):
    """
    Class decorator function to indicate classes in modules which are :class:`ModelSession`  
    extensions.  See :func:`ModelSessionExtension` for details about parameters.
    """
    def apply(cls):
        cls.modelSessionExtension = ModelSessionExtension(**kwargs)
        return cls
    return apply

class ModelSessionExtension(object):
    def __init__(self, name=None, names=None, clsName=None, clsNames=None):
        if name is None:
            self.names = names
        elif names is not None:
            self.names = names
            self.names.append(name)
        else:
            self.names = [name]

        if clsName is None:
            self.clsNames = clsNames
        elif clsNames is not None:
            self.clsNames = clsNames
            self.clsNames.append(clsName)
        else:
            self.clsNames = [clsName]

    def matches(self, target):
        if self.names is not None and hasattr(target, "objectName") and target.objectName() in self.names:
            return True

        if self.clsNames is not None and target.__class__.__name__ in self.clsNames:
            return True

class ModelSession(session.Session):
    """
    The ModelSession extends the sqlalchemy Session base class with tools for 
    convenience object addition and objects which are truly not a part of the 
    database persistence model (although may become so).
    
    The return of :func:`PBSessionMaker` is a class derived from ModelSession.
    """

    def modelListeners(self, event):
        for l in targetInstrumentation(self).event_list(event):
            yield l
        for l in targetInstrumentation(self.__class__).event_list(event):
            yield l

    def modelMessage(self, instance, flags, msg):
        r = None
        for listener in self.modelListeners("message"):
            r = listener(self, instance, flags, msg)
            if r is not None:
                break
        return r

    def npadd(self, obj):
        """
        npadd is an add for non-persistent objects.  This could be objects that 
        are candidates to join the persistent store, but have not due to been 
        confirmed by the user.  Alternatively, objects which are merely UI 
        artifacts may be added here so that their UserAttr attributes know 
        which session instance should be used for database interaction and 
        local caching.
        """
        targetInstrumentation(obj).session = self

    @classmethod
    def _prepExtensionClasses(cls):
        if not hasattr(cls, "extensionClasses"):
            cls.extensionClasses = []

    @classmethod
    def addExtensionModule(cls, module):
        """
        Add a module extension with classes.  It is expected that dialogs and
        command class emit events using :func:`event` which can be hooked by
        classes in the passed module.
        """
        cls._prepExtensionClasses()
        for n in dir(module):
            if hasattr(getattr(module, n), "modelSessionExtension"):
                cls.extensionClasses.append(getattr(module, n))

    @classmethod
    def event(cls, evt, target, *params, **kwargs):
        """
        Call an event on the extension classes associated with this ModelSession
        instance.  Extensions must be added to the ModelSession instance with
        :func:`addExtensionModule`.
        """
        cls._prepExtensionClasses()
        for e in cls.extensionClasses:
            if e.modelSessionExtension.matches(target) and hasattr(e, evt):
                getattr(e, evt)(target, *params, **kwargs)

def PBSessionMaker(**kwargs):
    """
    This is qtalchemy alternative for sqlalchemy.orm.sessionmaker.  We 
    default a few parameters specially and pass it on.  The returned 
    class is derived from :class:`ModelSession`.
    
    The parameters are the same as sqlalchemy.orm.sessionmaker.
    """
    # we're a gui framework we want to write on dialog ok
    if not kwargs.has_key("autoflush"):
        kwargs["autoflush"] = False
    # we want failed commits (due to pre-save validation) in a bound dialog to live on for the second try
    if not kwargs.has_key("expire_on_commit"):
        kwargs["expire_on_commit"] = False
    # When you get a server side commit failure this flag keeps sqlalchemy from expiring my session items.
    if not kwargs.has_key("_enable_transaction_accounting"):
        kwargs["_enable_transaction_accounting"] = False
    # pass it on
    return sessionmaker(class_=ModelSession,**kwargs)

class InstallAttributeListeners(InstrumentationManager):
    def post_configure_attribute(self, class_, key, inst):
        """Add an event listener to an InstrumentedAttribute."""
        inst.impl.extensions.insert(0, ModelChangeExtension(key))

class ModelChangeExtension(AttributeExtension):
    """
    This extension will activate a call-back on the object.  This 
    call-back is expected to iterate through a list of listening 
    models and notify them of the changes.
    """
    def __init__(self, key):
        self.key = key
    
    def append(self, state, value, initiator):
        self._report(state, value, None, "appended")
        return value

    def remove(self, state, value, initiator):
        self._report(state, value, None, "removed")
    
    def _report(self, state, value, oldvalue, verb):
        state.obj().receive_change_event(verb, self.key, value, oldvalue)


class Message:
    Ok      = 0x000001
    Cancel  = 0x000002
    Yes     = 0x000004
    No      = 0x000008
    Information = 0x001000
    Warning     = 0x002000
    Abort       = 0x004000

    # no return implies None and, thus, ContinueProcessing
    ContinueProcessing = None

class EventExtension(MapperExtension):
    """
    Enables hooks on mapped SA objects with names like:

    __before_insert__
    __after_insert__
    etc.

    See SA documentation and the _add_handler code below for details.
    """
    def handle_event(self, event, mapper, connection, instance):
        name = '__%s__' % event
        handler = getattr(instance, name, None)
        if handler:
            handler()

def _add_handler(event):
    def handle_event(self, *args, **kwargs):
        self.handle_event(event, *args, **kwargs)
        return EXT_CONTINUE
    setattr(EventExtension, event, handle_event)
    
for _name in ['before_insert',
            'after_insert',
            'before_update',
            'after_update',
            'before_delete',
            'after_delete']:
    _add_handler(_name)

event_extension = EventExtension()

class ModelInstrumentation(object):
    def __init__(self):
        self.events = {}
        self.setting = {}
        
    def event_list(self, event, attribute=None):
        if attribute is None:
            if self.events.has_key(event):
                return self.events[event]
            else:
                return []
        else:
            x = "{0}.".format(event)
            y = "{0}.{1}".format(event, attribute)
            return self.event_list(x) + self.event_list(y)

    def event_add(self, event, attribute, listener):
        if event not in ["message", "check", "set", "get"]:
            raise ValueError("Event '{0}' is not a valid event.".format(event))

        if attribute is not None:
            event = "{0}.{1}".format(event, attribute)
        if self.events.has_key(event):
            self.events[event].append(listener)
        else:
            self.events[event] = [listener]

    def add(self, event, attribute=None):
        def decorate(f):
            self.event_add(event, attribute, f)
            return f
        return decorate

def targetInstrumentation(target):
    if inspect.isclass(target):
        try:
            return target.classEvents
        except AttributeError as e:
            target.classEvents = ModelInstrumentation()
            return target.classEvents
    else:
        try:
            return target._instrumentation
        except AttributeError as e:
            target._instrumentation = ModelInstrumentation()
            return target._instrumentation

def instanceEvent(target, event, attribute=None):
    def decorate(f):
        x=targetInstrumentation(target)
        x.event_add(event, attribute, f)
        return f
    return decorate

class ModelObject(object):
    """
    A class derived from ModelObject provides an event model to notify 
    :class:`qtalchemy.PBTableModel` when attributes are modified.

    The method names in this class are prefixed with 'model' to keep them 
    separate from the application programmers attributes.
    """
    # Add the mapped object events
    __mapper_args__ = {'extension': EventExtension()}
    # add the attribute events for model call backs
    # TODO:  InstallAttributeListeners is broken in sqlalchemy 0.7.0 
    # We currently don't have code relying on these events.  The set was just replaced 
    # and the collection append/remove have not been utilized.
    # TODO 1:  append/remove notifications should notify the model
    # TODO 2:  clean up these event hooks
    #__sa_instrumentation_manager__ = InstallAttributeListeners

    # this is merely a name-space trick to make things more memorable
    Events = ModelInstrumentation

    def session(self):
        """
        Obtain a pointer to session in which this object lives.

        TODO:  rename session to modelSession
        """
        sessionCandidate = None
        try:
            sessionCandidate = object_session(self)
        except UnmappedInstanceError as e:
            pass
        if sessionCandidate is None and hasattr(targetInstrumentation(self), "session"):
            sessionCandidate = targetInstrumentation(self).session
        return sessionCandidate

    def modelListeners(self, event, attribute=None):
        """
        Enumerate the listeners on a particular event.
        """
        for l in targetInstrumentation(self).event_list(event, attribute):
            yield l
        #TODO:  Consider navigating the entire MRO
        #           for cls in self.__class__.mro()
        for l in targetInstrumentation(self.__class__).event_list(event, attribute):
            yield l

    def modelMessage(self, flags, msg):
        """
        Call out to the 'message' event handlers of this object and the session.
        
        When connected to a UI, it is expected that the session message event 
        is connected to the :class:`qtalchemy.dialogs.SessionMessageBox` object 
        which displays the message in a Qt message box.
        
        :param flags: bit mask of flags from `Message`
        """
        r = None
        s = self.session()
        for listener in self.modelListeners("message"):
            r = listener(self, flags, msg)
            if r is not None:
                break
        if r is None and s is not None:
            r = s.modelMessage(self, flags, msg)
        return r

    def __setattr__(self, attr, v):
        if attr.startswith("_instrumentation") or attr.startswith("_UserAttr"):
            super(ModelObject,self).__setattr__(attr,v)
        else:
            try:
                oldvalue = self.__dict__[attr]
            except KeyError as e:
                oldvalue = None
            inst = targetInstrumentation(self)
            if not inst.setting.has_key(attr):
                inst.setting[attr] = 0
            assert 0 == inst.setting[attr], "Recursive set of {0}".format(attr)
            inst.setting[attr] += 1
            try:
                for listener in self.modelListeners("check", attr):
                    listener(self, attr, v)
                super(ModelObject,self).__setattr__(attr,v)
                for listener in self.modelListeners("set", attr):
                    listener(self, attr, oldvalue)
                self.receive_change_event("set",attr,v,None)
            finally:
                inst.setting[attr] -= 1

    def receive_change_event(self, verb, key, value, oldvalue):
        if not hasattr(self,"_ModelObject__listening_models"):
            return # no models to notify
        
        for m in self.__listening_models:
            # tell the model about this event
            m.row_object_change(self,verb,key,value,oldvalue)

    def is_setting(self,attr):
        """
        Check current assignment recursion flags.  Return True if the specified 
        attribute is currently being assigned.
        """
        inst = targetInstrumentation(self)
        return inst.setting.has_key(attr) and inst.setting[attr] > 0

class ValidationError(Exception):
    """
    This validation class is meant to be used from the validation events connected via ModelObject.
    """
    pass

def user_message(exception):
    """
    This helper function returns a polite user message derived from a sqlalchemy database exception.
    
    It probably does a fairly horrible job of it.
    """
    try:
        if isinstance(exception,OperationalError):
            return exception.orig.args[1]
        if isinstance(exception,ProgrammingError):
            return "%s\n\nOffending SQL Statement:  %s" % (exception.orig.args[1], exception.statement)
    except:
        pass
    return str(exception)

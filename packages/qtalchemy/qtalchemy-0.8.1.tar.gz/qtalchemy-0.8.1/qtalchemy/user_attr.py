# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

import re
import decimal
import datetime

def default_for_type(type_):
    if type_ == str:
        return ""
    elif type_ == int:
        return 0
    elif type_ == datetime.date:
        return datetime.date(datetime.date.today().year,1,1)
    return type_()

def hasextendedattr(obj,attr):
    """
    >>> class Person:
    ...     name='Joe'
    ... 
    >>> class Group:
    ...     person1 = Person()
    ...     person2 = Person()
    ...
    >>> x = Group()
    >>> hasextendedattr(x,'person1.name')
    True
    >>> hasextendedattr(x,'person1')
    True
    >>> hasextendedattr(x,'person1.piggy')
    False
    """
    attrs = attr.split('.')
    o = obj
    #print attrs
    for a in attrs[:-1]:
        if hasattr(o,a):
            o = getattr(o,a)
        else:
            return False
    return hasattr(o,attrs[-1])

def getextendedattr(obj,attr):
    """
    >>> class Person:
    ...     name='Joe'
    ... 
    >>> class Group:
    ...     person1 = Person()
    ...     person2 = Person()
    ...
    >>> x = Group()
    >>> getextendedattr(x,'person1.name')
    'Joe'
    >>> getextendedattr(x,'person3.asdf')
    Traceback (most recent call last):
    ...
    AttributeError: Group instance has no attribute 'person3'
    >>> getextendedattr(x,'person2.asdf')
    Traceback (most recent call last):
    ...
    AttributeError: Person instance has no attribute 'asdf'
    """
    attrs = attr.split('.')
    o = obj
    for a in attrs:
        o = getattr(o,a)
    return o

def setextendedattr(obj,attr,value):
    """
    >>> class Person:
    ...     name='Joe'
    ... 
    >>> class Group:
    ...     person1 = Person()
    ...     person2 = Person()
    ...
    >>> x = Group()
    >>> setextendedattr(x,'person1.name','Sam')
    >>> x.person1.name
    'Sam'
    >>> x.person2.name
    'Joe'
    """
    attrs = attr.split('.')
    o = obj
    for a in attrs[:-1]:
        o = getattr(o,a)
    setattr(o,attrs[-1],value)

class UseCachedValue(Exception):
    """
    Raise this exception from UserAttr.on_get handlers to avoid returning a 
    new value.  This is useful when writing a handler for a calculated field 
    and the cached value is correct.  In these cases, we want to avoid 
    returning the cached value as newly computed because that will incur data 
    model updates which are not needed.
    """
    pass

class AttributeInstrumentation(object):
    """
    This is an internal class for the UserAttr objects.  It has flags for 
    recursion control in the getters and setters.
    """
    def __init__(self):
        self.getting = 0
        self.setting = 0

class UserAttr(property):
    """
    The UserAttr type provides python object attribute type validation.
    
    The UserAttr class is designed to be used in conjunction with
    :class:`qtalchemy.ModelObject`.  

    Currently the on_get event semantics is inconsistent with the use of the
    ModelObject.Events event model.  That is the UserAttr.on_get decorator is
    on the attribute itself, but the ModelObject.Events.add operator is based
    on an instance of ModelObject.Events.  The advantage of the latter is that
    it works consistently for both UserAttr and sqlalchemy column objects.

    EXAMPLE::
        >>> from qtalchemy import *
        >>> class Person(ModelObject):
        ...     name = UserAttr(str,"Person Name")
        ...     age = UserAttr(int,"Age")
        ...     married = UserAttr(bool,"Married")
        >>> 
        >>> fred = Person()
        >>> fred.name="Fred Jackson"
        >>> fred.age="1234"
        >>> fred.married = 4
        >>> (fred.name, fred.age, fred.married)
        ('Fred Jackson', 1234, True)
        >>> type(fred.age)
        <type 'int'>
        >>> type(fred.married)
        <type 'bool'>

        >>> jane = Person()
        >>> jane.age
        0
        >>> jane.name
        ''
        >>> jane.name=None
        >>> jane.name
        ''
        >>> jane.age=None
        >>> jane.age
        0
    """
    def __init__(self, atype, label, storage=None, readonly=False, **kwargs):
        """
        The UserAttr property extends python 'property' class to provide a type and label and default storage.
        
        :param atype: python type of the UserAttr
        :param label: label for display to application user
        :param storage: attribute which stores this in the object instances 
         - if not specified, it is derived by turning label into a python safe name with leading underscores, etc.
         - storage can be specified as a dot qualified multi-identifier and the components will be resolved iteratively
        :param readonly: display this property as read-only in the interface

        Possible arguments in kwargs include:
            - whats_this
            - yoke_specifier
            - alignment
            - empty_zero
        """
        property.__init__(self,self.fget,self.fset)
        self.atype = atype
        if storage is not None:
            self.storage = storage
        else:
            self.storage = "_UserAttr_" + re.sub("[^a-zA-Z0-9_]","_",label)
        self.label = label
        self.readonly = readonly
        self.__listeners = []
        self.__on_first_get = None
        self.__on_get = None

        self.empty_zero = False

        direct_assign_keys = ['whats_this', 'empty_zero']
        prop_keys = ['yoke_specifier', 'alignment']

        for x in prop_keys:
            if kwargs.has_key(x):
                setattr(self, '_'+x, kwargs[x])
        for x in direct_assign_keys:
            if kwargs.has_key(x):
                setattr(self, x, kwargs[x])

    @property
    def alignment(self):
        if self.__alignment is None:
            if hasattr(self.atype, "alignment"):
                return self.atype.alignment
            else:
                if self.atype in (int, float):
                    return "right"
        else:
            return "left"

    @property
    def base_type(self):
        if hasattr(self.atype, "base_type"):
            return self.atype.base_type
        else:
            return self.atype

    def yoke_specifier(self):
        if self._yoke_specifier is not None:
            return self._yoke_specifier
        else:
            return None

    def _instrumentation(self,row):
        attrName = "_instrumentation_"+self.storage.replace('.','_')
        if not hasattr(row,attrName):
            setattr(row,attrName,AttributeInstrumentation())
        return getattr(row,attrName)

    def fget(self,row):
        inst = self._instrumentation(row)
        inst.getting+=1
        if self.__on_get is not None:
            try:
                self.fset(row,self.__on_get(row))
            except UseCachedValue as e:
                pass
        elif not hasextendedattr(row, self.storage) and self.__on_first_get is not None:
            try:
                self.fset(row,self.__on_first_get(row))
            except UseCachedValue as e:
                pass
        inst.getting-=1
        return getextendedattr(row,self.storage) if hasextendedattr(row, self.storage) else default_for_type(self.base_type)

    def on_first_get(self,func):
        self.__on_first_get = func
        return func

    def on_get(self,func):
        self.__on_get = func
        return func

    def on_change(self,func):
        self.__listeners.append(func)
        return func

    def fset(self,row,value):
        inst = self._instrumentation(row)
        assert 0 == inst.setting, "Recursive set of {0}".format(self.storage)
        inst.setting+=1
        try:
            # if the underlying type is a 'type' and the value matches that type, we can skip directly to the assignment.
            if not isinstance(self.atype,type) or not isinstance(value,self.atype):
                if value is None:
                    value = self.atype()
                elif value in [""] and self.atype in (float,int,decimal.Decimal):                
                    value = self.atype("0")
                else:
                    value = self.atype(value)

            setextendedattr(row,self.storage,value)

            # notify 
            if 0 == self._instrumentation(row).getting:
                # Note that ModelObject.__setattr__ accounts for both SA 
                # columns and UserAttr during attribute setting
                for l in self.__listeners:
                    l(row)
        finally:
            inst.setting-=1

    def session(self, row):
        try:
            return row.session()
        except AttributeError as e:
            return None

    def session_maker(self, row):
        return self.session(row).__class__

class Nullable:
    """
    A type extender for use with UserAttr.  Wrapping a type with Nullable allows valid values for that type or None.
    
    EXAMPLE::
        >>> class Thing(object):
        ...     date = UserAttr(Nullable(datetime.date),"Optional Date")
        >>> 
        >>> t = Thing()
        >>> t.date = None          # succeeds and sets the date to None
        >>> t.date is None
        True
        >>> t.date = 12            # This will fail, datetime.date doesn't coerce an int.
        Traceback (most recent call last):
        ...
        TypeError: Required argument 'month' (pos 2) not found
        >>> t.date = datetime.date(2010,1,9) # my birthday
        >>> t.date
        datetime.date(2010, 1, 9)
    """
    def __init__(self,atype):
        self.atype = atype

    def __call__(self,v=None):
        if v is None:
            return v
        elif not isinstance(v,self.atype):
            return self.atype(v)
        else:
            return v

    @property
    def base_type(self):
        return self.atype

    def yoke_specifier(self):
        type_yoke_specifier(self.atype)

class AttrNumeric:
    """
    This class wraps decimal.Decimal with construction semantics compatible with the UserAttr class.
    
    EXAMPLE::
        >>> AttrNumeric(4)(12)
        Decimal('12.0000')
        >>> AttrNumeric(1)(23.352)
        Decimal('23.4')
        >>> AttrNumeric(1)("-3.9")
        Decimal('-3.9')

        
        >>> class BankAccount(object):
        ...     account_no = UserAttr(str,"Account Number")
        ...     open_date = UserAttr(datetime.date,"Opened")
        ...     balance = UserAttr(AttrNumeric(2),"Balance")
        ... 
        >>> b = BankAccount()
        >>> b.balance
        Decimal('0.00')
        >>> b.balance = 12.5352
        >>> b.balance
        Decimal('12.54')
        >>> b.balance = 3.235
        >>> b.balance
        Decimal('3.24')
        >>> b.balance = 12
        >>> b.balance
        Decimal('12.00')
        >>> b.balance = decimal.Decimal(100)/3
        >>> b.balance
        Decimal('33.33')
        >>> b.balance = decimal.Decimal(7)/200
        >>> b.balance
        Decimal('0.04')
    """
    def __init__(self, prec):
        assert prec>=0, "numeric precision must be at least zero"
        self.prec=prec

    def __call__(self, value=None):
        if value in ["", None]:
            return decimal.Decimal()._rescale(-self.prec,'ROUND_HALF_UP')
        elif type(value) in [float]:
            # take higher precision when converting to a string
            v = decimal.Decimal("%.*f" % (self.prec+2, value))
            #print value, v
            return v._rescale(-self.prec,'ROUND_HALF_UP')
        else:
            v = decimal.Decimal(value)
            return v._rescale(-self.prec,'ROUND_HALF_UP')

    @property
    def alignment(self):
        return "right"

    def yoke_specifier(self):
        if self.prec==0:
            return "int"
        else:
            return "float"

# -*- coding: utf-8 -*-
"""
We create models, attach to data and see if the events all propogate.
"""

from qtalchemy import UserAttr, ClassTableModel, ModelObject, UseCachedValue, instanceEvent
from PySide import QtCore, QtGui

count = 0

class PseudoModel(object):
    def __init__(self,obj=None):
        self.obj = None
        if obj is not None:
            self.connect_instance(obj)

    def connect_instance(self,obj):
        self.obj = obj
        instanceEvent(self.obj, "set", "")(self.row_object_change)

    def row_object_change(self, obj, attr, oldvalue):
        assert obj is self.obj
        global count
        if attr == '__primality':
            count += 1

class IntegerProperties(ModelObject):
    def __init__(self,specimen=0):
        self.specimen = specimen
    
    prime = UserAttr(bool,'Prime',storage='__primality')

    @prime.on_get
    def is_specimen_prime(self):
        try:
            if self.specimen == self.__last_computed_prime:
                raise UseCachedValue()
        except AttributeError as e:
            pass # first run will except on __last_computed_prime

        result = False
        if self.specimen >= 2:
            result = True
            for i in xrange(2, self.specimen):
                if i * i > self.specimen:
                    break
                if (self.specimen % i) == 0:
                    result = False
                    break
        self.__last_computed_prime = self.specimen
        return result

def test_set_counter():
    global count

    assert count == 0, 'should start at 0'

    x = IntegerProperties(54)
    hold_reference = PseudoModel(x)

    assert count == 0, 'should start at 0'

    if x.prime == True:
        raise RuntimeError( '{0} is not prime'.format(x.specimen) )

    assert count == 1, 'checked once (count={0})'.format(count)

    if x.prime == True:
        raise RuntimeError( '{0} is not prime'.format(x.specimen) )

    assert count == 1, 'checked twice, but redundant (count={0})'.format(count)

    x.specimen = 97

    if x.prime == False:
        raise RuntimeError( '{0} is prime'.format(x.specimen) )

    assert count == 2, 'new number (count={0})'.format(count)

    if x.prime == False:
        raise RuntimeError( '{0} is prime'.format(x.specimen) )

    assert count == 2, 'new number; 2nd check (count={0})'.format(count)

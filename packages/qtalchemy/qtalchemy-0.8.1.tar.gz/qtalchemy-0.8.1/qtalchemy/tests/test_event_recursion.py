# -*- coding: utf-8 -*-
"""
We test for recursion asserts in UserAttr events
"""

from qtalchemy import UserAttr, AttrNumeric, ModelObject
import nose.tools

class InvoiceDetail(ModelObject):
    classEvents = ModelObject.Events()

    ordered = UserAttr(AttrNumeric(2),"Ordered")
    shipped = UserAttr(AttrNumeric(2),"Shipped")
    unit_price = UserAttr(AttrNumeric(2),"Unit Price")
    ordered_price = UserAttr(AttrNumeric(2),"Price (ordered)")
    shipped_price = UserAttr(AttrNumeric(2),"Price (shipped)")

    # internal
    unit_num = UserAttr(int,"unit numerator")
    unit_den = UserAttr(int,"unit denominator")

    def __repr__(self):
        return "{0.ordered} {0.shipped} {0.unit_price} {0.ordered_price} {0.shipped_price}\n{0.unit_num} {0.unit_den}".format(self)

    @unit_price.on_first_get
    def on_get_unit_price(self):
        if self.unit_num is None or self.unit_den is None:
            return 0.0
        return float(self.unit_num)/self.unit_den

    @classEvents.add("set", "unit_price")
    def on_change_unit_price(self, attr, oldvalue):
        if not self.is_setting("ordered_price") and not self.is_setting("shipped_price"):
            self.unit_num = int(self.unit_price * 100)
            self.unit_den = 100
            self.ordered_price = self.ordered * self.unit_price
            self.shipped_price = self.shipped * self.unit_price

    @shipped_price.on_first_get
    def on_get_shipped_price(self):
        if self.unit_num is None or self.unit_den is None:
            return 0.0
        return self.shipped * float(self.unit_num) / self.unit_den

    @classEvents.add("set", "shipped_price")
    def on_change_shipped_price(self, attr, oldvalue):
        if not self.is_setting("ordered_price") and not self.is_setting("unit_price"):
            self.unit_num = int(self.shipped_price * 100)
            self.unit_den = int(self.shipped * 100)
            self.unit_price = self.shipped_price / self.shipped
            self.ordered_price = self.ordered * self.unit_num / self.unit_den

    @ordered_price.on_first_get
    def on_get_ordered_price(self):
        if self.unit_num is None or self.unit_den is None:
            return 0.0
        return self.ordered * float(self.unit_num) / self.unit_den

    @classEvents.add("set", "ordered_price")
    def on_change_ordered_price(self, attr, oldvalue):
        if not self.is_setting("shipped_price") and not self.is_setting("unit_price"):
            self.unit_num = int(self.ordered_price * 100)
            self.unit_den = int(self.ordered * 100)
            self.unit_price = self.ordered_price / self.ordered
            self.shipped_price = self.shipped * self.unit_num / self.unit_den

def assign_unit_test():
    x = InvoiceDetail()
    x.ordered = 5.50
    x.shipped = 3.25
    x.unit_price = 12
    assert (x.ordered_price, x.shipped_price) == (66,39)

def assign_extended_3for1_test():
    x = InvoiceDetail()
    x.ordered = 6
    x.shipped = 3
    x.shipped_price = 100
    assert (x.unit_num, x.unit_den) == (10000,300)
    assert x.ordered_price == 200

def assign_extended_5for9_test():
    x = InvoiceDetail()
    x.ordered = 5
    x.shipped = 15
    x.ordered_price = .09
    assert (x.unit_num, x.unit_den) == (9,500)
    assert x.shipped_price*100 == 27

def assign_extended_test():
    x = InvoiceDetail()
    x.ordered = 5.50
    x.shipped = 3.25
    x.shipped_price = 50
    assert (x.unit_num, x.unit_den) == (5000,325)
    assert x.ordered_price*100 == 8462


class UnsafeInvoiceDetail(ModelObject):
    classEvents = ModelObject.Events()

    ordered = UserAttr(AttrNumeric(2),"Ordered")
    unit_price = UserAttr(AttrNumeric(2),"Unit Price")
    ordered_price = UserAttr(AttrNumeric(2),"Price (ordered)")
    
    # internal
    unit_num = UserAttr(int,"unit numerator")
    unit_den = UserAttr(int,"unit denominator")

    @unit_price.on_first_get
    def on_get_unit_price(self):
        if self.unit_num is None or self.unit_den is None:
            return 0.0
        return float(self.unit_num)/self.unit_den

    @classEvents.add("set", "unit_price")
    def on_change_unit_price(self, attr, oldvalue):
        self.unit_num = int(self.unit_price * 100)
        self.unit_den = 100
        self.ordered_price = self.ordered * self.unit_price

    @ordered_price.on_first_get
    def on_get_ordered_price(self):
        if self.unit_num is None or self.unit_den is None:
            return 0.0
        return self.ordered * float(self.unit_num) / self.unit_den

    @classEvents.add("set", "ordered_price")
    def on_change_ordered_price(self, attr, oldvalue):
        self.unit_num = int(self.ordered_price * 100)
        self.unit_den = int(self.ordered * 100)
        self.unit_price = self.ordered_price / self.ordered

@nose.tools.raises(AssertionError)
def unsafe_test():
    x = UnsafeInvoiceDetail()
    x.ordered = 2
    x.unit_price = 12  # this asserts because the class doesn't do recursion control

# -*- coding: utf-8 -*-
"""
We test the basic UserAttr based events.
"""

from qtalchemy import UserAttr, ModelObject

class Line_A_Test(ModelObject):
    classEvents = ModelObject.Events()
    
    quantity = UserAttr(float,"Quantity")
    unit = UserAttr(float,"Unit Price")
    price = UserAttr(float,"Price")

    @classEvents.add("set", "quantity")
    @classEvents.add("set", "unit")
    def on_change_unit(self, attr, oldvalue):
        self.price = self.quantity * self.unit

class Line_B_Test(ModelObject):
    quantity = UserAttr(float,"Quantity")
    unit = UserAttr(float,"Unit Price")
    price = UserAttr(float,"Price")

    @price.on_get
    def on_get_price(self):
        return self.quantity * self.unit

def on_change_test():
    line = Line_A_Test()
    line.quantity = 3
    line.unit = 1.25
    assert abs(line.price - 3.75)<.001, "The price should be quantity*unit"

def on_get_test():
    line = Line_B_Test()
    line.quantity = 3
    line.unit = 1.25
    assert abs(line.price - 3.75)<.001, "The price should be quantity*unit"

# -*- coding: utf-8 -*-
"""
We create models, attach to data and see if the events all propogate.
"""

from qtalchemy import UserAttr, AttrNumeric, ClassTableModel, ModelObject
from PySide import QtCore, QtGui

class ItemTest(ModelObject):
    def __init__(self,item=""):
        self.item = item
    
    item = UserAttr(str,"item")
    price = UserAttr(AttrNumeric(2),"price")

def create_model_test():
    item_names = ["wrench", "hammer"]
    items = [ItemTest(item=b) for b in item_names]
    
    model = ClassTableModel(ItemTest,"item,price".split(','),readonly=False)
    model.reset_content_from_list(items)

    model.setData(model.index(1,1,None),3.235,QtCore.Qt.EditRole)

    model.setData(model.index(0,1,None),4,QtCore.Qt.EditRole)
    
    assert items[0].price == 4
    assert items[1].price*100 == 324

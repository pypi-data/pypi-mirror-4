# -*- coding: utf-8 -*-
"""
We create models, attach to data and see if the events all propogate.
"""

from qtalchemy import UserAttr, ClassTableModel, ModelObject
from PySide import QtCore, QtGui

class ItemTest(ModelObject):
    classEvents = ModelObject.Events()

    def __init__(self,domain=""):
        self.domain = domain
    
    name = UserAttr(str,"Name")
    domain = UserAttr(str,"Domain")
    email = UserAttr(str,"E-Mail")

    @classEvents.add("set", "name")
    @classEvents.add("set", "domain")
    def on_change_email_parts(self, attr, oldvalue):
        self.email = "%s@%s" % (self.name, self.domain)

def create_model_test():
    domains = ["a.com", "b.com", "c.com"]
    personas = [ItemTest(domain=b) for b in domains]
    
    # objects referenced in model_data_change
    these_were_touched = []
    
    def model_data_change(index1,index2):
        these_were_touched.append(index1.internalPointer())
    
    model = ClassTableModel(ItemTest,"name,domain,email".split(','),readonly=False)
    model.dataChanged.connect(model_data_change)
    model.reset_content_from_list(personas)
    
    model.setData(model.index(0,0,None),"jeff",QtCore.Qt.EditRole)
    
    assert personas[0].name == "jeff", "persona 0 should be jeff"
    assert len(these_were_touched) >= 1, "should have gotten a notification for jeff's modification"
    these_were_touched = []
    
    for p in personas:
        p.name='joe'
        
    assert len(these_were_touched) >= 3, "should have gotten a bunch of notifications for joe changes"

# -*- coding: utf-8 -*-
"""
We create models, attach to data and see if the events all propogate.
"""

from qtalchemy import *
from PySide import QtCore, QtGui

class ItemEntity(object):
    contextMenu = CommandMenu("_context_menu")
    
    @contextMenu.command("View Info", sort=200)
    def view_info(self, id):
        pass

    @contextMenu.command("Print Ticket")
    def print_ticket(self, id):
        pass

    @contextMenu.command("New Invoice", sort=400)
    def new_invoice(self, id):
        pass

def items_there_test():
    x = ItemEntity()
    assert len(x.contextMenu), "3 commands were added"
    assert x.contextMenu[0].descr.lower().startswith("view"), "view was explicitly put first"
    assert x.contextMenu[1].descr.lower().startswith("new"), "new was explicitly put next"

# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
The PBKeyEdit provides data sensitive editting for foreign key edits::

- search button
- context menus - for what? (look up referenced entity)
"""

from PySide import QtCore, QtGui
from button_edit import PBButtonEdit

class PBKeyEdit(PBButtonEdit):
    """
    PBKeyEdit is a QLineEdit derivative that offers a button on the right to 
    search for rows from a database table.  PBKeyEdit is best used in the 
    InputYoke infrastructure with a DomainEntity derived class.
    """
    def __init__(self,parent=None):
        PBButtonEdit.__init__(self,parent)
        self.button.setIcon(QtGui.QIcon(':/qtalchemy/widgets/edit-find-6.ico'))

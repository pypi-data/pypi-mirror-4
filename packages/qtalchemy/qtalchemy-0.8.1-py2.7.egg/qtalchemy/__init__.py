# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
The qtalchemy library builds a database application framework combining 
sqlalchemy and PyQt/PySide.
"""

# TODO:  Review for best use of our global namespace to highlight the correct 
# way to do things.

from PyQtHelpers import LayoutWidget, LayoutLayout, ButtonBoxButton, FormRow, \
            WindowGeometry, OnlineHelp, \
            writeTableColumnGeo, readTableColumnGeo, suffixExtId, \
            fromQType, toQType, qtapp, message_excepthook, \
            Signal, Slot, Property

from commands import DomainEntity, Command, CommandMenu, CommandEvent, \
        BoundCommandMenu, BoundCommandMenuItem

from user_attr import hasextendedattr, getextendedattr, setextendedattr, \
        UserAttr, Nullable, AttrNumeric, UseCachedValue
from sqlalchemy_helper import ModelObject, ModelSession, PBSessionMaker, UUID, \
        ValidationError, user_message, Message, instanceEvent, sessionExtension

from input_yoke import \
    addGlobalYoke, \
    InputYoke, \
    LineYoke, \
    SelectionYoke, \
    TextYoke, \
    IntegerYoke, \
    DateYoke, \
    FloatingPointYoke

# model elements
from PyQtModels import ClassTableModel, QueryTableModel, QueryClassTableModel, \
        ModelColumn, PBTableModel, AlchemyModelDelegate, modelMimeRectangle, \
        MapperMixin, WidgetAttributeMapper, ObjectRepresent, \
        attrLabel, ClassAttributeLabel, attrType, ClassAttributeType, attrReadonly

from foreign_key import ForeignKeyReferral, ForeignKeyEditYoke, ForeignKeyComboYoke

# TODO:  Some more of these should be moved to the widgets sub-module
# gui elements
from PBSearchDialog import PBSearchDialog, PBTableTab, PBMdiTableView

import icons_rc

__version_info__ = ['0', '8', '1']
__version__ = '.'.join(__version_info__)

# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2011, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from qtalchemy.widgets import PBKeyEdit
from user_attr import UserAttr
from PySide import QtCore, QtGui
from sqlalchemy.orm import mapper, create_session, relation, object_session, Query
from PyQtModels import QueryTableModel, attrReadonly
from input_yoke import InputYoke

class PopupKeyListing(PBKeyEdit):
    def __init__(self, parent, Session, foreignAttr):
        PBKeyEdit.__init__(self, parent)

        self.Session = Session
        self.foreignAttr = foreignAttr
        self.popupList = None

        self.textEdited.connect(self.refinePopup)
        self.buttonPressed.connect(self.search)

        self._initPopup()

    def _initPopup(self):
        if self.popupList is not None:
            return

        # configure the popup view as a popup
        # lots of logic copied from http://qt.gitorious.org/qt/qt/blobs/4.7/src/gui/util/qcompleter.cpp
        self.popupList = QtGui.QListView()
        self.popupList.setParent(None, QtCore.Qt.Popup)
        self.popupList.setFocusPolicy(QtCore.Qt.NoFocus)
        self.popupList.setFocusProxy(self)
        self.popupList.installEventFilter(self)

        self.popupList.clicked.connect(self.modelSelection)
        self.popupList.activated.connect(self.modelSelection)

        self.query = self.foreignAttr.getSelection()
        self.popupModel = QueryTableModel(self.query, ['name'])
        self.popupList.setModel(self.popupModel)

    def shutdown(self, obj):
        if self.popupList is not None:
            self.popupList.hide()
            self.popupList.close()
            self.popupList = None

    def event(self, e):
        if e.type() in [QtCore.QEvent.Hide]:
            self.shutdown(self)
        return PBKeyEdit.event(self, e)

    def eventFilter(self, o, e):
        if o is not self.popupList:
            return PBKeyEdit.eventFilter(self, o, e)

        if e.type() == QtCore.QEvent.KeyPress:
            if e.key() == QtCore.Qt.Key_Escape:
                self.popupList.hide()
                return True

            self.event(e)
            if e.isAccepted():
                return True

        if e.type() == QtCore.QEvent.MouseButtonPress:
            if self.popupList.isVisible() and not self.popupList.underMouse():
                self.popupList.hide()

        return False

    def modelSelection(self, index):
        self.setText(index.internalPointer().name)
        self.popupList.hide()

    def refinePopup(self, text):
        q = self.query.filter(self.foreignAttr.keyCol().ilike('{0}%'.format(text.replace('%', '%%'))))
        session = self.Session()
        q.session = session
        keys = q.limit(10).all()
        session.close()

        if len(keys) > 0:
            self.popupModel.reset_content_from_list(keys)
            rect = self.rect()
            self.popupList.move(self.mapToGlobal(rect.bottomLeft()))
            self.popupList.show()
            self.setFocus(QtCore.Qt.PopupFocusReason)
        else:
            self.popupList.hide()

    def search(self):
        self.foreignAttr.search(self, self.row)


class ForeignKeyReferral(UserAttr):
    """
    A ForeignKeyReferralEx UserAttr provides a display for a user-centric key 
    matching back to a database foreign key which is not expected to be 
    user-friendly.  This also wraps in the ability for search method which is 
    expected to display a dialog with a list of entities which can be chosen 
    in this attribute.

    :param atype:  python type of displayed key
    :param label:  widget label for UI
    :param backref:  python attribute name in the ModelObject holding the referred key object
    :param class_:  python class of referred key object
    :param userkey:  python attribute name of class_ to display or callable taking parameter of type class_
    :param entity:  The domain entity class this foreign key represents a member of.
    """
    def __init__(self, atype, label, backref, class_, userkey, entity=None, filter_query=None, readonly=False):
        self.backref = backref
        self.class_ = class_
        self.userkey = userkey
        self.filter_query = filter_query
        self.entityCls = entity
        UserAttr.__init__(self,atype,label,readonly=readonly)
        self.proxies = {}

    def fget(self,row):
        target = getattr(row,self.backref)
        if target is None:
            return None
        if callable(self.userkey):
            return self.userkey(target)
        else:
            return getattr(target, self.userkey)

    def fset(self,row,value):
        if value is None:
            # for null assignments, we don't need to look at the database
            setattr(row,self.backref,None)
            return
        s = self.session(row)
        try:
            # we use ilike to complement the QtCore.Qt.CaseInsensitive in the
            # QCompleter
            setattr(row,self.backref,s.query(self.class_).filter(getattr(self.class_,self.userkey).ilike(value)).one())
        except Exception as e:
            print e
            setattr(row,self.backref,None)

    def keyCol(self):
        return getattr(self.class_, self.userkey)

    def getSelection(self):
        q=Query((self.keyCol().label("name"),))
        if self.filter_query:
            q = self.filter_query(q)
        return q

    def yoke_specifier(self):
        if self.entityCls is None:
            return "foreign_key_combo"
        else:
            return "foreign_key"

    def WidgetFactory(self, parent, index):
        # Note that it's not entirely clear to me what criteria is appropriate
        # for selecting a PBKeyEdit or a QComboBox.
        if self.entityCls is not None:
            w = PopupKeyListing(parent, None, self)
            w.model_index = index
            # The PBKeyEdit has a 'search button' which offers a more
            # comprensive notion of a list of options.  The attached entityCls
            # is expected to know what data to display in the search list.
        else:
            # Some days we think this should be a combo-box.
            w = QtGui.QComboBox(parent)
            w.setEditable(True)
        return w

    def WidgetBind(self,widget,row):
        Session = self.session_maker(row)

        # note that a PBKeyEdit is a QLineEdit
        if isinstance(widget, PopupKeyListing):
            widget.Session = Session
            widget.row = row
        
        if isinstance(widget,QtGui.QComboBox):
            col_model = QueryTableModel(self.getSelection(),ssrc=Session)
            col_model.reset_content_from_session()
            widget.setModel(col_model)

    def search(self, widget, row):
        Session = self.session_maker(row)

        index = None
        parent = None
        try:
            index = widget.model_index
            parent = widget.parent()
        except:
            pass

        import PBSearchDialog
        srch = PBSearchDialog.PBSearchDialog(Session, self.entityCls, widget.parent())
        srch.setWindowModality(QtCore.Qt.ApplicationModal)
        srch.show()
        srch.exec_()
        result = srch.selectedItem(self.class_,self.session(row))
        if result is not None:
            if index is not None:
                index.model().ensureNoFlipper(index)

            # we set the data internally
            setattr(row, self.backref, result)
            #setattr(row, self.backref, srch.selected_id)
            #print "Selected item:  {0}\n".format(self.fget(row))

            if index is None:
                # We are not a widget associated with an abstract item view and
                # so we suppose we are a visual element on a "dialog box
                # lifespan".  Therefore the widget needs to be updated with the
                # visual identifier of this foreign key.
                widget.setText(self.fget(row))
            else:
                #index.model().setData(index, self.fget(row))
                parent.setFocus()

class ForeignKeyEditYoke(InputYoke):
    def __init__(self,mapper,attr):
        InputYoke.__init__(self,mapper)
        self.attr = attr
        mapper.reverse_yoke(attr,self)

    def Factory(self):
        self.widget = PBKeyEdit()
        self._baseAdoptWidget(self.widget)
        self.widget.editingFinished.connect(self.Save)
        self.widget.buttonPressed.connect(self.Search)
        if attrReadonly(self.mapper.cls, self.attr):
            self.widget.setReadOnly(True)
        return self.widget

    def AdoptWidget(self, widget):
        self.widget = widget
        self._baseAdoptWidget(self.widget)
        self.widget.editingFinished.connect(self.Save)
        self.widget.buttonPressed.connect(self.Search)
        if attrReadonly(self.mapper.cls, self.attr):
            self.widget.setReadOnly(True)

    def Search(self):
        user_attr = getattr(self.mapper.cls,self.attr)
        row = self.mapper.obj
        Session = user_attr.session_maker(row)

        index = None
        parent = None
        try:
            index = self.widget.model_index
            parent = self.widget.parent()
        except:
            pass

        import PBSearchDialog
        srch = PBSearchDialog.PBSearchDialog(Session, user_attr.entityCls, self.widget.parent())
        srch.setWindowModality(QtCore.Qt.ApplicationModal)
        srch.show()
        srch.exec_()
        result = srch.selectedItem(user_attr.class_,user_attr.session(row))
        if result is not None:
            setattr(row, user_attr.backref, result)
            #setattr(row, self.backref, srch.selected_id)
            #print "Selected item:  {0}\n".format(self.fget(row))

            if index is None:
                # We are not a widget associated with an abstract item view and
                # so we suppose we are a visual element on a "dialog box
                # lifespan".  Therefore the widget needs to be updated with the
                # visual identifier of this foreign key.
                self.widget.setText(user_attr.fget(row))
            else:
                #index.model().setData(index, user_attr.fget(row))
                parent.setFocus()

    def Bind(self):
        user_attr = getattr(self.mapper.cls,self.attr)
        Session = user_attr.session_maker(self.mapper.obj)

        # TODO: this is a very bad performance problem on large data-sets.  I
        # suspect we need a highly customized completer so as to only load the
        # parts with this prefix.
        col_model = QueryTableModel(user_attr.getSelection(),ssrc=Session)
        col_model.setParent(self.widget)
        col_model.reset_content_from_session()

        col_completer = QtGui.QCompleter(self.widget)

        col_completer.setCompletionMode(QtGui.QCompleter.InlineCompletion)
        col_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.widget.setCompleter(col_completer)
        #widget.setValidator(ForeignKeyValidator(fk=col_type,session=session))
        col_completer.setModel(col_model)

        if isinstance(self.widget, QtGui.QLineEdit):
            self.widget.setText(self.mapper.getObjectAttr(self.attr))
        else:
            self.widget.setEditText(self.mapper.getObjectAttr(self.attr))

    def Save(self):
        if attrReadonly(self.mapper.cls, self.attr):
            return
        if isinstance(self.widget, QtGui.QLineEdit):
            self.mapper.setObjectAttr(self.attr,self.widget.text())
        else:
            self.mapper.setObjectAttr(self.attr,self.widget.currentText())

class ForeignKeyComboYoke(InputYoke):
    def __init__(self,mapper,attr):
        InputYoke.__init__(self,mapper)
        self.attr = attr
        mapper.reverse_yoke(attr,self)

    def Factory(self):
        self.widget = QtGui.QComboBox()
        self._baseAdoptWidget(self.widget)
        self.widget.setEditable(True)
        #self.widget.editingFinished.connect(self.Save)
        return self.widget

    def AdoptWidget(self, widget):
        self.widget = widget
        self._baseAdoptWidget(self.widget)
        self.widget.setEditable(True)
        if hasattr(self.widget, "setReadOnly") and attrReadonly(self.mapper.cls, self.attr):
            self.widget.setReadOnly(True)
        #self.widget.editingFinished.connect(self.Save)
        return self.widget

    def Bind(self):
        user_attr = getattr(self.mapper.cls,self.attr)
        Session = user_attr.session_maker(self.mapper.obj)

        col_model = QueryTableModel(user_attr.getSelection(),ssrc=Session)
        col_model.reset_content_from_session()

        self.widget.setModel(col_model)
        self.widget.setEditText(self.mapper.getObjectAttr(self.attr))

    def Save(self):
        if attrReadonly(self.mapper.cls, self.attr):
            return
        self.mapper.setObjectAttr(self.attr,self.widget.currentText())

###
# I really want this ForeignKeyValidator to give aggressive foreign key validation, but QValidator evidently confuses me.
###
class ForeignKeyValidator(QtGui.QValidator):
    def __init__(self,parent=None,fk=None,session=None):
        QtGui.QValidator.__init__(self,parent)
        self.fkr = fk
        self.session = session

    def fixup(self,input):
        print "f"
        like_me = self.session.query(self.fkr.header_name).filter(self.fkr.header_name.ilike(str(input))).all()
        if len(like_me) == 1:
            print QtCore.QString(like_me[0].vid)
            input.replace(0,6,QtCore.QString(like_me[0].vid))
            print input, type(input)
        #return str(input)

    def validate(self,input,pos):
        print "v"
        try:
            like_me = self.session.query(self.fkr.header_name).filter(self.fkr.header_name.ilike(str(input))).one()
            print "v2"
            input.replace(0,6,QtCore.QString(like_me[0].vid))
            return QtGui.QValidator.Acceptable,pos
        except:
            return QtGui.QValidator.Intermediate,pos

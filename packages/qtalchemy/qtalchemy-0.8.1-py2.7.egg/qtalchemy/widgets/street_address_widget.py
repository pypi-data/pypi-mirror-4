# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from PySide import QtGui,QtCore
import re
from qtalchemy import *

from button_edit import *  # for Signal and Property

def is_country(s):
    """
    Return true if the string s looks like a country name.

    We only check that the string doesn't have numbers in it (very lame for the moment).
    """
    return re.search('[^ a-zA-Z]',s) is None

def city_state(s):
    """
    >>> city_state('bethlehem pa')
    ('Bethlehem', 'PA')
    >>> city_state('seattle, washington')
    ('Seattle', 'Washington')
    >>> city_state('New york, new york')
    ('New York', 'New York')
    """
    s = s.strip()
    if s.find(',')>-1:
        city,state = s.rsplit(',',2)
    elif s.find(' ')>-1:
        city,state = s.rsplit(' ',2)
    else:
        city,state = s,None
    city = city.strip()
    state = state.strip()
    if state is not None and len(state)==2:
        state = state.upper()
    else:
        state = state.title()
    city = city.title()
    return city,state

def parse_address(addr):
    """
    Parses a single string into street, city, state, zip and country.  
    Semi-colons, new lines, and carriage returns are all recognized as logical 
    line breaks.  Parsing proceeds roughly from right to left recognizing the 
    country first (if there), zip/postal code, state/province, city, and finally 
    street address components.  Two street addresses are recognized for PO Box 
    lines or other street details.

    >>> parse_address('5522 Penelope Parkway; dayton, me 12345')
    ('5522 Penelope Parkway', None, 'Dayton', 'ME', '12345', 'USA')
    >>> parse_address('PO box 14; 103 Kaiser Lane; Marksville, AK 98765')
    ('PO Box 14', '103 Kaiser Lane', 'Marksville', 'AK', '98765', 'USA')
    >>> parse_address('531 fiddley blvd; Marksville, AB K1A 0B1')
    ('531 Fiddley Blvd', None, 'Marksville', 'AB', 'K1A 0B1', 'Canada')
    """
    lines = [l for l in re.split('(;|\n|\r)',addr) if l not in list(';\n\r')]
    address1=address2=city=state=zip=country=None
    items = ("street","zip","country")
    while len(lines)>0 and len(items)>0:
        if items[-1] == "country":
            if is_country(lines[-1]):
                country = lines[-1]
                lines = lines[:-1]
            items = items[:-1]
            continue
        elif items[-1] == "zip":
            if re.search('[0-9]{5}$',lines[-1].strip()):
                # USA zip
                if country is None:
                    country="USA"
                zip = lines[-1].strip()[-5:]
                city, state = city_state(lines[-1].strip()[:-5])
                lines = lines[:-1]
                items = items[:-1]
            elif re.search('[0-9]{5}-[0-9]{4}$',lines[-1].strip()):
                # USA zip
                if country is None:
                    country="USA"
                zip = lines[-1].strip()[-10:]
                city, state = city_state(lines[-1].strip()[:-10])
                lines = lines[:-1]
                items = items[:-1]
            elif re.search('[0-9a-zA-Z]{3} [0-9a-zA-Z]{3}$',lines[-1].strip()):
                # Canada zip
                if country is None:
                    country="Canada"
                zip = lines[-1].strip()[-7:]
                city, state = city_state(lines[-1].strip()[:-7])
                lines = lines[:-1]
                items = items[:-1]
            else:
                items = items[:-1]
            continue
        else:
            if len(lines)==1:
                address1 = lines[0].strip().title()
            elif len(lines)==2:
                address1,address2 = lines[0].strip().title(),lines[1].strip().title()
            else:
                raise Exception("address can't be parsed")
            lines=[]
    if address1 is not None and address1.startswith('Po Box'):
        address1 = 'PO Box' + address1[6:]
    if address2 is not None and address2.startswith('Po Box'):
        address2 = 'PO Box' + address2[6:]
    return (address1,address2,city,state,zip,country)

def concat_address(addr1, addr2, city, state, zip, country, linebreak='\n'):
    '''
    This reverses the parsing action of :func:parse_address joining the 
    components of an address into a single string.
    
    >>> concat_address('230 E. Main Street', None, 'Bethlehem', 'OH', '18030', '', linebreak='; ')
    '230 E. Main Street; Bethlehem OH 18030'
    '''
    lines = []
    if addr1 not in (None,''):
        lines.append(addr1)
    if addr2 not in (None,''):
        lines.append(addr2)
    lines.append(' '.join([v for v in (city,state,zip) if v not in (None, '')]))
    if country not in (None,''):
        lines.append(country)
    return linebreak.join(lines)

class StreetAddressEdit(QtGui.QStackedWidget):
    addressParsed = Signal(name='addressParsed')

    def __init__(self,parent=None):
        QtGui.QStackedWidget.__init__(self,parent)

        self.concat_page = QtGui.QWidget()
        self.concat_page.setObjectName("concat_page")
        vbox = QtGui.QVBoxLayout(self.concat_page)
        vbox.setContentsMargins(1,1,1,1)
        self.unparsedAddress_edit = LayoutWidget(vbox,QtGui.QTextEdit(self.concat_page))
        self.unparsedAddress_edit.setObjectName("unparsedAddress_edit")
        hbox = LayoutLayout(vbox,QtGui.QHBoxLayout())
        self.btnParse = LayoutWidget(hbox,QtGui.QPushButton("Parse (F4)",self.concat_page))
        size = self.btnParse.minimumSize()
        size.setWidth(140)
        self.btnParse.setMinimumSize(size)
        hbox.addItem(QtGui.QSpacerItem(375, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.addWidget(self.concat_page)

        self.parsed_page = QtGui.QWidget()
        grid = QtGui.QGridLayout(self.parsed_page)
        grid.setContentsMargins(0,0,0,0)
        grid.setObjectName("gridLayout")
        self.address1_edit = QtGui.QLineEdit(self.parsed_page)
        self.address1_edit.setObjectName("address1_edit")
        grid.addWidget(self.address1_edit, 0, 0, 1, 3)
        self.address2_edit = QtGui.QLineEdit(self.parsed_page)
        self.address2_edit.setObjectName("address2_edit")
        grid.addWidget(self.address2_edit, 1, 0, 1, 3)
        self.city_edit = QtGui.QLineEdit(self.parsed_page)
        self.city_edit.setObjectName("city_edit")
        grid.addWidget(self.city_edit, 3, 0, 1, 1)
        self.state_edit = QtGui.QLineEdit(self.parsed_page)
        self.state_edit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.state_edit.setObjectName("state_edit")
        grid.addWidget(self.state_edit, 3, 1, 1, 1)
        self.zip_edit = QtGui.QLineEdit(self.parsed_page)
        self.zip_edit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.zip_edit.setObjectName("zip_edit")
        grid.addWidget(self.zip_edit, 3, 2, 1, 1)
        self.country_edit = QtGui.QLineEdit(self.parsed_page)
        self.country_edit.setObjectName("country_edit")
        grid.addWidget(self.country_edit, 4, 1, 1, 2)
        self.btnConcatenate = QtGui.QPushButton("Concatenate (F4)",self.parsed_page)
        self.btnConcatenate.setObjectName("btnConcatenate")
        size = self.btnConcatenate.minimumSize()
        size.setWidth(140)
        self.btnConcatenate.setMinimumSize(size)
        grid.addWidget(self.btnConcatenate, 4, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.addWidget(self.parsed_page)

        self.parseAct = QtGui.QAction("parse/concat",self)
        self.parseAct.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F4))
        self.parseAct.triggered.connect(self.parse_or_concat)
        self.addAction(self.parseAct)

        self.btnParse.clicked.connect(self.toParsed)
        self.btnConcatenate.clicked.connect(self.toConcat)

    def parse_or_concat(self):
        if self.currentIndex() == 0:
            self.toParsed()
        else:
            self.toConcat()

    def toParsed(self):
        try:
            address1,address2,city,state,zip,country = parse_address(self.unparsedAddress_edit.toPlainText())
            self.address1_edit.setText(address1)
            self.address2_edit.setText(address2)
            self.city_edit.setText(city)
            self.state_edit.setText(state)
            self.zip_edit.setText(zip)
            self.country_edit.setText(country)
            self.setCurrentIndex(1)
            self.addressParsed.emit()
        except Exception, e:
            QtGui.QMessageBox.information(self.parent(),QtGui.QApplication.applicationName(),str(e))

    def toConcat(self):
        addr = concat_address(
                    self.address1_edit.text(),
                    self.address2_edit.text(),
                    self.city_edit.text(),
                    self.state_edit.text(),
                    self.zip_edit.text(),
                    self.country_edit.text())
        self.unparsedAddress_edit.setPlainText(addr)
        self.setCurrentIndex(0)

    def implantProperty(self,prop,v):
        if self.currentIndex() == 0:
            self.toParsed()
        #print "Set {0}={1}".format(prop,v)
        getattr(self, prop+"_edit").setText(v)

    def extractProperty(self,prop):
        if self.currentIndex() == 0:
            t = parse_address(self.unparsedAddress_edit.toPlainText())
            index = 'address1,address2,city,state,zip,country'.split(',').index(prop)
            #print "Get (parsing) {0}={1}".format(prop,t[index])
            return t[index]
        else:
            #print "Get (easy) {0}={1}".format(prop,getattr(self, prop+"_edit").text())
            return getattr(self, prop+"_edit").text()

    address1 = Property("QString", 
            lambda self: self.extractProperty("address1"), 
            lambda self, v: self.implantProperty("address1", v))

    address2 = Property("QString", 
            lambda self: self.extractProperty("address2"), 
            lambda self, v: self.implantProperty("address2", v))

    city = Property("QString", 
            lambda self: self.extractProperty("city"), 
            lambda self, v: self.implantProperty("city", v))

    state = Property("QString", 
            lambda self: self.extractProperty("state"), 
            lambda self, v: self.implantProperty("state", v))

    zip = Property("QString", 
            lambda self: self.extractProperty("zip"), 
            lambda self, v: self.implantProperty("zip", v))

    country = Property("QString", 
            lambda self: self.extractProperty("country"), 
            lambda self, v: self.implantProperty("country", v))


class StreetAddressYoke(InputYoke):
    def __init__(self,mapper,attr):
        InputYoke.__init__(self,mapper)
        self.attr = attr
        user_attr = getattr(self.mapper.cls,self.attr)
        for x in user_attr.my_cols:
            mapper.reverse_yoke(x,self)
        self.trapRecurse = 0

    def Factory(self):
        self.widget = StreetAddressEdit()
        self.widget.addressParsed.connect(self.Save)
        self._baseAdoptWidget(self.widget)
        return self.widget

    def AdoptWidget(self, widget):
        raise NotImplementedError()

    def Bind(self):
        if self.trapRecurse > 0:
            return

        user_attr = getattr(self.mapper.cls,self.attr)
        
        parts = [self.mapper.getObjectAttr(a) for a in user_attr.my_cols]
        parts = ["" if p is None else p for p in parts]
        props = 'address1,address2,city,state,zip,country'.split(',')
        if parts == [""]*6:
            self.widget.setCurrentIndex(0)
        for i in range(6):
            self.widget.setProperty(props[i], parts[i])
        if parts != [""]*6:
            self.widget.setCurrentIndex(1)

    def Save(self):
        try:
            self.trapRecurse += 1
            user_attr = getattr(self.mapper.cls,self.attr)

            props = 'address1,address2,city,state,zip,country'.split(',')
            for i in range(6):
                self.mapper.setObjectAttr(user_attr.my_cols[i],self.widget.property(props[i]))
        finally:
            self.trapRecurse -= 1

class StreetAddress(UserAttr):
    """
    A StreetAddress UserAttr displays a street address in a stacked widget 
    allowing multi-line input which can be parsed into the constituent parts.

    TODO:  force the constituent parsing before allowing the bound attributes to passed off as valid.

    :param myCols:  A list of attribute names which store (in order):  
                address1, address2, city, state, zip, country
    """
    def __init__(self, label, myCols, whats_this=None):
        self.my_cols = myCols
        UserAttr.__init__(self, str, label, whats_this=whats_this)

    def fget(self,row):
        return concat_address(*map(lambda x: getattr(row,x),self.my_cols))

    def fset(self,row,value):
        raise NotImplementedError("StreetAddress types may not be assigned en-masse")

    def yoke_specifier(self):
        return 'address'

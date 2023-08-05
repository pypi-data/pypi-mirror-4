# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from qtalchemy import *
from qtalchemy.widgets import TableView
from qtalchemy.dialogs import *
from PySide import QtCore, QtGui
from sqlalchemy.orm.attributes import InstrumentedAttribute
import os.path
import decimal
import datetime
import fuzzyparsers

class ImportColumn(ModelObject):
    def __init__(self, identifier, label):
        self.identifier = identifier
        self.label = label
    
    identifier = UserAttr(str, "Identifier")
    label = UserAttr(str, "Label")

class ImportIntroPage(QtGui.QWizardPage):
    """
    This wizard page takes a class and displays the elements of that class for 
    import.
    """
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setTitle("Data Import")
        self.setSubTitle("\
The list of available fields in the import class are shown below.  Columns in \
import files are first matched with exact matches in the identifier list and then \
matched against prefixes of the labels.")

        main = QtGui.QVBoxLayout(self)
        self.table = LayoutWidget(main, TableView())
        self.model = ClassTableModel(ImportColumn, ("identifier", "label"))
        self.table.setModel(self.model)

    def loadImportColumns(self, cls, attrList=None):
        if attrList is None:
            attrList = []
            for attr in dir(cls):
                col = getattr(cls, attr)
                try:
                    x = attrLabel(cls, attr)
                    if x not in [None, ""] and not attrReadonly(cls, attr):
                        attrList.append(attr)
                except Exception as e:
                    # if we can't find a nice label, we skip it
                    pass

        items = [ImportColumn(attr, attrLabel(cls, attr)) for attr in attrList]
        items.sort(key=lambda x: x.label)
        self.model.reset_content_from_list(items)

class ImportDataSource(QtGui.QWizardPage):
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setTitle("Data Import")
        self.setSubTitle("Select a file from which to import the data.")

        main = QtGui.QVBoxLayout(self)
        fileSelection = LayoutLayout(main, QtGui.QHBoxLayout())
        self.label = LayoutWidget(fileSelection, QtGui.QLabel("&Data File:"))
        self.fileEdit = LayoutWidget(fileSelection, QtGui.QLineEdit())
        self.fileEdit.textChanged.connect(self.completeChanged.emit)
        self.label.setBuddy(self.fileEdit)
        LayoutWidget(fileSelection, QtGui.QPushButton("Bro&wse...")).clicked.connect(self.import_browse)

    def import_browse(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,"Data for Import",filter="Comma Separated Values (*.csv);;All Files (*.*)")
        if fileName != "":
            self.fileEdit.setText(fileName)
            self.completeChanged.emit()

    def isComplete(self):
        return os.path.isfile(self.fileEdit.text())

class ImportDataPreview(QtGui.QWizardPage):
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setTitle("Data Import")
        self.setSubTitle("Preview the imported data.")

        main = QtGui.QVBoxLayout(self)
        self.table = LayoutWidget(main, TableView())
        
        self.session = None

    def loadData(self, Session, cls, csvFile):
        import csv
        
        if self.session is not None:
            self.session.close()
            self.session = None

        self.session = Session()
        importObjects = []
        
        errors = []
        cols = None
        index = 0
        for row in csv.reader(open(csvFile, "r")):
            if cols is None:
                cols = []
                for item in row:
                    cols.append(item.strip())
                self.model = ClassTableModel(cls, cols)
                self.table.setModel(self.model)
            else:
                try:
                    index += 1
                    c = cls()
                    self.session.add(c)
                    importObjects.append(c)
                    for i in range(len(cols)):
                        type_ = ClassAttributeType(getattr(cls, cols[i]))
                        v = row[i]
                        if type_ in (decimal.Decimal, int, float) and v=="":
                            v = "0"
                        if type_ in (datetime.date, ):
                            v = fuzzyparsers.parse_date(v)
                        if not isinstance(v, type_):
                            v = type_(v)
                        #print row[i], type_, type_(row[i])
                        setattr(c, cols[i], v)
                except Exception as e:
                    errors.append("Row {0}:  {1}".format(index, str(e)))

        if len(errors) > 0 and len(errors) <= 5:
            errMsg = """\
There were {0} errors importing the data.

<ul>
{1}
</ul>""".format(len(errors), '\n'.join(["<li>{0}</li>".format(e) for e in errors]))
            appMessage(self, Message.Ok, errMsg)
        elif len(errors) > 5:
            errMsg = """\
There were {0} errors importing the data.  The first 5 are shown below.

<ul>
{1}
</ul>""".format(len(errors), '\n'.join(["<li>{0}</li>".format(e) for e in errors[:5]]))
            appMessage(self, Message.Ok, errMsg)

        self.model.reset_content_from_list(importObjects)

    def finishImport(self):
        messaged_commit(self.session, self)
        self.session.close()
        self.session = None
        

class ImportWizard(QtGui.QWizard):
    """
    Returns a QWizard to take rows given by the user and create an instance 
    of each cls from each row.  The rows may come from a csv file or via raw 
    entry in a table.

    Wizard Structure:

    - Intro page listing accepted elements of the class cls
    - Page asking for an input csv file or allowing raw entry
    - Page with list of data or allowing entry
    
    >>> from sqlalchemy import Table, Column, String, Integer, MetaData, create_engine
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> 
    >>> from qtalchemy import *
    >>> from qtalchemy.ext.dataimport import *
    >>> from PySide import QtCore, QtGui
    >>> 
    >>> metadata = MetaData()
    >>> Base = declarative_base(metadata=metadata, cls=ModelObject)
    >>> 
    >>> class People(Base):
    ...     __table__ = Table('people', metadata,
    ...                     Column('id', Integer, primary_key=True),
    ...                     Column('f_name', String(50), info={"label": "First Name"}),
    ...                     Column('l_name', String(50), info={"label": "Last Name"}),
    ...                     Column('title', String(10), info={"label": "Title"}))
    ... 
    >>> engine = create_engine("sqlite://")
    >>> metadata.bind = engine
    >>> metadata.create_all()
    >>> Session = PBSessionMaker(bind=engine)
    >>> 
    >>> app = qtapp()
    >>> wiz = ImportWizard(Session, People)
    >>> wiz.show()  #doctest: +SKIP
    >>> wiz.exec_()  #doctest: +SKIP
    """
    def __init__(self, Session, cls, parent=None):
        QtGui.QWizard.__init__(self, parent)

        self.Session = Session
        self.cls = cls

        self.setWindowTitle("Import Wizard")

        self.intro = ImportIntroPage()
        self.intro.loadImportColumns(cls)

        self.dataSource = ImportDataSource()

        self.dataPreview = ImportDataPreview()

        self.introId = self.addPage(self.intro)
        self.sourceId = self.addPage(self.dataSource)
        self.previewId = self.addPage(self.dataPreview)

        self.currentIdChanged.connect(self.pageFlip)
        self.accepted.connect(self.dataPreview.finishImport)

    def pageFlip(self, newid):
        if newid == self.previewId:
            self.dataPreview.loadData(self.Session, self.cls, self.dataSource.fileEdit.text())

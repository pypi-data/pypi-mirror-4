Introduction
------------

The QtAlchemy library is a collection of Qt Model-View classes and helper
functions to aid in rapid development of desktop database applications.  It
aims to provide a strong API for exposing foreign key relationships in elegant
and immediate ways to the user of applications.  Context menus, searches and
combo-boxes and tabbed interfaces are all utilized.  The use of SQLAlchemy
makes it possible that these features are supported on a variety of database
backends with virtually no code changes.

The Command class gives a way to construct menus and toolbars from decorated
python functions.  The power of this becomes more evident when bound to a view
where the command function can then receive the identifier of the selected item
of the view.  This provides a flexible way to link commands to any sqlalchemy
query generated views.

Documentation is available at http://qtalchemy.org .

QtAlchemy is currently being developed with python 2.7.x, SQLAlchemy 0.7.x and
PyQt 4.8.x.  It is expected that it would be functional on all nearby versions.
There is an effort made to make sure that feature parity is attained for
windows and linux (and, presumably, mac as well).

As of qtalchemy version 0.8.x, qtalchemy uses PySide.  See licensing comments
at the bottom of this file.  To use PyQt4 instead of PySide, you must install
from the source in the bitbucket repository.  Install in the following
way::

    python qtbindings.py --platform=PyQt4
    python setup.py build
    sudo python setup.py install

Example
-------

In the interests of being concise, the example given here does not reference a
database.

The UserAttr property class provides yet another type defined python property.
The purpose of reinventing this was to ensure that we could interact with our
models sufficiently and provide a uniform experience for SQLAlchemy column
properties and UserAttr properties.

    >>> from qtalchemy import UserAttr
    >>> import datetime
    >>> class Person(object):
    ...     name=UserAttr(str,"Name")
    ...     birth_date=UserAttr(datetime.date,"Birth Date")
    ...     age=UserAttr(int,"Age (days)",readonly=True)
    ...
    ...     @age.on_get
    ...     def age_getter(self):
    ...         return (datetime.date.today()-self.birth_date).days

With this declaration, we can declare a person and compute their age:

    >>> me = Person()
    >>> me.name = "Joel"
    >>> me.birth_date = datetime.date(1979,1,9)
    >>> me.age  #depends on today! -- #doctest: +SKIP
    11746
    >>> me.age-(datetime.date.today()-datetime.date(2011,1,9)).days  # on birthday 1<<5
    11688

We can create a dialog showing the name & birth-date.  The main magic happens
in the addBoundForm call which obtains labels from the UserAttr classes and
places the correct edit widgets on screen.

    >>> from PySide import QtCore, QtGui
    >>> from qtalchemy import MapperMixin, LayoutLayout, ButtonBoxButton, LayoutWidget
    >>> 
    >>> class PersonEdit(QtGui.QDialog,MapperMixin):
    ...     def __init__(self,parent,person):
    ...         QtGui.QDialog.__init__(self,parent)
    ...         MapperMixin.__init__(self)
    ... 
    ...         self.person = person
    ... 
    ...         vbox = QtGui.QVBoxLayout(self)
    ...         mm = self.mapClass(Person)
    ...         mm.addBoundForm(vbox,["name","birth_date"])
    ...         mm.connect_instance(self.person)
    ... 
    ...         buttons = LayoutWidget(vbox,QtGui.QDialogButtonBox())
    ...         self.close_button = ButtonBoxButton(buttons,QtGui.QDialogButtonBox.Ok)
    ...         buttons.accepted.connect(self.btnClose)
    ... 
    ...     def btnClose(self):
    ...         self.submit() # changes descend to model on focus-change; ensure receiving the current focus
    ...         self.close()

And, now, we only need some app code to actually kick this off

    >>> app = QtGui.QApplication([])
    >>> sam = Person()
    >>> sam.name = "Samuel"
    >>> d = PersonEdit(None,sam)
    >>> d.exec_()  # gui interaction -- #doctest: +SKIP
    0
    >>> sam.age    # assumes selection of yesterday in the gui -- #doctest: +SKIP
    1

Development
-----------

QtAlchemy is still in heavy core development as schedule allows.  Major new 
emphases include:

* abstracting query building for lists allowing user sorting and additional 
  columns
* html generation for use with the QtWebKit bridge
* qml view for queries

Changelog
---------

0.8.1:

* mainly bugfixes for PySide support

0.8.0:

* Change to PySide as default imports
* Relax license from GPL to LGPL
* Improve yoke change handling
* Create new PopupKeyListing for foreign key entry

0.7.1:

* QueryDataView gained basic ability to requery on column header clicks for
  sorting
* a few doc fixes
* new helper function family for using Geraldo in qtalchemy.ext.reporttools

0.7.0:

* improved exception error handling and reporting for GUI applications with-out
  console
* new yoke supporting a combo box 
* improve yoke documentation
* add complete examples to front of documentation
* various model/list improvements including column width defaulting

0.6.12:

* BoundCommandMenu has slots to be dispatched from html binding entity commands to 
  html viewing forms
* structured load and save extending the framework in BoundDialog
* new TreeView exposing the QTreeView
* tree model support in PBTableModel
* improved PySide portability and fixed various crash-bugs related to that

0.6.11:

* context sensitive help and status tips for fields
* new preCommand/refresh signals with CommandEvent structure allowing aborting by the ambient screen
* improvements in the generic data import wizard
* table view improvements (bug fixes, corrected model updates to be more precise)
* use pywin32 ShellExecute instead of os.system for better windows support

0.6.10:

* renamed to qtalchemy
* exposed Qt's association of icons with commands appearing in menus and toolbars
* moved qtalchemy.PBTable to qtalchemy.widgets.TableView
* new qtalchemy.ext module for common dialogs (a data import wizard for now)

0.6.9:

* wrote a broad outline of documentation
* added boolean, time, and formatted text input yokes
* rewrote DialogGeo as WindowGeometry saving and restoring window and splitter 
  geometry for arbitrary windows
* brand new command structure replacing DomainEntity

0.6.8:

* color and font control in the python business object layer
* improved packaging support for windows
* QGridLayout support in WidgetAttributeMapper
* extended UserAttr value storage to include attribute paths (e.g. self.sub.sub1.value)
* new QtAlchemy.xplatform module for cross platform helpers
* rewrote WidgetAttributeMapper using InputYoke methodology
* rename PBEventMappedBase to ModelObject
* additions and corrections to examples
* event model corrections (more needed)

0.6:

* new QtAlchemy.widgets sub-module for QLineEdit derived classes (others in the future)
* new QtAlchemy.dialogs sub-module for auth dialog classes
* continued tweaks for PySide and nosetests 

0.5.1

* first usable (??) release

License
-------

QtAlchemy is licensed under the LGPL now that it defaults to shipping with
PySide imports.  I find this to be a rather unique licensing situation that we
now have with PyQt4 and PySide.  I can write my code for PySide and LGPL it and
it is totally legitimate.  However, it also seems entirely legitimate for a
user of my library to switch the imports from PySide to PyQt4 ... but then
you will need to consult a lawyer about the license for that amalgamation since
depending on PyQt4 requires the library to be GPL.

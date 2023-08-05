# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from qtalchemy import *
from PySide import QtCore, QtGui
from auth_settings import AuthSettings
from objectforms import MapperDialog, exception_message_box

class MultiAuthDialog(MapperDialog):
    def __init__(self,parent=None,init_session_maker=None,init_db=None):
        MapperDialog.__init__(self,parent)
        self.init_session_maker = init_session_maker
        self.init_db = init_db

        self.settings = AuthSettings()
        self.settings.loadSettings()

        self.setWindowTitle(self.tr("Log In"))

        self.m = self.mapClass(AuthSettings)
        
        main = QtGui.QVBoxLayout(self)
        self.tabs = LayoutWidget(main,QtGui.QTabWidget())
        self.tabs.addTab(self.sqlite_tab(),"SQLite")
        self.tabs.addTab(self.firebird_tab(),"Firebird")
        self.tabs.addTab(self.mysql_tab(),"MySQL")
        self.tabs.addTab(self.postgresql_tab(),"PostgreSQL")
        for i in range(4):
            if self.tabs.widget(i).prefix == self.settings.server_type:
                self.tabs.setCurrentIndex(i)
                if self.settings.remember_user and hasattr(self.tabs.widget(i),"password"):
                    self.tabs.widget(i).password.setFocus()
                elif self.settings.remember_server and hasattr(self.tabs.widget(i),"user"):
                    self.tabs.widget(i).user.setFocus()

        remember_layout = LayoutLayout(main,QtGui.QHBoxLayout())
        self.m.addBoundField(remember_layout,"remember_server")
        self.m.addBoundField(remember_layout,"remember_user")
        self.m.connect_instance(self.settings)

        buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox())
        buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
        buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

    def sqlite_tab(self):
        wid = QtGui.QWidget()
        wid.prefix = "sqlite"
        wid.m = self.mapClass(AuthSettings)
        l1 = QtGui.QVBoxLayout(wid)
        selector = LayoutLayout(l1,QtGui.QHBoxLayout())
        LayoutWidget(selector, QtGui.QLabel("Database File:"))
        self.sqlite_file = wid.m.addBoundField(selector,"database")
        LayoutWidget(selector, QtGui.QPushButton("&Browse...")).clicked.connect(self.sqlite_browse)
        
        if self.init_db is not None:
            init = LayoutLayout(l1,QtGui.QHBoxLayout())
            init.addStretch()
            LayoutWidget(init, QtGui.QPushButton("&Initialize Database")).clicked.connect(self.sqlite_initialize)
        
        wid.m.connect_instance(self.settings)

        return wid

    def sqlite_browse(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,"Select Existing SQLite Database",filter="SQLite databases (*.db);;All Files (*.*)")
        if fileName != "":
            self.sqlite_file.setText(fileName)

    def sqlite_initialize(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,"New SQLite Database",filter="SQLite databases (*.db);;All Files (*.*)")
        if fileName != "":
            self.init_db("sqlite:///" + fileName)
            self.sqlite_file.setText(fileName)

    def mysql_tab(self):
        wid = QtGui.QWidget()
        wid.prefix = "mysql"
        wid.m = self.mapClass(AuthSettings)
        grid = QtGui.QFormLayout(wid)
        wid.server = wid.m.addBoundField(grid,"server")
        wid.m.addBoundField(grid,"database")
        wid.user = wid.m.addBoundField(grid,"user")
        wid.password = wid.m.addBoundField(grid,"password")
        wid.password.setEchoMode(QtGui.QLineEdit.Password)
        wid.m.connect_instance(self.settings)

        return wid

    def postgresql_tab(self):
        wid = QtGui.QWidget()
        wid.prefix = "postgres"
        wid.m = self.mapClass(AuthSettings)
        grid = QtGui.QFormLayout(wid)
        wid.server = wid.m.addBoundField(grid,"server")
        wid.m.addBoundField(grid,"database")
        wid.user = wid.m.addBoundField(grid,"user")
        wid.password = wid.m.addBoundField(grid,"password")
        wid.password.setEchoMode(QtGui.QLineEdit.Password)
        wid.m.connect_instance(self.settings)

        return wid

    def firebird_tab(self):
        wid = QtGui.QWidget()
        wid.prefix = "firebird"
        wid.m = self.mapClass(AuthSettings)
        grid = QtGui.QFormLayout(wid)
        wid.server = wid.m.addBoundField(grid,"server")
        wid.m.addBoundField(grid,"database")
        wid.user = wid.m.addBoundField(grid,"user")
        wid.password = wid.m.addBoundField(grid,"password")
        wid.password.setEchoMode(QtGui.QLineEdit.Password)
        wid.m.connect_instance(self.settings)

        return wid

    def accept(self):
        self.connection = ""
        self.tabs.currentWidget().m.submit()
        self.m.submit()
        self.settings.saveSettings()

        prefix = self.tabs.currentWidget().prefix
        if prefix == "sqlite":
            self.connection = "sqlite:///%s" % (self.sqlite_file.text(),)
        else:
            self.connection = "%s://%s:%s@%s/%s" % (self.settings.server_type, self.settings.user, self.settings.password, self.settings.server, self.settings.database)
        try:
            #print self.connection
            if self.init_session_maker is not None:
                self.init_session_maker(self.connection)
            super(MultiAuthDialog,self).accept()
        except Exception, e:
            exception_message_box(e,"There was an error initializing the data.",icon=QtGui.QMessageBox.Warning)

def multi_auth_dialog(parent=None,init_session_maker=None,init_db=None):
    a = MultiAuthDialog(parent,init_session_maker,init_db)
    a.show()
    return a.exec_()

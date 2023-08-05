# -*- coding: utf-8 -*-
from qtalchemy import ModelObject, UserAttr
from PySide import QtCore, QtGui

class AuthSettings(ModelObject):
    """
    :class:`AuthSettings` contains the attributes for the model to 
    attach to the authentication dialogs.
    """
    classEvents = ModelObject.Events()

    remember_server = UserAttr(bool, "Remember Data Source")
    remember_user = UserAttr(bool, "Remember User")
    
    server = UserAttr(str, "Server")
    database = UserAttr(str, "Database")
    user = UserAttr(str, "User")
    password = UserAttr(str, "Password")
    server_string = UserAttr(str, "Server Configuration", readonly=True)
    
    def __init__(self):
        self.remember_server = True
        self.remember_user = True
        self.server_type = "postgresql"
        self.server = None
        self.database = None
        self.user = None
        self.password = None

    @classEvents.add("set", "server")
    @classEvents.add("set", "database")
    def server_string_config_change(self, attr, oldvalue):
        self.server_string = "%s://%s/%s" % (self.server_type, self.server, self.database)

    def loadSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup("Data Settings (Authentication)")
        self.remember_server = settings.value("remember_server",self.remember_server)
        self.remember_user = settings.value("remember_user",self.remember_user)
        if self.remember_server:
            self.server_type = settings.value("server_type",self.server_type)
            self.server = settings.value("server",self.server)
            self.database = settings.value("database",self.database)
        if self.remember_user:
            self.user = settings.value("user",self.user)
        settings.endGroup()

    def saveSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup("Data Settings (Authentication)")
        settings.setValue("remember_server",self.remember_server)
        settings.setValue("remember_user",self.remember_user)
        settings.setValue("server_type",self.server_type if self.remember_server else "")
        settings.setValue("server",self.server if self.remember_server else "")
        settings.setValue("database",self.database if self.remember_server else "")
        settings.setValue("user",self.user if self.remember_user else "")
        settings.endGroup()

# -*- coding: utf-8 -*-
"""
We create a session and model objects and display messages.
"""

from sqlalchemy import create_engine
from qtalchemy import *
from PySide import QtCore

class Vegetable(ModelObject):
    def __init__(self):
        self.msgCounter = 0

    classEvents = ModelObject.Events()

    name = UserAttr(str, "Vegetable Name")
    color = UserAttr(str, "Color")

    @classEvents.add("check", "name")
    def check_name(self, attr, newvalue):
        if newvalue.lower() == "bean":
            raise ValueError("The name 'bean' is not allowed.")

    @classEvents.add("set", "name")
    def set_name(self, attr, oldvalue):
        if self.name.lower() == "tomato":
            self.color = "red"
        if self.name.lower() == "broccoli":
            self.color = "green"

    @classEvents.add("set", "")
    def set_name(self, attr, oldvalue):
        pass
        #print "{0} set to {1}".format(attr, getattr(self, attr))

    @classEvents.add("message")
    def message(self, flags, msg):
        self.msgCounter += 1
        assert msg == "The Message"

def test_class_hooks():
    i = Vegetable()
    try:
        i.name = "bEan"
        assert False, "the checker didn't run"
    except Exception as e:
        pass
    i.name = "Tomato"
    assert i.color == "red", "the set event failed"
    i.modelMessage(Message.Ok|Message.Warning, "The Message")

    assert i.msgCounter == 1, "the message hook wasn't called"

msgCounter = 0
def test_session_hook():
    i = Vegetable()

    Session = PBSessionMaker(bind=create_engine("sqlite://"))

    session = Session()
    session.npadd(i)

    @instanceEvent(session, "message")
    def session_message(self, instance, flags, msg):
        global msgCounter
        msgCounter += 1
        assert msg == "The Message"

    i.modelMessage(Message.Ok|Message.Warning, "The Message")

    assert i.msgCounter == 1, "the message hook wasn't called"
    assert msgCounter == 1, "the message hook wasn't called"

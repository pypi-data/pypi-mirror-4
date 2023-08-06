#!/usr/bin/env python

import pytest
if pytest.PLATFORM == "win32":
    pytest.skip("Broken on Windows")

from circuits import Component, Event
from circuits.net.sockets import Close
from circuits.node import Node, Remote
from circuits.net.sockets import UDPServer


class Foo(Event):
    """Foo Event"""


class App(Component):
    disconnected = False
    ready = False
    value = False

    def foo(self):
        return "Hello World!"

    def ready(self, *args):
        self.ready = True

    def disconnect(self, component):
        self.disconnected = True

    def remote_value_changed(self, value):
        self.value = True


@pytest.fixture()
def bind(manager, watcher):
    server = UDPServer(0).register(manager)
    assert watcher.wait("ready")

    host, port = server.host, server.port

    server.fire(Close())
    assert watcher.wait("closed")

    server.unregister()

    return host, port


def test_return_value(manager, watcher, bind):
    a1 = App().register(manager)
    n1 = Node().register(a1)

    a2 = (App() + Node(bind))
    a2.start(process=True)

    n1.add("a2", *bind)

    e = Event.create("foo")
    e.notify = True

    r = Remote(e, "a2")
    r.notify = True

    value = a1.fire(r)
    watcher.wait("remote_value_changed")

    assert value.value == "Hello World!"

    a2.stop()
    a1.unregister()
    n1.unregister()

# Module:   test_workers
# Date:     7th October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Workers Tests"""

import pytest

from os import getpid

from circuits import Task, Worker


@pytest.fixture(scope="module")
def worker(request, manager):
    worker = Worker().register(manager)

    def finalizer():
        worker.unregister()

    request.addfinalizer(finalizer)

    return worker


def err():
    return x * 2  # NOQA


def foo():
    x = 0
    i = 0
    while i < 1000000:
        x += 1
        i += 1
    return x


def pid():
    return "Hello from {0:d}".format(getpid())


def test_failure(manager, watcher, worker):
    e = Task(err)
    e.failure = True

    x = worker.fire(e)

    assert watcher.wait("task_failure")

    assert isinstance(x.value[1], Exception)


def test_success(manager, watcher, worker):
    e = Task(foo)
    e.success = True

    x = worker.fire(e)

    assert watcher.wait("task_success")

    assert x.value == 1000000

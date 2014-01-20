import os
import __builtin__


def path(name):
    return os.path.join(os.path.dirname(__file__), "test_files", name)


def open(name):
    return __builtin__.open(path(name))

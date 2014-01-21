import os
import sys

if sys.version_info[0] == 2:
    import __builtin__ as builtins
else:
    import builtins



def path(name):
    return os.path.join(os.path.dirname(__file__), "test_files", name)


def open(name, mode):
    return builtins.open(path(name), mode)

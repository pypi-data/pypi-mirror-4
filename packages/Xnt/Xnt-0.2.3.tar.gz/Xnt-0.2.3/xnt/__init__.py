#!/usr/bin/env python
__version__ = "Xnt 0.2.3"

def target(fn):
    def wrap():
        print(fn.__name__ + ":")
        return fn()
    wrap.decorator = "target"
    wrap.__doc__ = fn.__doc__
    return wrap

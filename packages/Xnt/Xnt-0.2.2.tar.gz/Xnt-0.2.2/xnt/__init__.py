#!/usr/bin/env python

def target(fn):
    def wrap():
        print(fn.__name__ + ":")
        return fn()
    return wrap

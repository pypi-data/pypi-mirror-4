#!/usr/bin/python

import warnings

def fxn():
    warnings.warn('teste', RuntimeWarning)
fxn()

print 'ok'

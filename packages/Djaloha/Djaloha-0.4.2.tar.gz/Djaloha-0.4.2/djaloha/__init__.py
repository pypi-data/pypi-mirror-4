# -*- coding: utf-8 -*-

VERSION = (0, 4, 2)

def get_version():
    version = '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])
    return version

__version__ = get_version()

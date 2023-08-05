# -*- coding: utf-8 -*-


__all__ = ('DEBUG', 'VERSION')


DEBUG = False
def switch_to_local(endpoint='http://api.local.greendizer.com/'):
    from greendizer.clients import http
    global DEBUG
    DEBUG = True
    http.API_ROOT = endpoint
    http.DEBUG = True

from greendizer import version
VERSION = version.VERSION
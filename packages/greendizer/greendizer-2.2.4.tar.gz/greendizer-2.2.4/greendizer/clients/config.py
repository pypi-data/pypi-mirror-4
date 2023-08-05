# -*- coding: utf-8 -*-


__all__ = ('DEBUG', 'VERSION')


DEBUG = False
def switch_to_local(endpoint='http://api.local.greendizer.com/'):
    from greendizer.clients import http
    global DEBUG
    http.DEBUG = DEBUG = True
    http.API_ROOT = endpoint
   
def switch_to_prod(debug=False, endpoint='https://api.greendizer.com/'):
    from greendizer.clients import http
    global DEBUG
    http.DEBUG = DEBUG = debug
    http.API_ROOT = endpoint

from greendizer import version
VERSION = version.VERSION
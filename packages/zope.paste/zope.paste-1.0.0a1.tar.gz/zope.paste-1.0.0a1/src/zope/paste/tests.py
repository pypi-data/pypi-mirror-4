##############################################################################
#
# Copyright (c) 2013 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests.
"""
import asyncore
import doctest
import gc
import os
import paste.deploy
import signal
import subprocess
import unittest
from waitress.server import WSGIServer

try:
    from urllib2 import urlopen
except ImportError:
    # Py3: The location moved.
    from urllib.request import urlopen

def setUp(test):
    test.orig_loadapp = paste.deploy.loadapp
    test.orig_loadserver = paste.deploy.loadserver

def tearDown(test):
    paste.deploy.loadapp = test.orig_loadapp
    paste.deploy.loadserver = test.orig_loadserver

def test_basic_serve():
    """Starting a paster server

    Let's stub the loader functions:

    >>> def loadapp(uri, name=None, **kw):
    ...     print('Application: ' + (name or 'main'))
    ...     print(uri)
    ...     return object()
    >>> paste.deploy.loadapp = loadapp

    >>> def server(app):
    ...     print('Start serving app')

    >>> def loadserver(uri, name=None, **kw):
    ...     print('Server: ' + (name or 'main'))
    ...     print(uri)
    ...     return server
    >>> paste.deploy.loadserver = loadserver

    We can now serve the app:

    >>> from zope.paste import serve
    >>> serve.serve(['/test/app.ini'])
    Server: main
    config:///test/app.ini
    Application: main
    config:///test/app.ini
    Start serving app

    We can also specify the names of the app and server:

    >>> serve.serve(
    ...     ['--app-name', 'app', '--server-name', 'server', '/test/app.ini'])
    Server: server
    config:///test/app.ini
    Application: app
    config:///test/app.ini
    Start serving app

    The startup fails, if the ini file is not specified:

    >>> serve.serve([])
    Traceback (most recent call last):
    ...
    SystemExit: No paster ini file specified.

    Now we get the args from ``sys``:

    >>> import sys
    >>> orig_args = sys.argv
    >>> sys.argv = ['serve', '/test/app.ini']

    >>> serve.serve()
    Server: main
    config:///test/app.ini
    Application: main
    config:///test/app.ini
    Start serving app

    >>> sys.argv = orig_args
    """

def test_serving_test_app():
    """Test serving a real app.

    >>> ini = os.path.join(os.path.dirname(__file__), 'test_app', 'app.ini')
    >>> import threading
    >>> from zope.paste import serve
    >>> server = threading.Thread(target=serve.serve, args=([ini],))
    >>> server.start()
    >>> import time; time.sleep(1)
    serving on http://127.0.0.1:8765

    >>> print(urlopen('http://localhost:8765/').read().decode())
    <html>
      <body>
        <h1>Hello World, Zope App!</h1>
      </body>
    </html>

    >>> _ = [asyncore.close_all(obj._map)
    ...      for obj in gc.get_objects() if isinstance(obj, WSGIServer)]
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE),
    ))

"""A specialized :class:`pulsar.apps.socket.SocketServer` for
serving web applications which conforms with the python web server
gateway interface (WSGI_).

The application can be used in conjunction with several web frameworks
as well as the :ref:`pulsar RPC middleware <apps-rpc>` and
the :ref:`websocket middleware <apps-ws>`.

An example of a web server written with ``pulsar.apps.wsgi`` which responds
with "Hello World!" for every request::

    from pulsar.apps import wsgi

    def hello(environ, start_response):
        data = b"Hello World!"
        response_headers = (
            ('Content-type','text/plain'),
            ('Content-Length', str(len(data)))
        )
        start_response("200 OK", response_headers)
        return [data]

    if __name__ == '__main__':
        wsgi.WSGIServer(callable=hello).start()


For more information regarding WSGI check the pep3333_ specification.

.. _pep3333: http://www.python.org/dev/peps/pep-3333/
.. _WSGI: http://www.wsgi.org
"""
import sys
from inspect import isclass

import pulsar
from pulsar.utils.importer import module_attribute
from pulsar.apps import socket

from .wsgi import *
from .server import *
from .middleware import *
from .request import *


class WsgiSetting(pulsar.Setting):
    virtual = True
    app = 'wsgi'
    section = "WSGI Servers"


class HttpParser(WsgiSetting):
    name = "http_parser"
    flags = ["--http-parser"]
    desc = """\
        The HTTP Parser to use. By default it uses the fastest possible.

        Specify `python` if you wich to use the pure python implementation
        """


class ResponseMiddleware(WsgiSetting):
    name = "response_middleware"
    flags = ["--response-middleware"]
    nargs = '*'
    desc = """\
    Response middleware to add to the wsgi handler
    """


class WSGIServer(socket.SocketServer):
    cfg_apps = ('socket',)
    _app_name = 'wsgi'
    socket_server_factory = HttpServer

    def handler(self):
        '''Build the wsgi handler from *hnd*. This function is called
at start-up only.

:parameter hnd: This is the WSGI handle which can be A :class:`WsgiHandler`,
    a WSGI callable or a list WSGI callables.
:parameter resp_middleware: Optional list of response middleware functions.'''
        hnd = self.callable
        if not isinstance(hnd, WsgiHandler):
            if not isinstance(hnd, (list, tuple)):
                hnd = [hnd]
            hnd = WsgiHandler(hnd)
        response_middleware = self.cfg.response_middleware or []
        for m in response_middleware:
            if '.' not in m:
                mm = getattr(middleware,m,None)
                if not mm:
                    raise ValueError('Response middleware "{0}" not available'\
                                     .format(m))
            else:
                mm = module_attribute(m)
            if isclass(mm):
                mm = mm()
            hnd.response_middleware.append(mm)
        return hnd

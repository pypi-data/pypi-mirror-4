'''A webmail application.
To run the server type::

    python manage.py
    
and open a web browser at http://localhost:8060    
'''
import os
import sys
import json
from random import random
import time
try:
    import pulsar
except ImportError: #pragma nocover
    sys.path.append('../../')
    import pulsar
from pulsar.apps import ws, wsgi, rpc

CHAT_DIR = os.path.dirname(__file__)
    
class Mail(ws.WS):
        
    def on_open(self, environ):
        # Add pulsar.connection environ extension to the set of active clients
        get_clients().add(environ['pulsar.connection'])
        
    def on_message(self, environ, msg):
        if msg:
            lines = []
            for l in msg.split('\n'):
                l = l.strip()
                if l:
                    lines.append(l)
            msg = ' '.join(lines)
            if msg:
                publish(msg)


def page(environ, start_response):
    """ This resolves to the web page or the websocket depending on the path."""
    path = environ.get('PATH_INFO')
    if not path or path == '/':
        data = open(os.path.join(CHAT_DIR, 'chat.html')).read()
        data = data % environ
        start_response('200 OK', [('Content-Type', 'text/html'),
                                  ('Content-Length', str(len(data)))])
        return [pulsar.to_bytes(data)]



def server(**kwargs):
    chat = ws.WebSocket('/message', Chat())
    api = rpc.RpcMiddleware(Rpc(), path='/rpc')
    middleware = wsgi.WsgiHandler(middleware=(chat, api, page))
    return wsgi.WSGIServer(name='webchat', callable=middleware, **kwargs)


if __name__ == '__main__':  #pragma nocover
    server().start()
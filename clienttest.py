from lib.owsocketio import *
import threading
import logging

__version__ = '0.1'


class Namespace(LoggingNamespace):
    _connected = True

    def on_connect(self):
        print('connected')

    def on_error(self, data):
        print('error')

    def on_response(*args):
        print(args)


socketIO = OWSocketIO('localhost', 5000, Namespace)
nsp = socketIO.define(Namespace, '/api')
nsp.emit('image', {'count': 1, 'checksum': 7156383362851305244, 'obj': {'path': 'path/to/image.png', 'resize': True}})
socketIO.wait(seconds=10)

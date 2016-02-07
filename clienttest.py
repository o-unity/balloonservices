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
        print('on_aaa_response', args)


socketIO = OWSocketIO('localhost', 5000, Namespace)
nsp = socketIO.define(Namespace, '/test')
nsp.emit('image', {'data': 'personal data, YES! it works'})
socketIO.wait(seconds=10)

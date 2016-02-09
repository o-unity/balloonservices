from lib.owsocketio import *
import json
import time
from threading import Thread
import wrapt

__author__ = 'andi'


class Image(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @property
    def serialize(self):
        ser = {}
        ser['path'] = self.kwargs['path']
        ser['resize'] = self.kwargs['resize']
        return ser

# --------------------------------------- //


class Instance(object):
    def __init__(self):
        self.js = {}

    def image(self, **kwargs):
        self.js['image'] = Image(**kwargs).serialize

# --------------------------------------- //


class SocketNamespace(LoggingNamespace):
    _connected = True

    def on_connect(self):
        print('connected')

    def on_error(self, data):
        print('error')

    def on_response(*args):
        print('on_aaa_response', args)

# --------------------------------------- //


class Socket(object):
    def __init__(self, wsdata):
        self.wsdata = wsdata
        self.nsp = self.open()
        self.instance = []
        self.register = []
        self.queue = []

    def open(self):
        socketio = OWSocketIO(self.wsdata['host'], self.wsdata['port'], SocketNamespace)
        return socketio.define(SocketNamespace, self.wsdata['namespace'])

    def add(self):
        inst = Instance()
        self.instance.append(inst)
        return inst

    def submit(self):
        for sub in self.instance:
            self.register = sub.js
        self.instance = []

    def setregister(self, param=""):
        if len(param):
            self.queue.append(param)
#            print("setregister called! %s, count objects: %s" % (param, len(self.queue)))

    def getregister(self):
        print("call getregister")
        pass

    register = property(getregister, setregister)

# --------------------------------------- //


class WebSocket(object):
    def __init__(self):
        self.wsdata = {}

    def connect(self):
        return Socket(self.wsdata)

    def sethost(self, value):
        self.wsdata['host'] = value

    def gethost(self):
        return self.wsdata['host']

    def setport(self, value):
        self.wsdata['port'] = int(value)

    def getport(self):
        return self.wsdata['port']

    def setnamespace(self, value):
        self.wsdata['namespace'] = value

    def getnamespace(self):
        return self.wsdata['namespace']

    host = property(gethost, sethost)
    port = property(getport, setport)
    namespace = property(getnamespace, setnamespace)

# --------------------------------------- //


class ImageCollector(object):
    def __init__(self, resize=False):
        self.resize = resize
        self.collect()

    def collect(self):
        ct = 0
        while ct < 3600:
            ct += 1
            time.sleep(5)
            self.register("path/to/image.png")

    def register(self, path):
        sock.add().image(path=path, resize=self.resize)
        sock.submit()

# --------------------------------------- //


ws = WebSocket()
ws.host = 'localhost'
ws.port = 5000
ws.namespace = "/api"
sock = ws.connect()

t = Thread(target=ImageCollector, args=(True, ))
t.start()

print("done")



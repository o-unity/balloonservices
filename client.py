from lib.owsocketio import *
from threading import Thread
import json
import time
from collections import OrderedDict

__author__ = 'over.unity'


class Image(object):
    def __init__(self, **kwargs):
        self.attr = kwargs
        self.prop = {}

    def gettype(self):
        return "image"


# --------------------------------------- //


class Instance(object):
    def __init__(self):
        self.obj = None
        self._hash = None

    def setattr(self, attr, value):
        self.obj.prop[attr] = value

    def getcount(self):
        return self.obj.prop['count']

    def gettype(self):
        return self.obj.gettype()

    def sethash(self, d):
        self._hash = hash(repr(d))

    def gethash(self):
        return self._hash

    def dict(self):
        d = dict()
        d['obj'] = dict()
        for prop, value in self.obj.prop.items():
            d[prop] = value

        for prop, value in self.obj.attr.items():
            d['obj'][prop] = value

        self.sethash(d)
        d['checksum'] = self.gethash()
        return d

    def image(self, **kwargs):
        self.obj = Image(**kwargs)
        return self.obj

# --------------------------------------- //


class ObjectCount(object):
    def __init__(self):
        self.objcount = 0
        self._objcount = 0

    def setobjcount(self, value):
        pass

    def getobjcount(self):
        self._objcount += 1
        return self._objcount

    objcount = property(getobjcount, setobjcount)

# --------------------------------------- //


class SocketNamespace(BaseNamespace):
    _connected = True
    _lock = False

    def on_connect(self):
        print('connected')

    def on_error(self, data):
        print('error')

    def on_response(*args):
        sock.unlockbyhash(args[1])


# --------------------------------------- //


class Socket(SocketNamespace):
    def __init__(self, wsdata):
        self.wsdata = wsdata
        self.socketio = None
        self.nsp = self.open()
        self.instance = []
        self.register = []
        self.queue = []
        self.oc = ObjectCount()
        self._sock = False

    def unlockbyhash(self, hash):
        for key, obj in enumerate(self.queue):
            if hash == obj.gethash():
                del self.queue[key]
                self.unlock()

    def unlock(self):
        print("unlock")
        self._lock = False

    def lock(self):
        self._lock = True

    def getlock(self):
        return self._lock

    def open(self):
        self.socketio = OWSocketIO(self.wsdata['host'], self.wsdata['port'], SocketNamespace)
        return self.socketio.define(SocketNamespace, self.wsdata['namespace'])

    def add(self):
        inst = Instance()
        self.instance.append(inst)
        return inst

    def submit(self):
        for obj in self.instance:
            obj.setattr("count", self.oc.objcount)
            self.addqueue(obj)
        self.instance = []

    def addqueue(self, obj):
        self.queue.append(obj)
        self.sortbycount()
        print("add to queue, current objects: %s" % len(self.queue))

        if not self.getlock():
            self.lock()
            self.emit(self.queue[0])

    def emit(self, qobj):
        self.nsp.emit(qobj.gettype(), qobj.dict())
        self.socketio.wait(seconds=1)

    def sortbycount(self):
        self.queue = sorted(self.queue, key=lambda x: x.obj.prop['count'], reverse=True)


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
            self.register("path/to/image.png")
            time.sleep(5)

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



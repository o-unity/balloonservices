from lib.owsocketio import *
from threading import Thread
import json
import time
from collections import OrderedDict
import logging
import sys
import os
from PIL import Image as Pil
import base64
import io
import dill

__author__ = 'over.unity'


root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class Image(object):
    img = None
    width = 300
    height = 300

    def __init__(self, **kwargs):
        self.attr = kwargs
        print(kwargs)
        self.prop = {}
        self.read().resize().convertbase64()

    def read(self):
        self.img = Pil.open(self.attr['path'])
        return self

    def resize(self):
        if "resize" in self.attr:
            size = self.width, self.height
            self.img.thumbnail(size, Pil.ANTIALIAS)

        return self

    def convertbase64(self):
        buffer = io.BytesIO()
        self.img.save(buffer, "JPEG")
        self.attr['payload'] = base64.b64encode(buffer.getvalue()).decode()

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
        self.obj.prop['loggingtype'] = self.obj.gettype()
        return self.obj.gettype()

    def sethash(self, d):
        self._hash = hash(repr(d))

    def gethash(self):
        return self._hash

    def settimestamp(self):
        self.obj.prop['timestamp'] = time.time()

    def gettimestamp(self):
        return self.obj.prop['timestamp']

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
        root.info('connected')

    def on_error(self, data):
        root.info('error')

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
        self.maxunlocktime = 30
        self.emittime = 0.1
        self.emittimemin = 0.02
        self.emitavg = 2
        ult = Thread(target=self.unlockbytime)
        ult.start()

    def unlockbytime(self):
        while True:
            time.sleep(1)
            if self.getlock():
                root.info("waiting for response")
                ct = 0
                while ct < self.maxunlocktime:
                    ct += 1
                    time.sleep(1)
                    if ct >= self.maxunlocktime:
                        root.info("response timeout, unlock!!!")
                        self.calcemittime(self.maxunlocktime / 2)
                        root.info("new emit wait time:%s" % self.emittime)
                        self.unlock()

                    if not self.getlock():
                        break

    def unlockbyhash(self, hashstr):
        for key, obj in enumerate(self.queue):
            if hashstr == obj.gethash():
                root.info("response for No:%s" % obj.getcount())
                del self.queue[key]
                self.unlock()
                ntime = time.time() - obj.gettimestamp()
                self.calcemittime(float(ntime))

    def calcemittime(self, ntime):
        self.emittime = (ntime * 2 + (self.emittime * (self.emitavg - 1))) / self.emitavg
        if self.emittime < ntime:
            self.emittime = ntime * 2

        if self.emittimemin > self.emittime:
            self.emittime = self.emittimemin

        self.emittime = round(self.emittime, 2)
#        root.info("new calc time:%s" % self.emittime)

    def unlock(self):
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
        root.info("add new object to queue, count: %s" % len(self.queue))

    def emitdata(self):
        while True:
            if not self.getlock() and len(self.queue):

                self.lock()
                self.queue[0].settimestamp()
                root.info("start emitting No:%s" % self.queue[0].getcount())

                self.nsp.emit(self.queue[0].gettype(), self.queue[0].dict())
                self.socketio.wait(seconds=self.emittime)
            else:
                time.sleep(0.2)

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
        root.info("starting ImageCollector")
        self.resize = resize
        self.collect()

    def collect(self):
        ct = 0
        while ct < 3600:
            ct += 1
            self.register("/Users/andi/PycharmProjects/balloonservices/client/data/images/test.jpg")
            time.sleep(30)

    def register(self, path):
        sock.add().image(path=path, resize=self.resize)
        sock.submit()

# --------------------------------------- //

# root = logging()
root.info("starting client")

# --------------------------------------- //

ws = WebSocket()
ws.host = 'localhost'
ws.port = 5000
ws.namespace = "/api"

sock = ws.connect()

procs = []
p1 = Thread(target=ImageCollector, args=(True, ))
p1.start()

sock.emitdata()


root.info("done")



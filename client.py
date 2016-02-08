import json
import time
from threading import Thread

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


class Instance(object):
    def __init__(self):
        self.js = {}

    def image(self, **kwargs):
        self.js['image'] = Image(**kwargs).serialize


class Socket(object):
    def __init__(self, wsdata):
        self.wsdata = wsdata
        self.open()
        self.instance = []
        self.register = []
        self.regit = []

    def open(self):
        pass

    def add(self):
        inst = Instance()
        self.instance.append(inst)
        return inst

    def submit(self):
        for sub in self.instance:
            self.register = sub.js
        self.instance = []

    def setregister(self, param):
        if len(param):
            self.regit.append(param)
            print("setregister called! %s, count objects: %s" % (param, len(self.regit)))
            for c in self.register:
                print("test")

    def getregister(self):
        print("call getregister")
        pass

    register = property(getregister, setregister)


class WebSocket(object):
    def __init__(self):
        self.wsdata = {}

    def connect(self):
        return Socket(self.wsdata)

    def sethost(self, value):
        self.wsdata['host'] = value

    def gethost(self):
        return self.wsdata['host']

    host = property(gethost, sethost)


# ----------------------------------

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



ws = WebSocket()
ws.host = 'ballon.myftp.org'
ws.port = "5000"
sock = ws.connect()

t = Thread(target=ImageCollector, args=(True, ))
t.start()

print("done")

#sock.add().image(path="path/to/image.png", resize=True)
#sock.submit()

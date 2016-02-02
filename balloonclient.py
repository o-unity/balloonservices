import json

__author__ = 'andi'


class Image(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @property
    def serialize(self):
        ser = {}
        ser['path'] = self.kwargs['path']
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

    def open(self):
        pass

    def add(self):
        inst = Instance()
        self.instance.append(inst)
        return inst

    def submit(self):
        for sub in self.instance:
            print(json.dumps(sub.js, indent=4))


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


ws = WebSocket()
ws.host = 'ballon.myftp.org'
ws.port = "5000"

sock = ws.connect()
sock.add().image(path="path/to/image.png", resize=True)
sock.submit()

import json

__author__ = 'andi'


class Image():
    def __init__(self):
        pass


class Instance(object):
    def __init__(self):
        self.js = {}

    def image(self, path):
        self.js['image'] = {}
        self.js['image']['path'] = path



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
ws.host = "zaugg.myftp.org"
ws.port = "5000"

sock = ws.connect()
sock.add().image("path/to/image.png")
sock.submit()

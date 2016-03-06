#!/usr/bin/env python
import time
from threading import Thread
from flask import Flask, render_template, session, request, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import base64
import datetime
from functools import wraps
import sqlite3 as lite
import sys
import uuid
import collections
import json
import io

async_mode = 'eventlet'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
msgcount = 0

# ------------------------
# DECORATOR


def MessageLogging(func):
    def wrapper(*args, **kwargs):
        db.settable("objects").map(args[0]['loggingtype'], args[0]).commit()
        #db.settable("objects").map(args[0]['loggingtype'], args[0])
        res = func(*args, **kwargs)
        return res
    return wrapper


def IsAuth(func):
    def wrapper(*args, **kwargs):
        res = None
        if usr.uuid(args[0]['uuid']).isauth():
            res = func(*args, **kwargs)
        return res
    return wrapper


# ------------------------
# CLASSES

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Bimg(object):
    pathimage = "static/received/images/"
    img = None

    def add(self, uxtimestamp):
        self.img = dict()
        self.genname(uxtimestamp)
        return self

    def genname(self, ux):
        self.img['name'] = datetime.datetime.fromtimestamp(
            int(ux)).strftime('%Y%m%d-%H%M%S.jpg')

    def setcontent(self, base64data):
        self.img['content'] = base64.b64decode(base64data.encode())
        return self

    def setcontent2(self, data):
        self.img['content'] = data
        return self

    def save(self):
        f = open(self.pathimage + self.img['name'], 'bw')
        f.write(self.img['content'])
        f.close()


class WebroomData(object):
    def __init__(self):
        self.obj = dict()
        self.obj['msgcount'] = 0
        self.obj['_lastmsg'] = time.time()

    def incmsg(self):
        self.obj['msgcount'] += 1
        self.lastmsg()
        self.resetlstmsg()

    def lastmsg(self):
        self.obj['lastmsg'] = int(time.time() - self.obj['_lastmsg'])

    def resetlstmsg(self):
        self.obj['_lastmsg'] = time.time()

    def dict(self, _uuid=""):
        d = dict()
        for prop, value in self.obj.items():
            d[prop] = value

        if uuid:
            d['auth'] = usr.uuid(_uuid).isauth()

        # LAST 100 RECORDS
        d['log'] = []
        for c in db.selecto("SELECT "
                                   "id, "
                                   "loggingtype, "
                                   "count, "
                                   "checksum, "
                                   "pushtimestamp, "
                                   "savetimestamp, "
                                   "data, length(payload) as payloadsize "
                                        "FROM objects ORDER BY id DESC LIMIT 100").each():
            d['log'].append(db.viewo(c))

        # LAST 9 IMAGES
        d['img'] = []
        query = "SELECT id FROM objects WHERE loggingtype = 'image' ORDER BY id DESC LIMIT 9"
        for c in db.selecto(query).each():
            d['img'].append(c.id)

        return d


class Mapping(object):
    def __init__(self):
        pass

    def setimage(self, data):
        datamapped = dict()
        datamapped['loggingtype'] = data['loggingtype']
        datamapped['count'] = data['count']
        datamapped['checksum'] = data['checksum']
        datamapped['pushtimestamp'] = data['timestamp']
        datamapped['savetimestamp'] = time.time()
        datamapped['payload'] = base64.b64decode(data['obj']['payload'].encode())
        return datamapped

    def setsystem(self, data):
        datamapped = dict()
        datamapped['loggingtype'] = data['loggingtype']
        datamapped['count'] = data['count']
        datamapped['checksum'] = data['checksum']
        datamapped['pushtimestamp'] = data['timestamp']
        datamapped['savetimestamp'] = time.time()
        datamapped['data'] = "{\"usage\": \"%s\",\"space\": \"%s\",\"strength\": \"%s\"}" % \
                             (data['obj']['usage'], data['obj']['space'], data['obj']['strength'])
        return datamapped

    def getsystem(self, data):
        jdata = json.loads(data.data)
        text = "%s/%s" % (str(data.id), str(data.count))
        text = text.ljust(15)
        text += "%s" % str(data.loggingtype).ljust(10)
        t1 = "%s" % datetime.datetime.fromtimestamp(
                            int(data.pushtimestamp)
                        ).strftime('%H:%M:%S')
        t1 += " / %s" % datetime.datetime.fromtimestamp(
                            int(data.savetimestamp)
                        ).strftime('%H:%M:%S')

        t1 += " (%s s)" % str(data.savetimestamp - data.pushtimestamp)[:5]
        text += t1.ljust(33)
        text += "cpu usage: %s, free space: %s, signal: %s" % \
                (str(jdata['usage']), str(jdata['space']), str(jdata['strength']))
        return text

    def getimage(self, data):
        text = "%s/%s" % (str(data.id), str(data.count))
        text = text.ljust(15)
        text += "%s" % str(data.loggingtype).ljust(10)
        t1 = "%s" % datetime.datetime.fromtimestamp(
                            int(data.pushtimestamp)
                        ).strftime('%H:%M:%S')
        t1 += " / %s" % datetime.datetime.fromtimestamp(
                            int(data.savetimestamp)
                        ).strftime('%H:%M:%S')

        t1 += " (%s s)" % str(data.savetimestamp - data.pushtimestamp)[:5]
        text += t1.ljust(33)

        if not data.payloadsize:
            data.payloadsize = 0

        text += "size: %s" % sizeof_fmt(data.payloadsize)

        return text

    def setimage_log(self):
        pass

    def setauth(self, data):
        datamapped = dict()
        datamapped['loggingtype'] = data['loggingtype']
        datamapped['savetimestamp'] = time.time()
        datamapped['data'] = "{\"remote_address\": \"%s\"}" % (request.remote_addr,)
        return datamapped

    def getauth(self, data):
        jdata = json.loads(data.data)
        text = "%s" % str(data.id).ljust(15)
        text += "%s" % str(data.loggingtype).ljust(10)
        text += "%s" % datetime.datetime.fromtimestamp(
                            int(data.savetimestamp)
                        ).strftime('%H:%M:%S').ljust(33)
        text += "remote address: %s" % str(jdata['remote_address']).ljust(10)
        return text

    def getcleanup(self, data):
        jdata = json.loads(data.data)
        text = "%s" % str(data.id).ljust(15)
        text += "%s" % str(data.loggingtype).ljust(10)
        text += "%s" % datetime.datetime.fromtimestamp(
                            int(data.savetimestamp)
                        ).strftime('%H:%M:%S').ljust(33)
        text += "remote address: %s" % str(jdata['remote_address']).ljust(10)
        return text

    def setcleanup(self, data):
        datamapped = dict()
        datamapped['loggingtype'] = data['loggingtype']
        datamapped['savetimestamp'] = time.time()
        datamapped['data'] = "{\"remote_address\": \"%s\"}" % (request.remote_addr,)
        return datamapped


class DB(Mapping):
    def __init__(self):
        self.con = None
        self.datamapped = None
        self.table = None
        self.seldata = None
        self.res = None
        self.connect()

    def settable(self, table):
        self.table = table
        return self

    def fetchconfig(self, attr):
        cur = self.con.execute("SELECT value FROM config WHERE attribute = '%s'" % attr)
        return cur.fetchone()[0]

    def getpasswd(self):
        return self.fetchconfig('password')

    def cleanup(self):
        self.con.execute("DELETE FROM objects")
        self.con.commit()
        self.con.execute("VACUUM")
        self.con.commit()

    def connect(self):
        self.con = lite.connect('db/data.db')

    def map(self, mappingfunction, data):
        self.datamapped = getattr(self, "set" + mappingfunction)(data)
        return self

    def view(self):
        return getattr(self, "get" + self.seldata.loggingtype)(self.seldata)

    def viewo(self, obj):
        return getattr(self, "get" + obj.loggingtype)(obj)

    def selectbyid(self, oid):
        self.seldata = self.select("SELECT "
                                   "id, "
                                   "loggingtype, "
                                   "count, "
                                   "checksum, "
                                   "pushtimestamp, "
                                   "savetimestamp, "
                                   "data, length(payload) as payloadsize "
                                        "FROM objects WHERE id = %s" % oid)
        return self

    def getpayload(self, oid):
        return self.select("SELECT "
           "id, "
           "payload "
                "FROM objects WHERE id = %s" % oid)

    def selecto(self, query):
        self.res = self.select(query)
        return self

    def each(self):
        try:
            for co in self.res:
                yield co
        except:
            return False

    def select(self, query):
        cur = self.con.cursor()
        cur.execute(query)
        res = []
        for c in self.iter(cur):
            res.append(c)
        if len(res) == 1:
            return c
        return res

    def commit(self):
        cur = self.con.cursor()
        columns = ', '.join(self.datamapped.keys())
        placeholders = ':' + ', :'.join(self.datamapped.keys())
        query = 'INSERT INTO %s (%s) VALUES (%s)' % \
                (self.table, columns, placeholders)
        cur.execute(query, self.datamapped)
        self.con.commit()

        emit('log', self.selectbyid(cur.lastrowid).view(), room='webroom')

    def iter(self, cur):
        result = {}
        for (pt, row) in enumerate(cur):
            result[pt] = {}
            result[pt]['fields'] = ""
            for (pt2, key) in enumerate(row):
                result[pt][cur.description[pt2][0]] = key
                result[pt]['fields'] += str(cur.description[pt2][0]) + ","
            yield Struct(**result[pt])


class UserLoggin(object):
    def __init__(self):
        self.user = dict()
        self.id = None
        pass

    def uuid(self, id=False):
        if id:
            self.id = id
        else:
            self.id = str(uuid.uuid4())

        if self.id not in self.user:
            self.user[self.id] = dict()

        if "auth" not in self.user[self.id]:
            self.user[self.id]['auth'] = False

        return self

    def getuuid(self):
        return self.id

    def auth(self, password=""):
        if password == db.getpasswd():
            self.user[self.id]['auth'] = True
        else:
            self.user[self.id]['auth'] = False

    def isauth(self):
        return self.user[self.id]['auth']


db = DB()

bimg = Bimg()
usr = UserLoggin()

wrdata = WebroomData()
wrdata.incmsg()


#img = db.getpayload(208)
#bimg.add(1456673720.10788)
#bimg.setcontent2(img.payload).save()
#sys.exit(0)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/getimage', methods=['POST', 'GET'])
def _getimage():
    img = db.getpayload(request.args.get('id', ''))
    return send_file(io.BytesIO(img.payload))


@app.route('/map')
def googlemap():
    return render_template('gtest.html')


@app.route('/ping')
def ping():
    return "pong"


@socketio.on('image', namespace='/api')
@MessageLogging
def sockimage(message):
    wrdata.incmsg()
    emit('response', message['checksum'])
#    emit('dataitems', wrdata.dict(), room='webroom')


@socketio.on('system', namespace='/api')
@MessageLogging
def socksystem(message):
    wrdata.incmsg()
    emit('response', message['checksum'])
#    emit('dataitems', wrdata.dict(), room='webroom')


@socketio.on('cleanup', namespace='/api')
@IsAuth
@MessageLogging
def cleanup(message):
    db.cleanup()


@socketio.on('auth', namespace='/api')
@MessageLogging
def auth(message):
    usr.uuid(message['uuid']).auth(message['password'])
    emit('auth', {'auth': usr.isauth(), 'uuid': usr.getuuid()})


@socketio.on('join', namespace='/api')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    wrdata.lastmsg()
    emit('startup', wrdata.dict(message['uuid']))


@socketio.on('disconnect request', namespace='/api')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/api')
def test_connect():
    return True


@socketio.on('disconnect', namespace='/api')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=False)

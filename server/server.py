#!/usr/bin/env python
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import base64
import datetime
from functools import wraps
import sqlite3 as lite
import sys
import uuid

async_mode = 'eventlet'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
msgcount = 0


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

    def dict(self):
        d = dict()
        for prop, value in self.obj.items():
            d[prop] = value

        d['auth'] = session['auth']
        return d


class MessageLogging(object):

    def __init__(self, view_func):
        self.view_func = view_func
        wraps(view_func)(self)

    def __call__(self, request, *args, **kwargs):
        db.settable("log").map(request['loggingtype'], request).commit()
        response = self.view_func(request, *args, **kwargs)
        return response


class Mapping(object):
    def __init__(self):
        pass

    def image(self, data):
        datamapped = dict()
        datamapped['loggingtype'] = data['loggingtype']
        datamapped['count'] = data['count']
        datamapped['checksum'] = data['checksum']
        datamapped['pushtimestamp'] = data['timestamp']
        datamapped['savetimestamp'] = time.time()
        return datamapped

    def image_log(self):
        pass

    def auth(self, data):
        datamapped = dict()
        datamapped['loggingtype'] = data['loggingtype']
        datamapped['savetimestamp'] = time.time()
        datamapped['data'] = "{'remote_address:' '%s', 'uid': '%s'}" % (request.remote_addr, session['id'])
        return datamapped


class DB(Mapping):
    def __init__(self):
        self.con = None
        self.datamapped = None
        self.table = None
        self.connect()

    def settable(self, table):
        self.table = table
        return self

    def connect(self):
        self.con = lite.connect('db/data.db')

    def map(self, mappingfunction, data):
        self.datamapped = getattr(self, mappingfunction)(data)
        return self

    def commit(self):
        cur = self.con.cursor()
        columns = ', '.join(self.datamapped.keys())
        placeholders = ':'+', :'.join(self.datamapped.keys())
        query = 'INSERT INTO %s (%s) VALUES (%s)' % \
                (self.table, columns, placeholders)
        cur.execute(query, self.datamapped)
        self.con.commit()
        print(cur.lastrowid)
        emit('log', self.datamapped, room='webroom')


class Logger(Mapping):
    def __init__(self):
        pass

    def getentrybyrowid(self):
        print("pass")

db = DB()
bimg = Bimg()
wrdata = WebroomData()
wrdata.incmsg()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map')
def googlemap():
    return render_template('gtest.html')


@socketio.on('image', namespace='/api')
@MessageLogging
def sockimage(message):
    wrdata.incmsg()
    bimg.add(message['timestamp'])
    bimg.setcontent(message['obj']['payload']).save()

    emit('response', message['checksum'])
    emit('dataitems', wrdata.dict(), room='webroom')


@socketio.on('cleanup', namespace='/api')
def join(message):
    print(message)


@socketio.on('auth', namespace='/api')
@MessageLogging
def join(message):
    try:
        if message['password'] == "service":
            emit('auth', {'auth': True})
            session['auth'] = True
        else:
            emit('auth', {'auth': False})
    except:
        emit('auth', {'auth': False})


@socketio.on('join', namespace='/api')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('disconnect request', namespace='/api')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/api')
def test_connect():
    wrdata.lastmsg()
    if not "auth" in session:
        session['auth'] = False
        print("auth to false")

    if not "id" in session:
        session['id'] = str(uuid.uuid4())
        print("gen new session id")

    emit('startup', wrdata.dict())


@socketio.on('disconnect', namespace='/api')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=False)
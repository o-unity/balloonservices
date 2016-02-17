#!/usr/bin/env python
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import base64
import datetime

async_mode = 'eventlet'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
msgcount = 0


class Bimg(object):
    pathimage = "received/images/"
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
        return d


wrdata = WebroomData()
bimg = Bimg()
wrdata.incmsg()
#print(wrdata.dict())


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('image', namespace='/api')
def test_message(message):
    wrdata.incmsg()
    bimg.add(message['timestamp'])
    bimg.setcontent(message['payload']).save()

    emit('response', message['checksum'])
    emit('dataitems', wrdata.dict(), room='webroom')


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
#    emit('my response', {'data': 'Connected', 'count': 0})
    wrdata.lastmsg()
    emit('startup', wrdata.dict())


@socketio.on('disconnect', namespace='/api')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
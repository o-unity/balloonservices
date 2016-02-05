from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace
import time
import threading
import logging
#logging.getLogger('requests').setLevel(logging.WARNING)
#logging.basicConfig(level=logging.DEBUG)


class NsImage(BaseNamespace):
    def on_my_response(*args):
        print("NSImageClass")
        print('on_aaa_response', args)


class Namespace(LoggingNamespace):
    _connected = True

    def on_connect(self):
        print('connected')

    def on_error(self, data):
        print('error')

    def on_response(*args):
        print('on_aaa_response', args)


socketIO = SocketIO('localhost', 5000, Namespace)
nsp = socketIO.define(Namespace, '/test')
nsp.emit('image', {'data': 'personal data, YES! it works'})
socketIO.wait(seconds=10)



"""
socketIO = SocketIO('localhost', 5000, transports=['websocket', 'xhr-polling'])
ns_image = socketIO.define(NsImage, '/test')
#ns_image_thread = threading.Thread(target=ns_image)
#ns_image_thread.start()

print("wait...")


time.sleep(3)

#ns_image.wait(seconds=1)
ns_image.emit('my event', {'data': 'personal data, YES! it works'})
time.sleep(3)
ns_image.emit('disconnect')
#ns_image.wait(seconds=1)
print("finish")
"""
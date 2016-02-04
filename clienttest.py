from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace


class NsImage(BaseNamespace):
    def on_aaa_response(*args):
        print('on_aaa_response', args)


socketIO = SocketIO('localhost', 5000)
ns_image = socketIO.define(NsImage, '/test')
ns_image.on('my response', on_aaa_response)
ns_image.emit('my event', {'data': 'personal data, YES! it works'})
ns_image.wait(seconds=1)

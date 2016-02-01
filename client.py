
class ConfigHolder(object):
    def __init__(self):
        print("invoke ConfigHolder()")

    def printconfig(self):
        print("kkka")
        pass


class WebSocket(ConfigHolder):
    def __init__(self):
        super(WebSocket, self).__init__()
        print("invoke WebSocket()")

        if not hasattr(ConfigHolder, 'socket'):
            print("jjjjj")
            ConfigHolder.socket = 1

    def printout(self, t):
        print(t)


class Submit(WebSocket):
    def __init__(self):
        super(Submit, self).__init__()
        print("invoke Submit()")

    def submit(self):
        self.printout("submit!!!! %s - %s" % (self.imagepath, self.ip))


class Image(Submit):
    def __init__(self, imagepath):
        super(Image, self).__init__()
        print("invoke Image")

        self.imagepath = imagepath
#        self.sObject = self.create()

    def create(self):
        self.read()

    def read(self):
        pass

    def hello(self):
        print("hello!")


class GPS(Submit):
    def __init__(self, imagepath):
        super(Image, self).__init__()
        print("invoke Image")

        self.imagepath = imagepath
#        self.sObject = self.create()

    def create(self):
        self.read()

    def read(self):
        pass

    def hello(self):
        print("hello!")


ConfigHolder.ip = "192.168.1.10"
Image("images/test.png").submit()
Image("images/test2.png").submit()

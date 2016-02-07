

class Observer(object):
    def notify(self, *args, **kwargs):
        print(args, kwargs)

    def notify2(self, *args, **kwargs):
        print("ssss")


class Target(object):
    def __init__(self, *observers):
        self.observes = observers

    def event(self, data):
        for obs in self.observes:
            obs.notify('event', data)
        print("event with", data)

t = Target(Observer())
t.event(1)

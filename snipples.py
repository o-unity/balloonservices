
def logger(func):
    def inner(*args, **kwargs):
        print("Arguments were: %s, %s %s" % (args, kwargs, func))
        return func(*args, **kwargs)
    return inner



    @wrapt.decorator
    def emit(wrapped, instance, args, kwargs):
        wrapped(*args, **kwargs)
        if len(args[1]):
#            wrapped.nsp.emit('image', {'data': 'personal data, YES! it works'})
            print(wrapped)
            print(instance)
            pass

    @emit
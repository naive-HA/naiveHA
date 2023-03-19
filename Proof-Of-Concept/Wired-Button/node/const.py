def constant(f):
    def fset(self, value):
        raise TypeError
    def fget(self):
        return f()
    return property(fget, fset)

class _LED_MODES(object):
    @constant
    def NETWORK_DISCONNECTED():
        return 0
    @constant
    def NETWORK_CONNECTED():
        return 1
    @constant
    def CONNECTING():
        return 2
    @constant
    def STOPPED_CONNECTING():
        return 3

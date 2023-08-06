from weakref import ref, WeakKeyDictionary


def make_proxy(strong_kls):
    kls_ref = ref(strong_kls)
    class WeakObject(object):
        def __new__(cls, *args, **kwargs):
            kls = kls_ref()
            obj = kls.__new__(kls, *args, **kwargs)
            obj.__class__ = WeakObject
            obj.__init__(*args, **kwargs)
            return obj

        def __getattribute__(self, name):
            kls = kls_ref()
            try:
                #__dict__ object.__getattribute__
                value = object.__getattribute__(self, name)
                print "[getattribute] via object.__getattribute__", name
                return value
            except AttributeError:
                pass

            try:
                attr = kls.__dict__[name]
            except KeyError:
                raise AttributeError(name)

            try:
                value = attr.__get__(self, kls)
                print "[getattribute] via attr.__get__", name
                return value
            except AttributeError:
                print "[getattribute] via class attribute", name
                return attr

        def __setattr__(self, name, value):
            print "[setattr]", name, value
            kls = kls_ref()
            kls.__setattr__(self, name, value)

    return WeakObject


class Descriptor(object):
    def __init__(self):
        self._instances = WeakKeyDictionary()

    def __get__(self, obj, kls=None):
        if obj is None:
            try:
                obj = self._instances[kls]
            except KeyError:
                obj = kls()
                self._instances[kls] = obj
        return obj.something()


class Example(object):
    foo = Descriptor()

    def __new__(cls, a='hello'):
        print "__new__", cls, a
        return super(Example, cls).__new__(cls)

    def __init__(self, a='hello'):
        print "__init__", a

    def something(self):
        return 100

    def ex(self):
        return self.x

    @property
    def readonly(self):
        return self.x * 2

    @property
    def readwrite(self):
        return self.x * 2

    @readwrite.setter
    def readwrite(self, value):
        self.x = value / 2


print Example.foo
print Example.foo


# x = make_proxy(Example)()
# x.x = 10
# print x.x
# print x.ex()
# print x.readonly
# x.readonly = 40
# print x.readonly
# print x.readwrite
# x.readwrite = 100
# print x.readwrite
# print x.ex()


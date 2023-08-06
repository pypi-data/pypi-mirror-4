import gc
from weakref import ref, WeakKeyDictionary


_instances = WeakKeyDictionary()

def leak_class(create_ref):
    class Foo(object):
        # make cycle non-garbage collectable
        def __del__(self):
            pass

    if create_ref:
        # create a strong reference cycle
        #Foo.bar = Foo()
        _instances[Foo] = Foo()
    return ref(Foo)


# without reference cycle
r = leak_class(False)
gc.collect()
print r() # prints None

# with reference cycle
r = leak_class(True)
gc.collect()
print r() # prints <class '__main__.Foo'>

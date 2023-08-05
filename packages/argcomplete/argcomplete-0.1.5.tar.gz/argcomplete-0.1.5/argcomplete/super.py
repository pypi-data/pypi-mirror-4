class Foo(object):
    def __call__(self):
        print "Callable of", self, "invoked"

x = Foo()
x()

def patch(i):
    print "Patching", i.__class__
    class IntrospectFoo(i.__class__):
        def __call__(self):
            print "Callable of", self, "invoked"
            print "My super is:"
            print super(self)

    i.__class__ = IntrospectFoo

patch(x)

x()

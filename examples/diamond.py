class A(object):
    foo = 2
    bar = 100

    def __init__(self):
        self.y = 0

    def cool(self):
        print("so cool")

    def modify(self, x):
        print("modify A")
        self.y = self.foo * x
        return self.y

    def root(self):
        return "A"


class B(A):
    foo = 3
    whatever = "man"


class One(object):
    def root(self):
        return "One"


class Two(A):
    def root(self):
        val = super(Two, self).root()
        return val + " Two"


class Three(Two):
    pass


class C(B):

    foo = 5

    def other(self):
        print("just another function")

    def modify(self, x):
        print("modify C")
        x = super(self, C).modify(x)
        self.y = self.foo * x
        return self.y

    def root(self):
        val = super(C, self).root()
        return val + " C"


class D(C, Three):
    def root(self):
        return super(D, self).root() + " D"

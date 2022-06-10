from examples.a import A
from examples.b import B

class Mixin(object):
    def mixin(self):
        # Another base class.
        return "mixin"


class C(A, B, Mixin):
    override_this_attr = False

    def c_method(self):
        return "C"

    def overridden(self):
        return "C override"

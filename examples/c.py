from examples.a import A
from examples.b import B

class Mixin(object):
    def mixin(self):
        # Another base class.
        return "mixin"


class C(A, B, Mixin):
    # C has overridden this
    # Second line of comment
    override_this_attr = False  # MORE COMMENTS!
    # trailing comment that will be dropped since it comes on the line after.

    # Method comment. We can drop it.
    def c_method(self):
        return "C"

    def overridden(self, s):
        return "C override" + s

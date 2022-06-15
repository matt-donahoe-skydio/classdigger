from examples.c import C


class D(C):
    def d_method(self):
        if getattr(self, 'a'):
            return self.a
        return "D"

    @property
    def cool(self):
        return True

    def overridden(self, s):
        val = super(D, self).overridden(s)
        return "D override" + " " + val

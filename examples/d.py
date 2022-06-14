from examples.c import C


class D(C):
    def d_method(self):
        if getattr(self, 'a'):
            return self.a
        return "D"

    def overridden(self):
        val = super(D, self).overridden()
        return "D override" + " " + val

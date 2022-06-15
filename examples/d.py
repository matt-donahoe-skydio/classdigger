from examples.c import C


class D(C):
    def d_method(self):
        if getattr(self, 'a'):
            return self.a
        return "D"

    @property
    def cool(self):
        return True

    def overridden(self):
        val = super(D, self).overridden()
        return "D override" + " " + val

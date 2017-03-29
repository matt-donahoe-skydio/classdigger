from examples.c import C


class D(C):
    def __init__(self):
        print("override the __init__ method")

    def d_method(self):
        if getattr(self, 'a'):
            return self.a
        return

    def overridden(self):
        print('This is D')
        print('Calling super of D:')
        super().overridden()

class Base1(object):
    def common(self):
        # this method is also common to all subclasses, and they don't need to change it
        return "common"


class Base2(Base1):
    def other(self):
        # this method is also common to all subclasses, and they don't need to change it
        return "other"

class A(Base2):
    an_attr = True
    another_attr = False

    def a_method(self):
        self.a = "B"
        return self.a

    def overridden(self, s):
        return "A override" + s

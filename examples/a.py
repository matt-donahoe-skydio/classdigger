class Base1(object):

    # A base attribute
    BASE_ATTR = 1

    def common(self):
        # this method is also common to all subclasses, and they don't need to change it
        return "common"


class Base2(Base1):
    def other(self):
        # this method is also common to all subclasses, and they don't need to change it
        return "other"

class A(Base2):

    # This is just an attribute
    an_attr = True
    another_attr = False  # with a trailing comment

    def a_method(self):
        self.a = "B"
        return self.a

    def overridden(self, s):
        return "A override" + s

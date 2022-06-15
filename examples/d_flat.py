from examples.a import Base2
from examples.c import Mixin


class DFlat(Base2, Mixin):

    __A__an_attr = True
    an_attr = __A__an_attr

    __A__another_attr = False
    another_attr = __A__another_attr

    __B__override_this_attr = True
    __C__override_this_attr = False
    override_this_attr = __C__override_this_attr

    @property
    def __D__cool(self):
        return True

    @property
    def cool(self):
        return self.__D__cool

    def __A__a_method(self):
        self.a = "B"
        return self.a

    def a_method(self):
        return self.__A__a_method()

    def __B__b_method(self):
        return "B"

    def b_method(self):
        return self.__B__b_method()

    def __C__c_method(self):
        return "C"

    def c_method(self):
        return self.__C__c_method()

    def __D__d_method(self):
        if getattr(self, 'a'):
            return self.a
        return "D"

    def d_method(self):
        return self.__D__d_method()

    def __A__overridden(self, s):
        return "A override" + s

    def __C__overridden(self, s):
        return "C override" + s

    def __D__overridden(self, s):
        # Super call
        val = self.__C__overridden(s)

        return "D override" + " " + val

    def overridden(self, s):
        return self.__D__overridden(s)

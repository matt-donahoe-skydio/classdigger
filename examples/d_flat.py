from examples.a import Base2
from examples.c import Mixin


class DFlat(Base2, Mixin):


    # On X2, the motor cant is about the arm axis, so we specify them explicitly. This is from CAD
    # and gets normalized when used downstream.
    __B__MOTOR_CANT_AXES = [
        (-1.029, 1.715, 0.0),  # back left
        (1.029, 1.715, 0.0),  # front left
        (-1.029, -1.715, 0.0),  # back right
        (1.029, -1.715, 0.0),  # front right
    ]
    MOTOR_CANT_AXES = __B__MOTOR_CANT_AXES

    # This is just an attribute
    __A__an_attr = True
    an_attr = __A__an_attr

    __A__another_attr = False  # with a trailing comment
    another_attr = __A__another_attr

    __A__five = 2 + 3
    five = __A__five

    # B creates this, but C will override it
    __B__override_this_attr = True
    # C has overridden this
    # Second line of comment
    __C__override_this_attr = False  # MORE COMMENTS!
    override_this_attr = __C__override_this_attr

    __A__six = five + 1
    six = __A__six

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
        # begin super() call
        val = self.__C__overridden(s)
        # end super() call
        return "D override" + " " + val

    def overridden(self, s):
        return self.__D__overridden(s)

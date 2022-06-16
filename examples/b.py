class B(object):
    # B creates this, but C will override it
    override_this_attr = True

    def b_method(self):
        return "B"

    # On X2, the motor cant is about the arm axis, so we specify them explicitly. This is from CAD
    # and gets normalized when used downstream.
    MOTOR_CANT_AXES = [
        (-1.029, 1.715, 0.0),  # back left
        (1.029, 1.715, 0.0),  # front left
        (-1.029, -1.715, 0.0),  # back right
        (1.029, -1.715, 0.0),  # front right
    ]

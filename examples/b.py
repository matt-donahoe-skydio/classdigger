class B(object):
    # B creates this, but C will override it
    override_this_attr = True

    def b_method(self):
        return "B"

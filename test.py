import unittest

from flattener import member_defs, member_history, PY2_SUPER_PATTERN, arg_names
import examples.a
import examples.c
import examples.d
import examples.d_flat
import examples.diamond


class TestDiamondInheritance(unittest.TestCase):
    """
    Python inheritance is more complicated than I thought.
    I knew about the mro(), but situations can arise that
    short-circuit it.

    Guido's guide is here
    https://www.python.org/download/releases/2.2.3/descrintro/#cooperation

    Though he didn't explicit mention other cases besides the diamond.

    I found that blog from this one:
    https://gaopinghuang0.github.io/2018/12/29/dig-into-python-super-and-mro
    """

    def test_super(self):
        d = examples.diamond.D()
        self.assertEqual("A Two C D", d.root())


class TestMe(unittest.TestCase):
    maxDiff = 4000

    def test_py2_super_pattern(self):
        line = "val = super(Foo, self).method(arg, kwd=1)  # some comment"
        m = PY2_SUPER_PATTERN.search(line)

        self.assertNotEqual(None, m)

        self.assertEqual("Foo", m.group(2))
        self.assertEqual("val = ", m.group(1))
        self.assertEqual("method(arg, kwd=1)  # some comment", m.group(3))

        # Reconstruct the original line from the groups
        new_line = m.group(1) + "super(" + m.group(2) + ", self)." + m.group(3)
        self.assertEqual(line, new_line)

        bad_line = "This is super interesting"
        m = PY2_SUPER_PATTERN.search(bad_line)
        self.assertEqual(None, m)

        # TODO(matt): support py3 style super()

    def test_member_history(self):
        with open('examples/d_flat.py') as infile:
            lines = infile.readlines()
        # skip the first lines
        expected = ''.join(lines[4:]).strip()
        output = member_history(examples.d.D, output_parent_classes=[examples.a.Base2, examples.c.Mixin])
        self.assertEqual(expected, output)

    def test_member_history_values(self):
        # Test that the dflat.py file has a DFlat class with the the same members as original D.
        d = examples.d.D()
        df = examples.d_flat.DFlat()
        num = 0
        for attr in dir(d):
            if attr.startswith("__"):
                continue
            v = getattr(d, attr)
            vf = getattr(df, attr)
            
            # Detect method or value.
            if callable(v):
                args = arg_names(v)[1:]  # remove `self`
                out = v(*args)
                outf = vf(*args)
                self.assertEqual(repr(out), repr(outf), attr)
            else:
                self.assertEqual(v, vf, attr)
            num += 1
        print(f"tested {num} members")

    def test_member_defs(self):
        expected = {}
        expected["__A__an_attr"] = ("    # This is just an attribute", "True")
        expected["__A__another_attr"] = (None, "False  # with a trailing comment")
        expected["__A__six"] = (None, "3 + 3")
        expected["__A__seven"] = (None, "six + 1")
        expected["__B__MOTOR_CANT_AXES"] = (
            "    # On X2, the motor cant is about the arm axis, so we specify them explicitly. This is from CAD\n    # and gets normalized when used downstream.",
            "[\n        (-1.029, 1.715, 0.0),  # back left\n        (1.029, 1.715, 0.0),  # front left\n        (-1.029, -1.715, 0.0),  # back right\n        (1.029, -1.715, 0.0),  # front right\n    ]"
        )
        expected["__B__override_this_attr"] = ("    # B creates this, but C will override it", "True")
        expected["__C__override_this_attr"] = ("    # C has overridden this\n    # Second line of comment", "False  # MORE COMMENTS!")

        actual, ordering = member_defs(examples.d.D, set([examples.a.Base1, examples.a.Base2, examples.c.Mixin]))

        self.assertDictEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()

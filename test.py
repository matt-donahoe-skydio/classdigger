import unittest
from classdigger import ClassDigger, member_history, PY2_SUPER_PATTERN
import examples.a
import examples.c
import examples.d
import examples.d_flat
import examples.diamond


class TestClassDigger(unittest.TestCase):
    maxDiff = 2500

    def test_init(self):
        ClassDigger(examples.d.D)

    def test_structure(self):
        ClassDigger(examples.d.D).structure


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
                out = v()
                outf = vf()
                self.assertEqual(repr(out), repr(outf), attr)
            else:
                self.assertEqual(v, vf, attr)
            num += 1
        print(f"tested {num} members")

if __name__ == "__main__":
    unittest.main()

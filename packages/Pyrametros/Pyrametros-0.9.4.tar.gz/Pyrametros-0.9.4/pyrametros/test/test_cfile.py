from pyrametros import CFile
from common import Common
import os
import unittest

class TestCFile(unittest.TestCase):
    def setUp(self):
        c = Common()
        self.fname = c.static_dir+"ccode.c"
        self.bcomment = "/* Begin generated code: tagy */\n"
        self.ecomment = "/* End generated code: tagy */\n"
        with open(self.fname, 'w') as f:
            f.write(self.bcomment)
            f.write(self.ecomment)


    def test_simple_filling(self):
        cf = CFile(self.fname, "tagy")
        cf.push_line("simple line\n")
        cf.flush()

        with file(self.fname, 'r') as f:
            self.assertIn(self.bcomment, f)
            self.assertIn("simple line\n", f)
            self.assertIn(self.ecomment, f)

    def tearDown(self):
        os.remove(self.fname)

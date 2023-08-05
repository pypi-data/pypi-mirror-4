from ..parser import Line, parse_file
import os
import unittest

class TestLine(unittest.TestCase):
    def test_separator_in_line(self):
        # Separate per 5 characters.
        line = Line("aaaaa|aaaa|a|aa|aaaa", separators=[5,10,15])
        self.assertEquals(line.to_list[2], "a|aa")


if __name__ == "__main__":
    unittest.main()

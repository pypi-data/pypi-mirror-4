#!/usr/bin/python

# Commentary: parse_file will parse a table file and return a list of
# lists of strings for you do do whatever you want with. See Line
# class documentation for more info.

# For future versions:
#   make separators escapable
#   add comment support
#   support for optional columns


import re
from itertools import takewhile, dropwhile
from line import Line

class Parser(object):

    def __init__(self, filename, sep = '|', single_line_header=True):
        """Returns a list of lists with the cells of a table separated by
        separator. The header line is separated from the rest with an
        empty_line. Lines that are not standalone are merged with the
        previous line.  See Line class for more info on parameters.

        single_line_header removes newlines from multiline headers
        """
        line_setup = dict(linum=0, filename=filename, force_edges=(None, None), separator='|')
        self.head = None
        self.filename = filename
        itf = iter(open(filename, 'r').readlines())

        # Find a header line to use retrieve the line setup
        while not self.head:
            line_setup['linum'] += 1
            try:
                tmp = itf.next()
                self.head = Line(tmp, **line_setup)
            except StopIteration:
                raise Exception("No table found in file '%s'" % filename)

        line_setup.update(dict(force_edges=self.head.edge_separators, separators=self.head.separator_positions))

        # Create the rows
        rrows = []
        for s in itf:
            line_setup['linum'] += 1
            rrows.append(Line(s, **line_setup))

        # Merge until the horizontal separator to create the real
        # header, note that this consumes the separator aswell
        cursor = iter(rrows)
        self.head.merge([i for i in takewhile(lambda (x): bool(x), cursor)], "")
        self.lines = []
        for i in cursor:
            self.consume_line(i)

        if len(self.lines) == 0:
            print "W: Found just one line  of table"
            return

        # Consume remaining horizontal separators
        if not self.lines[0]:
            del self.lines[0]

        # The header must be able to standalone
        assert self.lines[0].standalone()

    def consume_line(self, line):
        """If the line is a continuation then merge it with the last
        encountered line. If not merge it with the last one ok."""
        if not line.standalone() and len(self.lines):
            self.lines[-1].merge([line])
        else:
            self.lines.append(line)

    @property
    def rows(self):
        """List of rows."""
        return [Row(self.head.to_list, i.to_list, self.filename) for i in self.lines]


class Row(dict):
    """Use this class to obtain a dict of the row with the column
    names as keys. It also removes leading and trailing spaces from cells.
    """

    def __init__(self, headers, cells, filename=None):
        """Only headers and cells are rest is for debug purposes"""
        self.filename = filename
        self._headers = map(self._strip_numbers, headers)
        for i,c in zip(self._headers, cells):
            if i:
                self[i] = c.strip()

    def _strip_numbers(self, cell):
        return re.sub("\d", "", cell).strip()

    def validate_columns(self, names):
        """Raise a key error if the row misses a header"""
        for h in names:
            if h not in self:
                raise KeyError("Table in %s is missing column named '%s'" % (self.filename, h))

    def tags_column(self, column_name):
        """This indicates that the `column_name' column is actualy a
        coma separated list of tags and should be turned into a list of tags
        """
        self[column_name] = [i.strip() for i in self[column_name].split(',')]


def parse_file(filename, assert_columns=[]):
    """For backwards compatibility basically"""
    rows = Parser(filename).rows
    for r in rows:
        r.validate_columns(assert_columns)

    return rows




if __name__ == "__main__":
    from sys import argv, exit
    USAGE = """parser.py <filename> <row> <column>
Outputs the text of the cell you queried for."""


    if len(argv) == 1 or argv[1] == "help":
        print USAGE
        exit()

    rows = parse_file(argv[1], '|')

    print rows

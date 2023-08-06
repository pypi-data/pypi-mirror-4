"""A line should be first checking if it should remove side
separators, then finding separators nearest to the ones line setup
dictates.
"""

from itertools import izip_longest

class Line(object):
    """Just a line aware of it's header, it is able to merge
    """

    def __init__(self, string, linum=-1, filename="<Unknown file>", force_edges=(None,None), separator='|', separators=None):
        """Try to use head to parse string into cells of a row and
        then put them into _row which you can retrieve form
        to_list. If head is None then we read solely based on the
        string provided. You can provide your own separator and the
        number (the line number is only used for debug messages).

        Force_lead and force trail configure wether the line has a
        beginning and ending separator. If None the line tries to
        figure them out. It fails if there is no leading separator and
        the line is a continuation so in that case these must be set.
        """
        # No processing
        self._line = linum
        self._filename = filename
        self._sep_lead,self._sep_trail = force_edges
        self._separator = separator

        # First remove side separators if needed
        self._string = self._strip_edge_separators(string, self._sep_lead, self._sep_trail)

        # See if line has any content
        if self._separator not in self._string:
            if separators is not None:
                cell_num = len(separators)+1
            else:
                cell_num = 1

            self._row = ['']*cell_num
            return

        # Do the heavy lifting
        self._row = self.split_cells(self._string, separators)

    def _strip_edge_separators(self, string, lead=None, trail=None):
        """If after any leadingor trailing spaces there are separators
        remove both spaces and separators"""
        if not string.rstrip():
            return ""

        # if we are sould choose or if we are forced
        if (string.rstrip()[-1] == self._separator and trail is None) or trail == True:
            string = string.rstrip()[:-1]
            self._sep_trail = True
        else:
            self._sep_trail = False

        # If we are to choose choose or if we are forced
        if (string.strip()[0] == self._separator and lead is None) or lead == True:
            string = string.strip()[1:]
            self._sep_lead = True
        else:
            self._sep_lead = False

        return string

    def split_cells(self, string, separators):
        """Split cells froma a string intelligently, see where the
        separators should be and split as close as possible to that
        """
        if separators is None:
            return string.split(self._separator)

        for s in separators:
            # Clamp to string length
            s = len(string)-1 if s >= len(string) else s

            # Search outwards from s and null-separate the parts
            pin = found = False
            for bc,fc in izip_longest(range(s,0,-1), range(s, len(string))):
                if fc is not None:
                    if string[fc] == self._separator:
                        string = string[:fc] + '\x00' + string[fc+1:]
                        found = True
                        break
                    elif string[fc] == '\x00':
                        # This means that we have something like this
                        # |xx|xx|xx|xx|
                        # |xxxxxxxxxxxxxxx|xx|xx|xx|xx|
                        # The separators are deected left-to-right so
                        # if we have detected one to the right, there
                        # is no way we are finding one to the left
                        pin = True

                if bc is not None and not pin:
                    if string[bc] == self._separator:
                        string = string[:bc] + '\x00' + string[fc+1:]
                        found = True
                        break
                    elif string[bc] == '\x00':
                        # Dont move past a previouly marked separator
                        pin = True

                if not found:
                    raise ValueError("Unable to determine cells correctly in %s:%d" % (self._filename, self._line))

        # String is now NULL-terminated on the valid separators
        return string.split('\x00')

    @property
    def edge_separators(self):
        """A touple of bools lead,trail on wether we omited a
        leading/trailing separator"""
        return self._sep_lead, self._sep_trail

    def clean_spaces(self, s):
        """Remove spaces from string in the front and back"""
        return s.strip()

    def merge(self, line_list, join_char = "\n"):
        """Merge the list of lines with this line. Join cells with provided character."""
        for l in line_list:
            if len(l) != len(self._row):
                raise Exception("Unmatched number fo cells while merging lines.")

            def smart_concat(x, y):
                if not x:
                    return y
                if not y:
                    return x
                return x.rstrip()+join_char+y.lstrip()

            self._row = map(smart_concat, self._row, l._row)

    def empty_line(self):
        """All cells are empty. most probably a separator or an empty
        line or later maybe a comment"""
        for i in self._row:
            if i != "":
                return False
        return True

    def standalone(self):
        """A standalone row is a row that is not the continuation of
        it's above and that is if it's first field is empty. Note that
        that includes lines that are completely empty and invalid
        lines (that are converted to completely empty."""
        return bool(self._row[0].strip().rstrip())

    def __len__(self):
        return len(self._row)

    def __repr__(self):
        return str(self._row)

    @property
    def to_list(self):
        """After a row is created and merged the above functions are
        of no use yet we may need to access slices etc. For now the
        solution is to turn it into a list. Later, we mayn need to be
        able to recosntruct the table, so I will implement the rest
        then."""
        return self._row

    def __nonzero__(self):
        """The bool conversion"""
        for i in self._row:
            if i != '':
                return True
        return False

    @property
    def separator_positions(self):
        """Return the positions that we found the separators"""
        sum = 0
        ret = []
        for c in self._row:
            sum += len(c)
            ret.append(sum)
            sum += 1
        return ret[:-1]

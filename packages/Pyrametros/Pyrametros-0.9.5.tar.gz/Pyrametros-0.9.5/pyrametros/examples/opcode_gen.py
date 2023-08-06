#!/usr/bin/python
"""This is binutils and kind of NemaWeaver specific but demonstrates
the way to read an ascii table

We have a class to represent the opcode struct literal as binutils
understands it. The class reads a line and draws information from
there. Then we have a factory function to create the struct."""

from  pyrametros import Row, parse_file
import re

REGISTER_SEQUENCE = ['s', 't', 'd', 'i']

class InstrType(object):
    """The instruction type binary
    """

    def __init__(self, row):
        """The row must have the following columns:
        bitfield
        syntax
        MINOR

        Then this object becomes an int that can serve as instr_type.
        Also performs a couple of checks to see of the table is valid.

        Arguments:
        - `row`:
        """
        global REGISTER_SEQUENCE
        assert 'bitfield' in row, "missing 'bitfield' column in table"
        assert 'syntax' in row, "missing 'syntax' column in table"
        assert 'MINOR' in row, "missing 'MINOR' column in table"
        assert 'opcode' in row, "missing 'opcode' column in table"


        self.fields = {}
        self.fields['minor'] = True
        self.fields['immediate'] = 0
        self._row = row

        bitfields = [row['bitfield'][i:i+5] for i in range(0,20,5)]
        register_map = dict(zip(REGISTER_SEQUENCE, bitfields))

        # Registers to be read
        self.fields['register_fields'] = dict.fromkeys(REGISTER_SEQUENCE[:3], False)

        # The following rules apply:
        #  DONE: 5bit fields should have alla the same char
        #  DONE: the char should be s, t, d, x or i
        #  DONE: if the character is i the rest of the fields also have i
        #  DONE: the registers detected in the bitfield should be also in the syntax and vice versa
        allowed_chars = None
        for i in REGISTER_SEQUENCE:
            assert len(set(register_map[i])) == 1,\
                "There seems to be a problem in bitfield of command '%s': bitfield: '%s' (substring '%s' should contain five of a kind)" % \
                (row["opcode"], row["bitfield"], register_map[i])

            # If we havent yet encountered i anything is alowed
            if allowed_chars != ('i'):
                allowed_chars = ('x', 'i', i)

            # Once imm val is encountered all the rest MUST imm
            if register_map[i][0] == 'i':
                self.fields['immediate'] += 1
                allowed_chars = ('i')

            assert register_map[i][0] in allowed_chars, \
                "Found '%s' in bitfield '%s' where only %s should be" % (register_map[i][0], row['bitfield'], allowed_chars)

            if register_map[i][0] == i and i not in ('i', 'x'):
                self.fields['register_fields'][i] = True


        syntax_regs = re.compile("(?<=r)[dst]")
        syntax = syntax_regs.findall(row['syntax'])
        assert sorted([i for i in self.fields['register_fields'] if self.fields['register_fields'][i]]) == sorted(syntax),\
                "Syntax does not match bitfield in command %s (%s - %s)" % (row['opcode'], sorted(self.fields['register_fields'].keys()), sorted(syntax))

        self.fields['permutation_code'] = self._permutation_code(syntax)

        if row['MINOR'] == "iiiiii":
            self.fields['minor'] = False
            self.fields['immediate'] += 1

    def _shift_list(self, lst, shift):
        return [lst[-shift]]+lst[:-shift]

    def _permutation_code(self, reg_list):
        """The algorithm is shift right, then exchange the other
        members. The place of the supposedly first is the num of
        shifts (so x2). Then shift the thing to see if it is the first
        or second occurnace.

        ATTENTION: for more or less than 3 types of registers this
        breaks real hard."""
        global REGISTER_SEQUENCE

        # fill the missing registers in reg_list
        for i in REGISTER_SEQUENCE[:3]:
            if i not in reg_list:
                reg_list.append(i)

        shift = reg_list.index(REGISTER_SEQUENCE[0])
        if self._shift_list(REGISTER_SEQUENCE[:3], shift) == reg_list:
            mod = 0
        else:
            mod = 1
        return shift*2+mod


    def __dict__(self):
        return self.fields

    def __int__(self):
        """Return the hash of the instruction type"""
        global  REGISTER_SEQUENCE

        offset = 3;
        # 3bits for the permutation
        ret = self.fields['permutation_code'] & 7

        # 1bit for each register in bitfield order
        for i in REGISTER_SEQUENCE[:3]:
            ret |= self.fields['register_fields'][i] << offset
            offset += 1

        assert self.fields['immediate'] == self.fields['immediate']&7, \
            "Looks like too many fields for immediate %d" % self.fields['immediate']
        ret |= self.fields['immediate'] & 7 << offset
        offset += 3

        ret |= self.fields['minor'] << offset

        return ret


class OpcodeStruct:
    """This class represents the C struct in binutils vreated in
    binutils/opcodes/<target-name>-opc.h"""

    def __init__(self, row):
        """The argument here is a dict with the names and values of
        info obtained from tables. Supported names:
        syntax: <comma split argument list [rd | rs | rt | imm | Imm<num>]
        """
        self._row = row
        self._private_args = None

    def get_name(self):
        return self._row["opcode"]

    def _match_arg(self, regex, args = None):
        """Match once and dont match again. Providing args resets
        self._private_args"""
        if args:
           self._private_args = args

        for i in range(len(self._private_args)):
            if regex.match(self._private_args[i]):
                del self._private_args[i]
                return True
        return False

    def get_inst_type(self):
        return hex(int(InstrType(self._row)))

    def get_bitfield(self):
        # MAJOR/MINOR : 6bit, ALL: 32bit
        non_dig = re.compile("\D")

        minor = 0
        major = int(self._row["MAJOR"])
        if not non_dig.search(self._row["MINOR"]):
            minor = int(self._row["MINOR"])

        return major<<26 | minor

    def get_mask(self):
        mask = 0x3f<<(32-6)

        non_dig = re.compile("\D")
        if not non_dig.search(self._row["MINOR"]):
            mask |= 0x3f

        return mask

    def get_instr_type(self):
        """This has to do with the nature of the intruction"""
        if not "instruction type" in self._row.keys():
            return "0"

        return self._row["instruction type"]

    def __repr__(self):
        init = '{"%(name)s", %(inst_type)s,  INST_NO_OFFSET, NO_DELAY_SLOT, IMMVAL_MASK_NON_SPECIAL, %(bitfield)s, %(mask)s, %(name)s_opcode, %(instr_type)s }' % dict(name = self.get_name(), inst_type = self.get_inst_type(), bitfield = hex(self.get_bitfield()), mask = hex(self.get_mask()), instr_type = self.get_instr_type())
        return init


    def __str__(self):
        return self.__repr__()

def opcodeStructFactory(filename):
    """Create a list of opcode struct as presented in the table in filename (deliminer = '|')"""
    table = parse_file(filename)
    head = table[0]
    return [OpcodeStruct(i) for i in table[1:]]


if __name__ == "__main__":
    from sys import argv
    if len(argv) < 2:
        print "Please provide a filename for the ascii table"
    else:
        for i in opcodeStructFactory(argv[1]): print i

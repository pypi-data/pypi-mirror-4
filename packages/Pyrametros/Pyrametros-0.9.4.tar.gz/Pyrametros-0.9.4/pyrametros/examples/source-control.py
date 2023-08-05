#!/usr/bin/python
"""Fills opcodes in scavenger-opcm.h"""

from pyrametros import CFile, parse_file

# Open a file to edit
f = CFile('scavenger-opcm.h', 'instruction names')

for i in grid[1:]:
    # Create dictionary style rows. Note that numbers are striped from header keys.
    dictionary = parce_file("testtable.txt")

    # Put a line in the file
    f.push_line(dictionary['opcode']+"_opcode,\n")

# Dont forget to flush
f.flush()

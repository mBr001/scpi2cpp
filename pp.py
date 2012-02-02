#!python

import sys

ind = '  '
indent = 0
closed = False

for line in sys.stdin:
	for c in line:
		if c.isspace():
			continue
		print(c, end='')
		if c in ('(', '[', '{', ):
			indent = indent + 1
			print()
			print(ind * indent, end='')
			continue
		if c in (')', ']', '}', ):
			indent = indent - 1
			if closed:
				print()
				print(ind * indent, end='')
			closed = True
			continue
		if c in (',', ):
			print()
			print(ind * indent, end='')
			continue
		if not c.isspace():
			closed = False


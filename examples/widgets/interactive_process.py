"""
Simple interactive process used to demonstrate the use of the
InteractiveConsole widget.
"""
import sys
print('running an interactive process')

if sys.version_info[0] == 2:
    value1 = raw_input('Enter value1: ')
    value2 = raw_input('Enter value2: ')
else:
    value1 = input('Enter value1: ')
    value2 = input('Enter value2: ')
print("Result: %d" % (int(value1) + int(value2)))


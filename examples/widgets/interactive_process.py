"""
Simple interactive process used to demonstrate the use of the
InteractiveConsole widget.
"""
import sys
print('running an interactive process')


if sys.version_info[0] == 2:
    input_fct = raw_input
else:
    input_fct = input

print('"/home/pyqt-distutils/file.py"')
print('"/home/pyqt distutils/file.py"')

value1 = input_fct('Enter value1: ')
value2 = input_fct('Enter value2: ')
value3 = input_fct('Enter value3: ')
value4 = input_fct('Enter value4: ')

print('You entered: %r - %r - %r - %r' % (value1, value2, value3, value4))

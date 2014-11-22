"""
This example show you how to use the InteractiveConsole. To make this example
complete and cross-platform, we created an interactive process which prints some text
and asks for user inputs. That way you can see that the console is actually interactive.
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


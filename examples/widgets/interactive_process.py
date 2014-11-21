"""
This example show you how to use the InteractiveConsole. To make this example
complete and cross-platform, we created an interactive process which prints some text
and asks for user inputs. That way you can see that the console is actually interactive.
"""
import sys
print('running an interactive process')

if sys.version_info[0] == 2:
    text = raw_input('Please enter some text: ')
else:
    text = input('Please enter some text: ')
print("You've just typed: %s" % text)

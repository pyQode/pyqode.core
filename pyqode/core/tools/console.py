"""
This script wraps the execution of console program so that a prompt appear
after the end of the console program (so that the console does not close as
soon as the user program finished).


Usage:
    pyqode-console program [options]

Example:

    $ pyqode-console python /path/to/a/script.py --spam eggs
    $ ...
    $ The process terminated with exit code 0.
    $ Press a key to close this window...
    $
"""
import os
import sys
import subprocess


def main():
    global program, args, ret
    print(os.getcwd())
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) == 1:
        print(__doc__)
        sys.exit(0)
    else:
        program = sys.argv[1]
        args = sys.argv[2:]
        if args:
            ret = subprocess.call([program] + args)
        else:
            ret = subprocess.call([program])
        print('Process terminated with exit code %d' % ret)
        if sys.version_info[0] == 3:
            input('Press any key to close this window...')
        else:
            raw_input('Press any key to close this window...')
        sys.exit(ret)


if __name__ == '__main__':
    main()

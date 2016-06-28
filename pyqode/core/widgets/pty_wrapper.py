import sys


def pty_wrapper_main():
    """
    Main function of the pty wrapper script
    """
    from pyqode.core.widgets import pty
    # fixme: find a way to use a pty and keep stdout and stderr as separate channels
    pty.spawn(sys.argv[1:])


if __name__ == '__main__':
    pty_wrapper_main()

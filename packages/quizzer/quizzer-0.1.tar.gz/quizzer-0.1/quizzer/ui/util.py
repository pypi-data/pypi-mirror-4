# Copyright

try:
    import curses as _curses
except ImportError as _curses_import_error:
    _curses = None
import os as _os
import sys as _sys


ANSI_COLORS = [  # from the 'Color Handling' section of terminfo(5)
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white',
    ]

COLORS = None
SETAF = None

# https://gist.github.com/interstar/3005137
def setup_colors():
    global COLORS, SETAF
    COLORS = None
    if _curses:
        capname = 'setaf'  # set ansi foreground color
        try:
            code = _curses.tigetstr(capname)
        except _curses.error:
            term = _os.environ.get('TERM', 'ansi')
            with open('/dev/null', 'w') as f:
                # setupterm() is required for curses.tiget*()
                _curses.setupterm(term, f.fileno())
            code = _curses.tigetstr(capname)
        if code is not None:
            n = _curses.tigetnum('colors')
            if n:
                SETAF = code
                COLORS = []
                for i,color in zip(range(n), ANSI_COLORS):
                    COLORS.append(color)

def set_foreground_color(color):
    if SETAF and COLORS:
        i = COLORS.index(color)
        code = SETAF.replace(b'%p1%d', str(i).encode('ascii'))
        _sys.stdout.flush()
        _sys.stdout.buffer.write(code)

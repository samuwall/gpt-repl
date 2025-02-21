#################################################
## file         : input.py
## description  :
##
#################################################

import os
import sys
import re
from prompt_toolkit import prompt
from gpt_repl.render import count_lines, clear_lines

def getch():

    if os.name == "nt":
        import msvcrt
        return msvcrt.getch().decode("utf-8")
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        except KeyboardInterrupt:
            ch = '\x03'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def get_input(prev_input, bindings):

    user_input = prompt(": ", key_bindings=bindings, default=prev_input).strip()

    normalized_input = user_input.lower()
    if normalized_input in ["q", "-q"]:
        return ('quit', None)
    elif normalized_input in ["-h", "--h", "--help"]:
        return ('help', None)
    elif re.match(r"^--?c \d+$", normalized_input):
        id = int(normalized_input.split()[1])
        return ('copy_code', id)
    elif re.match(r"^--?p\s+raw$", normalized_input):
        return ('render', 'raw')
    elif re.match(r"^--?p\s+lite$", normalized_input):
        return ('render', 'lite')
    elif re.match(r"^--?p\s+rich$", normalized_input):
        return ('render', 'rich')
    elif re.match(r"^--?[a-z]$", normalized_input) or re.match(r"^--?.\s", normalized_input):
        return ('invalid_command', None)
    else:
        print("\rAre you sure you want to submit? \x1b[96m[y/n]\x1b[0m", end='')
        confirm = getch().lower()
        if confirm == 'y':
            sys.stdout.write("\r\x1b[K")
            sys.stdout.flush()
            return ('input', user_input)
        else:
            num_lines = count_lines(f": {user_input}")
            clear_lines(num_lines)
            return ('cancel', user_input)

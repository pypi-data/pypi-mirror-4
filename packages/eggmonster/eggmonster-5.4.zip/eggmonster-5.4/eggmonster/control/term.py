"""Send TERM signal to end nicely."""
from eggmonster.control._common import putargs, control_command
import sys

def main():
    return control_command(sys.stdin, 'term')

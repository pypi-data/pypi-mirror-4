"""Dump configuration to stdout."""
import sys

from eggmonster.control._common import getjson, reset_sigpipe

def main():
    reset_sigpipe()
    version, config = getjson('config')
    sys.stdout.write(config)

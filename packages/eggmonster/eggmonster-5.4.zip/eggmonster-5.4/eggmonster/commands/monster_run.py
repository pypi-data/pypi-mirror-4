#!/usr/bin/env python

import sys
import argparse

import eggmonster.runner
from eggmonster.listutil import partition_list

def get_args(in_args):
    usage = "%(prog)s <config file> <application id> [options]"
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('config', help="config file path")
    parser.add_argument('app_id', help="application id")
    parser.add_argument("-u", "--update",
        action="store_true", default=False,
        help="Update dependencies and other egg info using `sudo "
            "python setup.py develop` before running (setup.py "
            "must be in cwd; user must have sudo permission)")
    parser.add_argument("-i", "--interact",
        action="store_true", default=False,
        help="Open up an interactive prompt with the correct environment.")
    parser.add_argument("-n", "--num", type=int, default=1,
        help="Use config substitution, swapping $num for given value.")
    parser.add_argument("--spawn", action="store",
        help="Used internally when spawning processes.")
    return parser.parse_args(in_args)

def run():
    monster_args, sep, prog_args = partition_list(sys.argv, '!')

    args = get_args(monster_args[1:])

    eggmonster.runner.main(args.config, args.app_id, args.update,
        args.interact, args.num, args.spawn, prog_args)

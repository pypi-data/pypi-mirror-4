#!/usr/bin/env python

import subprocess
import argparse
import sys

from eggmonster import emenv

def get_args():
    parser = ArgumentParser()
    parser.add_argument('-s', '--source', dest='source', action='store_true',
        default=False, help="Upload as 'sdist' instead of 'bdist_egg'",)
    return parser.parse_args()

def run():
    args = get_args()

    cheeseshop = emenv.cheeseshop
    command = 'sdist' if args.source else 'bdist_egg'
    cmd = [
        sys.executable, 'setup.py', command,
        'upload', '-r', emenv.cheeseshop,
    ]
    subprocess.call(cmd)

if __name__ == '__main__':
    run()

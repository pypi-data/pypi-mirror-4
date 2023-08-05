#!/usr/bin/env python

import subprocess
import argparse

from eggmonster import packages

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('module', nargs='+')
    args = parser.parse_args()
    packages.install_many(args.module)

if __name__ == '__main__':
    run()

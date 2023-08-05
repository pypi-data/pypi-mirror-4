#!/usr/bin/env python

import sys
import logging
import argparse

class EMCommandAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        command = values
        try:
            setattr(namespace, self.dest, self.get_command(command))
        except ImportError:
            parser.error("No such command '%(command)s'" % vars())

    @classmethod
    def get_command(cls, name):
        modname = 'eggmonster.control.' + name
        return __import__(modname, fromlist=['main'])

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('command', action=EMCommandAction,
        default=EMCommandAction.get_command('help'))
    args, rest = parser.parse_known_args()
    return args, rest

def run():
    logging.basicConfig(format='%(message)s')
    args, rest = get_args()
    args.command.main(*rest)

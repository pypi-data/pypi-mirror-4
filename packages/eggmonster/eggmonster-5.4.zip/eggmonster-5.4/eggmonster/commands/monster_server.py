#!/usr/bin/env python

import sys
import os
import argparse

import eggmonster.server

class ExistingDirAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            parser.error("the given path is not a directory")
        setattr(namespace, self.dest, values)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", type=int,
        default=8000, help="listen on port PORT (default 8000)",)
    parser.add_argument("-a", "--authdb", dest="passwd", type=str,
        default = '', help="path to file with Basic Auth password hashes "
        "(default no auth)", metavar="PASSWD")
    parser.add_argument("config_path", type=str, action=ExistingDirAction,
        help="directory where YAML config revisions will be stored",
    )
    return parser.parse_args()

def run():
    args = get_args()
    eggmonster.server.main(args.config_path, args.port, args.passwd)

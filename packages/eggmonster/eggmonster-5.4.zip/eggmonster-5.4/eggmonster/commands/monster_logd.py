#!/usr/bin/env python

import sys
import optparse

import eggmonster.logger

def get_option_parser():
    op = optparse.OptionParser()
    op.add_option("-T", "--no-timestamps",
        action="store_false", dest="timestamp", default=True,
        help="Do not prefix log lines with timestamps",
    )
    op.add_option("-p", "--port",
        type="int", dest="port", default=eggmonster.logger_port,
        metavar="PORT", help="Listen on port PORT",
    )

    return op

def run():
    parser = get_option_parser()

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("monster_logd requires exactly one argument: log base directory")

    basedir = args[0]

    eggmonster.logger.main(basedir, options)

#!/usr/bin/env python

import sys
from eggmonster.eggserver import main
from optparse import OptionParser

def setup_parser():
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", type=int,
        help="port on which to run the HTTP server (default=8010)")
    parser.add_option("-a", "--auth", dest="authdb",
        help="Basic AUTH database (default=no auth)")
    parser.set_defaults(port=8010, authdb='')
    return parser

def run():
    parser = setup_parser()
    (options, args) = parser.parse_args()
    if not args:
        parser.error("One required argument: path to repository base")
    repo = args[0]

    main(repo, options.authdb, options.port)

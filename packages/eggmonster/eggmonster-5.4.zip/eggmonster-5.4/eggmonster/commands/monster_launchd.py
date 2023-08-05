#!/usr/bin/env python

import os
import getpass
from eggmonster.launch import main
from optparse import OptionParser
import platform
try:
    import pwd
except ImportError:
    pass

def setup_parser():
    parser = OptionParser()
    current_user = getpass.getuser()
    parser.add_option("-u", "--user", default=current_user,
        help="setuid() to this user in application processes "
        "(default: %(current_user)s)" % vars())

    default_host_id = platform.node()
    parser.add_option('-i', '--host-id', default=default_host_id,
        help="The host id to use (defaults to %(default_host_id)s)." %
        vars(),
        )
    parser.add_option('--debug', action='store_true',
        help='Print debug information about launching processes.')
    return parser

def get_options():
    parser = setup_parser()
    options, args = parser.parse_args()
    if args:
        parser.error("Received unexpected positional arguments")

    uid = pwd.getpwnam(options.user).pw_uid

    if os.getuid() and uid != os.getuid():
        parser.error(
            "monster_launchd must be run as root to setuid for %s" %
            options.user)

    return options

def run():
    options = get_options()

    try:
        main(options.user, options.debug, host_id=options.host_id)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        import logging
        logging.getLogger('em.launchd').exception('Exited unexpectedly.')

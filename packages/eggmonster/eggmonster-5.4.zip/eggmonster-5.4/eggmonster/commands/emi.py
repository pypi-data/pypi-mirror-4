#!/usr/bin/env python

import sys
from eggmonster.client._em_emi import main

def run():
    if '!' in sys.argv:
        delimiter_index = sys.argv.index('!')
        prog_args = sys.argv[delimiter_index+1:]
        monster_args = sys.argv[:delimiter_index]
    else:
        prog_args = []
        monster_args = sys.argv

    import optparse
    parser = optparse.OptionParser()
    parser.add_option('--spawn', dest='spawn_app', action='store')
    parser.add_option('--debug', action='store_true')

    options, values = parser.parse_args(monster_args[1:])
    app_id, n = values

    try:
        main(app_id, n, options.spawn_app, prog_args, options.debug)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        import logging
        logging.getLogger('em.emi').exception('Exited unexpectedly.')

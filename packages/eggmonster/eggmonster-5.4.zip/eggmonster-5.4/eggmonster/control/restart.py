"""Restart one or more services gracefully, in a sequential fashion."""
from eggmonster.control._common import (control_command, getjson,
    stat_to_node_def, timestr, reset_sigpipe, reset_sigint)
from eggmonster.control.status import getstatus
from optparse import OptionParser
import sys
import time

last_node = None
def log(message, node=None):
    '''Prints a log statement with a timestamp.'''

    timestamp = time.strftime('[%H:%M:%S]', time.localtime())
    if node:
        global last_node
        if last_node != node:
            print '%s.%s (%s:%s)' % tuple(node)
            last_node = node
        print ' ', timestamp, message
    else:
        print timestamp, message

# Node will be something like
# ('pkgname', 'appname.instname', 'hostname', 1)
def uptime(node):
    '''Returns a two-tuple of how long the service has been up for,
    and when the service was started (using Eggmonster service time).'''
    servertime, stattimes = getstatus()
    for statline in stattimes:
        if (statline['host'] == node[2]
            and statline['num'] == node[3]
            and statline['app_name'] == ('%s.%s' % node[:2])
            ):
            ts = statline.get('launchtime', 0)
            if not ts:
                return 0, ts
            return (servertime - ts), ts
    raise RuntimeError, 'could not find node in status: %s' % (node,)

def main(*args):
    reset_sigpipe()
    reset_sigint()

    parser = OptionParser()
    parser.add_option(
        '--delay', type='int', default=20, metavar='SECS',
        action='store',
        help='Number of seconds to wait before attempting to restart '
            'following services (default: 20)',
        )
    parser.add_option(
        '--killafter', type='int', default=None, metavar='SECS',
        action='store',
        help='Number of seconds to wait before forcing a restart of '
            'services using a KILL signal (default: off)',
        )

    options, values = parser.parse_args(list(args))

    # Process each node, one at a time.
    nodes = [(line, stat_to_node_def(line)) for line in sys.stdin]
    for stat_line, node in nodes:

        # Send a TERM signal to this service.
        node_uptime, node_birthtime = uptime(node)
        control_command([stat_line], 'term')
        log('Sent TERM signal.', node)

        sent_kill = False
        term_signal_time = time.time()

        # Loop over, and wait for confirmation the service restarted.
        while True:
            time.sleep(3)

            # Check to see when the service was "born", according to the
            # server.
            new_node_uptime, new_node_birthtime = uptime(node)
            if new_node_birthtime > node_birthtime:
                log('Restarted successfully. Waiting.', node)
                break

            # If we've been waiting a long while (too long), then try
            # KILL instead.
            #
            # If we have been waiting a long while, *and* have sent a
            # KILL signal, then give up - we're stuck here.
            if options.killafter is not None and \
                    (time.time() - term_signal_time) > options.killafter:
                if sent_kill:
                    msg = 'Aborting - %(node)s did not respond to KILL signal.'
                    log(msg % vars(), node)
                    sys.exit(1)
                sent_kill = True
                control_command([stat_line], 'kill')
                log('Sent KILL signal.', node)
                term_signal_time = time.time()

        # Now we know the service is terminated, let's wait for it to
        # have a stable uptime.
        last_log_time = time.time()
        while True:
            if new_node_uptime > options.delay:
                # I have seen quite strange uptimes, where it appears to
                # be returning a timestamp rather than an uptime, so
                # this is a basic check for this.
                if new_node_uptime > (2000 + options.delay):
                    log("Got odd uptime value from Eggmonster server: %s"
                        % timestr(new_node_uptime), node)
                else:
                    log('Uptime: %s. Done.' % timestr(new_node_uptime),
                        node)
                    break
            else:
                now = time.time()
                last_logged = now - last_log_time

                # Update if the last log message was 10+ seconds ago, and there is
                # still 5 seconds before the next log message.
                if last_logged > 10 and ((new_node_uptime + 5) < options.delay):
                    log('Uptime: %s. Waiting.' % timestr(new_node_uptime), node)
                    last_log_time = time.time()

            time.sleep(3)
            new_node_uptime = uptime(node)[0]

    log('Finished.')

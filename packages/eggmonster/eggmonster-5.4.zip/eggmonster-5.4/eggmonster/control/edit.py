"""Edit eggmonster configuration."""
import os
import mimetypes
import logging

import pkg_resources

from eggmonster.control._common import getjson, putargs
from eggmonster.control.status import getstatus
from eggmonster.editor import EditableFile

from optparse import OptionParser

log = logging.getLogger(__file__)

CONF_SYNC_SHORT_WARNING = """
WARNING: Applications running with out-of-sync configuration. Please run either:

  em edit -n            # no restarts
  em edit -i            # ignore sync problems

Or run the following to explain the problem in more detail:
  em edit --explain-conf-sync
"""

CONF_SYNC_FULL_WARNING = """
There are currently some applications which are running which are using
configurations which are not in sync with the Eggmonster server.

If you make any modifications to the configuration, it will cause those
applications to restart. These applications had their configurations
modified by passing the --no-restart option to "em edit", which prevented
them from being restarted.

To see what applications are currently running in this state, run:
  em status | grep '*'

If you want to modify the configuration without forcing these applications
to restart, run:
  em edit --no-restart (or "em edit -n" for short)

That option will prevent any modified applications from being restarted
when you have modified the configuration - even for applications you want
restarted. You will then need to manually restart the processes you want
to use the new configuration (using "em term" or "em restart").

Alternatively - you can just modify the configuration and force these
applications to restart (and bypass this warning) by running:
  em edit --ignore-conf-sync (or "em edit -i" for short)
"""

def main(*args):

    if '--explain-conf-sync' in args:
        raise SystemExit(CONF_SYNC_FULL_WARNING)

    parser = OptionParser()
    parser.add_option('-n', '--no-restart', default=False,
        action='store_true',
        help='Make changes without restarting services (be careful '
        'with this!)',
    )
    parser.add_option('-i', '--ignore-conf-sync', default=False,
        action='store_true',
        help="Ignore warnings about running apps which have "
            "out-of-sync configs",
    )
    options, values = parser.parse_args(list(args))

    # If we are allowing restarts, but there are config-out-of-sync
    # applications running, then warn users about the consequences of
    # doing so.
    if (not options.ignore_conf_sync) and (not options.no_restart):
        servertime, statlines = getstatus()
        if [sl for sl in statlines if not sl.get('conf_sync', True)]:
            raise SystemExit(CONF_SYNC_SHORT_WARNING)

    version, config = getjson('config')
    # add a content-type for YAML so the editor can give a useful
    #  extension to the file.
    mimetypes.add_type('text/yaml', '.yaml')
    editor = EditableFile(config, 'text/yaml')
    try:
        editor.edit()
    except Exception, e:
        print e, '; aborting.'

    if not editor.changed:
        print "File unchanged; skipping upload."
        return

    new_config = editor.data

    if not new_config.strip():
        print "Empty config; skipping upload."
        return

    resp, body = putargs('config', dict(
            config = new_config,
            last_version = int(version),
            allow_restart = int(not options.no_restart),
        ),
        check_status=False,
    )

    status = resp.code
    if status != 202:
        temp_config_fn = write_temp(new_config)
        raise ValueError(
            "Non-202 server response: %(status)s\nBody:%(body)s\n"
            "Your modified config file was saved to "
            "'%(temp_config_fn)s'\n" % vars())

    print "Uploaded to master."
    report_changes(config, editor.data)

def write_temp(new_config):
    fn = "eggmonster-config.tmp"
    if os.path.exists(fn):
        count = 1
        def mknumbered(count):
            return "eggmonster-config.%s.tmp" % count
        while os.path.exists(mknumbered(count)):
            count += 1
        fn = mknumbered(count)
    open(fn, 'w').write(new_config)
    return fn

def report_changes(orig_config, new_config):
    """
    The config has changed, allow other libraries to provide plugins
    to handle the changes.
    """
    group = 'eggmonster_config_updates'
    handlers = (
        entrypoint.load()
        for entrypoint in pkg_resources.iter_entry_points(group=group)
        )
    for handle in handlers:
        try:
            handle(orig_config, new_config)
        except Exception:
            log.exception("Update report hook failed.")


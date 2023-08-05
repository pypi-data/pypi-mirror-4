"""Displays available commands and their docstrings."""
import os
import sys
import textwrap

import eggmonster.control

# Override docstring with a contextually relevant one.
__doc__ = """Displays this help message."""

def main():
    cmds = get_cmds()

    # Store command maxlength to enable pretty formatting
    maxlen = max((len(k) for k in cmds))
    fmtstr = "  %%-%ds   %%s" % maxlen

    # Finally output the available commands
    print "Usage: %s <command>\n" % os.path.basename(sys.argv[0])
    for k in sorted(cmds):
        print "\n".join(textwrap.wrap(
                        fmtstr % (k, cmds[k] or ''),
                        width=79,
                        subsequent_indent=" " * (maxlen + 5),
                ))
    print

def get_cmds():
    cmds = {}
    for f in filter(filter_files, os.listdir(eggmonster.control.__path__[0])):
        mod_name = f[:-3]
        try:
            cmd_mod = __import__(
                            'eggmonster.control.%s' % mod_name, fromlist=[mod_name])
        except ImportError:
            sys.stderr.write("could not import command '%s'\n" % mod_name)
            raise SystemExit(1)

        # Save command and docstring
        cmds[mod_name] = cmd_mod.__doc__
    return cmds

def filter_files(f):
    return not f.startswith("_") and f.endswith(".py")

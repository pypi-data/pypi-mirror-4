import os
import sys
import subprocess

import eggmonster.runner


def construct_fake_monster_command(app_name, exec_args, args):
    """
    Construct a command to launch the app named `app_name` in the same
    package as this FakeMonster app, but with `args`.
    """
    em_app, config_path = eggmonster.runner.FakeMonster.parse_args()
    em_app.name = app_name

    command = [exec_args[0], '--config-path', config_path, str(em_app)]
    command.extend(args)
    return command

def construct_monster_run_command(entry_point, exec_args, args):

    # If we have parameters intended for the target application, we can't
    # include those for the spawned application, so drop those parameters.
    try:
        delim_index = exec_args.index('!')
    except ValueError:
        pass
    else:
        del exec_args[delim_index:]

    # This is how we specify the app to run.
    exec_args[1:1] = ['--spawn=%s' % entry_point]

    # Add any extra arguments.
    if args:
        exec_args.append('!')
        exec_args.extend(args)

    return exec_args

def spawn_process(entry_point, args=(), **kwargs):
    if '.' in entry_point:
        raise ValueError("Application entry point must not include package "
            "name: %s" % entry_point)

    exec_args = sys.argv[:]

    # Currently, only monster_run and emi are launching applications for
    # Eggmonster, and both support the --spawn flag.
    #
    # fake-monster can now spawn a process, but it won't use the spawn
    # parameter.
    supported_cmds = ('monster_run', 'emi', 'fake-monster')
    if os.path.basename(exec_args[0]) not in supported_cmds:
        raise RuntimeError("executable is not in %s, it is %s" % (
            supported_cmds, exec_args[0]))

    # If we have a spawned app invoking another spawned app, remove the
    # --spawn part of the command.
    for i, arg in enumerate(exec_args):
        if arg.startswith('--spawn='):
            del exec_args[i]
            break

    # Prepare any command line parameters to be added.
    args = [str(x) for x in args]

    is_fake_monster = os.path.basename(exec_args[0]) == 'fake-monster'
    if is_fake_monster:
        exec_args = construct_fake_monster_command(entry_point, exec_args,
            args)
    else:
        exec_args = construct_monster_run_command(entry_point, exec_args,
            args)

    return subprocess.Popen(args=exec_args, **kwargs)

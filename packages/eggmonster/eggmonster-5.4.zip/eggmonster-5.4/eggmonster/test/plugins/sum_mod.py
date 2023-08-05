
def main(progname, argv):
    from eggmonster.spawn import spawn_process
    spawn_process('sum_subproc', argv)
    return

def subproc(progname, argv):
    from eggmonster import env
    import sys
    sys.stdout.write(str(env.base_number + int(argv[0])))
    sys.stdout.flush()

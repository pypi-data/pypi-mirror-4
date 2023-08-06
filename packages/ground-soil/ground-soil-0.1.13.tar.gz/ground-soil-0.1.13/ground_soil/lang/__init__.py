import shlex
import subprocess
import sys


def import_from_string(path):
    path_components = path.split('.')
    class_name = path_components[-1]
    package = '.'.join(path_components[:-1])
    return getattr(__import__(package, fromlist=[class_name]), class_name)


def exec_command(cmd, capture=False, quiet_run=False, abort_on_fail=True):
    if not quiet_run:
        print cmd

    try:
        p = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None
        )
    except OSError, e:
        if not quiet_run:
            print 'Command not found. OSError: %s' % e
        return -2

    try:
        stdout, stderr = p.communicate()
    except KeyboardInterrupt:
        return -1

    if abort_on_fail and p.returncode != 0:
        if stderr and len(stderr):
            print stderr
        print ''
        print 'Failed to run command'
        sys.exit(1)

    if capture:
        return stdout[:-1], stderr[:-1], p.returncode
    else:
        return p.returncode

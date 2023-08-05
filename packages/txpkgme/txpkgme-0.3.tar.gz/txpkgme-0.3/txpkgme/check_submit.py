import optparse
import os
import sys

from txpkgme.submitfromdisk import check_saved_output


def main():
    # Nagios plugin, so:
    #   Write to stdout
    #   One line only
    #   returncodes: 0 == OK, 1 == WARN, 2 == CRIT
    parser = optparse.OptionParser()
    parser.add_option('--last-run-grace', dest="last_run_grace",
            help="Maximum number of seconds since the last run")
    parser.add_option('--warn-duration', dest="warn_duration",
            help="Generate a warning if the last run took longer than this.")
    opts, args = parser.parse_args()
    if len(args) != 1:
        sys.stdout.write("You must specify filename that the check outputs too.\n")
        return 2
    if not opts.last_run_grace:
        sys.stdout.write("You must specify --last-run-grace.\n")
        return 2
    if not opts.warn_duration:
        sys.stdout.write("You must specify --warn-duration.\n")
        return 2
    last_run_grace = int(opts.last_run_grace)
    warn_duration = int(opts.warn_duration)
    filename = args[0]
    if not os.path.exists(filename):
        sys.stdout.write(
            "No such file or directory: %s, has submit-for-packaging ever run?"
            % (filename,))
        return 2
    with open(filename) as f:
        output = f.read()
    result, message = check_saved_output(
        output, last_run_grace, warn_duration, filename)
    sys.stdout.write(message + '\n')
    return result

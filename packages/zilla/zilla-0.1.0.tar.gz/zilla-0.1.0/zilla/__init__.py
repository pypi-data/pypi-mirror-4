import sys

from utils import usage, command_importer

import pkg_resources
__version__ = pkg_resources.require("zilla")[0].version

double_dash_commands = {
    "--help": "help",
    "--version": "version"
}

def run(args):
    if len(args) == 0:
        usage()
    else:
        subcmd = command_importer(double_dash_commands.get(args[0], args[0]))
        subcmd.run(args[1:])
        sys.exit(0)

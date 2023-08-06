"""
This is the pigeonhole Python module.
"""
import sys
from mrbob.cli import main as mrbob


def main(args=sys.argv[1:]):
    openfile = open(args[0], 'r')
    for line in openfile.readlines():
        args = line.split()
        mrbob(args = args)
    # XXX To be done: Render the templates to a complete dashboard
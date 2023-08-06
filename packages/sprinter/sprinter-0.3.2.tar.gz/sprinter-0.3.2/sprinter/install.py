"""
The install script for a sprinter-based setup script.
"""
import argparse
import logging
import os
import shutil
import signal
import sys
from sprinter.lib import get_recipe_class
from sprinter.environment import Environment

description = \
"""
Install an environment as specified in a sprinter config file
"""

parser = argparse.ArgumentParser(description=description)
parser.add_argument('command', metavar='C',
                    help="The operation that sprinter should run (install, deactivate, activate, switch)")
parser.add_argument('target', metavar='T', help="The path to the manifest file to install", nargs='?')
parser.add_argument('--namespace', dest='namespace', default=None,
                    help="Namespace to check environment against")
parser.add_argument('-v', dest='verbose', action='store_true', help="Make output verbose")

def signal_handler(signal, frame):
    print "Shutting down sprinter..."
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    args = parser.parse_args()
    command = args.command.lower()
    logging_level = logging.DEBUG if args.verbose else logging.INFO
    e = Environment(logging_level=logging_level)
    if command == "install":
        e.install(args.target, namespace=args.namespace)
    elif command == "update":
        e.update(args.target)
    elif command == "remove":
        e.remove(args.target)
    elif command == "deactivate":
        e.deactivate(args.target)
    elif command == "activate":
        e.activate(args.target)
    elif command == "reload":
        e.reload(args.target)
    elif command == "environments":
        SPRINTER_ROOT = os.path.expanduser(os.path.join("~", ".sprinter"))
        for env in os.listdir(SPRINTER_ROOT):
            print "%s" % env

if __name__ == '__main__':
    if len(sys.argv) > 0 and sys.argv[1] == 'doctest':
        import doctest
        doctest.testmod()
    else:
        main()

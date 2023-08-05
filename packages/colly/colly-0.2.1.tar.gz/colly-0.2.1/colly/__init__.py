__version__ = "0.2.1"

import os
import sys
import optparse
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

from colly.commands import command_dict, load_command, load_all_commands, command_names
from colly.optbase import parser

def main(initial_args=None):
    if initial_args is None:
        initial_args = sys.argv[1:]
    options, args = parser.parse_args(initial_args)
    if options.help and not args:
        args = ['help']
    if not args:
        parser.error("Please give a command, see 'colly help'.")
    command = args[0].lower()
    load_command(command)
    if command not in command_dict:
        parser.error("Oop don't know that one?")
    command = command_dict[command]
    return command.main(options, args[1:])

if __name__ == '__main__':
    exit = main()
    if exit:
        sys.exit(exit)

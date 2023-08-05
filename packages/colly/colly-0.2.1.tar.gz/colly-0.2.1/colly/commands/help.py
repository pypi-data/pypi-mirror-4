from colly.commands import (Command, command_dict, load_all_commands)
from colly.optbase import parser

class HelpCommand(Command):
    name = 'help'
    usage = '%prog'
    summary = 'Show available commands'

    def run(self, options, args):
        load_all_commands()
        parser.print_help() # general help, opts common to all commands
        print '\nCommands available:'
        commands = list(set(command_dict.values()))
        commands.sort(key=lambda x: x.name)
        for command in commands:
            print '  %s:  %s' % (command.name, command.summary)
        return 0

HelpCommand()

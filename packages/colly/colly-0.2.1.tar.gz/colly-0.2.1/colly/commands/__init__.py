import sys
from pkgutil import walk_packages
import logging
import optparse

from colly.optbase import parser
from colly.core import Collate
from colly.exceptions import CommandError

__all__ = ['command_dict', 'Command', 'load_command',
           'load_all_commands', 'command_names']

command_dict = {}

''' Base command
'''

class Command(object):
    name = None
    usage = None

    def __init__(self):
        assert self.name
        self.parser = optparse.OptionParser(
            usage=self.usage,
            prog='%s %s' % ("colly", self.name),
            version=parser.version)
        for option in parser.option_list:
            if not option.dest or option.dest == 'help':
                # -h, --version, etc
                continue
            self.parser.add_option(option)
        command_dict[self.name] = self

    def main(self, initial_options, args):
        options, args = self.parser.parse_args(args)
        self.run(options, args)


''' CSV base command
    --
    @ Parses common options to initialize colly's core(.py) object
'''

class CsvCommand(Command):
    usage = "%prog FILE(S) [OPTIONS]"
    objects = []

    def __init__(self):
        super(CsvCommand, self).__init__()
        
        self.parser.add_option('-H', '--headings', 
            dest='headings',
            action='callback',
            callback=split_callback,
            default=[],
            type='str',    
            help='Comma separated headings for CSV columns')
        
        self.parser.add_option('-i', '--index', 
            dest='index',
            action='callback',
            callback=split_callback,
            default=[],
            type='str',
            help='Define index column on CSV, shortcut to using -H pk,etc.')
        
        '''
        TODO:
        self.parser.add_option('-z', '--lazy',
            dest='lazy',
            action='store_true',
            help='Will make assumptions rather than throw errors')
        
        self.parser.add_option('-i', '--index',
            dest='pk',
            action='store',
            help='Column to set as the index (pk)')

        self.parser.add_option('-f', '--format',
            dest='format',
            action='store',
            help='Output format [default: JSON]')
        
        self.parser.add_option('-c', '--compress',
            dest='compress',
            action='store_true',
            help='Column to set as the index (pk)')
        '''

    def main(self, initial_options, args): #:! overwrites Command.main
        options, args = self.parser.parse_args(args)
        
        if options.headings and options.index:
            self.parser.error('Options HEADINGS and INDEX are mutually exclusive')
       
        n = 0
        for csv_file in args:
            kwargs = {}
            
            if options.headings:
                try:
                    kwargs['headings'] = options.headings[n]
                except IndexError:
                    pass
            elif options.index:
                 try:
                     kwargs['headings'] = [] # leave out index for now
                 except IndexError:
                     pass
            else:
                 pass
            
            self.objects.append(Collate(csv_file, **kwargs))
            n += 1
        
        self.run(options, args)
        
# Utils

def split_callback(option, opt, value, parser):
    ''' Callback, extra option parsing
    '''
    value_list = map(lambda v: v.split(','), value.split(':'))
    setattr(parser.values, option.dest, value_list)


def load_command(name):
    full_name = 'colly.commands.%s' % name
    if full_name in sys.modules:
        return
    try:
        __import__(full_name)
    except ImportError:
        pass

def load_all_commands():
    for name in command_names():
        load_command(name)

def command_names():
    names = set((pkg[1] for pkg in walk_packages(path=__path__)))
    return list(names)

import sys
import logging

from colly.commands import CsvCommand

class FormatCommand(CsvCommand):
    name = 'format'
    usage = "%prog FILE [OPTIONS]" #: overwrites baseparser
    summary = "Turn collated CSV file into JSON, or other format"
    
    def __init__(self):
        super(FormatCommand, self).__init__()
       
        ''' 
        self.parser.add_option('-f', '--format', 
            dest='format',
            action='callback',
            callback=headings_callback,
            default='json',
            type='str',    
            help='Convert to format (-f) from CSV.')
        '''
    
    def run(self, options, args):
        print self.objects[0].as_json()
        
FormatCommand()

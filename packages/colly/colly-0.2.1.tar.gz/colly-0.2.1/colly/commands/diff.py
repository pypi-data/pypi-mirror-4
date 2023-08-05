import sys
import logging

from colly.commands import CsvCommand
from colly.exceptions import CommandError

class DiffCommand(CsvCommand):
    name = 'diff'
    summary = "Compare two CSV files by index column (pk)"
    
    def __init__(self):
        super(DiffCommand, self).__init__()
       
        self.parser.add_option('-a', '--added',
            dest="method", # i.e. the set method to call
            action="store_const",
            const="added",
            help='Show rows in CSV 2 not in CSV 1.')
        
        self.parser.add_option('-e', '--erased',
            dest="method",
            action="store_const",
            const="erased",
            help='Show rows in CSV 1 not in CSV 2.')
        
        self.parser.add_option('-c', '--clean',
            dest="method",
            action="store_const",
            const="clean",
            help='Show rows in CSV 1 and in CSV 2.')
        
        self.parser.add_option('-A', '--all',
            dest="method",
            action="store_const",
            const="all",
            help='Show all rows in CSV 1 and CSV 2.')
    
    def run(self, options, args):
        A = self.objects[0]
        B = self.objects[1]

        if not options.method:
           self.parser.error('Use one of the options [aAce] make a comparison.')

        filtered = { 
            'added': B.column.difference(A.column),
            'erased': A.column.difference(B.column),
            'clean': A.column.intersection(B.column),
            'all' : A.column.union(B.column)
        }[options.method]

        if not ('pk' in A.headings or 'pk' in B.headings):
           logging.warning("pk should be set, for csv file A and B")
           raise CommandError("Please set 'pk' columns for both files")
        
        for row in filtered:
            try:
                print A.get_row(row)
            except KeyError:
                print B.get_row(row)
         
DiffCommand()

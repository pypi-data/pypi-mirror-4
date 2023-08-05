import sys
import logging

from colly.commands import CsvCommand
from colly.core import Collate

class DummyCommand(CsvCommand):
    name = 'dummy'
    summary = 'Does nothing (of import).'
    
    def run(self, options, args):
        logging.info(options)
        logging.info(args)
        print self.objects[0].as_json()

DummyCommand()

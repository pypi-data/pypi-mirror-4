import sys
import string
import logging
import csv
from collections import namedtuple

from colly.exceptions import CsvImportError

import simplejson as json

class Collate(object):
    
    _rows = {}
    headings = ""
    
    ''' Csv parsing and formatting.
    '''
    def __init__(self, csv_file, **options):
        with open(csv_file, "rb") as f:
            raw = csv.reader(f)
            
            ''' Determine given columns, check against CSV.
            '''
            first_row = raw.next() # discards first row
            if 'headings' in options:
                headings = options['headings']
                f.seek(0) # reset iter to first row ^
            else:
                headings = first_row
                logging.info('Interpretting headings as row #1')
#                if 'pk' in options:
#                    try:
#                        pk = int(options['pk'])
#                        headings[pk] = 'pk' #: denote primary key
#                    except ValueError:
#                        logging.warning('Ignoring pk, should be a number denoting the primary key column')
            
            cL = len(first_row) #: column length
            hL = len(headings)
            if hL != cL:
                if cL < hL: 
                    raise CsvImportError("Given headings exceeded those in CSV")
                else:
                    ''' Pad extra columns alphabeticaly
                        * fieldnames have to be unique, & not empty, or number.
                    '''
                    pad = list(string.uppercase[hL:cL]) #:FIX/ limited to 26 column CSV
                    headings += pad 
            
            self.headings = headings
            logging.info("CSV columns given headings: %s" % (headings))
            
            ''' OK, columns should be in order, ready to generate a map of the
                @csv_file.
            '''
            index, pk = {}, 0 #: set empty vars
            
            try:
                Head = namedtuple("row", ",".join(headings), verbose=False)
            except ValueError, err:
                raise CsvImportError(err)
            
            for row in map(Head._make, raw):
                ''' Perhaps not immediately obvious, index contains the full 
                    dataset. The "pk" (primary key) should be unique, or if 
                    not given it will be incremented.
                '''
                if hasattr(row, 'pk'):
                    index[row.pk] = row
                else:
                    pk += 1
                    index[pk] = row
        self.column = index #: saves to all to _rows, and the pk column as a set.
    
    ''' Make properties use validation & write-once only
    '''
    @property
    def column(self): return False
    
    @column.setter
    def column(self, v):
        if not self._rows:
            self._rows = v
    
    @column.getter
    def column(self): return set(self._rows) #: NB this will rtn the pk column

    ''' Utils
    '''
    def pad(self, headings):
        ''' Padding rows (e.g. csv headings), and all that.
        '''
        pass

    def get_row(self, pk):
        return self._rows[pk]

    ''' Rehashing/ formatting
    '''
    def as_json(self):
        m = {}
        for i in self.column:
            m[i] = self._rows[i]._asdict() #: turn _rows (namedtuple) into dict => dump.
        return json.dumps(m)

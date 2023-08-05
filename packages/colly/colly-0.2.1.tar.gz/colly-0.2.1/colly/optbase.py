import optparse
from colly import __version__

parser = optparse.OptionParser(
    usage='%prog COMMAND [OPTIONS]',
    version=__version__,
    add_help_option=False)

parser.add_option(
    '-h', '--help',
    dest='help',
    action='store_true',
    help='Show help')

parser.disable_interspersed_args()

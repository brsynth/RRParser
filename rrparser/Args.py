"""
Created on May 4 2020

@author: Joan Hérisson

"""

from argparse  import ArgumentParser
from os import path as os_path
from rrparser._version import __version__

__PACKAGE_FOLDER = os_path.dirname(
    os_path.realpath(__file__)
)
DEFAULT_RULES_DIR = __PACKAGE_FOLDER
DEFAULT_RULES_FILE = 'retrorules'

def build_args_parser():
    parser = ArgumentParser(prog='rrparser', description='Python wrapper to fetch RetroRules')
    parser = _add_arguments(parser)
    return parser


def _add_arguments(parser):

    ## Positional arguments
    #
    parser.add_argument(
        '--rules_file', # must be '_' otherwise it will be touchy in 'args' Namespace
        type=str,
        default=DEFAULT_RULES_FILE,
        help="rules file to parse. If set to 'retrorules', RetroRules are considered as input file, either locally or fetched over Internet."
    )

    ## Optional arguments
    #
    parser.add_argument('-o', '--outfile',
                        type=str,
                        help="file where results are written. If file ends with '.gz', it will be gzipped.")
    parser.add_argument('-if', '--input-format',
                        type=str,
                        choices=['csv', 'tsv'],
                        default='csv',
                        help='input file format (default: csv)')
    parser.add_argument('-rt', '--rule-type',
                        type=str,
                        choices=['all', 'retro', 'forward'],
                        default='all',
                        help="rule usage to filter from rules file")
    parser.add_argument('-d', '--diameters',
                        type=str,
                        default='2,4,6,8,10,12,14,16',
                        help='diameter of the sphere including the atoms around the reacting center (default is including all values: 2,4,6,8,10,12,14,16). The higher is the diameter, the more specific are the rules')
    parser.add_argument('-of', '--output-format',
                        type=str,
                        choices=['csv', 'tsv'],
                        default='csv',
                        help='output file format (default: csv)')
    # parser.add_argument('-c', '--compress',
    #                     action='store_true',
    #                     help='compress output file as a .gz archive')
    # parser.add_argument('--version', action='version',
    #                     version='%(prog)s {version}'.format(version=__version__))

    ## Program options
    #
    parser.add_argument('--log', metavar='ARG',
                        type=str, choices=['debug', 'info', 'warning', 'error', 'critical',
                                           'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='def_info',
                        help='Adds a console logger for the specified level (default: error)')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__),
                        help='show the version number and exit')
    parser.add_argument(
        '--rules-dir',
        default=__PACKAGE_FOLDER,
        help=('Path to the rules directory (default in package directory).')
    )

    return parser

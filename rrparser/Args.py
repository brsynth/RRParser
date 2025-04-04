"""
Created on May 4 2020

@author: Joan Hérisson

"""

from argparse import ArgumentParser
from os import path as os_path
from rrparser._version import __version__

__PACKAGE_FOLDER = os_path.dirname(
    os_path.realpath(__file__)
)
DEFAULT_RULES_DIR = __PACKAGE_FOLDER
DEFAULT_RULES_FILE = 'retrorules'


def build_args_parser():
    """
    Build the argument parser for the rrparser command line interface.

    Returns
    -------
    parser: ArgumentParser
        Argument parser for the rrparser command line interface.

    """
    parser = ArgumentParser(prog='rrparser', description='Python wrapper to fetch RetroRules')
    parser = _add_arguments(parser)
    return parser


def _add_arguments(parser):

    # Positional arguments
    parser.add_argument(
        '--rules_file',  # must be '_' otherwise it will be touchy in 'args' Namespace
        type=str,
        default=DEFAULT_RULES_FILE,
        help="rules file to parse. If set to 'retrorules'," \
            + " RetroRules are considered as input file, either locally or fetched over Internet."
    )

    # Optional arguments
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
                        help='diameter of the sphere including the atoms around " \
                            + "the reacting center (default is including all values: 2,4,6,8,10,12,14,16)." \
                            + " The higher is the diameter, the more specific are the rules')
    parser.add_argument('-of', '--output-format',
                        type=str,
                        choices=['csv', 'tsv'],
                        default='csv',
                        help='output file format (default: csv)')

    # Options --ecx and --ec are mutually exclusive
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-ecx', '--ecx',
                       type=str,
                       help='file containing EC numbers to filter out')
    group.add_argument('-ec', '--ec',
                       type=str,
                       help='file containing EC numbers to filter in')

    # Option to customize rules score with a dedicated file (CSV or TSV)
    # where each line is the rule name and its score
    parser.add_argument('-s', '--scores',
                        type=str,
                        help='CSV or TSV file containing rules names and scores')

    # Program options
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
        help='Path to the rules directory (default in package directory).'
    )

    return parser

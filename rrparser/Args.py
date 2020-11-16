"""
Created on May 4 2020

@author: Melchior du Lac, Joan Hérisson

"""

# import csv
# from tarfile import open as tf_open
# from tempfile import NamedTemporaryFile
# from shutil import copyfile
# from os import makedirs, remove
from argparse  import ArgumentParser

def build_args_parser():
    parser = ArgumentParser(prog='rrparser', description='Python wrapper to fetch RetroRules')
    parser = _add_arguments(parser)
    return parser

def _add_arguments(parser):
    parser.add_argument('rules_file',
                        type=str,
                        help="rules file to parse. If set to 'retrorules', RetroRules are considered as input file, either locally or fetched over Internet.")
    parser.add_argument('-o', '--outfile',
                        type=str,
                        help="file where results are written")
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
    parser.add_argument('-c', '--compress',
                        action='store_true',
                        help='compress output file as a tar.gz archive')
    # parser.add_argument('--version', action='version',
    #                     version='%(prog)s {version}'.format(version=__version__))
    return parser

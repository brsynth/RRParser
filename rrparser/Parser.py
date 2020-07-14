"""
Created on May 4 2020

@author: Melchior du Lac, Joan Hérisson

"""

import csv
from tarfile import open as tf_open
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile
from shutil import copyfile
from os import path as os_path
from os import makedirs
from os.path import dirname
from brs_utils import download_and_extract_gz
# from .infos import __version__, __readme__

def build_args_parser():
    parser = ArgumentParser('Python wrapper to fetch RetroRules')
    parser = _add_arguments(parser)
    return parser


class Parser:

    def __init__(self):
        self._retrorules_url = \
            'https://retrorules.org/dl/preparsed/rr02/rp2/hs'
        self._rules_path = ""


    def parse_rules(self,
                    rules_file='',
                    input_format='csv',
                    rule_type='all',
                    diameters='2,4,6,8,10,12,14,16',
                    outdir='./out',
                    outfile=None,
                    output_format='csv'):

        # Check args is here since the method is directly callable.

        orig_rules_file = rules_file
        # If rules_file is set, it takes precedence on rule_type
        if not rules_file:
            if rule_type:
                if rule_type not in ['all', 'retro', 'forward']:
                    raise ValueError('Cannot detect \'rule_type\' input: '+str(rule_type))
                if self._rules_path == "":
                    self._rules_path = NamedTemporaryFile().name+'/rules'
                rules_file = os_path.join(self._rules_path,
                                          'retrorules_rr02_rp2_hs',
                                          'retrorules_rr02_rp2_flat_'+rule_type+'.csv')
                if not os_path.exists(rules_file):
                    download_and_extract_gz(self._retrorules_url, self._rules_path)
            else:
                raise ValueError(
                        "at least one of --rules_file or --rule_type required")

        diameters_list = diameters.split(',')
        for d in diameters_list:
            if not d.isdigit():
                raise ValueError(
                        "--diameters takes only digit separated by comma")

        outfile_temp = NamedTemporaryFile().name
        try:
            if orig_rules_file == '':
                _parse_and_write(rules_file,
                                 list(map(int, diameters_list)),
                                 outfile_temp)
            else:
                if input_format == 'tsv':
                    _parseTSV_and_write(rules_file, rule_type,
                                        list(map(int, diameters_list)),
                                        outfile_temp)
                elif input_format == 'csv':
                    _parseCSV_and_write(rules_file, rule_type,
                                        list(map(int, diameters_list)),
                                        outfile_temp)
                else:
                    raise ValueError('Can only have input formats of TSV or CSV')
        except ValueError as e:
            raise ValueError(str(e))

        output_format = output_format.lower()
        if not outfile or outfile == '':
            outfile = os_path.basename(os_path.splitext(rules_file)[0]) + \
                      '_d' + '-'.join(diameters_list)
            outfile = _pkg_out(outfile_temp, outdir, outfile, output_format)
            return outdir+'/'+outfile
        else:
            if output_format == 'tar.gz':
                outfile_name = os_path.basename(os_path.splitext(rules_file)[0]) + \
                          '_d' + '-'.join(diameters_list)
                with tf_open(outfile, mode='w:gz') as tf:
                    tf.add(outfile_temp, outfile_name+'.csv')
            else:
                copyfile(outfile_temp, outfile)
            return outfile




def _pkg_out(file_res_name, outdir, outfile_name, output_format):
    makedirs(outdir, exist_ok=True)
    if output_format.lower() == 'tar.gz':
        with tf_open(outdir+'/'+outfile_name+'.tar.gz', mode='w:gz') as tf:
            tf.add(file_res_name, outfile_name+'.csv')
        outfile_name += '.tar.gz'
    else:
        outfile_name += '.csv'
        copyfile(file_res_name, outdir+'/'+outfile_name)
    return outfile_name


def _parse_and_write(infile, diameters, outfile):
    with open(infile, 'r') as rf:
        with open(outfile, 'w') as o:
            rf_csv = csv.reader(rf)
            o_csv = csv.writer(o, delimiter=',', quotechar='"')
            o_csv.writerow(next(rf_csv))
            for row in rf_csv:
                try:
                    if int(row[4]) in diameters:
                        o_csv.writerow(row)
                except ValueError:
                    raise ValueError(
                        'Cannot convert diameter to integer: '+str(row[4]))


def _parseTSV_and_write(infile, rule_type, diameters, outfile):
    with open(infile, 'r') as in_f:
        with open(outfile, 'w') as out_f:
            out_csv = csv.writer(out_f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            out_csv.writerow([
                "Rule ID",
                "Rule",
                "EC number",
                "Reaction order",
                "Diameter",
                "Score",
                "Legacy ID",
                "Reaction direction",
                "Rule relative direction",
                "Rule usage",
                "Score normalized"])
            for row in csv.DictReader(in_f, delimiter='\t'):
                try:
                    if int(row['Diameter']) in diameters:
                        if rule_type=='all' or (rule_type=='retro' and (row['Rule_usage']=='both' or row['Rule_usage']=='retro')) or (rule_type=='forward' and (row['Rule_usage']=='both' or row['Rule_usage']=='forward')):
                            out_csv.writerow([
                                row['# Rule_ID'],
                                row['Rule_SMARTS'],
                                row['Reaction_EC_number'],
                                row['Rule_order'],
                                row['Diameter'],
                                row['Score'],
                                row['Legacy_ID'],
                                row['Reaction_direction'],
                                row['Rule_relative_direction'],
                                row['Rule_usage'],
                                row['Score_normalized']])
                except ValueError:
                    raise ValueError(
                        'Cannot convert diameter to integer: '+str(row['Diameter']))

def _parseCSV_and_write(infile, rule_type, diameters, outfile):
    with open(infile, 'r') as rf:
        with open(outfile, 'w') as o:
            rf_csv = csv.reader(rf)
            o_csv = csv.writer(o, delimiter=',', quotechar='"')
            o_csv.writerow(next(rf_csv))
            for row in rf_csv:
                try:
                    if int(row[4]) in diameters:
                        if rule_type=='all' or (rule_type=='retro'   and (row[9]=='both' or row[9]=='retro')) or (rule_type=='forward' and (row[9]=='both' or row[9]=='forward')):
                            o_csv.writerow(row)
                except ValueError:
                    raise ValueError(
                        'Cannot convert diameter to integer: '+str(row[4]))



def _add_arguments(parser):
    parser.add_argument('-rf', '--rules-file',
                        type=str,
                        help="rules file to parse")
    parser.add_argument('-if', '--input-format',
                        type=str,
                        choices=['csv', 'tsv'],
                        default='csv',
                        help='input file format (default: csv)')
    parser.add_argument('-rt', '--rule-type',
                        type=str,
                        choices=['all', 'retro', 'forward'],
                        default='all',
                        help="rules file to parse")
    parser.add_argument('--outdir',
                        type=str,
                        default='./out',
                        help="folder where result file is written")
    parser.add_argument('--outfile',
                        type=str,
                        help="file where results are written")
    parser.add_argument('-d', '--diameters',
                        type=str,
                        default='2,4,6,8,10,12,14,16',
                        help='diameter of the sphere including the atoms around the reacting center (default is including all values: 2,4,6,8,10,12,14,16). The higher is the diameter, the more specific are the rules')
    parser.add_argument('-of', '--output-format',
                        type=str,
                        choices=['csv', 'tar.gz'],
                        default='csv',
                        help='output file format (default: csv)')
    # parser.add_argument('--version', action='version',
    #                     version='%(prog)s {version}'.format(version=__version__))
    return parser

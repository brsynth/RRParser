"""
Created on May 4 2020

@author: Joan Hérisson

"""

from os        import path as os_path
from brs_utils import download_and_extract_tar_gz
from pandas    import read_csv
from pandas.core.computation.ops import UndefinedVariableError
from csv       import QUOTE_ALL, QUOTE_NONE


RETRORULES_URL  = 'https://retrorules.org/dl/preparsed/rr02/rp2/hs'
RETRORULES_PATH = os_path.dirname(os_path.abspath( __file__ ))

def parse_rules(rules_file,
                outfile,
                input_format='csv',
                rule_type='all',
                diameters='2,4,6,8,10,12,14,16',
                output_format='csv'):
    """Parse a reaction rules file and extract sub-part according 'diameters' and 'rule_type' filters.

    Keyword arguments:
    rules_file -- reactions file (if not set RetroRules are considered)
    outfile -- filename where to write results (if not set results are returned as a string)
    input_format -- input format of rules_file ['csv', 'tsv'] (default 'csv')
    rule_type -- type of reaction rules ['all', 'forward', 'retro'] (default 'all')
    diameters -- diameters to filter [2,4,6,8,10,12,14,16] (default)
    output_format -- format of file results are written into
    """

    # Check args is here since the method is directly callable.
    diameters, sep, quoting = check_args(rule_type,
                                         diameters,
                                         input_format,
                                         output_format)

    # If 'rules_file' is set to RetroRules, then fetch RetroRules on Internet
    if rules_file == 'retrorules':
        rules_file = fetch_retrorules()

    # Read 'csv' as 'tsv' by specying separator
    rf = read_csv(rules_file, sep=sep)

    # Filter rules according to 'rule_type' and 'diameters'
    results = filter(rf, rule_type, diameters)

    return results.to_csv(outfile, index=False, sep=sep, quoting=quoting)


def filter(df, rule_type, diameters):
    """Filter a pandas dataframe with 'Diameters' and 'Rule usage' criteria.

    Keyword arguments:
    df -- pandas dataframe
    rule_type -- type of reaction rules ('all', 'forward', 'retro')
    diameters -- diameters to filter
    """
    query = 'Diameter == @diameters'
    if rule_type!='all':
        query += ' & `Rule usage` == @rule_usage_filter'
    rule_usage_filter = ['both', rule_type]
    try:
        return df.query(query)
    except UndefinedVariableError as e:
        raise KeyError(e)


def fetch_retrorules():
    """Fetch RetroRules over Internet if not already on disk.

    Keyword arguments:
    df -- pandas dataframe
    diameters -- diameters to filter
    """
    filename = 'retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_all.csv'
    rules_file = os_path.join(RETRORULES_PATH, filename)

    if not os_path.exists(rules_file):
        download_and_extract_tar_gz(RETRORULES_URL, RETRORULES_PATH, filename)
    return rules_file


def check_args(rule_type, diameters, input_format, output_format):

    # Rule type
    if not rule_type or rule_type not in ['all', 'retro', 'forward']:
        raise ValueError('Cannot detect \'rule_type\' input: '+str(rule_type))

    # Diameter
    diameters = diameters.split(',')
    for d in diameters:
        if not d.isdigit():
            raise ValueError(
                    "--diameters takes only digit separated by comma")

    # Input format
    if input_format == 'csv':
        sep = ','
    elif input_format == 'tsv':
        sep = '\t'
    else:
        raise ValueError('Can only have \'csv\' or \'tsv\' input formats')

    # Output format
    if output_format == 'csv':
        quoting = QUOTE_NONE
    elif output_format == 'tsv':
        quoting = QUOTE_ALL
    else:
        raise ValueError('Can only have \'csv\' or \'tsv\' input formats')



    return list(map(int, diameters)), sep, quoting

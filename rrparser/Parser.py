"""
Created on May 4 2020

@author: Joan Hérisson

"""

from os import (
    path as os_path
)
from brs_utils import (
    download_and_extract_tar_gz
)
from pandas import (
    read_csv,
    DataFrame
)
from pandas.core.computation.ops import (
    UndefinedVariableError
)
from csv import (
    QUOTE_ALL,
    QUOTE_NONE
)
from typing import (
    Dict,
    List,
    Tuple
)
from logging import (
    Logger,
    getLogger
)


RETRORULES_URL  = 'https://zenodo.org/record/5828017/files/retrorules_rr02_rp2_hs.tar.gz'
RETRORULES_PATH = os_path.dirname(os_path.abspath( __file__ ))


def parse_rules(
    rules_file:       str,
    outfile:          str,
    input_format:     str = 'csv',
    rule_type:        str = 'all',
    diameters:        str = '2,4,6,8,10,12,14,16',
    output_format:    str = 'csv',
    logger:        Logger = getLogger(__name__)
    ) -> None or str:
    """
    Parse a reaction rules file and extract sub-part according 'diameters' and 'rule_type' filters.

    Parameters
    ----------
    rules_file: str
        Reactions file (if not set RetroRules are considered)
    outfile: str
        Filename where to write results (if not set results are returned as a string)
    input_format: str
        Input format of rules_file ['csv', 'tsv'] (default 'csv')
    rule_type: str
        Type of reaction rules ['all', 'forward', 'retro'] (default 'all')
    diameters: str
        Diameters to filter [2,4,6,8,10,12,14,16] (default)
    output_format: str
        Format of file results are written into
    logger : Logger
        The logger object.

    Returns
    -------
    None or str If outfile is None, returns the resulting csv format as a string. Otherwise returns None..

    """

    # Check args is here since the method is directly callable.
    diameters, sep, quoting = check_args(
        rule_type,
        diameters,
        input_format,
        output_format
    )

    # If 'rules_file' is set to RetroRules, then fetch RetroRules on Internet
    if rules_file == 'retrorules':
        rules_file = fetch_retrorules()

    logger.debug('Reading values...')
    # Read 'csv' as 'tsv' by specying separator
    rf = read_csv(
        rules_file,
                    sep = sep,
        float_precision = 'round_trip'
    )

    # Filter rules according to 'rule_type' and 'diameters'
    results = filter(rf, rule_type, diameters)

    return results.to_csv(
        outfile,
          index = False,
            sep = sep,
        quoting = quoting
    )


def filter(
    df: DataFrame,
    rule_type: str,
    diameters: List[int],
    logger: Logger = getLogger(__name__)
    ) -> List[int]:
    """
    Filter a pandas dataframe with 'Diameters' and 'Rule usage' criteria.

    Parameters
    ----------
    df: DataFrame
        Pandas dataframe
    rule_type: str
        Type of reaction rules ['all', 'forward', 'retro']
    diameters: List[int]
        Diameters to filter
    logger : Logger
        The logger object.

    Returns
    -------
    query: Pandas dataframe
        Original dataframe filtered according to 'rule_type' and 'diameters'.
    """
    logger.debug(
        'Args: {df}, {rt}, {dia}'.format(
            df = df,
            rt = rule_type,
            dia = diameters
        )
    )
    query = 'Diameter == @diameters'
    if rule_type!='all':
        query += ' & `Rule usage` == @rule_usage_filter'
    rule_usage_filter = ['both', rule_type]
    try:
        return df.query(query)
    except UndefinedVariableError as e:
        raise KeyError(e)


def fetch_retrorules(
    logger: Logger = getLogger(__name__)
    ) -> str:
    """
    Fetch RetroRules over Internet if not already on disk.

    Parameters
    ----------
    logger : Logger
        The logger object.

    Returns
    -------
    filename: str
        Path to downoaded filename.
    """
    filename = 'retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_all.csv'
    rules_file = os_path.join(RETRORULES_PATH, filename)

    if not os_path.exists(rules_file):
        logger.info('Downloading retrorules file...')
        download_and_extract_tar_gz(
            RETRORULES_URL,
            RETRORULES_PATH,
            filename
        )

    return rules_file


def check_args(
    rule_type: str,
    diameters: str,
    input_format: str,
    output_format: str,
    logger: Logger = getLogger(__name__)
    ) -> Tuple[List[int], str, str]:
    """
    Check arguments are well-formed and format them.

    Parameters
    ----------
    rule_type: str
        Type of reaction rules ['all', 'forward', 'retro'] (default 'all')
    diameters: str
        Diameters to filter [2,4,6,8,10,12,14,16] (default)
    input_format: str
        Input format of rules_file ['csv', 'tsv'] (default 'csv')
    output_format: str
        Format of file results are written into
    logger : Logger
        The logger object.

    Returns
    -------
    diameters, sep, quoting: Tuple[List[int], str, str]
        diameters - diameters converted into list of int.
        sep - separation character detected from 'input_format'.
        quoting - quoting behavior detected from 'output_format'.
    """
    logger.debug(
        'Args: {rt}, {dia}, {i_f}, {o_f}'.format(
            rt = rule_type,
            dia = diameters,
            i_f = input_format,
            o_f = output_format
        )
    )

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

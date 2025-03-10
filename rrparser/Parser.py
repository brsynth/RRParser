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
from csv import (
    QUOTE_ALL,
    QUOTE_NONE
)
from typing import (
    List,
    Tuple,
    Literal
)
from logging import (
    Logger,
    getLogger
)

from .Args import (
    DEFAULT_RULES_FILE,
    DEFAULT_RULES_DIR
)


RETRORULES_URL = 'https://zenodo.org/record/5828017/files/retrorules_rr02_rp2_hs.tar.gz'


def read_ecx(
    ecx_file: str,
    logger: Logger = getLogger(__name__)
) -> List[str]:
    """
    Read EC numbers from a file.

    Parameters
    ----------
    ecx_file: str
        File containing EC numbers
    logger : Logger
        The logger object.

    Returns
    -------
    ecx: List[str]
        List of EC numbers.
    """
    logger.debug('Reading EC numbers from file...')
    with open(ecx_file, 'r') as f:
        ecx = f.read().split(',')
    return ecx


def parse_rules(
    outfile:          str,
    rules_file:       str = DEFAULT_RULES_FILE,
    rules_dir:        str = DEFAULT_RULES_DIR,
    input_format:     str = 'csv',
    rule_type:        str = 'all',
    diameters:        str = '2,4,6,8,10,12,14,16',
    ecx:    List[str] = [],
    output_format:    str = 'csv',
    logger:           Logger = getLogger(__name__)
) -> None or str:
    """
    Parse a reaction rules file and extract sub-part according 'diameters' and 'rule_type' filters.

    Parameters
    ----------
    rules_file: str
        Reactions file (if not set RetroRules are considered)
    rules_dir: str
        Directory where to store RetroRules (if not set RetroRules are stored in the current directory)
    outfile: str
        Filename where to write results (if not set results are returned as a string)
    input_format: str
        Input format of rules_file ['csv', 'tsv'] (default 'csv')
    rule_type: str
        Type of reaction rules ['all', 'forward', 'retro'] (default 'all')
    diameters: str
        Diameters to filter [2,4,6,8,10,12,14,16] (default)
    ecx: List[str]
        List of EC numbers to remove from rules
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
        rules_file = fetch_retrorules(rules_dir)

    logger.debug('Reading values...')
    # Read 'csv' as 'tsv' by specying separator
    rf = read_csv(
        rules_file,
        sep=sep,
        float_precision='round_trip'
    )

    # Filter rules according to 'rule_type' and 'diameters'
    results = filter_(rf, rule_type, diameters, ecx, logger=logger)

    logger.info('Writing results...')
    return results.to_csv(
        outfile,
        index=False,
        sep=sep,
        quoting=quoting
    )


def filter_(
    df: DataFrame,
    rule_type: str,
    diameters: List[int],
    ecx: List[str] = [],
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
    ecx: List[str]
        List of EC numbers to filter
    logger : Logger
        The logger object.

    Returns
    -------
    query: Pandas dataframe
        Original dataframe filtered according to 'rule_type' and 'diameters'.
    """
    logger.debug(
        'Args: {df}, {rt}, {dia}'.format(
            df=df,
            rt=rule_type,
            dia=diameters,
            ecx=ecx
        )
    )

    # Remove rules that contains EC numbers in 'ecx'
    if ecx:
        logger.info('Filtering out rules that contain at least one EC number starting by a pattern contained in: {ecx}'.format(ecx=ecx))
        # Consider EC numbers as list (separator: ';')
        ec_numbers = df['EC number'].apply(lambda x: x.split(';'))
        # Remove rules that contain at least one EC number that starts with one in 'ecx',
        # e.g. rule with EC numbers = ['1.1.1.1', '2.2.2.2'] will be removed if 'ecx' contains '1.1'
        rules_idx = []
        for i, ec in enumerate(ec_numbers):
            for _ecx in ecx:
                if any([ec.startswith(_ecx) for ec in ec]):
                    rules_idx.append(i)
                    logger.debug('Tagging rule {i} with EC numbers {ec} because \'{ecx}\' appear in the exclusion filter'.format(i=i, ec=ec, ecx=_ecx))
                    break
        logger.info('Removing {n} rules...'.format(n=len(rules_idx)))
        df = df.drop(rules_idx)

    query = 'Diameter == @diameters'
    if rule_type != 'all':
        query += ' & `Rule usage` == @rule_usage_filter'
    # Used in 'e' in case of exception raised
    rule_usage_filter = ['both', rule_type]
    try:
        return df.query(query)
    except Exception as e:
        raise KeyError(e)


def fetch_retrorules(
    rules_dir: str = DEFAULT_RULES_DIR,
    logger: Logger = getLogger(__name__)
) -> str:
    """
    Fetch RetroRules over Internet if not already on disk.

    Parameters
    ----------
    rules_dir: str
        Directory where to store RetroRules (if not set RetroRules are stored in the current directory)
    logger : Logger
        The logger object.

    Returns
    -------
    filename: str
        Path to downoaded filename.
    """
    filename = 'retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_all.csv'
    rules_file = os_path.join(rules_dir, filename)

    if not os_path.exists(rules_file):
        logger.info('Downloading retrorules file...')
        download_and_extract_tar_gz(
            RETRORULES_URL,
            rules_dir,
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
            rt=rule_type,
            dia=diameters,
            i_f=input_format,
            o_f=output_format
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

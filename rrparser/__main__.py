#!/usr/bin/env python

"""
rrparser command line interface.

"""
from rrparser import (
    build_args_parser,
    parse_rules,
    read_ecnumbers
)
from colorlog import ColoredFormatter
from logging import (
    Logger,
    getLogger,
    StreamHandler
)

from rrparser._version import __version__


def entry_point():
    """
    Entry point for the rrparser command line interface.
    
    """
    parser = build_args_parser()
    args  = parser.parse_args()

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.info(
        '\n{prog} {version}\n'.format(
            prog=logger.name,
            version=__version__
        )
    )
    logger.debug(args)

    # Read 'ecx' from file
    # EC numbers are separated by a comma
    ecx = []
    if args.ecx:
        ecx = read_ecnumbers(args.ecx, logger)
    ec = []
    if args.ec:
        ec = read_ecnumbers(args.ec, logger)

    try:
        results = parse_rules(
            rules_file=args.rules_file,
            rules_scores_file=args.rules_scores,
            rules_dir=args.rules_dir,
            outfile=args.outfile,
            input_format=args.input_format,
            rule_type=args.rule_type,
            diameters=args.diameters,
            ecx=ecx,
            ec=ec,
            output_format=args.output_format,
            logger=logger
        )

        # Print results if 'outfile' is empty
        if results:
            logger.info(results)

    except ValueError as e:
        logger.error(str(e))


def create_logger(
    name: str = __name__,
    log_level: str = 'def_info'
) -> Logger:
    """
    Create a logger with name and log_level.

    Parameters
    ----------
    name : str
        A string containing the name that the logger will print out

    log_level : str
        A string containing the verbosity of the logger

    Returns
    -------
    Logger
        The logger object.

    """    
    logger = getLogger(name)
    handler = StreamHandler()

    if log_level.startswith('def_'):
        log_format = '%(log_color)s%(message)s%(reset)s'
        log_level = log_level[4:]
    else:
        log_format = \
            '%(log_color)s%(levelname)-8s' \
            + ' | %(asctime)s.%(msecs)03d %(module)s' \
            + ' - %(funcName)s(): %(message)s%(reset)s'
 
    formatter = ColoredFormatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level.upper())

    return logger


if __name__ == '__main__':
    entry_point()

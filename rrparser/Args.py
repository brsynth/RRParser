# ruff: noqa: N999 -- Preserve the public rrparser.Args import path.
"""
Created on May 4 2020

@author: Joan Hérisson

"""

from argparse import ArgumentParser
from os import path as os_path
from re import fullmatch

from rrparser._version import __version__

DEFAULT_RULES_DIR = os_path.join(os_path.dirname(os_path.realpath(__file__)), "cache")
DEFAULT_RULES_FILE = "retrorules"
DEFAULT_RELEASE = "3.1.0"
DEFAULT_RADII = tuple(range(11))


def _parse_sizes(expression, maximum, step):
    values = set()
    for term in expression.split(","):
        term = term.strip()
        interval = fullmatch(r"(\d+)\s*-\s*(\d+)", term)
        comparison = fullmatch(r"([<>])(=?)\s*(\d+)", term)
        if term.isdigit():
            value = int(term)
            if value > maximum or value % step:
                raise ValueError(
                    f"Values must be multiples of {step} from 0 to {maximum}"
                )
            values.add(value)
        elif interval:
            lower, upper = map(int, interval.groups())
            if lower > upper:
                raise ValueError("Range must have its lower bound first")
            values.update(
                value
                for value in range(0, maximum + 1, step)
                if lower <= value <= upper
            )
        elif comparison:
            operator, inclusive, bound = comparison.groups()
            bound = int(bound)
            values.update(
                value
                for value in range(0, maximum + 1, step)
                if (value < bound if operator == "<" else value > bound)
                or (inclusive and value == bound)
            )
        else:
            raise ValueError("Use a list (0,2,4), range (0-8), <8, <=8, >8 or >=8")
    return sorted(values)


def parse_radii(expression):
    """Expand a radius expression into integer radii 0–10."""
    return _parse_sizes(expression, 10, 1)


def parse_diameters(expression):
    """Expand a diameter expression and convert it to integer radii."""
    return [diameter // 2 for diameter in _parse_sizes(expression, 20, 2)]


def build_args_parser():
    """
    Build the argument parser for the rrparser command line interface.

    Returns
    -------
    parser: ArgumentParser
        Argument parser for the rrparser command line interface.

    """
    parser = ArgumentParser(
        prog="rrparser", description="Python wrapper to fetch RetroRules"
    )
    parser = _add_arguments(parser)
    return parser


def _add_arguments(parser):

    # Positional arguments
    parser.add_argument(
        "--rules_file",  # must be '_' otherwise it will be touchy in 'args' Namespace
        type=str,
        default=DEFAULT_RULES_FILE,
        help="rules file to parse. If set to 'retrorules',"
        + " RetroRules are considered as input file, either locally or fetched over Internet.",
    )

    # Optional arguments
    parser.add_argument(
        "--list-releases",
        action="store_true",
        help="List releases and datasets available on retrorules.org, then exit",
    )
    parser.add_argument(
        "--release",
        default=DEFAULT_RELEASE,
        help="RetroRules version, latest or rr02 (default: 3.1.0)",
    )
    parser.add_argument(
        "--dataset",
        default="metanetx",
        help="Dataset names (metanetx,rhea or metanetx+rhea), or all (default: metanetx; see --list-releases)",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=str,
        help="file where results are written. If file ends with '.gz', it will be gzipped.",
    )
    parser.add_argument(
        "-if",
        "--input-format",
        type=str,
        choices=["csv", "tsv"],
        default="csv",
        help="input file format (default: csv)",
    )
    parser.add_argument(
        "-rt",
        "--rule-type",
        type=str,
        choices=["all", "retro", "forward"],
        default="all",
        help="rule usage to filter from rules file",
    )
    sizes = parser.add_mutually_exclusive_group()
    sizes.add_argument(
        "-d",
        "--diameters",
        type=parse_diameters,
        dest="radii",
        default=DEFAULT_RADII,
        help='Diameters: list (0,2,4), inclusive range (0-8), "<8", "<=8", ">8" or ">=8". '
        "Ranges and comparisons select even values from 0 to 20 (default: all). "
        "For templates, diameter = 2 * radius; rr02 provides diameters 2 to 16",
    )
    sizes.add_argument(
        "--radii",
        type=parse_radii,
        help='Radii: list (0,1,2), inclusive range (0-4), "<4", "<=4", ">4" or ">=4". '
        "Values range from 0 to 10 (default: all); mutually exclusive with --diameters.",
    )
    parser.add_argument(
        "-of",
        "--output-format",
        type=str,
        choices=["csv", "tsv"],
        default="csv",
        help="output file format (default: csv)",
    )

    # Options --ecx and --ec are mutually exclusive
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-ecx", "--ecx", type=str, help="file containing EC numbers to filter out"
    )
    group.add_argument(
        "-ec", "--ec", type=str, help="file containing EC numbers to filter in"
    )

    # Option to customize rules score with a dedicated file (CSV or TSV)
    # where each line is the rule name and its score
    parser.add_argument(
        "-s",
        "--scores",
        type=str,
        help="CSV or TSV file containing rules names and scores",
    )

    # Program options
    parser.add_argument(
        "--log",
        metavar="ARG",
        type=str,
        choices=[
            "debug",
            "info",
            "warning",
            "error",
            "critical",
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ],
        default="def_info",
        help="Adds a console logger for the specified level (default: error)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="show the version number and exit",
    )
    parser.add_argument(
        "--rules-dir",
        "--cache-dir",
        default=DEFAULT_RULES_DIR,
        help="Source archive cache (default: %(default)s). Extracted rules are written to --outfile.",
    )

    return parser

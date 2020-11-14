"""
Created on June 23 2020

@author: Joan Hérisson

"""


# from .infos import __version__
from rrparser.Parser import parse_rules, fetch_retrorules
from rrparser.Args   import build_args_parser

__all__ = ["parse_rules", "build_args_parser", "fetch_retrorules"]

"""
Created on June 23 2020

@author: Joan Hérisson

"""


# from .infos import __version__
from rrparser.Parser   import parse_rules
from rrparser.Args     import build_args_parser
from rrparser._version import __version__

__all__ = ["parse_rules", "build_args_parser"]

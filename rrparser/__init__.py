"""
Created on June 23 2020

@author: Joan Hérisson

"""


from os.path import dirname
from .Parser import Parser, build_args_parser

__all__ = ["Parser", "build_args_parser"]

with open(dirname(__file__) + '/../RELEASE.md', 'r') as f:
    __version__ = f.readline().split()[0]

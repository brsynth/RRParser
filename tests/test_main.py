"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from unittest import TestCase

# Specific for tool
from rrparser import __path__ as pkg_path


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR(TestCase):


    diameters   = ['2', '4', '6', '8', '10', '12', '14', '16']
    rules_file  = 'data/rules.csv'
    ref_d2_csv  = 'data/out_d2.csv'
    ref_d2_tsv  = 'data/out_d2.tsv'
    pkg_path    = pkg_path

"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from unittest import TestCase
from os import path as os_path
# Specific for tool
from rrparser import __path__ as pkg_path


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR(TestCase):


    diameters   = ['2', '4', '6', '8', '10', '12', '14', '16']
    data = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'data'
    )
    rules_file  = os_path.join(
        data,
        'rules.csv'
    )
    ref_d2_csv  = os_path.join(
        data,
        'out_d2.csv'
    )
    ref_d2_tsv  = os_path.join(
        data,
        'out_d2.tsv'
    )
    pkg_path    = pkg_path

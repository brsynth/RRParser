"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from unittest import TestCase

# Specific for tool
from sys import path as sys_path
from os  import path as os_path
from rrparser import Parser


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR(TestCase):

    def setUp(self):
        self.diameters = ['2', '4', '6', '8', '10', '12', '14', '16']
        self.rr_parser = Parser()
        self.hash_d2 = 'a6c2852a991e394bdbaf04791a90e803d4410a53f037165a7f08956edde63066'

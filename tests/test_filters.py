"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from test_main import Test_RR

# Specific for tool
from rrparser.Parser import filter_, read_ecnumbers

# Specific for tests themselves
from pandas import read_csv, DataFrame
from os import path



# Cette classe est un groupe de tests pour la fonction filter_. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR_Filters(Test_RR):

    def setUp(self):
        super().setUp()
        self.here = path.abspath(path.dirname(__file__))
        self.rules_file = path.join(self.here, 'data', 'rules.csv')
        self.df = read_csv(self.rules_file)

    def test_filter_by_rule_type(self):
        for rule_type in ['forward', 'retro', 'all']:
            with self.subTest(rule_type=rule_type):
                df_expected = read_csv(
                    path.join(self.here, 'data', f'rules_{rule_type}.csv')
                )
                df = filter_(
                    df=self.df,
                    rule_type=rule_type,
                    diameters=[2,4,6,8,10,12,14,16],
                    ecx=[]
                )
                # reindex df
                df = df.reset_index(drop=True)
                self.assertTrue(df.equals(df_expected))

    def test_filter_by_diameters(self):
        for diameters in [[2,4,6,8,10,12,14,16], [2]]:
            with self.subTest(diameters=diameters):
                df_expected = read_csv(
                    path.join(self.here, 'data', f'rules_d_{"-".join(str(x) for x in diameters)}.csv')
                )
                df = filter_(
                    df=self.df,
                    rule_type='all',
                    diameters=diameters,
                    ecx=[]
                )
                # reindex df
                df = df.reset_index(drop=True)
                self.assertTrue(df.equals(df_expected))
    
    def test_filter_by_ecx(self):
        ecx = read_ecnumbers(path.join(self.here, 'data', 'ec.csv'))
        df_expected = read_csv(
            path.join(self.here, 'data', 'rules_ecx.csv')
        )
        df = filter_(
            df=self.df,
            rule_type='all',
            diameters=[2,4,6,8,10,12,14,16],
            ecx=ecx
        )
        # reindex df
        df = df.reset_index(drop=True)
        self.assertTrue(df.equals(df_expected))

"""
Created on June 17 2020

@author: Joan Hérisson
"""

# Generic for test process
from test_main import Test_RR

# Specific for tool
from rrparser.Parser import replace_scores

# Specific for tests themselves
from pandas import read_csv, DataFrame
from os import path



# Cette classe est un groupe de tests pour la fonction filter_. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
# 'Test_' prefix is mandatory
class Test_RR_ScoreReplacing(Test_RR):

    def setUp(self):
        super().setUp()
        self.here = path.abspath(path.dirname(__file__))
        self.rules_file = path.join(self.here, 'data', 'rules_forward.csv')
        self.df = read_csv(self.rules_file)


    def test_score_replacing(self):
        # Read rules
        df = read_csv(self.rules_file)
        # Read rules scores
        rules_scores_file = path.join(self.here, 'data', 'scores.csv')
        df_scores = read_csv(rules_scores_file)
        # Replace scores
        df_replaced = replace_scores(
            results=df,
            scores=df_scores
        )
        # Read expected results
        df_expected = read_csv(
            path.join(self.here, 'data', 'rules_scores.csv')
        )
        # reindex df
        df_replaced = df_replaced.reset_index(drop=True)
        df_expected = df_expected.reset_index(drop=True)
        # Compare dataframes
        self.assertTrue(df_replaced.equals(df_expected))
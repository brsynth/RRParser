from test_main import Test_RR

from rrparser import parse_rules


class Test_RR_InputFormat(Test_RR):
    def test_BadInputFormatCSV_1(self):
        self.assertRaises(
            KeyError,
            parse_rules,
            None,
            rules_file=self.rules_file,
            input_format="tsv",
            diameters="2",
        )

    def test_BadInputFormatCSV_2(self):
        self.assertRaises(
            ValueError,
            parse_rules,
            None,
            rules_file=self.rules_file,
            input_format="other",
            diameters="2",
        )

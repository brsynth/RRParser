from test_main import Test_RR

from rrparser import parse_rules
from rrparser.Args import parse_diameters


class Test_RR_InputFormat(Test_RR):
    def test_BadInputFormatCSV_1(self):
        self.assertRaises(
            KeyError,
            parse_rules,
            None,
            rules_file=self.rules_file,
            input_format="tsv",
            radii=parse_diameters("2"),
        )

    def test_BadInputFormatCSV_2(self):
        self.assertRaises(
            ValueError,
            parse_rules,
            None,
            rules_file=self.rules_file,
            input_format="other",
            radii=parse_diameters("2"),
        )

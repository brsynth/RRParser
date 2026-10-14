from test_main import Test_RR

from rrparser.Args import parse_diameters
from rrparser.Parser import parse_rules


class Test_RR_RuleType(Test_RR):
    def test_BadRuleTypeArgument(self):
        for rule_type in ["test", "reto"]:
            with self.subTest(rule_type=rule_type):
                self.assertRaises(
                    ValueError,
                    parse_rules,
                    None,
                    rule_type=rule_type,
                    radii=parse_diameters("2"),
                )

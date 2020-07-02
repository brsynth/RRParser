from os import path, mkdir
from logging import error as logging_error

from rrparser import Parser, build_args_parser


def _cli():
    parser = build_args_parser()
    params = parser.parse_args()

    if not path.exists(params.output_folder):
        mkdir(params.output_folder)

    if not params.rules_file and not params.rule_type:
        parser.error("at least one of --rules_file or --rule_type required")
    if params.rules_file and params.rule_type:
        parser.error("at most one of --rules_file or --rule_type required")

    try:
        return Parser().parse_rules(outdir=params.output_folder,
                                    rules_file=params.rules_file,
                                    rule_type=params.rule_type,
                                    diameters=params.diameters,
                                    output_format=params.output_format)
    except ValueError as e:
        logging_error(str(e))


if __name__ == '__main__':
    _cli()

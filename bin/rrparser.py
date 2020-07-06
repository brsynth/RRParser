#!/usr/bin/env python

from os import path, mkdir
from logging import error as logging_error

from rrparser import Parser, build_args_parser


def _cli():
    parser = build_args_parser()
    params = parser.parse_args()

    try:
        return Parser().parse_rules(rules_file=params.rules_file,
                                    rule_type=params.rule_type,
                                    diameters=params.diameters,
                                    outdir=params.outdir,
                                    outfile=params.outfile,
                                    output_format=params.output_format)
    except ValueError as e:
        logging_error(str(e))


if __name__ == '__main__':
    _cli()

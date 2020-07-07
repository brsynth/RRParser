#!/usr/bin/env python

from os import path, mkdir
from logging import error as logging_error

from rrparser import Parser, build_args_parser


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

    try:
        return Parser().parse_rules(rules_file=args.rules_file,
                                    input_format=args.input_format,
                                    rule_type=args.rule_type,
                                    diameters=args.diameters,
                                    outdir=args.outdir,
                                    outfile=args.outfile,
                                    output_format=args.output_format)
    except ValueError as e:
        logging_error(str(e))


if __name__ == '__main__':
    _cli()

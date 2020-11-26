#!/usr/bin/env python

from logging   import error as logging_error
from rrparser  import build_args_parser, parse_rules
from tempfile  import gettempdir, NamedTemporaryFile
from os        import path as os_path
from shutil    import copyfile

def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

    try:
        results = parse_rules(rules_file=args.rules_file,
                              outfile=args.outfile,
                              input_format=args.input_format,
                              rule_type=args.rule_type,
                              diameters=args.diameters,
                              output_format=args.output_format)
        # Print results if 'outfile' is empty
        if results:
            print(results)
    except ValueError as e:
        logging_error(str(e))



if __name__ == '__main__':
    _cli()

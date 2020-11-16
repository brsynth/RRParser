#!/usr/bin/env python

from logging   import error as logging_error
from rrparser  import build_args_parser, parse_rules
from brs_utils import compress_tar_gz
from tempfile  import gettempdir
from os        import path as os_path

def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

    if args.compress: # Check if 'outfile' is required as a tar.gz archive
        outfile = os_path.join(gettempdir(), args.rules_file \
                                        +'-'+args.rule_type  \
                                        +'-'+args.diameters  \
                                        +'.'+args.output_format)
    else:
        outfile = args.outfile

    try:
        results = parse_rules(rules_file=args.rules_file,
                              outfile=outfile,
                              input_format=args.input_format,
                              rule_type=args.rule_type,
                              diameters=args.diameters,
                              output_format=args.output_format)
        # Print results if 'outfile' is empty
        if results:
            print(results)
        elif args.compress: # Check if 'outfile' is required as a tar.gz archive
            compress_tar_gz(path=outfile, outFile=args.outfile, delete=True)
    except ValueError as e:
        logging_error(str(e))



if __name__ == '__main__':
    _cli()

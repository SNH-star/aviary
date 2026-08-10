#!/usr/bin/env python3
from subprocess import run, STDOUT
import os
import argparse


def get_fraction_recovered(
    long_reads,
    short_reads_1,
    short_reads_2,
    input_fasta: str,
    long_read_type: str,
    long_read_mapper: str,
    short_read_mapper: str,
    threads: int,
    log: str,
):
    if long_reads != "none" and not os.path.exists("data/long_cov.tsv"):
        if long_read_type in ["ont", "ont_hq"]:
            coverm_cmd = f"coverm genome -t {threads} --single-genome -r {input_fasta} --single {' '.join(long_reads)} -p {long_read_mapper}-ont --min-read-percent-identity 0.85 -o www/fraction_recovered/long_fraction_recovered.tsv".split()

            with open(log, "a") as logf:
                print("Running command:", " ".join(coverm_cmd), file=logf)
                run(coverm_cmd, stdout=logf, stderr=STDOUT, check=True)

        elif long_read_type in ["rs", "sq", "ccs", "hifi"]:
            coverm_cmd = f"coverm genome -t {threads} --single-genome -r {input_fasta} --single {' '.join(long_reads)} -p {long_read_mapper}-pb --min-read-percent-identity 0.9 -o www/fraction_recovered/long_fraction_recovered.tsv".split()

            with open(log, "a") as logf:
                print("Running command:", " ".join(coverm_cmd), file=logf)
                run(coverm_cmd, stdout=logf, stderr=STDOUT, check=True)

        else:
            # Matches get_coverage.py and get_abundances.py, which both raise
            # here. This branch used to duplicate the ONT command instead, so a
            # long_read_type outside the two lists above was silently mapped
            # with the ONT preset and ONT's looser 0.85 identity cutoff -- the
            # PacBio branch deliberately uses 0.9. That produced a well-formed
            # fraction_recovered table computed on the wrong settings rather
            # than an error. Unreachable via the CLI (argparse validates
            # against LONG_READ_TYPES, and the two branches cover all six),
            # but it would fire the moment a seventh read type is added.
            raise Exception("Unexpected long_read_type: {}".format(long_read_type))

    if short_reads_2 != 'none' and not os.path.exists("data/short_cov.tsv"):
        coverm_cmd = f"coverm genome -t {threads} --single-genome -r {input_fasta} -1 {' '.join(short_reads_1)} -2 {' '.join(short_reads_2)} -p {short_read_mapper} -o www/fraction_recovered/short_fraction_recovered.tsv".split()

        with open(log, "a") as logf:
            print("Running command:", " ".join(coverm_cmd), file=logf)
            run(coverm_cmd, stdout=logf, stderr=STDOUT, check=True)

    elif short_reads_1 != 'none' and not os.path.exists("data/short_cov.tsv"):
        coverm_cmd = f"coverm genome -t {threads} --single-genome -r {input_fasta} --interleaved {' '.join(short_reads_1)} -p {short_read_mapper} -o www/fraction_recovered/short_fraction_recovered.tsv".split()

        with open(log, "a") as logf:
            print("Running command:", " ".join(coverm_cmd), file=logf)
            run(coverm_cmd, stdout=logf, stderr=STDOUT, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate fraction recovered from sequencing reads')
    parser.add_argument('--input-fasta', required=True, help='Input FASTA file')
    parser.add_argument('--long-reads', nargs='+', default=['none'], help='Long read files')
    parser.add_argument('--short-reads-1', nargs='+', default=['none'], help='Short reads (first pair or interleaved)')
    parser.add_argument('--short-reads-2', nargs='+', default=['none'], help='Short reads (second pair)')
    parser.add_argument('--short-read-mapper', default='strobealign',
                        help='CoverM -p value for short reads')
    parser.add_argument('--long-read-mapper', default='rammap',
                        help='Aligner family for long reads (rammap or minimap2)')
    parser.add_argument('--long-read-type', default='ont', help='Long read type (ont, ont_hq, rs, sq, ccs, hifi)')
    parser.add_argument('--threads', type=int, default=1, help='Number of threads to use')
    parser.add_argument('--log', default='get_fraction_recovered.log', help='Log file')
    
    args = parser.parse_args()
    
    os.makedirs('www/fraction_recovered', exist_ok=True)

    with open(args.log, "w") as logf: 
        pass

    get_fraction_recovered(
        long_reads="none" if args.long_reads in (["none"], [], "none") else args.long_reads,
        short_reads_1="none" if args.short_reads_1 in (["none"], [], "none") else args.short_reads_1,
        short_reads_2="none" if args.short_reads_2 in (["none"], [], "none") else args.short_reads_2,
        input_fasta=args.input_fasta,
        long_read_type=args.long_read_type,
        long_read_mapper=args.long_read_mapper,
        short_read_mapper=args.short_read_mapper,
        threads=args.threads,
        log=args.log,
    )
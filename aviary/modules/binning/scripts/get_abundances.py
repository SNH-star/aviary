#!/usr/bin/env python

import argparse
from subprocess import run, STDOUT
import os

# Long-read aligners coverm accepts. rammap is a minimap2-compatible Rust
# implementation and takes the same -x presets; --long-read-mapper selects
# which family is used.
LONG_READ_MAPPERS = ("minimap2-ont", "minimap2-pb", "rammap-ont", "rammap-pb")


def run_coverm(
    reads: str,
    minimap2_type: str,
    output_file: str,
    read_type: str,
    threads: int,
    strain_analysis: bool,
    output_dir: str,
    log: str,
    bins_dir: str,
    long_reads: bool = False,
):
    # CoverM >=0.7.0 defaults to strobealign, which is SHORT READ ONLY. Long
    # reads must therefore always name a minimap2 mapper explicitly -- omitting
    # -p would map them with strobealign, which returns a well-formed coverage
    # table of near-zero depths rather than failing, so the mistake would show
    # up as wrong abundances rather than an error.
    if long_reads and minimap2_type not in LONG_READ_MAPPERS:
        raise ValueError(
            "Long reads require an explicit long-read mapper "
            f"({' or '.join(LONG_READ_MAPPERS)}), got {minimap2_type!r}."
        )

    strain_analysis_flag = f"--bam-file-cache-directory {output_dir} --discard-unmapped" if strain_analysis else ""

    coverm_cmd = f"coverm genome -t {threads} {strain_analysis_flag} -d {bins_dir} -m relative_abundance covered_fraction {read_type} {reads} -p {minimap2_type} --output-file {output_file} --min-covered-fraction 0.0 -x fna".split()

    with open(log, "a") as logf:
        # Logged so the mapper actually used is recoverable from the run, the
        # same as get_coverage.py does.
        print("Running command:", " ".join(coverm_cmd), file=logf)
        # check=True because CoverM creates its --output-file before it fails:
        # a mid-run crash leaves a 0-byte abundance table behind, which
        # satisfies snakemake's missing-output check, so the rule is marked
        # successful and finalise_stats folds an empty table into bin_info.tsv.
        # Verified against coverm 0.8: exit 1, output file present, 0 bytes.
        run(coverm_cmd, stdout=logf, stderr=STDOUT, check=True)

def get_abundances(
    long_reads,
    short_reads_1,
    short_reads_2,
    long_read_type: str,
    long_read_mapper: str,
    short_read_mapper: str,
    threads: int,
    strain_analysis: bool,
    log: str,
    bins_dir: str,
):
    if long_reads != "none":
        if long_read_type in ["ont", "ont_hq"]:
            run_coverm(
                reads=" ".join(long_reads),
                minimap2_type=f"{long_read_mapper}-ont",
                long_reads=True,
                output_file="data/long_abundances.tsv",
                read_type="--single",
                threads=threads,
                strain_analysis=strain_analysis,
                output_dir="data/reads_mapped_to_mags/long/",
                log=log,
                bins_dir=bins_dir,
            )

        elif long_read_type in ["rs", "sq", "ccs", "hifi"]:
            run_coverm(
                reads=" ".join(long_reads),
                minimap2_type=f"{long_read_mapper}-pb",
                long_reads=True,
                output_file="data/long_abundances.tsv",
                read_type="--single",
                threads=threads,
                strain_analysis=strain_analysis,
                output_dir="data/reads_mapped_to_mags/long/",
                log=log,
                bins_dir=bins_dir,
            )

        else:
            raise Exception("Unexpected long_read_type: {}".format(long_read_type))

    if short_reads_2 != 'none':
        reads_str = []
        for r1, r2 in zip(short_reads_1, short_reads_2):
            reads_str.append(f"{r1} {r2}")
        reads_str = " ".join(reads_str)

        run_coverm(
            reads=reads_str,
            minimap2_type=short_read_mapper,
            output_file="data/short_abundances.tsv",
            read_type="--coupled",
            threads=threads,
            strain_analysis=strain_analysis,
            output_dir="data/reads_mapped_to_mags/short/",
            log=log,
            bins_dir=bins_dir,
        )

    elif short_reads_1 != 'none':
        run_coverm(
            reads=" ".join(short_reads_1),
            minimap2_type=short_read_mapper,
            output_file="data/short_abundances.tsv",
            read_type="--interleaved",
            threads=threads,
            strain_analysis=strain_analysis,
            output_dir="data/reads_mapped_to_mags/short/",
            log=log,
            bins_dir=bins_dir,
        )

    # Concatenate the two coverage files if both long and short exist
    if long_reads != "none" and short_reads_1 != "none":
        with open('data/coverm_abundances.tsv', 'w') as file3:
            with open('data/short_abundances.tsv', 'r') as file1:
                with open('data/long_abundances.tsv', 'r') as file2:
                    for line1, line2 in zip(file1, file2):
                        long_cov_line = "\t".join([l.strip() for l in line2.strip().split('\t')[1::]])
                        print(line1.strip(), "\t", long_cov_line, file=file3)
    elif long_reads != "none":  # rename long reads cov if only it exists
        os.rename("data/long_abundances.tsv", "data/coverm_abundances.tsv")
    elif short_reads_1 != "none":  # rename short reads cov if only they exist
        os.rename("data/short_abundances.tsv", "data/coverm_abundances.tsv")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get abundances using CoverM.")
    parser.add_argument("--long-reads", nargs="+", default="none", help="Paths to long reads files.")
    parser.add_argument("--short-reads-1", nargs="+", default="none", help="Paths to first set of short reads files.")
    parser.add_argument("--short-reads-2", nargs="+", default="none", help="Paths to second set of short reads files.")
    parser.add_argument("--short-read-mapper", type=str, default="strobealign",
                        help="CoverM -p value for short reads.")
    parser.add_argument("--long-read-mapper", type=str, default="rammap",
                        help="Aligner family for long reads (rammap or minimap2).")
    parser.add_argument("--long-read-type", type=str, required=True, help="Type of long reads (e.g., ont, rs, etc.).")
    parser.add_argument("--threads", type=int, required=True, help="Number of threads to use.")
    parser.add_argument("--strain-analysis", type=lambda x: x.lower() == 'true', nargs='?', const=True, default=False, help="Enable strain analysis (True/False).")
    parser.add_argument("--log", type=str, required=True, help="Path to log file.")
    parser.add_argument("--bins-dir", type=str, required=True, help="Directory containing bins to quantify.")

    args = parser.parse_args()

    with open(args.log, "w") as logf:
        pass

    get_abundances(
        long_reads="none" if args.long_reads == ["none"] or args.long_reads == [] else args.long_reads,
        short_reads_1="none" if args.short_reads_1 == ["none"] or args.short_reads_1 == [] else args.short_reads_1,
        short_reads_2="none" if args.short_reads_2 == ["none"] or args.short_reads_2 == [] else args.short_reads_2,
        long_read_type=args.long_read_type,
        long_read_mapper=args.long_read_mapper,
        short_read_mapper=args.short_read_mapper,
        threads=args.threads,
        strain_analysis=args.strain_analysis,
        log=args.log,
        bins_dir=args.bins_dir,
    )

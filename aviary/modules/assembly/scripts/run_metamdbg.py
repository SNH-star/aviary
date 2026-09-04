#!/usr/bin/env python3

import argparse
import gzip
import os
import re
import shutil
import subprocess
from pathlib import Path

from Bio import SeqIO


# Match Flye's assembly_info.txt header so downstream parsing remains consistent
HEADER = "#seq_name\tlength\tcov.\tcirc.\trepeat\tmult.\talt_group\tgraph_path\n"
DEFAULT_FIELDS = {
    "cov": 0.0,
    "circ": "N",
    "repeat": "N",
    "mult": "1",
    "alt_group": "NA",
    "graph_path": "NA",
}


def parse_metadata(description: str) -> dict:
    metadata = DEFAULT_FIELDS.copy()
    coverage = re.search(r"coverage=([\d.]+)", description)
    if not coverage:
        raise ValueError(f"Missing coverage metadata in contig header: {description}")
    metadata["cov"] = float(coverage.group(1))

    circularity = re.search(r"circular=(yes|no)", description)
    if not circularity:
        raise ValueError(f"Missing circularity metadata in contig header: {description}")
    metadata["circ"] = "Y" if circularity.group(1) == "yes" else "N"

    return metadata


def write_assembly_info(fasta_path: str, info_path: str) -> None:
    Path(info_path).parent.mkdir(parents=True, exist_ok=True)
    with open(info_path, "w") as info_handle:
        info_handle.write(HEADER)
        for record in SeqIO.parse(fasta_path, "fasta"):
            metadata = parse_metadata(record.description)
            info_handle.write(
                f"{record.id}\t{len(record.seq)}\t{metadata['cov']}\t{metadata['circ']}\t"
                f"{metadata['repeat']}\t{metadata['mult']}\t{metadata['alt_group']}\t"
                f"{metadata['graph_path']}\n"
            )


def ensure_placeholder(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).touch()


def select_read_flag(long_read_type: str) -> str:
    # metaMDBG supports HiFi/CCS and modern (lr:hq-tier) ONT reads. Aviary's
    # own --longread-type ont is already the modern chemistry v14 preset (see
    # aviary.py's -z/--longread-type help text), so it maps to --in-ont same
    # as ont_hq. Only PacBio CLR-style rs/sq (not Nanopore at all) is
    # genuinely unsupported by metaMDBG.
    read_type = (long_read_type or "").lower()
    if read_type in {"hifi", "ccs"}:
        return "--in-hifi"
    if read_type in {"ont", "ont_hq"}:
        return "--in-ont"
    raise ValueError(
        f"metaMDBG does not support long_read_type={long_read_type!r}; "
        "use --longread-type hifi/ccs/ont/ont_hq, or choose --long-read-assembler "
        "myloasm or flye for this read type"
    )


def run_metamdbg(input_fastq: str, output_dir: str, long_read_type: str, threads: int, log: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    read_flag = select_read_flag(long_read_type)

    contigs_gz = os.path.join(output_dir, "contigs.fasta.gz")
    assembly_fasta = os.path.join(output_dir, "assembly.fasta")
    assembly_graph = os.path.join(output_dir, "assembly_graph.gfa")
    assembly_info = os.path.join(output_dir, "assembly_info.txt")

    allow_empty = False
    cmd = [
        "metaMDBG",
        "asm",
        "--out-dir",
        output_dir,
        read_flag,
        input_fastq,
        "--threads",
        str(threads),
    ]

    with open(log, "w") as logf:
        try:
            subprocess.run(cmd, check=True, stdout=logf, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            if not os.path.exists(contigs_gz) or os.path.getsize(contigs_gz) == 0:
                allow_empty = True
            else:
                raise

        # Check unconditionally, regardless of the asm subprocess's exit code:
        # metaMDBG can exit 0 while still failing to produce contigs (e.g. very
        # low-coverage or degenerate input), just like myloasm can.
        if not allow_empty and (not os.path.exists(contigs_gz) or os.path.getsize(contigs_gz) == 0):
            allow_empty = True

        if allow_empty:
            logf.write(
                "metaMDBG produced no contigs; continuing with empty assembly outputs.\n"
            )
            ensure_placeholder(assembly_fasta)
            ensure_placeholder(assembly_graph)
        else:
            with gzip.open(contigs_gz, "rb") as gz_in, open(assembly_fasta, "wb") as fasta_out:
                shutil.copyfileobj(gz_in, fasta_out)

            gfa_probe = subprocess.run(
                ["metaMDBG", "gfa", "--assembly-dir", output_dir, "--k", "0"],
                capture_output=True,
                text=True,
            )
            gfa_probe_output = gfa_probe.stdout + gfa_probe.stderr
            if gfa_probe.returncode != 0 or gfa_probe.stderr:
                logf.write(
                    f"metaMDBG gfa --k 0 probe (rc={gfa_probe.returncode}):\n"
                    f"{gfa_probe_output}\n"
                )
            # metaMDBG prints the "Available k value" listing to stderr, not
            # stdout, confirmed by direct execution against a real assembly.
            k_values = [int(match) for match in re.findall(r"-\s+(\d+)\s+\(", gfa_probe_output)]

            if not k_values:
                logf.write(
                    "metaMDBG reported no available k values for graph generation; "
                    "continuing with an empty assembly graph.\n"
                )
                ensure_placeholder(assembly_graph)
            else:
                max_k = max(k_values)
                subprocess.run(
                    ["metaMDBG", "gfa", "--assembly-dir", output_dir, "--k", str(max_k)],
                    check=True,
                    stdout=logf,
                    stderr=subprocess.STDOUT,
                )
                assembly_graph_src = os.path.join(output_dir, f"assemblyGraph_k{max_k}.gfa")
                if os.path.exists(assembly_graph_src):
                    shutil.copyfile(assembly_graph_src, assembly_graph)
                else:
                    ensure_placeholder(assembly_graph)

    if not os.path.exists(assembly_info):
        write_assembly_info(assembly_fasta, assembly_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run metaMDBG assembler")
    parser.add_argument("--input-fastq", required=True, help="Input long read FASTQ")
    parser.add_argument("--output-dir", default="data/metamdbg", help="Output directory")
    parser.add_argument("--long-read-type", default="ont", help="Long read technology")
    parser.add_argument("--threads", type=int, default=8, help="Number of threads")
    parser.add_argument("--log", required=True, help="Log file")

    args = parser.parse_args()

    run_metamdbg(
        input_fastq=args.input_fastq,
        output_dir=args.output_dir,
        long_read_type=args.long_read_type,
        threads=args.threads,
        log=args.log,
    )

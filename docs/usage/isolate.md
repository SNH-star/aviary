---
title: aviary isolate
---

# aviary isolate

Step-down hybrid assembly for isolated pure culture sequencing results. For use with isolate (not metagenomic) sequencing data.

```
aviary isolate -1 reads_1.fq.gz -2 reads_2.fq.gz --longreads reads.fastq.gz --long_read_type ont
```

> This subcommand also accepts `--dry-run`, `--clean`, `--strict`, `--request-gpu`, `--build`, `--build-gpu`, `--download`, `--rerun-triggers`, `--default-resources`, `--snakemake-profile`, `--snakemake-cmds`, `--cluster-retries`, `--local-cores`, and `--workflow`, which are shared across every aviary subcommand — see [Centralised commands](centralised_commands.md).

## Input options (short reads)

Long reads (below) are required — isolate assembly is Flye-based and has no short-read-only
path. Short reads are optional and, when given, are used for one additional Pilon/racon
polishing round on top of the long-read assembly.

**`-1`**, **`--pe-1`** FILE [FILE ...]

  Forward short read files.

**`-2`**, **`--pe-2`** FILE [FILE ...]

  Reverse short read files.

**`-i`**, **`--interleaved`** FILE [FILE ...]

  Interleaved read files.

**`-c`**, **`--coupled`** FILE [FILE ...]

  Forward and reverse read files in a coupled space-separated list.

## Input options (long reads)

**`-l`**, **`--longreads`** FILE [FILE ...]

  Long-read files.

**`-z`**, **`--longread-type`** TYPE

  Sequencing platform: `rs`, `sq`, `ccs`, `hifi`, `ont`, `ont_hq`. [default: ont]

**`--medaka-model`** MODEL

  Medaka model for polishing. [default: r941_min_hac_g507]

## Isolate options

**`--genome-size`** INT

  Approximate size of the isolate genome in base pairs. [default: 5000000]

## Performance options

**`-t`**, **`--max-threads`** INT

  Maximum threads per process. [default: 8]

**`-n`**, **`--n-cores`** INT

  Maximum cores available. [default: 16]

**`-m`**, **`--max-memory`** INT

  Maximum memory in gigabytes. [default: 250]

## Output options

**`-o`**, **`--output`** DIR

  Output directory. [default: ./]

## Examples

### Long-read only

The minimum viable input — Flye assembly, racon and medaka polishing, then dnaapler
reorientation. No illumina polishing round runs, since no short reads are given:
```
aviary isolate --longreads reads.fastq.gz --long-read-type ont
```

### Hybrid: long reads + short reads for polishing

The typical case for a bacterial isolate closed with ONT and cleaned up with Illumina — adds one
extra Pilon/racon polishing round using the short reads on top of the long-read assembly:
```
aviary isolate -1 reads_1.fq.gz -2 reads_2.fq.gz --longreads reads.fastq.gz --long-read-type ont
```

Short reads accept the same input shapes as the other subcommands:
```
aviary isolate -i sample_interleaved.fq.gz --longreads reads.fastq.gz --long-read-type ont
aviary isolate -c sample_1.fq.gz sample_2.fq.gz --longreads reads.fastq.gz --long-read-type ont
```

`aviary isolate` has no `--long-read-assembler`/`--use-megahit`/`--use-unicycler` flags — unlike
`assemble`/`recover`/`complete`, the isolate assembly path is fixed to Flye rather than
user-selectable, since it targets a single pure-culture genome rather than a mixed community.

### Sizing the assembly

Set `--genome-size` to roughly the expected isolate genome size (bacterial genomes are typically
2–10 Mbp); it tunes Flye's assembly parameters and is unrelated to `--min-bin-size`, which
doesn't apply here since isolate assembly produces one genome rather than binning a community:
```
aviary isolate --longreads reads.fastq.gz --long-read-type ont --genome-size 4500000
```

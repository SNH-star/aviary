---
title: Input reference
---

# Input reference

## Short reads

Aviary accepts paired reads as separate forward and reverse lists (`-1` and
`-2`), interleaved reads (`--interleaved`), or a coupled list (`--coupled`).

```text
reads/
├── sample_A_R1.fastq.gz
├── sample_A_R2.fastq.gz
├── sample_B_R1.fastq.gz
└── sample_B_R2.fastq.gz
```

When supplying lists to `-1` and `-2`, keep samples in the same order. FASTQ
files may be gzip-compressed. With multiple files, assembly behaviour depends
on `--coassemble`; all supplied reads may still contribute differential
coverage during genome recovery.

## Long reads

Supply one or more files with `--longreads`. `--long-read-type` accepts:

| Value | Sequencing data |
| --- | --- |
| `ont` | Oxford Nanopore reads |
| `ont_hq` | high-quality/Q20 Oxford Nanopore reads |
| `rs` | PacBio RS II reads |
| `sq` | PacBio Sequel reads |
| `ccs` | PacBio CCS reads |
| `hifi` | PacBio HiFi reads |

The default is `ont`. This selection affects parameters passed to upstream
tools, so set it to the actual sequencing technology.

## Assemblies

`--assembly` accepts FASTA files containing scaffolded metagenome contigs.
`recover` uses the supplied reads to calculate coverage. SemiBin2 multi-sample
mode accepts multiple assemblies and requires `--semibin-mode multi`.

## Genome collections

`annotate` reads FASTA files from `--genome-fasta-directory`. Use
`--fasta-extension` when files do not use the default `fna` extension.

## Previous Aviary runs

`cluster --input-runs` expects completed Aviary output directories containing
the final-bin collection and bin summary needed for dereplication.

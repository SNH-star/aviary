---
title: Aviary
---

# Aviary

Aviary assembles metagenomes, recovers metagenome-assembled genomes (MAGs),
and coordinates their taxonomic and functional annotation. Short-read,
long-read and hybrid analyses run through one reproducible Snakemake
workflow, locally or across an HPC cluster.

[Install Aviary](installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[Read the PDF manual](https://snh-star.github.io/aviary/pdf/aviary-manual.pdf){ .md-button }

## A complete analysis in one command

```bash
aviary complete \
  -1 sample_R1.fastq.gz \
  -2 sample_R2.fastq.gz \
  --output sample_aviary \
  --max-threads 8 \
  --n-cores 8
```

See the [first complete analysis](getting-started/first-analysis.md) walkthrough
for what each stage does and where its outputs land.

## Find what you need

- [Guide](guide/README.md) — how reads become assemblies, candidate genomes and
  annotated MAGs.
- [Worked analyses](examples.md) — end-to-end examples with real commands.
- [CLI reference](usage/README.md) — every command, option, default and output.
- [Troubleshooting](faqs.md) — validation messages, failed rules, resource limits.

## The commands

| Command | Does |
|---|---|
| [`assemble`](usage/assemble.md) | Reads → contigs |
| [`recover`](usage/recover.md) | Assembly → MAGs |
| [`annotate`](usage/annotate.md) | MAGs → annotations |
| [`complete`](usage/complete.md) | Reads → annotated MAGs, end to end |
| [`cluster`](usage/cluster.md) | Dereplicate genomes across samples |
| [`isolate`](usage/isolate.md) | Assemble and annotate a single isolate genome |

Using Aviary in research? See the [citation guide](citations.md) for Aviary
and its upstream tools. Aviary is released under GPL-3.0.

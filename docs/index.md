---
title: Aviary
---

<div class="aviary-hero" markdown>
<span class="aviary-hero__eyebrow">Metagenomics · Snakemake workflow</span>

# Aviary

Aviary assembles metagenomes, recovers metagenome-assembled genomes (MAGs),
and coordinates their taxonomic and functional annotation. Short-read,
long-read and hybrid analyses run through one reproducible Snakemake
workflow, locally or across an HPC cluster.

[Install Aviary](installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[Read the PDF manual](https://snh-star.github.io/aviary/pdf/aviary-manual.pdf){ .md-button }
</div>

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

<div class="grid cards" markdown>

- :material-compass-outline:{ .lg .middle } **[Guide](guide/README.md)**

    ---

    How reads become assemblies, candidate genomes and annotated MAGs.

- :material-book-open-page-variant-outline:{ .lg .middle } **[Worked analyses](examples.md)**

    ---

    End-to-end examples with real commands.

- :material-console:{ .lg .middle } **[CLI reference](usage/README.md)**

    ---

    Every command, option, default and output.

- :material-lifebuoy:{ .lg .middle } **[Troubleshooting](faqs.md)**

    ---

    Validation messages, failed rules, resource limits.

</div>

## The commands

<div class="grid cards" markdown>

- :material-dna:{ .lg .middle } **[`assemble`](usage/assemble.md)**

    ---

    Reads → contigs

- :material-layers-outline:{ .lg .middle } **[`recover`](usage/recover.md)**

    ---

    Assembly → MAGs

- :material-tag-text-outline:{ .lg .middle } **[`annotate`](usage/annotate.md)**

    ---

    MAGs → annotations

- :material-rocket-launch-outline:{ .lg .middle } **[`complete`](usage/complete.md)**

    ---

    Reads → annotated MAGs, end to end

- :material-account-group-outline:{ .lg .middle } **[`cluster`](usage/cluster.md)**

    ---

    Dereplicate genomes across samples

- :material-flask-outline:{ .lg .middle } **[`isolate`](usage/isolate.md)**

    ---

    Assemble and annotate a single isolate genome

</div>

Using Aviary in research? See the [citation guide](citations.md) for Aviary
and its upstream tools. Aviary is released under GPL-3.0.

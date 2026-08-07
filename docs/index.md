---
title: Aviary
---

<div class="aviary-hero" markdown>
  <svg class="aviary-hero__motif" viewBox="0 0 900 460" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <path d="M -40 380 C 160 380, 220 300, 340 260 C 460 220, 520 140, 700 90" />
    <path d="M -40 420 C 200 430, 280 360, 420 320 C 560 280, 620 200, 820 150" />
    <path d="M 340 260 C 380 200, 440 190, 480 130" />
    <path d="M 420 320 C 470 300, 500 250, 560 220" />
    <circle cx="700" cy="90" r="5"></circle>
    <circle cx="820" cy="150" r="5"></circle>
    <circle cx="480" cy="130" r="4"></circle>
    <circle cx="560" cy="220" r="4"></circle>
    <circle cx="340" cy="260" r="4"></circle>
    <circle cx="420" cy="320" r="4"></circle>
  </svg>

<div class="aviary-hero__inner" markdown>
<div markdown>
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

<div class="aviary-terminal aviary-reveal">
<div class="aviary-terminal__bar"><span></span><span></span><span></span></div>
<pre class="aviary-terminal__body"><span class="aviary-terminal__prompt">$</span><code class="aviary-terminal__type" data-commands="aviary complete, aviary assemble, aviary recover, aviary annotate, aviary cluster, aviary isolate">aviary complete</code></pre>
</div>
</div>
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

## The commands

<div class="aviary-bento">

<a class="aviary-bento__item aviary-bento__item--feature aviary-reveal" href="usage/complete.md">
  <span class="aviary-bento__icon">🚀</span>
  <div><strong><code>complete</code></strong></div>
  <span class="aviary-bento__desc">Reads → annotated MAGs, end to end. One command for the whole pipeline.</span>
</a>

<a class="aviary-bento__item aviary-reveal" href="usage/assemble.md">
  <span class="aviary-bento__icon">🧬</span>
  <div><strong><code>assemble</code></strong></div>
  <span class="aviary-bento__desc">Reads → contigs</span>
</a>

<a class="aviary-bento__item aviary-reveal" href="usage/recover.md">
  <span class="aviary-bento__icon">🧩</span>
  <div><strong><code>recover</code></strong></div>
  <span class="aviary-bento__desc">Assembly → MAGs</span>
</a>

<a class="aviary-bento__item aviary-reveal" href="usage/annotate.md">
  <span class="aviary-bento__icon">🏷️</span>
  <div><strong><code>annotate</code></strong></div>
  <span class="aviary-bento__desc">MAGs → annotations</span>
</a>

<a class="aviary-bento__item aviary-reveal" href="usage/cluster.md">
  <span class="aviary-bento__icon">👥</span>
  <div><strong><code>cluster</code></strong></div>
  <span class="aviary-bento__desc">Dereplicate genomes across samples</span>
</a>

<a class="aviary-bento__item aviary-reveal" href="usage/isolate.md">
  <span class="aviary-bento__icon">🧪</span>
  <div><strong><code>isolate</code></strong></div>
  <span class="aviary-bento__desc">Assemble and annotate a single isolate genome</span>
</a>

</div>

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

Using Aviary in research? See the [citation guide](citations.md) for Aviary
and its upstream tools. Aviary is released under GPL-3.0.

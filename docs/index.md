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

Scroll — each command in turn, what it does and where to read more.

<div class="aviary-scrolly">

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🚀</span>
<h3 class="aviary-scrolly__title"><code>aviary complete</code></h3>
<p class="aviary-scrolly__tagline">Reads → annotated MAGs, end to end</p>
<p class="aviary-scrolly__body">Performs all steps in the Aviary pipeline: Assembly → Binning → Refinement → Annotation. One command for the whole pipeline — the one used in the example above.</p>
<a class="aviary-scrolly__link" href="usage/complete/">Read the <code>complete</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🧬</span>
<h3 class="aviary-scrolly__title"><code>aviary assemble</code></h3>
<p class="aviary-scrolly__tagline">Reads → contigs</p>
<p class="aviary-scrolly__body">Step-down hybrid assembly using long and short reads, or assembly using only short or long reads.</p>
<a class="aviary-scrolly__link" href="usage/assemble/">Read the <code>assemble</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🧩</span>
<h3 class="aviary-scrolly__title"><code>aviary recover</code></h3>
<p class="aviary-scrolly__tagline">Assembly → MAGs</p>
<p class="aviary-scrolly__body">Recover metagenome-assembled genomes (MAGs) from an assembly using multiple binning algorithms, followed by quality assessment and taxonomic classification. If no assembly is provided, Aviary runs the assembly pipeline first.</p>
<a class="aviary-scrolly__link" href="usage/recover/">Read the <code>recover</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🏷️</span>
<h3 class="aviary-scrolly__title"><code>aviary annotate</code></h3>
<p class="aviary-scrolly__tagline">MAGs → annotations</p>
<p class="aviary-scrolly__body">Annotate a given set of MAGs using EggNOG, GTDB-Tk, and CheckM2.</p>
<a class="aviary-scrolly__link" href="usage/annotate/">Read the <code>annotate</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">👥</span>
<h3 class="aviary-scrolly__title"><code>aviary cluster</code></h3>
<p class="aviary-scrolly__tagline">Dereplicate genomes across samples</p>
<p class="aviary-scrolly__body">Dereplicate and choose representative genomes from multiple Aviary runs using Galah.</p>
<a class="aviary-scrolly__link" href="usage/cluster/">Read the <code>cluster</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🧪</span>
<h3 class="aviary-scrolly__title"><code>aviary isolate</code></h3>
<p class="aviary-scrolly__tagline">Assemble and annotate a single isolate genome</p>
<p class="aviary-scrolly__body">Step-down hybrid assembly for isolated pure culture sequencing results — for use with isolate, not metagenomic, sequencing data.</p>
<a class="aviary-scrolly__link" href="usage/isolate/">Read the <code>isolate</code> documentation →</a>
</div>

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

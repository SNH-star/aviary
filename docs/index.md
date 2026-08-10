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
<p class="aviary-scrolly__body">Every stage in one command: assembly, binning, refinement, then annotation. Works from short reads, long reads, or both together — this is the command used in the example above. Already have an assembly? Pass it with <code>--assembly</code> and Aviary picks up from binning instead of starting over.</p>
<a class="aviary-scrolly__link" href="usage/complete/">Read the <code>complete</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🧬</span>
<h3 class="aviary-scrolly__title"><code>aviary assemble</code></h3>
<p class="aviary-scrolly__tagline">Reads → contigs</p>
<p class="aviary-scrolly__body">Step-down hybrid assembly that uses long and short reads together, playing each to its strengths — long reads for contiguity, short reads for accuracy. Either read type alone works too. Hand it several short-read samples with no long reads and they are co-assembled with MEGAHIT or metaSPAdes.</p>
<a class="aviary-scrolly__link" href="usage/assemble/">Read the <code>assemble</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🧩</span>
<h3 class="aviary-scrolly__title"><code>aviary recover</code></h3>
<p class="aviary-scrolly__tagline">Assembly → MAGs</p>
<p class="aviary-scrolly__body">Sorts an assembly's contigs into metagenome-assembled genomes, running several binning algorithms rather than trusting any single one, then refines the results and reports quality and taxonomy for each MAG. No assembly to hand? It runs the assembly pipeline first. Pass multiple assemblies to enable SemiBin2 multi-sample binning.</p>
<a class="aviary-scrolly__link" href="usage/recover/">Read the <code>recover</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🏷️</span>
<h3 class="aviary-scrolly__title"><code>aviary annotate</code></h3>
<p class="aviary-scrolly__tagline">MAGs → annotations</p>
<p class="aviary-scrolly__body">Point it at a directory of genomes and it answers the three questions you have about every MAG: what genes are in it (EggNOG), what it is (GTDB-Tk), and how much you can trust it (CheckM2 completeness and contamination). Assemblies can be passed alongside for QUAST QC.</p>
<a class="aviary-scrolly__link" href="usage/annotate/">Read the <code>annotate</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">👥</span>
<h3 class="aviary-scrolly__title"><code>aviary cluster</code></h3>
<p class="aviary-scrolly__tagline">Dereplicate genomes across samples</p>
<p class="aviary-scrolly__body">Run enough samples and the same organism turns up again and again. Point this at your finished Aviary runs and Galah collapses those near-duplicates into clusters, choosing one representative genome each — 97% ANI by default, adjustable with <code>--ani</code>.</p>
<a class="aviary-scrolly__link" href="usage/cluster/">Read the <code>cluster</code> documentation →</a>
</div>

<div class="aviary-scrolly__panel aviary-reveal">
<span class="aviary-scrolly__node">🧪</span>
<h3 class="aviary-scrolly__title"><code>aviary isolate</code></h3>
<p class="aviary-scrolly__tagline">Assemble and annotate a single isolate genome</p>
<p class="aviary-scrolly__body">The same step-down hybrid assembly as <code>assemble</code>, but tuned for a single organism from pure culture rather than a mixed community. Reach for this when you sequenced one isolate — on metagenomic data, use <code>assemble</code> or <code>recover</code> instead.</p>
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

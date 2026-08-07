---
title: Aviary
hide:
  - navigation
  - toc
---

<section class="aviary-hero">
  <div class="aviary-hero__copy">
    <span class="aviary-eyebrow">METAGENOMICS WORKFLOW</span>
    <h1>From sequencing reads<br>to microbial genomes.</h1>
    <p class="aviary-hero__lead">
      Aviary assembles metagenomes, recovers metagenome-assembled genomes and
      coordinates taxonomic and functional annotation.
    </p>
    <p class="aviary-hero__support">
      Run short-read, long-read or hybrid analyses locally or across an HPC
      cluster through one reproducible Snakemake workflow.
    </p>
    <div class="aviary-actions">
      <a href="getting-started/quickstart/" class="md-button md-button--primary">Run your first analysis</a>
      <a href="pdf/aviary-manual.pdf" class="md-button">Read the PDF manual</a>
    </div>
  </div>
  <div class="aviary-hero__visual" aria-label="Aviary workflow from reads through assembly and genome recovery">
    <svg viewBox="0 0 560 430" role="img" aria-labelledby="workflow-title workflow-desc">
      <title id="workflow-title">Aviary metagenomics workflow</title>
      <desc id="workflow-desc">Short and long sequencing reads flow through quality control, assembly, genome recovery and annotation.</desc>
      <defs>
        <linearGradient id="flow-gradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="var(--aviary-accent)" />
          <stop offset="1" stop-color="var(--aviary-blue)" />
        </linearGradient>
      </defs>
      <path class="workflow-line" d="M104 103 C180 103 168 176 242 176 S310 249 386 249 S390 326 462 326" />
      <g class="workflow-node workflow-node--reads" transform="translate(28 58)">
        <rect width="142" height="90" rx="14" />
        <path d="M27 27h35M27 38h48M27 49h29M27 60h43" />
        <text x="94" y="36">READS</text><text class="workflow-sub" x="94" y="56">short + long</text>
      </g>
      <g class="workflow-node" transform="translate(174 131)">
        <rect width="142" height="90" rx="14" />
        <path d="M26 58l12-28 13 28 13-18 15 18" />
        <text x="98" y="36">ASSEMBLY</text><text class="workflow-sub" x="98" y="56">contigs</text>
      </g>
      <g class="workflow-node" transform="translate(316 204)">
        <rect width="142" height="90" rx="14" />
        <circle cx="35" cy="32" r="12"/><circle cx="61" cy="48" r="12"/><circle cx="34" cy="61" r="12"/>
        <text x="101" y="36">RECOVER</text><text class="workflow-sub" x="101" y="56">MAGs</text>
      </g>
      <g class="workflow-node workflow-node--last" transform="translate(390 281)">
        <rect width="142" height="90" rx="14" />
        <path d="M27 65V28m0 10h17m-17 13h29m-12-13v14m12-1v14" />
        <text x="100" y="36">ANNOTATE</text><text class="workflow-sub" x="100" y="56">interpret</text>
      </g>
    </svg>
  </div>
</section>

<section class="aviary-proof" aria-label="Aviary capabilities">
  <div><strong>3</strong><span>sequencing modes</span></div>
  <div><strong>8</strong><span>focused commands</span></div>
  <div><strong>1</strong><span>tracked workflow</span></div>
  <div><strong>HPC</strong><span>scheduler ready</span></div>
</section>

## Start with the question you have

<div class="aviary-card-grid">
  <a class="aviary-card" href="getting-started/quickstart/">
    <span class="aviary-card__icon">01</span>
    <h3>Run Aviary</h3>
    <p>Install the software, configure reference data and produce a first meaningful result.</p>
    <span class="aviary-card__link">Quickstart <span aria-hidden="true">→</span></span>
  </a>
  <a class="aviary-card" href="guide/">
    <span class="aviary-card__icon">02</span>
    <h3>Understand the workflow</h3>
    <p>Learn how reads become assemblies, candidate genomes and annotated MAGs.</p>
    <span class="aviary-card__link">User guide <span aria-hidden="true">→</span></span>
  </a>
  <a class="aviary-card" href="usage/">
    <span class="aviary-card__icon">03</span>
    <h3>Find an exact option</h3>
    <p>Search command syntax, accepted values, defaults and output behaviour.</p>
    <span class="aviary-card__link">CLI reference <span aria-hidden="true">→</span></span>
  </a>
  <a class="aviary-card" href="faqs/">
    <span class="aviary-card__icon">04</span>
    <h3>Resolve a problem</h3>
    <p>Diagnose real validation messages, failed rules, resource limits and run state.</p>
    <span class="aviary-card__link">Troubleshooting <span aria-hidden="true">→</span></span>
  </a>
</div>

<section class="aviary-split">
  <div>
    <span class="aviary-eyebrow">ONE WORKFLOW, SEVERAL ENTRY POINTS</span>
    <h2>Use only the stages your analysis needs.</h2>
    <p>
      Assemble raw reads, recover genomes from an existing assembly, annotate a
      MAG collection, or run the complete path. Aviary records rule logs,
      resource benchmarks and workflow state throughout.
    </p>
    <a href="concepts/" class="aviary-text-link">How Aviary fits together <span aria-hidden="true">→</span></a>
  </div>
  <div class="aviary-command-list">
    <a href="usage/assemble/"><code>assemble</code><span>Reads → contigs</span></a>
    <a href="usage/recover/"><code>recover</code><span>Assembly → MAGs</span></a>
    <a href="usage/annotate/"><code>annotate</code><span>MAGs → annotations</span></a>
    <a href="usage/complete/"><code>complete</code><span>End-to-end analysis</span></a>
  </div>
</section>

## A complete analysis starts with one command

```bash
aviary complete \
  -1 sample_R1.fastq.gz \
  -2 sample_R2.fastq.gz \
  --output sample_aviary \
  --max-threads 8 \
  --n-cores 8
```

<div class="aviary-next-band">
  <div>
    <span class="aviary-eyebrow">READY TO BEGIN?</span>
    <h2>Take Aviary from installation to interpreted output.</h2>
  </div>
  <div class="aviary-actions">
    <a href="installation/" class="md-button md-button--primary">Install Aviary</a>
    <a href="getting-started/first-analysis/" class="md-button">Follow the walkthrough</a>
  </div>
</div>

<p class="aviary-citation-note">
  Using Aviary in research? See the <a href="citations/">citation guide</a> for
  Aviary and its upstream tools. Aviary is released under GPL-3.0.
</p>

---
title: Aviary
---

![Aviary](/images/aviary_logo.png)

# Assemble metagenomes and recover microbial genomes

Aviary is a Snakemake workflow for quality-controlling sequencing reads,
assembling metagenomes, recovering metagenome-assembled genomes (MAGs), and
adding taxonomic and functional annotations. It supports short reads, long
reads, and hybrid datasets, and can run locally or through a Snakemake HPC
profile.

## Choose a workflow

| Goal | Command | Start here |
| --- | --- | --- |
| Run assembly through annotation | `aviary complete` | [Quickstart](/getting-started/quickstart) |
| Quality-control and assemble reads | `aviary assemble` | [Assembly guide](/guide/assembly) |
| Recover MAGs from an assembly | `aviary recover` | [Genome recovery guide](/guide/genome-recovery) |
| Annotate an existing MAG collection | `aviary annotate` | [Annotation guide](/guide/annotation) |
| Assemble a cultured isolate | `aviary isolate` | [`isolate` reference](/usage/isolate) |
| Dereplicate genomes across runs | `aviary cluster` | [`cluster` reference](/usage/cluster) |

## Install

Bioconda is the recommended user installation:

```bash
conda create -n aviary -c conda-forge -c bioconda aviary
conda activate aviary
aviary --version
```

Aviary also needs local reference data for the analysis stages you enable.
See [installation and database setup](/installation) before a
production run.

## Smallest complete analysis

For paired short reads:

```bash
aviary complete \
  -1 sample_R1.fastq.gz \
  -2 sample_R2.fastq.gz \
  --output sample_aviary \
  --max-threads 8 \
  --n-cores 8
```

The workflow records rule logs in `sample_aviary/logs/`, resource benchmarks
in `sample_aviary/benchmarks/`, the final assembly at
`sample_aviary/assembly/final_contigs.fasta`, and recovered genomes beneath
`sample_aviary/bins/`.

## What Aviary coordinates

Aviary prepares inputs, selects workflow stages, manages resources and invokes
specialised upstream tools. Depending on the selected command and options,
those tools perform read filtering, assembly, coverage calculation, binning,
bin refinement, quality assessment, taxonomy and functional annotation.
Snakemake tracks completed outputs so interrupted analyses can normally resume.

![Aviary workflow](/figures/aviary_workflow.png)

## Where next?

- New to Aviary? Follow the [quickstart](/getting-started/quickstart).
- Planning an analysis? Read [core concepts](/concepts) and the relevant
  workflow guide.
- Looking for an exact flag? Use the [CLI reference](/usage).
- Interpreting a run? See the [output reference](/guides/output).
- Running on a cluster? See [HPC and scaling](/guides/hpc).
- Diagnosing a failure? Start with [troubleshooting](/faqs).

## Citation and licence

If you use Aviary in research, cite the software and the upstream tools used by
your selected workflow. See the [citation guide](/citations) for the
complete list. Aviary is distributed under the GPL-3.0 licence.

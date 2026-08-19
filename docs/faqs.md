---
title: Troubleshooting and FAQ
---

# Troubleshooting and FAQ

Start with the terminal summary, then inspect the rule-specific files beneath
`output_dir/logs/`. A failed upstream tool normally writes the useful diagnostic
there rather than to the top-level Aviary log.

## A rule failed

### Cause

Aviary reports the Snakemake rule and its `shell:` command. The cause may be
invalid input, an upstream-tool error, missing reference data or an exhausted
scheduler resource. A failure looks like this in the terminal:

```text
Error in rule polish_metagenome_flye:
    jobid: 12
    output: data/assembly.pol.rac.fasta
    shell:
        pixi run --manifest-path ... -e polishing .../polish.py --input-fastq ... \
        --output-fasta data/assembly.pol.rac.fasta ... --log logs/polish_metagenome_flye/20260819_231204/attempt1.log
    (one of the commands exited with non-zero exit code; note that snakemake uses bash strict mode!)
```

Most Aviary rules don't declare a Snakemake `log:` field, so Snakemake's own
error block usually won't show one. Instead, the tool's own log path is the
value passed to `--log` inside the `shell:` command shown in the error, under
`output_dir/logs/<rule-name>/<run-timestamp>/attempt<N>.log`.

### Resolution

```bash
ls output_dir/logs/<rule-name>/
less output_dir/logs/<rule-name>/<run-timestamp>/attempt1.log
```

In the example above, that's
`less output_dir/logs/polish_metagenome_flye/20260819_231204/attempt1.log`, taken
directly from the `--log` argument in the failed rule's `shell:` command.

Correct the underlying problem and repeat the same Aviary command with the same
output directory. Snakemake normally retains completed valid work.

## `Number of forward reads != Number of reverse reads`

### Cause

The `-1` and `-2` lists contain different numbers of files.

### Resolution

Provide one reverse file for every forward file and keep sample order aligned:

```bash
aviary complete \
  -1 A_R1.fastq.gz B_R1.fastq.gz \
  -2 A_R2.fastq.gz B_R2.fastq.gz
```

## `Cannot read short read file ... Please check permissions.`

### Cause

The path does not exist from the execution host, or the process cannot read it.
This is common when a path is visible on the login node but not mounted on a
compute node.

### Resolution

Check spelling, permissions and compute-node visibility. Prefer absolute paths
for scheduler runs.

## `Multiple readsets detected`

### Cause

More than one read set was supplied without an explicit assembly decision.

### Resolution

Use `--coassemble` to combine supported inputs, or `--coassemble false` to make
the non-coassembly behaviour explicit. Review the resulting assembly strategy
in a `--dry-run` before starting a large analysis.

## `File ... exists` for `--log`

### Cause

Aviary refuses to overwrite an existing explicit top-level log file.

### Resolution

Choose a new `--log` path or archive the existing file. Rule-level logs inside
the output directory follow the workflow's own resume behaviour.

## `prepare_binning_files` fails or temporary storage fills

### Cause

Read mapping and coverage preparation can exhaust the filesystem used for
temporary files, especially when `TMPDIR` points to a small `/tmp` partition.

### Resolution

Choose a larger temporary filesystem:

```bash
aviary recover ... --tmpdir /scratch/$USER/aviary-tmp
```

Create the directory before running and ensure cluster jobs can access it.

## SPAdes exits with code `-9`

An operating-system or scheduler kill commonly indicates that the process
exceeded an enforced resource limit. Confirm the scheduler accounting record
and SPAdes log before assuming memory is the cause. If memory was exhausted,
increase the job allocation and keep `--max-memory` consistent with that hard
limit, or reduce concurrency.

## The output directory is locked after an interrupted run

First confirm that no Aviary or Snakemake process is still using the directory.
Then use the documented `--unlock` workflow option from the
[workflow-control guide](guides/workflow-control.md). Unlocking a live run can
allow concurrent processes to corrupt workflow state.

## No bins were found

This can be a valid result rather than a software failure. Inspect assembly
quality, read mapping, binner logs, minimum contig/bin sizes and available
coverage variation. Do not lower quality thresholds solely to force a non-empty
result.

## Can Aviary use a GPU?

GPU-enabled binners can use compatible hardware when their environments are
built. On a cluster, `--request-gpu` marks applicable submitted work for GPU
resources. It does not accelerate every workflow stage. See
[performance and resources](advanced/performance.md).

## How do I remove host-associated reads?

Supply one or more host reference FASTA files with `--host-filter`. Aviary maps
reads to those references during quality control and removes mapped reads before
assembly. Record the exact host-reference build because it affects which reads
remain.

## Which databases are required?

Requirements depend on enabled stages. GTDB-Tk taxonomy, EggNOG functional
annotation, CheckM2 quality assessment, SingleM analysis and Metabuli-enabled
workflows each use their own local data. See [installation](installation.md) and
the [`configure` reference](usage/configure.md).

## How should Aviary be cited?

See the [citation guide](citations.md). Cite Aviary and the upstream programs used
by the selected workflow.

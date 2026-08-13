---
title: aviary cluster
---

# aviary cluster

Dereplicate and choose representative genomes from multiple aviary runs using Galah.

```
aviary cluster --input-runs aviary_output_folder_1/ aviary_output_folder_2/
```

> This subcommand also accepts `--dry-run`, `--clean`, `--strict`, `--request-gpu`, `--build`, `--build-gpu`, `--download`, `--rerun-triggers`, `--default-resources`, `--snakemake-profile`, `--snakemake-cmds`, `--cluster-retries`, `--local-cores`, and `--workflow`, which are shared across every aviary subcommand — see [Centralised commands](centralised_commands.md).

## Input options

**`-i`**, **`--input-runs`** DIR [DIR ...]

  Paths to previous finished aviary runs. Each must contain `bins/checkm.out` and `bins/final_bins`. **(required)**

## Clustering options

**`--ani`** FLOAT

  Overall ANI level to dereplicate at with FastANI. [default: 97]

**`--precluster-ani`** FLOAT

  Minimum dashing-derived ANI for preclustering. [default: 95]

**`--precluster-method`** METHOD

  Method for rough ANI in preclustering: `dashing` (HyperLogLog) or `finch` (MinHash). [default: dashing]

**`--min-completeness`** FLOAT

  Ignore genomes below this completeness percentage. [default: none]

**`--max-contamination`** FLOAT

  Ignore genomes above this contamination percentage. [default: none]

**`--use-checkm2-scores`**

  Use CheckM2 completeness and contamination scores for Galah dereplication.

**`--pggb-params`** STRING

  Parameters for pggb. [default: `-k 79 -G 7919,8069`]

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

The basic shape — dereplicate the final bins from two or more finished `recover`/`complete`
runs down to one representative genome per cluster:
```
aviary cluster --input-runs run1/ run2/
```

Each directory in `--input-runs` must be a completed aviary output (i.e. it already has
`bins/checkm.out` and `bins/final_bins/` — the output of `recover`/`complete`, not raw MAGs from
elsewhere). If you have loose FASTA files instead, use `aviary recover`/`annotate` first, or
[`galah cluster`](https://github.com/wwood/galah) directly.

### Species- vs strain-level dereplication

`--ani` sets the FastANI cutoff for the final clustering step. Lower it for broader,
species-level groups; raise it to only merge near-identical strains:
```
aviary cluster --input-runs run1/ run2/ run3/ --ani 95   # species-level
aviary cluster --input-runs run1/ run2/ run3/ --ani 99.5 # strain-level
```

`--precluster-ani` is a separate, cheaper first pass (rough ANI via dashing/finch sketching)
that groups obviously-similar genomes before the expensive FastANI all-vs-all step — it should
normally stay below `--ani`, not be tuned to the same value:
```
aviary cluster --input-runs run1/ run2/ run3/ --ani 97 --precluster-ani 90
```

### Swapping the preclustering method

`dashing` (HyperLogLog sketching, the default) is the faster choice for large genome
collections. `finch` (MinHash) is worth trying if preclustering seems to be merging genomes it
shouldn't, since the two sketching approaches can disagree at the margins:
```
aviary cluster --input-runs run1/ run2/ run3/ --precluster-method finch
```

### Filtering by quality before dereplication

Drop low-quality genomes from consideration entirely, and trust CheckM2's scores (rather than
the default CheckM1-derived ones already in `bins/checkm.out`) when Galah picks the cluster
representative:
```
aviary cluster --input-runs run1/ run2/ \
  --min-completeness 70 --max-contamination 5 --use-checkm2-scores
```

### Building pangenome graphs for each cluster

Aviary can run `pggb` per cluster to build a pangenome graph across its member genomes; tune its
divergence/segment-length parameters for genome sets that are more diverged than pggb's defaults
expect:
```
aviary cluster --input-runs run1/ run2/ run3/ --pggb-params "-k 47 -G 4057,4229"
```

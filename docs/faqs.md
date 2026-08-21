---
title: FAQs & Troubleshooting
---

FAQs & Troubleshooting
========

This page is just meant for general questions that I notice are asked with some frequency. If you feel like something
is missing from here and you'd like to see it included, feel free to ask it by raising an issue on GitHub.


### I want to perform both MAG recovery and assembly, how do I do that?

If you supply all reads to the `recover` command then Aviary will perform assembly first and then perform MAG recovery. You can perform assembly first by using the `assemble` command and then using the output assembly file as the input to the `recover` command. However, it is much simpler to let aviary handle this process for you.

### An error occurred but I don't know where to look for the error message

All of the error messages are stored in the `logs/` folder. The error messages are stored in the `logs/` folder with the name of the file corresponding the name of the rule that they originate from. If you had an error occur in the `qc_short_reads` rule then consult the `logs/qc_short_reads.log` file for the error message.

### Is Aviary cluster compatible?

Yes! Consult the examples page for more information.

### I have access to a GPU, can I use it?

Yes! Aviary supports the use of GPUs for the binning process (taxvamb, comebin, semibin). If the GPU is on a local machine, you must first install the `cuda` package into your conda environment. Then, programs that use GPUs should automatically detect its presence.

If you are using a cluster, you can supply the `--request-gpu` flag and Aviary will attempt to place rules that use GPUs on to a machine that has GPUs available.

### Error in prepare_binning_files

This error is almost always caused by the user running out of storage in their `/tmp` folder when `coverm` performs the mapping process. To fix this, you can either increase the amount of storage available to the `/tmp` folder or you can change the location of the temporary folder by setting the `TMPDIR` environment variable to a folder with more storage. Aviary also allows the user to specify the location of the temporary folder by using the `--tmpdir` parameter.

### I wish to remove host contamination from my reads

Aviary supports the removal of host contamination during the assembly process via the `-r`, `--host-filter` parameter. This flag can take one or more compressed or non-compressed fasta files. Aviary will then compare the reads to these references and remove any reads that map to them.

### SPAdes error: "Error code: -9" or other errors

The most likely solution to this is that you are running out of memory. SPAdes is a memory intensive program and will exit unexpectedly if it reaches the maximum memory limit of your machine or supplied by aviary.
To increase the amount of memory available to SPAdes, you can either increase the amount of memory available to the entire pipeline by using the `-m` parameter.



### qsub and pysam - ModuleNotFoundError

A known issue with using snakemake + pysam + qsub results in the a break in the pipeline. The issue arises because pysam 
does not activate correctly when using qsub by default. To fix this you just need to add the `-V ` parameter to your qsub
command.

### Which databases do I download?

It is probably best to just let Aviary handle the downloading of your databases via the `--download` parameter. But, if you
would like to set them up yourself, please read ahead

For the GTDB:
* [GTDB](https://gtdb.ecogenomic.org/downloads) Required for taxonomic annotation
Download and point the GTDB environment variable to the `db/` folder inside of that download.

The **required** databases are as follows:
* [EggNog](https://github.com/eggnogdb/eggnog-mapper/wiki/eggNOG-mapper-v2.1.5-to-v2.1.7#setup).
Download this database and point to the root folder of the database.

Aviary will ask for the paths to these database files if they don't exist, otherwise you can place these lines into
the `activate.d/aviary.sh` or `.bashrc` files changing the specific paths:
```
export GTDBTK_DATA_PATH=/path/to/gtdb/gtdb_release232/db/ # https://gtdb.ecogenomic.org/downloads
export EGGNOG_DATA_DIR=/path/to/eggnog-mapper/2.1.3/ # https://github.com/eggnogdb/eggnog-mapper/wiki/eggNOG-mapper-v2.1.5-to-v2.1.8#setup
export SINGLEM_METAPACKAGE_PATH=/path/to/singlem_metapackage.smpkg/
export CHECKM2DB=/path/to/checkm2db/
```

### My coverage / abundance numbers differ from an older Aviary version

The default read mappers changed. Aviary now uses **strobealign** for short
reads and **rammap** for long reads, where previous versions used minimap2
throughout. Both are faster, and rammap is a minimap2-compatible implementation,
but a different aligner makes different alignment decisions -- so coverage
depths, bin abundances and polished contigs will not be bit-identical to those
from an earlier release.

Nothing needs to change to keep using Aviary: every existing command still runs,
and no new flag is required.

To reproduce the previous behaviour exactly, ask for minimap2 explicitly:

```
aviary recover --short-read-mapper minimap2 --long-read-mapper minimap2 ...
```

This matters most if you are partway through an analysis, or comparing against
results produced by an earlier version. For new work, the defaults are the
faster option.

### Which read mapper should I use?

The defaults are a reasonable choice for almost everyone. The alternatives exist
for continuity and for cases where a particular aligner is preferred:

| Flag | Options |
|---|---|
| `--short-read-mapper` | `strobealign` (default), `minimap2`, `rammap`, `minibwa`, `bwa-mem`, `bwa-mem2`, `strobealign-aemb` |
| `--long-read-mapper` | `rammap` (default), `minimap2`, `minibwa` |

The `-x`/preset for long reads is chosen from `--longread-type` by default, so
`--long-read-mapper` changes only which aligner runs, not which preset it uses.
Note that strobealign, bwa-mem and bwa-mem2 are short-read only, which is why
the two flags are separate.

#### Choosing a preset explicitly with `--*-mapper-model`

`minimap2` and `rammap` are the only families with more than one CoverM
preset. Use `--short-read-mapper-model` (`sr`, `no-preset`) or
`--long-read-mapper-model` (`lr-hq`, `ont`, `pb`, `hifi`, `no-preset`) to pick
one directly instead of relying on the `--long-read-type` default:

```bash
aviary recover --long-read-mapper rammap --long-read-mapper-model hifi ...
```

This also fixes a previously dead code path: `ont_hq` and `hifi` used to be
silently mapped with the `ont`/`pb` presets respectively, because CoverM's
`lr-hq` and `hifi` presets were never actually reachable. They are now used
automatically for `--long-read-type ont_hq` / `hifi`, which changes coverage
numbers slightly for those two read types compared to earlier versions of
this flag. Giving `--*-mapper-model` for `strobealign`, `minibwa`, `bwa-mem`,
`bwa-mem2` or `strobealign-aemb` (which have no selectable model) is an error.

`ont` and `pb` are legacy presets — see below.

Models are also checked against read length: `sr` and `no-preset` are the only
valid `--short-read-mapper-model` values, and `lr-hq`, `ont`, `pb`, `hifi` and
`no-preset` the only valid `--long-read-mapper-model` values. Crossing them
(e.g. `--short-read-mapper-model ont`) is rejected up front, because CoverM
would otherwise accept it and return a well-formed coverage table of near-zero
depths — a wrong number rather than an error.

#### `ont` and `pb` are legacy presets, `lr-hq` and `hifi` are the defaults

`--longread-type ont` (and `ont_hq`) now default to the `lr-hq` model
(minimap2/rammap `-x lr:hq`), not `ont` (`-x map-ont`). `--longread-type ccs`
now defaults to `hifi` (`-x map-hifi`), not `pb` (`-x map-pb`). Per
[minimap2's own docs](https://lh3.github.io/minimap2/minimap2.html):

- `map-ont` "align[s] noisy long reads of ~10% error rate" — accurate for
  older ONT chemistry, far too liberal for current chemistry v14 reads (~99%
  accuracy).
- `map-pb` "is effectively deprecated by HiFi... unless you work on very old
  data, you probably want to use `map-hifi` or `lr:hq`."
- `lr:hq` "was recommended by ONT developers for recent Nanopore reads
  produced with chemistry v14... shown to work better for accurate Nanopore
  reads than `map-hifi`."

CCS reads are, by PacBio's current terminology, HiFi reads (CCS at sufficient
pass count *is* HiFi), so routing them through the CLR-era `map-pb` preset was
the same class of problem.

**`ont` (`map-ont`) and `pb` (`map-pb`) remain fully available** — they were
not removed, only demoted from being the default. Use them explicitly for
genuinely noisy/legacy data:

```bash
aviary recover --long-read-mapper minimap2 --long-read-mapper-model ont ...
```

`rs`/`sq` (PacBio RSII/Sequel) are unaffected — they are genuine older CLR
chemistry, so `map-pb` is still the correct preset for them, not a
deprecated-by-mistake one. `hifi` was already on `map-hifi` and is unchanged.

#### Mappers are checked against the reads you supply

Naming a mapper for reads you did not provide is an error rather than a
silently ignored flag:

```bash
# error: --short-read-mapper given, but no short reads to map
aviary recover --assembly contigs.fasta --short-read-mapper bwa-mem ...
```

The same applies to `--long-read-mapper` / `--long-read-mapper-model` without
`-l/--longreads`, and to `--minibwa-params` when `minibwa` is not the selected
mapper. Defaults (`strobealign` for short reads, `rammap` for long reads) are
unaffected — they only apply to reads that were actually supplied, so a
short-read-only run never trips the long-read check.

#### `bwa-mem` / `bwa-mem2`

These are the reference BWA implementations, usable as `--short-read-mapper`
for coverage, abundance and racon polishing. They are the slowest option here
(no inline indexing, and polishing re-indexes the reference every racon
round), but are included for continuity with pipelines built around them.

#### `strobealign-aemb`

This is not a normal aligner choice like the others -- it is CoverM's
`-m strobealign-aemb` fast direct abundance estimator, which shells out to
`strobealign --aemb` and skips alignment/pileup entirely. It has narrower
scope than the other `--short-read-mapper` values:

- Only used for the per-contig binning coverage step (`data/coverm.cov`).
  Per-genome relative abundance (`bins/coverm_abundances.tsv`) always falls
  back to plain `strobealign` instead, since CoverM cannot run
  `strobealign-aemb` through `coverm genome` at all.
- Faster than a full alignment, but less precise -- treat it as a speed/
  precision tradeoff, not a strictly-better default.
- No selectable model: `--short-read-mapper-model` is an error alongside it,
  the same as for `strobealign`, `minibwa`, `bwa-mem` and `bwa-mem2`.
- Short-read only, like `strobealign`/`bwa-mem`/`bwa-mem2`.

#### `minibwa` for long reads

`minibwa` has no long-read preset of its own in CoverM. Use
`--minibwa-params` to pass its native preset flag directly, e.g.:

```bash
aviary recover --long-read-mapper minibwa --minibwa-params "-x lr" ...
```

`minibwa` cannot be used for racon polishing: racon needs PAF, and minibwa
takes a `map` subcommand rather than minimap2's bare `-x <preset>`, so aviary
cannot build a PAF command for it. A run that would polish — one where aviary
does the assembly itself and the reads are PacBio-family — is rejected up
front with an error. Use `rammap` or `minimap2`, or pass a pre-built
`--assembly` to skip polishing.

#### Raw per-aligner passthrough params

CoverM exposes a raw params passthrough for every aligner it wraps, and
aviary now exposes all of them, mirroring `--minibwa-params`:

| Flag | Applies to |
|---|---|
| `--bwa-params` | `--short-read-mapper bwa-mem` / `bwa-mem2` |
| `--strobealign-params` | `--short-read-mapper strobealign` (not `strobealign-aemb`, which does not accept it) |
| `--minimap2-params` | `--short-read-mapper` or `--long-read-mapper` `minimap2` |
| `--rammap-params` | `--short-read-mapper` or `--long-read-mapper` `rammap` |
| `--minibwa-params` | `--short-read-mapper` or `--long-read-mapper` `minibwa` |

Each is checked against the reads you supply and the mapper you selected the
same way `--minibwa-params` always was — giving one without the matching
mapper selected is an error rather than a silently ignored flag.

### Can I bin multiple assemblies together with SemiBin2?

Yes, via `--semibin-mode multi`. By default (`--semibin-mode single`, unchanged
from before) SemiBin2 bins a single assembly with `single_easy_bin`. Passing
`--semibin-mode multi` instead runs `multi_easy_bin`, which co-bins several
assemblies together and lets SemiBin2 learn across samples — supply the
assemblies as multiple `--assembly` files:

```
aviary recover --assembly sample1.fasta sample2.fasta \
  -1 sample1_R1.fastq.gz sample2_R1.fastq.gz \
  -2 sample1_R2.fastq.gz sample2_R2.fastq.gz \
  --semibin-mode multi ...
```

`--semibin-model` is ignored in multi mode, since SemiBin2's pre-trained
environments only apply to single-sample binning. Contig names that collide
across assemblies (e.g. `NODE_1` appearing in more than one sample, which is
normal for independently-assembled samples) are kept distinct internally by a
per-sample prefix, so this is safe even when assemblies were not given
pre-uniquified contig names.

### Why the name "Aviary"? Why the bird names in general?

Put all your birds in one place.

### Where did the logo come from?

I made it (among other bird based + CoverM logos) using [GIMP](https://www.gimp.org/) and based the idea off of this 
[tutorial](https://www.youtube.com/watch?v=fSOR7mPwb4I). They are very easy to make so just follow that video if you 
feel like making something similar.

### Where's the paper?

Please cite:

> Newell RJP, Aroney STN, Zaugg J, Sternes P, Tyson GW, Woodcroft BJ.
> **Aviary: Hybrid assembly and genome recovery from metagenomes with Aviary.**
> Zenodo (2024). https://doi.org/10.5281/zenodo.10806928
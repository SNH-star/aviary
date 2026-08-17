# Changelog

## v0.13.3 - 2026-08-13

### Added

- **`--short-read-mapper`** — aligner for short-read coverage, abundance and
  racon polishing: `strobealign` (default), `minimap2`, `rammap`, `minibwa`,
  `bwa-mem`, `bwa-mem2` or `strobealign-aemb`. bwa-mem/bwa-mem2 have no PAF
  output mode, so polishing converts their SAM output with
  `paftools.js sam2paf`, and both need a fresh on-disk index built for every
  racon round since the reference changes each round — meaningfully slower
  for polishing than the other options. `strobealign-aemb` uses CoverM's
  `-m strobealign-aemb` fast direct abundance estimator instead of a normal
  alignment; it only applies to the per-contig binning coverage step, has no
  selectable model, and per-genome abundance/polishing always fall back to
  plain `strobealign` since CoverM cannot run it through `coverm genome`.

- **`--long-read-mapper`** — aligner for long-read coverage and abundance:
  `rammap` (default), `minimap2` or `minibwa`. For rammap/minimap2 the preset
  is chosen from `--long-read-type` by default, or explicitly via
  `--long-read-mapper-model`. `minibwa` has no long-read preset in CoverM;
  steer it with `--minibwa-params` (e.g. `-x lr`) instead. `minibwa` is not
  used for racon polishing.

- **`--short-read-mapper-model` / `--long-read-mapper-model`** — explicit
  CoverM preset (`sr`, `lr-hq`, `ont`, `pb`, `hifi`, `no-preset`) for mappers
  that support more than one (`minimap2`, `rammap`). Errors if given for a
  mapper with no selectable model.

- **`--minibwa-params`** — raw passthrough parameters for minibwa, forwarded
  to CoverM's own `--minibwa-params`. Only meaningful when minibwa is
  selected as the short- or long-read mapper.

- **`--bwa-params` / `--strobealign-params` / `--minimap2-params` /
  `--rammap-params`** — raw per-aligner passthrough parameters, mirroring
  `--minibwa-params`, forwarded to CoverM's own equivalent flag. Each only
  applies when the matching mapper is actually selected (`--strobealign-params`
  does not apply to `strobealign-aemb`, which does not accept it).

### Changed

- **`ont_hq` and `hifi` now use their own CoverM presets** — `get_coverage.py`,
  `get_abundances.py` and `fraction_recovered.py` each independently lumped
  `ont_hq` in with `ont` and `hifi` in with `rs`/`sq`/`ccs`, so CoverM's
  `lr-hq` and `hifi` presets existed but were never actually reachable. Long
  reads of type `ont_hq` or `hifi` now resolve to those presets by default,
  which will shift coverage/abundance numbers slightly for those two read
  types compared to earlier versions of this flag; other read types are
  unaffected. Override with `--long-read-mapper-model` to reproduce the old
  behaviour explicitly if needed.

- **Mapper flags are now validated against the reads supplied** — naming a
  mapper for reads that were not provided (`--short-read-mapper` with no
  `-1/-2`, `--long-read-mapper` with no `-l`) used to be silently ignored; it
  is now an error. Mapper models are also checked against read length: `sr` and
  `no-preset` for short reads, `lr-hq`/`ont`/`pb`/`hifi`/`no-preset` for long
  reads. Crossing them previously reached CoverM, which accepts the
  combination and returns a well-formed table of near-zero depths — a wrong
  number rather than a failure. Defaults are unchanged (`strobealign` short,
  `rammap` long) and a run that passes no mapper flags is unaffected.

- **Default aligners are now strobealign (short) and rammap (long)** — CoverM
  bumped to `>=0.8`, which defaults short reads to strobealign. Aviary now names
  its mapper explicitly at every call site rather than relying on that default,
  so a non-default mapper can be selected when needed.

- **Bin abundances use the same mapper as the binners** — `get_abundances.py`
  hardcoded `minimap2-sr`, so the binners saw strobealign-derived depths while
  reported abundances came from minimap2. Both now follow
  `--short-read-mapper`.

- The coverage, abundance and polishing scripts log the command they run, so the
  aligner actually used is recoverable from a completed run.

### Fixed

- **`--short-read-mapper-model` produced an invalid aligner command for every
  preset except `sr`** — CoverM's `-p` suffix is not the aligner's own `-x`
  value (CoverM `lr-hq` is minimap2's `lr:hq`, `ont` is `map-ont`, and
  `no-preset` means no `-x` at all), but `polish.py` passed the suffix straight
  through. racon polishing therefore died with `unknown preset 'lr-hq'` partway
  through a run. The translation is now explicit and shared.

- **`--minibwa-params` could never be used** — the value is passed through to
  the coverage scripts by the Snakemake rules, unquoted, so any real value
  (which begins with `-`, e.g. `-x lr`) was parsed as a flag rather than a
  value and the rule failed immediately with an argparse error.

- **`--long-read-mapper minibwa` failed during racon polishing** — minibwa
  takes a `map` subcommand rather than minimap2's bare `-x <preset>`, so it
  cannot emit the PAF racon needs. Runs that would polish are now rejected up
  front with an explanation instead of failing after assembly.

- **bwa-mem/bwa-mem2 racon polishing produced empty PAFs** — `bwa mem` was run
  without `-p`, so it never ran in paired mode and never set the SAM FLAG bits
  (`0x1`/`0x40`/`0x80`) that `paftools.js sam2paf` relies on to restore `/1`/`/2`
  mate suffixes, so racon's read lookup matched nothing and it died with
  `error: empty sequences set!`. `-p` is now passed only when the reads are
  genuinely interleaved (not the paired-R1-then-R2-concatenated block that
  `clean_short_reads()` produces, where `-p` would wrongly pair up two R1
  reads).

- **GPU rules are scheduled correctly on both SLURM and PBS** — Snakemake has no
  portable GPU resource, so its SLURM executor plugin reads `gpu` while
  `snakemake_mqsub` reads `gpus`. Declaring only `gpus` makes SLURM silently
  schedule the rule onto a CPU node, where the CUDA environment fails to
  activate before any log file is written. `taxvamb`, `semibin`, `comebin` and
  `polish_metagenome_flye` now declare both keys; each scheduler ignores the
  one it does not recognise, so there is no conflict.

- **concoct now runs** — it needs numpy below version 2, but pinning numpy
  alone was not enough: newer scipy versions ask for numpy 2, which made
  concoct's own version check fail at runtime. Scipy is now pinned as well, and
  concoct's error messages go to its log instead of being discarded.

- **`assembly_quality` can be built again** — two rules both produced
  `www/assembly_stats.txt`, which snakemake refuses, so nothing needing that
  file could run. Only one is now defined at a time, depending on whether the
  assembly was supplied or built by aviary.

- **`read_fraction_recovered` now completes** — the rule failed at several
  points and had never produced output. Its script, output path, arguments and
  CoverM call have all been corrected. It reports the fraction of reads mapping
  back to the assembly, and is reached by requesting its output file directly.


---

## v0.13.2 - 2026-07-22

Patch release fixing a crash in Metabuli taxonomy conversion.

---

### Fixed

- **`convert_metabuli` crashed on unclassified reads** — Metabuli writes
  unclassified rows (`is_classified=0`) with a trailing tab, giving 9
  tab-separated fields against classified rows' 8, so `pd.read_csv(header=None)`
  inferred 8 columns from the leading classified rows and aborted on the first
  unclassified one (`ParserError: Expected 8 fields, saw 9`). The read now pins
  `usecols=range(8)`, absorbing the phantom field without discarding data. Any
  run with at least one unclassified read was affected.


---

## v0.13.1 - 2026-07-08

Patch release focused on repairing database downloads (`aviary configure --download`).

---

### Fixed

- **`aviary configure --download` no longer requires read inputs** — `download_databases` added to `SUBCOMMANDS_WITHOUT_READS`; previously failed with "both long_reads and short_reads_1 are set to none"
- **eggNOG database download** — `eggnogdb.embl.de` was decommissioned; files are now fetched from `eggnog5.embl.de`
- **Metabuli GTDB database download** — upstream relocated the tarball to an `archive/` path. The old command 404'd but exited 0, silently leaving an empty database; it now downloads the archived index directly and fails loudly on error
- **CheckM2 database download** — unsets `CHECKM2DB` and runs under `bash -e -o pipefail` so download failures are no longer swallowed

### Changed

- **pixi 0.71+ compatibility** — `pixi.toml` migrated to rich platforms (CUDA on platform entries); minimum `pixi` bumped to `>=0.71`; lockfile regenerated

---

## v0.13.0 - 2026-03-31

Forked from [wwood/aviary](https://github.com/wwood/aviary) at v0.12.0 (`myloasm` branch). All changes below are relative to that base.

---

### Changed

- **SingleM updated to v0.21.3** — minimum version bumped from 0.20.3 to 0.21.3; `singlem-appraise` environment unpinned from 0.19.0 now that the v0.20 performance regression for `--genome-fasta-files` input is fixed in v0.21
- **GTDB-Tk updated to v2.7.2** — minimum version bumped from 2.6.1 to 2.7.2. v2.7+ removes the `--skip_ani_screen` flag; replaced by `--place_species`
- **Database updated to GTDB R232** — SingleM metapackage updated to `S6.5.0.GTDB_r232` and GTDB-Tk database updated to `release232`; download URL in `aviary configure --download` updated accordingly
- **Benchmark added to `singlem_appraise` rule** — runtime now recorded in `benchmarks/singlem_appraise.benchmark.txt`

### Added

#### Web Interface (`aviary/web/`) — experimental

An experimental browser-based monitor and results explorer served via Flask. Start with:

```bash
ssh -L 8090:localhost:8090 username@address.com
pixi install -e web
pixi run -e web server --output-dir /path/to/aviary_output
```

Then open `http://localhost:8090` in your browser. Includes a pipeline monitor for current and past runs (with log information), bin quality report, results visualisation, taxonomy tree view (sunburst, Radial and Horizontal cladogram), assembly graph viewer (GFA files), and export functionality.

#### Pipeline

- **myloasm assembler support** — myloasm added as an alternative long-read assembler alongside Flye (Myloasm default)
- **GFA graph generation for short and long read assembly** — assembly graphs produced and retained for use in the assembly graph viewer
- **`skip_reads_check` parameter** — added to `template_config.yaml` and config handling to support running subcommands without providing reads
- **SingleM metapackage support in integration tests**
- **FastQC replaced with RastQC** — RastQC is implemented as a drop-in replacement for FastQC, providing equivalent short-read QC reporting. All files are processed in a single command invocation for clean, readable log output.

#### Environment

- **Web environment in main `pixi.toml`** — flask added as `[feature.web]` so a single `pixi install` covers both the pipeline and the web interface
- **`server` task** — `pixi run -e web server` starts the web interface directly

---

### Fixed

- Updated symlinks to be working correctly
- Added diamond dependency to das-tool environment
- Added gzip dependencies so packages can read compressed files
- Updated `pbsim.fq.gz` binary file
- Fixed quickbin rule to use relative path for `quickbin.sh` after BBTool update
- Added conditional check for `skip_reads_check` to prevent errors when no reads are provided
- Normalised qnames in PAF output to match original fastq read names
- Handle unexpected long read types by raising a clear exception
- Ensured `bam_cache` directory is created in `get_coverage` before use
- Added memory allocation parameter to quickbin rule to prevent crashes
- Added `--only-id` flag to seqkit command in `filter_contigs_by_size` rule
- Refactored log permission handling in `onsuccess`/`onerror` to check file existence first
- Added temporary directory creation for GFA conversion in `assemble_short_reads`
- Unset CUDA environment variables in taxvamb, semibin, and comebin rules for improved compatibility
- Added file locking to NanoPlot command for improved concurrency handling
- Fixed `OUTPUT_DIR` path to use `PIXI_PROJECT_ROOT` environment variable
- Added pandas import to `prepare_binning_files_gather` rule
- Updated blas and blas-devel package versions in `pixi.lock` for compatibility
- Refactored unrefined binners list formatting
- Removed unnecessary `--no-assign-taxonomy` flag from SingleM commands
- Handle `"none"` input for read lists in `ReadContainer` initialisation
- Added scratch directory to gtdbtk rule for better temporary file and memory handling
- Removed `--skip_ani_screen` flag in gtdbtk rule (removed in GTDB-Tk v2.7.0)
- Added sleep delays between GPU test submissions to prevent resource contention
- Increased memory allocation for GPU and expensive tests in mqsub commands
- Fixed isolate functionality, with medaka updated to `>=2.2.1` (previously restricted to `<2.1.0` due to [nanoporetech/medaka#566](https://github.com/nanoporetech/medaka/issues/566), fixed in 2.2.x) and dnaapler updated to `>=1.0.0`

---

### Changed (pipeline only)

- Assembly rules now retain GFA graph files for downstream use
- Test output directory naming split for CPU and GPU tests to prevent log/data overwrites
- Log completion message added after refinery process finishes

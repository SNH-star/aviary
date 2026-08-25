# Port stageguard (assembly checkpointing) from aviary-0.13.3 to aviary-v0.13.4

## Context

`aviary-0.13.3` (at `/home/herholdt/aviary-0.13.3`, remote `v0133` in this repo)
has an in-progress feature ("stageguard") that was developed and merged
alongside an unrelated feature (SemiBin2 multi-sample binning, "semibin-multi")
in commit `5e4a224` ("Merge aviary-Stage-Multi-test (Multi_Stage_test):
stageguard + semibin-multi"). `aviary-v0.13.4` (this repo, branch
`slurm-concoct-coverm`) already has semibin-multi and all other current
features up to date — it is missing only stageguard. This spec covers porting
stageguard alone, without touching or regressing any other feature already
present in this repo.

## What stageguard is

`assembly_checkpointing` is a separate, already-published Python package
(`https://github.com/SNH-star/assembly_checkpointing`, branch
`assembly-stageguard`) that wraps SPAdes/MEGAHIT short-read assembly in its
own internal (resumable) Snakemake workflow with checkpoint files at each
assembly stage (e.g. MEGAHIT's k-mer iterations). If the process is killed
(walltime limit, OOM, preemption — all realistic on this PBS cluster),
re-running resumes from the last completed checkpoint instead of restarting
the assembly from scratch.

Aviary's role is purely as a caller: build the right CLI invocation to
`assembly_checkpointing`, point it at aviary's own pixi manifest (so it can
activate the right sub-environment for the assembler), and copy its output
back into the file layout aviary's downstream rules already expect.

## Source of truth

The stageguard-relevant code in `aviary-0.13.3` was introduced by commit
`fd0baef` and has received small refinements since (comments, a
`skip_reads_check` mirroring fix, retry/log-path wiring) as later commits
landed on `main`. **The current `aviary-0.13.3` `HEAD` state of
`aviary/modules/assembly/assembly.smk` and `aviary/pixi.toml` is the
authoritative version to port from** — not the original `fd0baef` diff.

Confirmed NOT part of stageguard (semibin-multi's, or unrelated, and already
current in this repo or out of scope): `binning.smk`, `das_tool.py`,
`aviary.py`, `processor.py`, `template_config.yaml`, `docs/examples.md`,
`README.md`, `web/server.py` (its `CHECKPOINT_RE` is pre-existing Snakemake
checkpoint-log parsing, unrelated to this feature), and the combined
`test/dryrun_stageguard_semibin.sh` / `test/smalltest_stageguard_semibin.sh`
scripts (they exercise semibin-multi scenarios together with stageguard and
reference a specific `/work/microbiome/...` test-data path).

A diff of `assembly.smk` between the two repos' current `HEAD` states shows
only two unrelated pre-existing renames in this repo
(`short_read_mapper` → `short_read_mapper_aligner`,
`long_read_type` → `long_read_type_spades`) outside the stageguard region, so
this ports as a clean addition/replacement with minimal conflict risk.

## Changes

### 1. `aviary/pixi.toml`

- In `[environments]`, immediately after the existing `spades = ["spades",
  "cpu"]` line, add:
  ```toml
  megahit = ["spades", "cpu"]
  stageguard = ["stageguard", "cpu"]
  ```
- Immediately after `[feature.spades.dependencies]`'s block (before
  `[feature.pysam.dependencies]`), add:
  ```toml
  [feature.stageguard.dependencies]
  python = ">=3.8"
  # assembly_checkpointing makes a nested `pixi run` against this manifest, so the
  # in-env pixi must be new enough to parse the rich-platform tables (cuda on
  # platforms entries). Unpinned "*" let a stale 0.69.0 in, which failed with
  # "expected a string, found table". Match [feature.main] >=0.71.
  pixi = ">=0.71"
  snakemake = ">=7,<8"
  snakemake-executor-plugin-cluster-generic = "*"

  [feature.stageguard.pypi-dependencies]
  # On release: publish assembly_checkpointing to PyPI, tag v0.1.0, then replace
  # the git line below with the PyPI spec:
  # assembly-checkpointing = ">=0.1.0"
  assembly-checkpointing = { git = "https://github.com/SNH-star/assembly_checkpointing.git", branch = "assembly-stageguard" }
  ```
  Ported verbatim from source `HEAD`, comments included — they explain a real
  pixi-version pitfall already hit upstream.

### 2. `aviary/modules/assembly/assembly.smk`

- Add near the top (after the existing `pixi_run, setup_log` import):
  ```python
  import importlib.resources
  ...
  with importlib.resources.path("aviary", "pixi.toml") as manifest_path:
      AVIARY_PIXI_MANIFEST = str(manifest_path)
  ```
- Add, near the other module-level validators (`_validate_reads`,
  `_validate_bool`):
  ```python
  NEEDS_READ_CONCATENATION = (
      config["skip_qc"] and
      config["coassemble"] and
      not config["use_megahit"] and
      config["short_reads_1"] != "none" and
      len(config["short_reads_1"]) > 1
  )


  def _stageguard_reads(reads, mate):
      if not config["skip_qc"]:
          return "data/short_reads.fastq.gz" if mate == 1 else "none"

      if reads == "none":
          return "none"

      if not config["coassemble"] or len(reads) == 1:
          return reads[0]

      if config["use_megahit"]:
          return " ".join(reads)

      # SPAdes + multiple readsets: reads are concatenated by concatenate_reads_for_stageguard
      return f"data/short_reads.{mate}.fastq.gz"
  ```
- Add the conditional rule (placed immediately before `assemble_short_reads`,
  matching source layout):
  ```python
  if NEEDS_READ_CONCATENATION:
      rule concatenate_reads_for_stageguard:
          input:
              reads1 = config["short_reads_1"],
              reads2 = config["short_reads_2"] if config["short_reads_2"] != ["none"] else []
          output:
              reads1 = "data/short_reads.1.fastq.gz",
              reads2 = "data/short_reads.2.fastq.gz" if config["short_reads_2"] != ["none"] else []
          log:
              f"{logs_dir}/concatenate_reads_for_stageguard.log"
          shell:
              "cat {input.reads1} > {output.reads1} 2> {log} && "
              "cat {input.reads2} > {output.reads2} 2>> {log}"
  ```
- Replace the body of `rule assemble_short_reads` (input, params, shell) with
  the source `HEAD` version: `qc_reads` gains the `NEEDS_READ_CONCATENATION`
  branch mirroring the concatenation rule's outputs; `params` swaps
  `kmer_sizes`/`use_megahit`/`coassemble`/`tmpdir`/`final_assembly` for
  `short_reads_1`/`short_reads_2` (via `_stageguard_reads`), `assembler`,
  `stageguard_output`, `pixi_manifest`, `pixi_run`, `runtime`; `shell` calls
  `{pixi_run} -e stageguard assembly_checkpointing ...` instead of the old
  `assemble_short_reads.py` script, then copies/reconstructs
  `scaffolds.fasta` + the assembly graph into `data/short_read_assembly/`
  (branching on assembler: direct copy for SPAdes, fastg→gfa reconstruction
  via `megahit_toolkit`/`agtools` for MEGAHIT). Full text as it exists in
  source `HEAD` — no modifications, since it already matches this repo's
  surrounding conventions (`pixi_run`, `setup_log`, `resources.log_path`
  pattern).
- `aviary/modules/assembly/scripts/assemble_short_reads.py` is left in place,
  unreferenced, matching upstream's current state (per user decision — not
  worth diverging from source here).

### 3. `test/test_integration.py`

- Add `import signal` and `import time` to the existing import block (not
  currently imported in this repo's copy).
- Port two test methods verbatim from source `HEAD`, appended in the same
  relative position (end of the assembly-related test methods, before
  `if __name__ == "__main__":`):
  - `test_assembly_stageguard_checkpoint_resume` — runs `aviary assemble
    --use-megahit --skip-qc`, waits for the `k21.done` stageguard checkpoint,
    SIGTERMs the whole process group, restarts, and asserts the final
    assembly exists and every megahit checkpoint file is present.
  - `test_assembly_stageguard_spades_multi_read_coassemble` — runs `aviary
    assemble --skip-qc --coassemble` with two distinct-path readsets and
    asserts both the final assembly and the concatenated intermediate reads
    file exist (exercising `concatenate_reads_for_stageguard`).
  - Both use existing helpers already present in this repo's
    `test_integration.py` (`data`, `setup_output_dir`) — no new test
    infrastructure needed.
- The combined `dryrun_stageguard_semibin.sh` / `smalltest_stageguard_semibin.sh`
  scripts are explicitly **not** ported (per user decision) — they conflate
  semibin-multi scenarios and a hardcoded external data path.

## Out of scope

- Any change to `binning.smk`, `das_tool.py`, `aviary.py`, `processor.py`,
  `template_config.yaml`, `web/server.py`, `README.md`, `docs/examples.md`.
- Adding new user-facing documentation for stageguard (upstream has none
  either; per user decision, skipped here too).
- Deleting `assemble_short_reads.py` (per user decision, left in place).
- Any change to the `assembly_checkpointing` package itself — it is consumed
  as an external git dependency, not vendored into this repo.

## Testing plan

- `pixi run -e dev aviary --help` (or equivalent) after the pixi.toml edit,
  to confirm the manifest still parses and `stageguard`/`megahit`
  environments resolve.
- Dry-run only (`aviary assemble --dry-run ...` with `--use-megahit
  --skip-qc` and separately with `--skip-qc --coassemble` and two readsets)
  to confirm the Snakemake DAG resolves cleanly with the new rule wiring,
  before attempting the full subprocess-level integration tests (which are
  slow/expensive and require the `stageguard` pixi environment to actually
  build, i.e. the external `assembly_checkpointing` dependency to be
  fetchable).
- Run the two ported integration tests
  (`test_assembly_stageguard_checkpoint_resume`,
  `test_assembly_stageguard_spades_multi_read_coassemble`) if the environment
  build succeeds in this sandbox; if pixi can't fetch the git dependency here
  (network-restricted sandbox), note that as a follow-up to run outside the
  sandbox / in CI.

# Port stageguard (assembly checkpointing) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the stageguard (resumable assembly-checkpointing) feature from `aviary-0.13.3` into this repo (`aviary-v0.13.4`), without touching any other feature already present here (semibin-multi and everything else stays as-is).

**Architecture:** Add a new `stageguard` pixi environment wrapping an external, already-published package (`assembly_checkpointing`), then rewrite the `assemble_short_reads` Snakemake rule in `aviary/modules/assembly/assembly.smk` to shell out to that package's CLI instead of running SPAdes/MEGAHIT directly. The package handles resumable checkpointing internally; aviary's job is building the right CLI call and copying results back into the file layout downstream rules already expect. Two integration tests are ported to cover kill/resume and multi-readset coassembly-concatenation.

**Tech Stack:** Snakemake (Python DSL), pixi (environment/dependency manager), pytest/unittest (integration tests), the external `assembly_checkpointing` package (git dependency, not vendored).

**Spec:** `docs/superpowers/specs/2026-08-25-stageguard-port-design.md`

## Global Constraints

- Port verbatim from `aviary-0.13.3` current `HEAD` (not the original `fd0baef` commit — later refinements landed on top of it). Reference commands throughout this plan use `git -C /home/herholdt/aviary-0.13.3 show HEAD:<path>` to pull exact source text.
- Touch only: `aviary/pixi.toml`, `aviary/modules/assembly/assembly.smk`, `test/test_integration.py`. Do not modify `binning.smk`, `das_tool.py`, `aviary.py`, `processor.py`, `template_config.yaml`, `web/server.py`, `README.md`, `docs/examples.md`.
- Do not delete or modify `aviary/modules/assembly/scripts/assemble_short_reads.py` — it becomes unreferenced dead code, left in place per explicit decision.
- Do not port `test/dryrun_stageguard_semibin.sh` or `test/smalltest_stageguard_semibin.sh` — they conflate semibin-multi scenarios and a hardcoded external data path.
- Do not add new user-facing docs for stageguard.
- **Sandbox note:** file writes in this session must go to `/mnt/hpccs01/home/herholdt/aviary-v0.13.4/...`, not the `/home/herholdt/aviary-v0.13.4/...` alias — the latter is read-only in this mqyolo sandbox.
- Never commit without the user's explicit go-ahead for that commit (per this user's global git-workflow rules) — each task below ends with a prepared `git commit` command; run it, but do not push.

---

### Task 1: Add stageguard/megahit pixi environments and dependencies

**Files:**
- Modify: `aviary/pixi.toml:153-154` (environments table), `aviary/pixi.toml:263-271` (feature dependency blocks)

**Interfaces:**
- Produces: two new pixi environments, `megahit` and `stageguard`, and a `[feature.stageguard]` dependency group that Task 2's rule invokes via `pixi_run -e stageguard`.

- [ ] **Step 1: Add the two new environment entries**

In `aviary/pixi.toml`, find this exact block (currently lines 153-154):

```toml
spades = ["spades", "cpu"]
pysam = ["pysam", "cpu"]
```

Replace it with:

```toml
spades = ["spades", "cpu"]
megahit = ["spades", "cpu"]
stageguard = ["stageguard", "cpu"]
pysam = ["pysam", "cpu"]
```

- [ ] **Step 2: Add the `[feature.stageguard]` dependency blocks**

In the same file, find this exact block (currently lines 263-271):

```toml
[feature.spades.dependencies]
python = ">=3.12.0"  # Keep things consistent to aid debugging.
spades = ">=4.0.0"
megahit = ">=1.2.9"
pyyaml = ">=6.0.2"
joblib = ">=1.4.2"
agtools = ">=1.0.0"

[feature.pysam.dependencies]
python = ">=3.6"
```

Replace it with:

```toml
[feature.spades.dependencies]
python = ">=3.12.0"  # Keep things consistent to aid debugging.
spades = ">=4.0.0"
megahit = ">=1.2.9"
pyyaml = ">=6.0.2"
joblib = ">=1.4.2"
agtools = ">=1.0.0"

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

[feature.pysam.dependencies]
python = ">=3.6"
```

- [ ] **Step 3: Verify the manifest still parses as valid TOML**

Run:
```bash
python3 -c "import tomllib; tomllib.load(open('aviary/pixi.toml','rb')); print('TOML OK')"
```
Expected: `TOML OK` with no exception. (This only checks syntax — full dependency resolution happens in Task 4, since it requires network access to fetch the external git dependency.)

- [ ] **Step 4: Commit**

```bash
git add aviary/pixi.toml
git commit -m "feat: add stageguard and megahit pixi environments"
```

---

### Task 2: Wire assemble_short_reads to the stageguard CLI in assembly.smk

**Files:**
- Modify: `aviary/modules/assembly/assembly.smk:1-3` (imports/manifest lookup), `aviary/modules/assembly/assembly.smk:28-33` (helpers, after `_validate_bool`, before `SHORT_READS_1 = ...`), `aviary/modules/assembly/assembly.smk:545-586` (the `assemble_short_reads` rule and its new sibling rule)

**Interfaces:**
- Consumes: `pixi_run` (already imported from `aviary.modules.common` at line 2), `setup_log` (same import), `config[...]` dict entries `skip_qc`, `coassemble`, `use_megahit`, `short_reads_1`, `short_reads_2`, `max_memory` (all pre-existing in this repo's config schema — no config schema changes needed).
- Produces: `AVIARY_PIXI_MANIFEST` (str, absolute path to `aviary/pixi.toml`), `NEEDS_READ_CONCATENATION` (bool), `_stageguard_reads(reads, mate)` (str) — all module-level in `assembly.smk`, usable by the rules defined later in the same file. Rule `concatenate_reads_for_stageguard` (conditional on `NEEDS_READ_CONCATENATION`) produces `data/short_reads.1.fastq.gz` and (when `short_reads_2` is set) `data/short_reads.2.fastq.gz`. Rule `assemble_short_reads` continues to produce `data/short_read_assembly/scaffolds.fasta` and `SHORT_ASSEMBLY_GRAPH` exactly as before — no change to what downstream rules consume.

- [ ] **Step 1: Add the pixi manifest lookup**

In `aviary/modules/assembly/assembly.smk`, find this exact block (currently lines 1-3):

```python
ASSEMBLY_SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(workflow.snakefile)), 'scripts')
from aviary.modules.common import pixi_run, setup_log
logs_dir = "logs"
```

Replace it with:

```python
ASSEMBLY_SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(workflow.snakefile)), 'scripts')
import importlib.resources
from aviary.modules.common import pixi_run, setup_log
logs_dir = "logs"

with importlib.resources.path("aviary", "pixi.toml") as manifest_path:
    AVIARY_PIXI_MANIFEST = str(manifest_path)
```

- [ ] **Step 2: Add the stageguard read-selection helpers**

In the same file, find this exact block (the end of `_validate_bool`, immediately before `SHORT_READS_1 = config['short_reads_1']`):

```python
def _validate_bool(value, key):
    if isinstance(value, bool):
        return value
    raise Exception(f"Programming error: config[{key!r}] must be a boolean.")


SHORT_READS_1 = config['short_reads_1']
```

Replace it with:

```python
def _validate_bool(value, key):
    if isinstance(value, bool):
        return value
    raise Exception(f"Programming error: config[{key!r}] must be a boolean.")


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


SHORT_READS_1 = config['short_reads_1']
```

- [ ] **Step 3: Replace the `assemble_short_reads` rule and add `concatenate_reads_for_stageguard`**

In the same file, find this exact block (currently lines 545-586 — the comment, then the whole `assemble_short_reads` rule):

```python
# Perform short read assembly only with no other steps
rule assemble_short_reads:
    input:
        qc_reads = config["short_reads_1"] if config["skip_qc"] else "data/short_reads.fastq.gz",
    output:
        fasta = "data/short_read_assembly/scaffolds.fasta",
        # We cannot mark the output_folder as temp as then it gets deleted,
        # causing the "TypeError: '>' not supported between instances of
        # 'TBDString' and 'int'" error
        output_folder = directory("data/short_read_assembly/"),
        graph = SHORT_ASSEMBLY_GRAPH
        # reads1 = temporary("data/short_reads.1.fastq.gz"),
        # reads2 = temporary("data/short_reads.2.fastq.gz")
    params:
        short_reads_1 = ",".join(config["short_reads_1"]) if config["skip_qc"] else "data/short_reads.fastq.gz",
        short_reads_2 = ",".join(config["short_reads_2"]) if config["skip_qc"] else "none",
        max_memory = config["max_memory"],
        kmer_sizes = config["kmer_sizes"],
        use_megahit = config["use_megahit"],
        coassemble = config["coassemble"],
        tmpdir = f"--tmp-dir {config['tmpdir']}" if 'tmpdir' in config and config['tmpdir'] else "",
        final_assembly = True
    threads:
        config["max_threads"]
    resources:
        mem_mb = lambda wildcards, attempt: min(int(config["max_memory"])*1024, 512*1024*attempt),
        runtime = lambda wildcards, attempt: 72*60 + 24*60*attempt,
        log_path = lambda wildcards, attempt: setup_log(f"{logs_dir}/assemble_short_reads", attempt),
    benchmark:
        "benchmarks/short_read_assembly_short.benchmark.txt"
    shell:
        f'{pixi_run} -e spades {ASSEMBLY_SCRIPTS_DIR}/'+\
        """assemble_short_reads.py \
        --short-reads-1 {params.short_reads_1} \
        --short-reads-2 {params.short_reads_2} \
        --max-memory {config[max_memory]} \
        --use-megahit {params.use_megahit} \
        --coassemble {params.coassemble} \
        --threads {threads} \
        {params.tmpdir} \
        --kmer-sizes {params.kmer_sizes} \
        --log {resources.log_path}
        """
```

Replace it with:

```python
# Perform short read assembly only with no other steps
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


rule assemble_short_reads:
    input:
        qc_reads = (
            # Mirror the concatenate_reads_for_stageguard outputs: reads2 only exists
            # when short_reads_2 is provided (single-end coassembly produces reads1 only).
            (["data/short_reads.1.fastq.gz"]
             + (["data/short_reads.2.fastq.gz"] if config["short_reads_2"] != ["none"] else []))
            if NEEDS_READ_CONCATENATION
            else config["short_reads_1"] if config["skip_qc"]
            else "data/short_reads.fastq.gz"
        ),
    output:
        fasta = "data/short_read_assembly/scaffolds.fasta",
        # We cannot mark the output_folder as temp as then it gets deleted,
        # causing the "TypeError: '>' not supported between instances of
        # 'TBDString' and 'int'" error
        output_folder = directory("data/short_read_assembly/"),
        graph = SHORT_ASSEMBLY_GRAPH
        # reads1 = temporary("data/short_reads.1.fastq.gz"),
        # reads2 = temporary("data/short_reads.2.fastq.gz")
    params:
        short_reads_1 = _stageguard_reads(config["short_reads_1"], 1),
        short_reads_2 = _stageguard_reads(config["short_reads_2"], 2),
        max_memory = config["max_memory"],
        assembler = "megahit" if config["use_megahit"] else "spades",
        stageguard_output = "data/stageguard_short_read_assembly",
        pixi_manifest = AVIARY_PIXI_MANIFEST,
        pixi_run = pixi_run,
        runtime = "48h",
    threads:
        config["max_threads"]
    resources:
        mem_mb = lambda wildcards, attempt: min(int(config["max_memory"])*1024, 512*1024*attempt),
        runtime = lambda wildcards, attempt: 72*60 + 24*60*attempt,
        log_path = lambda wildcards, attempt: setup_log(f"{logs_dir}/assemble_short_reads", attempt),
    benchmark:
        "benchmarks/short_read_assembly_short.benchmark.txt"
    shell:
        f'{pixi_run} -e stageguard '+\
        """assembly_checkpointing \
        --assembler {params.assembler} \
        --r1 "{params.short_reads_1}" \
        --r2 "{params.short_reads_2}" \
        --output-directory {params.stageguard_output} \
        --threads {threads} \
        --cores {threads} \
        --jobs 1 \
        --mem-mb {resources.mem_mb} \
        --runtime {params.runtime} \
        --pixi-manifest {params.pixi_manifest} \
        --snakemake-args=--nolock \
        >> {resources.log_path} 2>&1 && \
        mkdir -p data/short_read_assembly && \
        if [ "{params.assembler}" = "megahit" ]; then \
            cp {params.stageguard_output}/megahit/assembly_output/final.contigs.fa {output.fasta}; \
            intermediate_dir="{params.stageguard_output}/megahit/assembly_output/intermediate_contigs"; \
            max_kmer=$(find "$intermediate_dir" -name 'k*.contigs.fa' -printf '%f\n' | sed 's/^k//; s/\\.contigs\\.fa$//' | sort -n | tail -1); \
            {params.pixi_run} -e spades megahit_toolkit contig2fastg "$max_kmer" "$intermediate_dir/k${{max_kmer}}.contigs.fa" > "$intermediate_dir/k${{max_kmer}}.fastg" 2>> {resources.log_path}; \
            mkdir -p data/short_read_assembly/gfa_tmp; \
            {params.pixi_run} -e spades agtools fastg2gfa --graph "$intermediate_dir/k${{max_kmer}}.fastg" -o data/short_read_assembly/gfa_tmp 2>> {resources.log_path}; \
            mv data/short_read_assembly/gfa_tmp/converted_graph.gfa {output.graph}; \
            rm -rf data/short_read_assembly/gfa_tmp; \
        else \
            cp {params.stageguard_output}/spades/assembly_output/scaffolds.fasta {output.fasta}; \
            cp {params.stageguard_output}/spades/assembly_output/assembly_graph_with_scaffolds.gfa {output.graph}; \
        fi
        """
```

**Note for the executor:** the line `max_kmer=$(find "$intermediate_dir" ... -printf '%f\n' ...)` contains a literal `\n` inside the Snakemake triple-quoted Python string — copy it exactly as shown (it is `%f` followed by a backslash-n inside the shell `-printf` format string, not a Python newline escape at that position). If your editor auto-reformats backslashes, diff the result against `git -C /home/herholdt/aviary-0.13.3 show HEAD:aviary/modules/assembly/assembly.smk | sed -n '627,660p'` to confirm an exact match.

- [ ] **Step 4: Verify the DAG resolves — MEGAHIT, single readset, skip-qc**

Run:
```bash
mkdir -p /tmp/stageguard-dryrun-1
pixi run -e dev aviary assemble \
  -1 test/data/wgsim.1.fq.gz \
  -2 test/data/wgsim.2.fq.gz \
  --use-megahit --skip-qc \
  -o /tmp/stageguard-dryrun-1/out \
  -n 2 -t 2 \
  --dry-run
```
Expected: exits 0, the printed job list includes `assemble_short_reads`, and does **not** include `concatenate_reads_for_stageguard` (single readset, so `NEEDS_READ_CONCATENATION` is `False`).

- [ ] **Step 5: Verify the DAG resolves — SPAdes, multi-readset coassembly, skip-qc**

Run:
```bash
mkdir -p /tmp/stageguard-dryrun-2
cp test/data/wgsim.1.fq.gz /tmp/stageguard-dryrun-2/reads2.1.fq.gz
cp test/data/wgsim.2.fq.gz /tmp/stageguard-dryrun-2/reads2.2.fq.gz
pixi run -e dev aviary assemble \
  -1 test/data/wgsim.1.fq.gz /tmp/stageguard-dryrun-2/reads2.1.fq.gz \
  -2 test/data/wgsim.2.fq.gz /tmp/stageguard-dryrun-2/reads2.2.fq.gz \
  --skip-qc --coassemble \
  -o /tmp/stageguard-dryrun-2/out \
  -n 2 -t 2 \
  --dry-run
```
Expected: exits 0, the printed job list includes both `concatenate_reads_for_stageguard` and `assemble_short_reads` (two distinct-path readsets force `NEEDS_READ_CONCATENATION` to `True` — using two copies of the same file under different paths, matching the source repo's own test technique, since aviary deduplicates identical paths).

If either dry-run fails, fix the `assembly.smk` edit before proceeding — do not commit a rule that fails to resolve its own DAG.

- [ ] **Step 6: Commit**

```bash
git add aviary/modules/assembly/assembly.smk
git commit -m "feat: wire assemble_short_reads to the stageguard checkpointing CLI"
```

---

### Task 3: Port the stageguard integration tests

**Files:**
- Modify: `test/test_integration.py:24-32` (imports), `test/test_integration.py` (append two new methods to `class Tests(unittest.TestCase)`, immediately after the existing `test_error_integration` method and before `if __name__ == "__main__":`)

**Interfaces:**
- Consumes: `data` (module-level constant, `test/test_integration.py:34`), `setup_output_dir(output_dir)` (existing helper, `test/test_integration.py:44`) — both already present in this repo, unchanged.
- Produces: two new test methods, `test_assembly_stageguard_checkpoint_resume` and `test_assembly_stageguard_spades_multi_read_coassemble`, collectible by pytest.

- [ ] **Step 1: Add the missing imports**

In `test/test_integration.py`, find this exact block (currently lines 24-32):

```python
import pytest
import os
import os.path
import subprocess
import shutil
import unittest
import glob
import random
import re
```

Replace it with:

```python
import pytest
import os
import os.path
import subprocess
import shutil
import unittest
import glob
import random
import re
import signal
import time
```

- [ ] **Step 2: Append the two test methods**

Find the end of `test_error_integration` (the last few lines of the method, currently ending right before the blank line and `if __name__ == "__main__":`):

```python
        # One of the printed log paths should match an existing file
        printed_paths = re.findall(r"BEGIN LOG \([^)]*\):\s*(.*?)\s*=====", combined)
        if printed_paths:
            # Normalize whitespace and test for existence of at least one printed log
            self.assertTrue(any(os.path.exists(p.strip()) for p in printed_paths))

if __name__ == "__main__":
```

Replace it with (inserting the two new methods, still indented as class methods, before `if __name__ == "__main__":`):

```python
        # One of the printed log paths should match an existing file
        printed_paths = re.findall(r"BEGIN LOG \([^)]*\):\s*(.*?)\s*=====", combined)
        if printed_paths:
            # Normalize whitespace and test for existence of at least one printed log
            self.assertTrue(any(os.path.exists(p.strip()) for p in printed_paths))

    def test_assembly_stageguard_checkpoint_resume(self):
        """Verify that aviary assembly resumes correctly after SIGTERM mid-run.

        Starts aviary assemble with megahit (skip-qc for speed), kills it after
        the first stageguard checkpoint done file appears, then restarts. The
        second run must resume from the checkpoint and produce a valid assembly.
        """
        output_dir = os.path.join("example", "test_assembly_stageguard_resume")
        setup_output_dir(output_dir)
        aviary_out = os.path.join(output_dir, "aviary_out")

        stageguard_done_dir = os.path.join(
            aviary_out, "data", "stageguard_short_read_assembly", "megahit", "done"
        )
        # Watch for k21.done: triggered when megahit finishes the k21 iteration
        # and starts k29. At this point megahit has written k21 intermediate
        # files, so --continue can genuinely resume from k29.
        kill_checkpoint = os.path.join(stageguard_done_dir, "k21.done")
        final_assembly = os.path.join(aviary_out, "data", "final_contigs.fasta")

        base_cmd = (
            f"aviary assemble "
            f"-o {aviary_out} "
            f"-1 {data}/wgsim.1.fq.gz "
            f"-2 {data}/wgsim.2.fq.gz "
            f"--use-megahit --skip-qc "
            f"-n 32 -t 32 "
        )

        # ── Phase 1: start aviary, kill the whole process group once k21 is done ──
        # start_new_session=True puts aviary and all its children (inner snakemake,
        # megahit) in a new process group so os.killpg reaches them all.
        proc = subprocess.Popen(base_cmd, shell=True, start_new_session=True)
        deadline = time.time() + 1800  # 30-minute safety timeout

        while not os.path.exists(kill_checkpoint):
            if time.time() > deadline:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                self.fail("Timed out waiting for stageguard k21 checkpoint")
            rc = proc.poll()
            if rc is not None:
                # Aviary finished before we could catch it — only acceptable if
                # it completed successfully (fast machine / tiny dataset).
                if rc == 0 and os.path.isfile(final_assembly):
                    self.skipTest(
                        "Aviary completed before k21 checkpoint could be caught; "
                        "resume test skipped (try on a slower machine or larger dataset)"
                    )
                self.fail(
                    f"Aviary exited with rc={rc} before k21 checkpoint appeared"
                )
            time.sleep(5)

        # Kill the entire process group (aviary + inner snakemake + megahit).
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass  # already exited
        try:
            proc.wait(timeout=60)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()

        # Aviary uses --nolock so no Snakemake lock remains; clear it anyway
        # in case the lock behaviour changes.
        lock_dir = os.path.join(aviary_out, ".snakemake", "locks")
        if os.path.exists(lock_dir):
            shutil.rmtree(lock_dir)

        # ── Phase 2: restart — must resume from the existing checkpoint ──────
        subprocess.run(base_cmd, shell=True, check=True)

        self.assertTrue(
            os.path.isfile(final_assembly),
            "Final assembly missing after stageguard checkpoint resume",
        )

        # Every megahit checkpoint done file must be present after a full run.
        # Note: preprocess2 was removed — megahit internally checkpoints k21 before
        # printing 'Start assembly', so --continue skips k21 and there is no reachable
        # string to intercept between preprocess and k29 starting.
        megahit_checkpoints = [
            "preprocess", "k21", "k29", "k39", "k59", "k79", "k99", "done"
        ]
        for cp in megahit_checkpoints:
            self.assertTrue(
                os.path.exists(os.path.join(stageguard_done_dir, f"{cp}.done")),
                f"Checkpoint {cp}.done missing after resume",
            )

    def test_assembly_stageguard_spades_multi_read_coassemble(self):
        """Verify SPAdes coassembly with skip-qc and multiple readsets works.

        This tests the concatenate_reads_for_stageguard rule which was added to
        replace the old assemble_short_reads.py concatenation behaviour. Two
        distinct file paths are required — aviary deduplicates identical paths,
        which would collapse the readsets to one and skip concatenation.
        """
        output_dir = os.path.join("example", "test_assembly_stageguard_spades_coassemble")
        setup_output_dir(output_dir)
        aviary_out = os.path.join(output_dir, "aviary_out")

        # Create copies of the test reads under distinct paths so aviary sees
        # two separate readsets and does not deduplicate them.
        reads2_1 = os.path.join(output_dir, "reads2.1.fq.gz")
        reads2_2 = os.path.join(output_dir, "reads2.2.fq.gz")
        shutil.copy(f"{data}/wgsim.1.fq.gz", reads2_1)
        shutil.copy(f"{data}/wgsim.2.fq.gz", reads2_2)

        final_assembly = os.path.join(aviary_out, "data", "final_contigs.fasta")
        concatenated_reads = os.path.join(aviary_out, "data", "short_reads.1.fastq.gz")

        subprocess.run(
            f"aviary assemble "
            f"-o {aviary_out} "
            f"-1 {data}/wgsim.1.fq.gz {reads2_1} "
            f"-2 {data}/wgsim.2.fq.gz {reads2_2} "
            f"--skip-qc --coassemble "
            f"-n 32 -t 32 ",
            shell=True, check=True
        )

        self.assertTrue(
            os.path.isfile(final_assembly),
            "Final assembly missing after SPAdes multi-read coassemble with skip-qc"
        )
        self.assertTrue(
            os.path.isfile(concatenated_reads),
            "Concatenated reads file missing — concatenate_reads_for_stageguard did not run"
        )

if __name__ == "__main__":
```

- [ ] **Step 3: Verify the new tests are collected without errors**

Run:
```bash
pixi run -e dev pytest test/test_integration.py --collect-only -k stageguard -v
```
Expected: both `test_assembly_stageguard_checkpoint_resume` and `test_assembly_stageguard_spades_multi_read_coassemble` are listed, no collection errors. This confirms the file parses and the imports resolve — it does **not** run the (slow, subprocess-heavy) tests themselves; that happens in Task 4 once the `stageguard` pixi environment is confirmed buildable.

- [ ] **Step 4: Commit**

```bash
git add test/test_integration.py
git commit -m "test: port stageguard checkpoint-resume and multi-read coassemble integration tests"
```

---

### Task 4: Full environment build and integration test verification

**Files:** none (verification only — no code changes expected; this task only produces a commit if `aviary/pixi.lock` changes)

**Interfaces:**
- Consumes: everything from Tasks 1-3.
- Produces: confirmation that the `stageguard` pixi environment actually solves and installs (requires network access to fetch the external `assembly_checkpointing` git dependency), and, if the sandbox allows it, a passing run of the two ported integration tests.

- [ ] **Step 1: Attempt to build the stageguard environment**

Run:
```bash
pixi install -e stageguard
```
Expected: solves and installs successfully, pulling `assembly_checkpointing` from `https://github.com/SNH-star/assembly_checkpointing.git` (branch `assembly-stageguard`).

If this fails specifically due to network restrictions in this sandbox (not a config error — check the failure message for DNS/connection errors vs. a genuine dependency conflict), stop here and report it as a known follow-up: this step must be re-run outside the sandbox (interactive HPC session or CI) before the feature can be considered fully verified. Do not attempt to work around a network failure by vendoring the dependency or editing `pixi.toml` further — that would be a scope change requiring its own sign-off.

- [ ] **Step 2: If Step 1 succeeded, check whether `aviary/pixi.lock` changed**

Run:
```bash
git status --short aviary/pixi.lock
```
If it shows as modified, commit it:
```bash
git add aviary/pixi.lock
git commit -m "chore: update pixi.lock for stageguard environment"
```

- [ ] **Step 3: If Step 1 succeeded, run the two ported integration tests**

Run:
```bash
pixi run -e dev pytest test/test_integration.py -k stageguard -v --run-expensive
```
Expected: both tests pass. `test_assembly_stageguard_checkpoint_resume` takes up to ~30 minutes (it waits for a real MEGAHIT checkpoint, kills the process group, and restarts); `test_assembly_stageguard_spades_multi_read_coassemble` is faster. If `--run-expensive` isn't a recognized flag in this repo's pytest config, check `test/test_integration.py`'s existing `@pytest.mark` usage near the top of the file and match whatever gating convention is already used for the other slow tests in this file (e.g. `test_error_integration`).

If Step 1 failed due to network restrictions, skip this step and report Task 4 as partially complete: config and rule wiring verified (Tasks 1-3's dry-runs passed), but full external-dependency install and the two integration tests still need to be run in an environment with network access.

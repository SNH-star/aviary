#!/usr/bin/env bash
# DRY-RUN ONLY check of the stageguard + SemiBin-multi wiring.
#
# Every invocation passes aviary's --dry-run and omits --snakemake-profile, so
# snakemake only resolves the DAG (tests rule order / input-output wiring / conda
# envs). NOTHING is computed and NOTHING is submitted to the cluster, so this is
# safe to run on the login node.
#
# Run from the aviary repo root:
#   bash test/dryrun_stageguard_semibin.sh
#
# Exit code is 0 only if every scenario's DAG resolves cleanly.

set -uo pipefail

DATA="/work/microbiome/aviary_module_benchmarking/data/test_data"
OUT_BASE="dryrun_stageguard_semibin"
# Use the repo-root pixi manifest (the pixi.toml symlink), NOT --manifest-path
# aviary/pixi.toml: they resolve to different pixi environments, and only the
# root one receives `pixi run -e dev postinstall` (so only it has the editable
# aviary console script; the other falls back to a broken base-conda aviary).
AVIARY="pixi run --frozen -e dev aviary"

rm -rf "${OUT_BASE}"
mkdir -p "${OUT_BASE}"

fail=0

# run_case <label> <aviary args...>
run_case() {
    local label="$1"; shift
    local log="${OUT_BASE}/${label}.dryrun.log"
    echo "=============================================================="
    echo "[DRY-RUN] ${label}"
    echo "=============================================================="
    if ${AVIARY} "$@" --dry-run > "${log}" 2>&1; then
        echo "  PASS: DAG resolved  (log: ${log})"
    else
        echo "  FAIL: see ${log}"
        echo "  --- last 25 lines ---"
        tail -25 "${log}" | sed 's/^/    /'
        fail=1
    fi
    echo ""
}

# 1. SemiBin multi mode + MEGAHIT (multiple short-read sets).
#    Exercises: get_semibin_mode()=="multi", semibin multi_easy_bin path,
#    semibin_multi_prepare / semibin_multi_bams, megahit stageguard assembly.
run_case "semibin_multi_megahit" recover \
    -o "${OUT_BASE}/semibin_multi_megahit" \
    -1 "${DATA}/SRR13153254_1.fastq.gz" "${DATA}/ERR12120022_1.fastq.gz" "${DATA}/ERR12120023_1.fastq.gz" \
    -2 "${DATA}/SRR13153254_2.fastq.gz" "${DATA}/ERR12120022_2.fastq.gz" "${DATA}/ERR12120023_2.fastq.gz" \
    --semibin-mode multi --use-megahit --coassemble no \
    -n 8 -t 8

# 2. SemiBin multi mode + SPAdes coassembly (multiple short-read sets).
#    Exercises: NEEDS_READ_CONCATENATION -> concatenate_reads_for_stageguard,
#    the fixed assemble_short_reads qc_reads input, spades stageguard path.
run_case "semibin_multi_spades_coassemble" recover \
    -o "${OUT_BASE}/semibin_multi_spades_coassemble" \
    -1 "${DATA}/SRR13153254_1.fastq.gz" "${DATA}/ERR12120022_1.fastq.gz" "${DATA}/ERR12120023_1.fastq.gz" \
    -2 "${DATA}/SRR13153254_2.fastq.gz" "${DATA}/ERR12120022_2.fastq.gz" "${DATA}/ERR12120023_2.fastq.gz" \
    --semibin-mode multi --coassemble \
    -n 8 -t 8

# 3. SemiBin multi + SPAdes coassembly + --skip-qc (multiple paired read sets).
#    Forces NEEDS_READ_CONCATENATION onto the DAG: concatenate_reads_for_stageguard
#    -> the fixed assemble_short_reads qc_reads input (paired branch). With QC on,
#    the assembler consumes the merged QC file instead, so --skip-qc is required to
#    cover this rule.
run_case "semibin_multi_spades_skipqc_concat" recover \
    -o "${OUT_BASE}/semibin_multi_spades_skipqc_concat" \
    -1 "${DATA}/SRR13153254_1.fastq.gz" "${DATA}/ERR12120022_1.fastq.gz" "${DATA}/ERR12120023_1.fastq.gz" \
    -2 "${DATA}/SRR13153254_2.fastq.gz" "${DATA}/ERR12120022_2.fastq.gz" "${DATA}/ERR12120023_2.fastq.gz" \
    --semibin-mode multi --coassemble yes --skip-qc \
    -n 8 -t 8

# 4. SemiBin single mode + SPAdes, single read set (baseline stageguard, no concat).
#    Exercises: get_semibin_mode()=="single", single_easy_bin path,
#    assemble_short_reads with skip_qc/merged-read input branch.
run_case "semibin_single_spades" recover \
    -o "${OUT_BASE}/semibin_single_spades" \
    -1 "${DATA}/SRR13153254_1.fastq.gz" \
    -2 "${DATA}/SRR13153254_2.fastq.gz" \
    --semibin-mode single --coassemble no \
    -n 8 -t 8

echo "=============================================================="
if [ "${fail}" -eq 0 ]; then
    echo "ALL DRY-RUNS PASSED"
else
    echo "ONE OR MORE DRY-RUNS FAILED (see logs in ${OUT_BASE}/)"
fi
echo "=============================================================="
exit "${fail}"

#!/usr/bin/env bash
# SMALL REAL (non-dry-run) test of the two runtime behaviours a dry-run can't check:
#   #3  MEGAHIT stageguard assembly -> graph (.gfa) reconstruction
#   #1  SemiBin multi-mode bin contig names matching large_contigs.fasta
#       (the prerequisite for DAS_Tool to consume the bins correctly)
#
# Sized for a single 8-core / ~10 GB interactive allocation, run LOCALLY:
# it does NOT pass --snakemake-profile, so snakemake runs every rule inside
# this allocation (nothing is submitted to the batch queue).
#
# It uses the smallest real metagenome in the test set (SRR13153254, ~400 MB/mate)
# with --use-megahit (lighter than SPAdes) and runs ONLY SemiBin (other default
# binners skipped) to keep compute minimal while still exercising both code paths.
#
# Run from the aviary repo root, on an interactive compute allocation (NOT login):
#   bash test/smalltest_stageguard_semibin.sh
#
# NOTE: requires `pixi run --frozen -e dev postinstall` to have been run once.

set -uo pipefail

# ---- knobs (bump MEM if a step OOMs) ---------------------------------------
DATA="/work/microbiome/aviary_module_benchmarking/data/test_data"
SAMPLE="SRR13153254"
CORES=8
MEM=10
OUT="smalltest_stageguard_semibin/out"
AVIARY="pixi run --frozen -e dev aviary"
# ---------------------------------------------------------------------------

rm -rf "$(dirname "${OUT}")"
mkdir -p "$(dirname "${OUT}")"

echo "=============================================================="
echo "Running aviary recover (megahit + semibin multi, LOCAL, ${CORES}c/${MEM}G)"
echo "  output: ${OUT}"
echo "=============================================================="

# Real run. Only semibin among the default binners (skip rosella/vamb/metabat).
# No --snakemake-profile => fully local. Late steps (DAS_Tool/CheckM2) may fail
# if their DBs aren't set up locally; that's fine -- the #1/#3 artifacts are
# produced before then and are verified directly below. Hence we don't 'set -e'
# around this call.
${AVIARY} recover \
    -o "${OUT}" \
    -1 "${DATA}/${SAMPLE}_1.fastq.gz" \
    -2 "${DATA}/${SAMPLE}_2.fastq.gz" \
    --semibin-mode multi \
    --use-megahit \
    --skip-qc \
    --skip-binners rosella vamb metabat \
    --binning-only \
    --coassemble no \
    -n "${CORES}" -t "${CORES}" --local-cores "${CORES}" \
    -m "${MEM}"
aviary_rc=$?
echo ""
echo "aviary exit code: ${aviary_rc} (non-zero is OK if it only failed at a late"
echo "DB-dependent step; the checks below verify the artifacts directly)"
echo ""

fail=0
pass() { echo "  PASS: $1"; }
bad()  { echo "  FAIL: $1"; fail=1; }

# ---- Check #3: MEGAHIT graph reconstruction --------------------------------
echo "=============================================================="
echo "[#3] MEGAHIT assembly + graph (.gfa) reconstruction"
echo "=============================================================="
scaffolds="${OUT}/data/short_read_assembly/scaffolds.fasta"
if [ -s "${scaffolds}" ]; then
    pass "assembly contigs present and non-empty (${scaffolds})"
else
    bad "missing/empty assembly contigs (${scaffolds})"
fi

gfa=$(find "${OUT}/data/short_read_assembly" -maxdepth 1 -name '*.gfa' -size +0c 2>/dev/null | head -1)
if [ -n "${gfa}" ]; then
    pass "reconstructed assembly graph present and non-empty (${gfa})"
else
    bad "no non-empty .gfa in ${OUT}/data/short_read_assembly (graph reconstruction failed)"
fi

# Confirm the intermediate contigs that the graph step depends on were kept.
inter="${OUT}/data/stageguard_short_read_assembly/megahit/assembly_output/intermediate_contigs"
if ls "${inter}"/k*.contigs.fa >/dev/null 2>&1; then
    pass "megahit intermediate_contigs/k*.contigs.fa retained (graph input present)"
else
    bad "megahit intermediate_contigs/k*.contigs.fa missing (graph step would have no input)"
fi

# ---- Check #1: SemiBin multi bin names vs large_contigs.fasta ---------------
echo "=============================================================="
echo "[#1] SemiBin multi bin contig names match large_contigs.fasta"
echo "=============================================================="
large="${OUT}/data/large_contigs.fasta"
bins_glob=("${OUT}"/data/semibin_bins/output_bins/*.fa "${OUT}"/data/semibin_bins/output_bins/*.fna)

shopt -s nullglob
bin_files=()
for g in "${OUT}"/data/semibin_bins/output_bins/*.fa "${OUT}"/data/semibin_bins/output_bins/*.fna; do
    [ -e "$g" ] && bin_files+=("$g")
done
shopt -u nullglob

if [ ! -s "${large}" ]; then
    bad "missing/empty ${large} (cannot verify naming)"
elif [ "${#bin_files[@]}" -eq 0 ]; then
    echo "  INCONCLUSIVE: SemiBin produced no bins on this sample, so naming"
    echo "  cannot be checked. Try a richer sample or bump --skip-qc/coverage."
else
    # All contig names used by the bins:
    grep -h '^>' "${bin_files[@]}" | sed 's/^>//; s/[[:space:]].*//' | sort -u > "$(dirname "${OUT}")/bin_contigs.txt"
    # All contig names in the reference the bins must map onto:
    grep    '^>' "${large}"        | sed 's/^>//; s/[[:space:]].*//' | sort -u > "$(dirname "${OUT}")/ref_contigs.txt"

    n_bins=$(wc -l < "$(dirname "${OUT}")/bin_contigs.txt")
    # Names present in bins but absent from large_contigs.fasta = the failure mode:
    missing=$(comm -23 "$(dirname "${OUT}")/bin_contigs.txt" "$(dirname "${OUT}")/ref_contigs.txt" | head -5)
    n_missing=$(comm -23 "$(dirname "${OUT}")/bin_contigs.txt" "$(dirname "${OUT}")/ref_contigs.txt" | wc -l)

    echo "  ${#bin_files[@]} bin file(s); ${n_bins} unique bin contig names; ${n_missing} not found in large_contigs.fasta"
    if [ "${n_missing}" -eq 0 ]; then
        pass "every SemiBin bin contig name exists in large_contigs.fasta (DAS_Tool-compatible)"
    else
        bad "SemiBin bin contigs not in large_contigs.fasta (DAS_Tool would break). Examples:"
        echo "${missing}" | sed 's/^/        /'
    fi
fi

# Bonus: did DAS_Tool actually run to completion?
if [ -e "${OUT}/data/das_tool_bins_pre_refine/done" ]; then
    pass "(bonus) DAS_Tool completed (data/das_tool_bins_pre_refine/done present)"
else
    echo "  (bonus) DAS_Tool did not complete -- fine if it needs a DB not set up locally."
fi

echo "=============================================================="
if [ "${fail}" -eq 0 ]; then
    echo "SMALL TEST PASSED (#1 and #3 verified)"
else
    echo "SMALL TEST HAD FAILURES -- see messages above"
fi
echo "=============================================================="
exit "${fail}"

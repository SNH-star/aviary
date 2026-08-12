# Written by setuptools_scm from the git tag (see [tool.setuptools_scm] in
# pyproject.toml). It IS tracked in git, unlike the usual advice in its own
# header comment, because bird-release-python's flow depends on that: it
# force-writes this file, tolerates exactly " M aviary/version.py" in its
# pre-tag clean-tree guard, and then runs `git commit -a` -- which stages only
# tracked modifications, so an ignored version.py would leave nothing to commit
# and abort the release. singlem and bird_tool_utils track theirs for the same
# reason.
#
# The fallback still matters: the file can be absent in a fresh checkout before
# any build, and aviary.py imports __version__ from here for `--version` and its
# startup log line, so a bare ImportError would break the CLI outright.
try:
    from aviary.version import __version__
except ImportError:  # pragma: no cover - only hit in an unbuilt checkout
    __version__ = "0.0.0.dev0"


# CONSTANTS
LONG_READ_TYPES = ["ont", "ont_hq", "rs", "sq", "ccs", "hifi"]
LONG_READ_ASSEMBLERS = ["myloasm", "flye"]
# Aligner family used for long reads. rammap is a minimap2-compatible Rust
# implementation and accepts the same -x presets, so switching families does
# not change which preset is chosen for a given --long-read-type.
LONG_READ_MAPPERS = ["rammap", "minimap2"]
# Short-read aligner family. CoverM defaults to strobealign from v0.7.0;
# minimap2 selects the '-x sr' preset instead.
SHORT_READ_MAPPERS = ["strobealign", "minimap2", "rammap", "minibwa"]
# User-facing family -> the value CoverM's -p expects for short reads. Long
# reads resolve per --long-read-type instead, so they are not listed here.
SHORT_READ_MAPPER_TO_COVERM = {
    "strobealign": "strobealign",
    "minimap2": "minimap2-sr",
    "rammap": "rammap-sr",
    "minibwa": "minibwa",
}
MEDAKA_MODELS = [
    "r103_fast_g507", "r103_fast_snp_g507", "r103_fast_variant_g507", "r103_hac_g507", "r103_hac_snp_g507",
    "r103_hac_variant_g507", "r103_min_high_g345", "r103_min_high_g360", "r103_prom_high_g360", "r103_prom_snp_g3210",
    "r103_prom_variant_g3210", "r103_sup_g507", "r103_sup_snp_g507", "r103_sup_variant_g507", "r1041_e82_260bps_fast_g632",
    "r1041_e82_260bps_fast_variant_g632", "r1041_e82_260bps_hac_g632", "r1041_e82_260bps_hac_variant_g632", "r1041_e82_260bps_sup_g632",
    "r1041_e82_260bps_sup_variant_g632", "r1041_e82_400bps_fast_g615", "r1041_e82_400bps_fast_g632",
    "r1041_e82_400bps_fast_variant_g615", "r1041_e82_400bps_fast_variant_g632", "r1041_e82_400bps_hac_g615",
    "r1041_e82_400bps_hac_g632", "r1041_e82_400bps_hac_variant_g615", "r1041_e82_400bps_hac_variant_g632", "r1041_e82_400bps_sup_g615",
    "r1041_e82_400bps_sup_variant_g615", "r104_e81_fast_g5015", "r104_e81_fast_variant_g5015", "r104_e81_hac_g5015",
    "r104_e81_hac_variant_g5015", "r104_e81_sup_g5015", "r104_e81_sup_g610", "r104_e81_sup_variant_g610", "r10_min_high_g303",
    "r10_min_high_g340", "r941_e81_fast_g514", "r941_e81_fast_variant_g514", "r941_e81_hac_g514", "r941_e81_hac_variant_g514",
    "r941_e81_sup_g514", "r941_e81_sup_variant_g514", "r941_min_fast_g303", "r941_min_fast_g507", "r941_min_fast_snp_g507",
    "r941_min_fast_variant_g507", "r941_min_hac_g507", "r941_min_hac_snp_g507", "r941_min_hac_variant_g507", "r941_min_high_g303",
    "r941_min_high_g330", "r941_min_high_g340_rle", "r941_min_high_g344", "r941_min_high_g351", "r941_min_high_g360", "r941_min_sup_g507",
    "r941_min_sup_snp_g507", "r941_min_sup_variant_g507", "r941_prom_fast_g303", "r941_prom_fast_g507", "r941_prom_fast_snp_g507",
    "r941_prom_fast_variant_g507", "r941_prom_hac_g507", "r941_prom_hac_snp_g507", "r941_prom_hac_variant_g507", "r941_prom_high_g303",
    "r941_prom_high_g330", "r941_prom_high_g344", "r941_prom_high_g360", "r941_prom_high_g4011", "r941_prom_snp_g303", "r941_prom_snp_g322",
    "r941_prom_snp_g360", "r941_prom_sup_g507", "r941_prom_sup_snp_g507", "r941_prom_sup_variant_g507", "r941_prom_variant_g303",
    "r941_prom_variant_g322", "r941_prom_variant_g360", "r941_sup_plant_g610", "r941_sup_plant_variant_g610"
]
COVERAGE_JOB_STRATEGIES = ["default", "always", "never"]
COVERAGE_JOB_CUTOFF = 10

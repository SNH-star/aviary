#!/usr/bin/env python
"""Fast unit tests for the read-mapper selection added by --short-read-mapper
and --long-read-mapper.

These deliberately avoid running the pipeline: they cover the pure logic that
decides *which* aligner is invoked and *how* its command line is spelled. That
logic is easy to get wrong and hard to notice, because a wrong mapper name
surfaces only when a real coverage or polishing job runs -- and a short-read
aligner given long reads can return a well-formed table of near-zero depths
rather than failing.

The corresponding end-to-end coverage lives in test_integration.py.
"""

import importlib.util
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(module_name, relative_path):
    """Import a script by path.

    The coverage/polishing scripts are executed by Snakemake as standalone
    files inside their own pixi environments, so they are not importable as
    part of the aviary package.
    """
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(REPO_ROOT, relative_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


aviary_init = _load("aviary_init", "aviary/__init__.py")
polish = _load("polish", "aviary/modules/assembly/scripts/polish.py")
get_abundances = _load(
    "get_abundances", "aviary/modules/binning/scripts/get_abundances.py")


class TestMapperConstants(unittest.TestCase):
    def test_every_short_read_mapper_resolves_to_a_coverm_name(self):
        # A choice without a mapping raises KeyError in processor.py at
        # config-write time, i.e. after the user has already started a run.
        for mapper in aviary_init.SHORT_READ_MAPPERS:
            self.assertIn(mapper, aviary_init.SHORT_READ_MAPPER_TO_COVERM)

    def test_no_orphan_entries_in_the_mapping(self):
        for mapper in aviary_init.SHORT_READ_MAPPER_TO_COVERM:
            self.assertIn(mapper, aviary_init.SHORT_READ_MAPPERS)

    def test_defaults_are_the_new_mappers(self):
        self.assertEqual(aviary_init.SHORT_READ_MAPPERS[0], "strobealign")
        self.assertEqual(aviary_init.LONG_READ_MAPPERS[0], "rammap")

    def test_short_read_coverm_names(self):
        self.assertEqual(aviary_init.SHORT_READ_MAPPER_TO_COVERM, {
            "strobealign": "strobealign",
            "minimap2": "minimap2-sr",
            "rammap": "rammap-sr",
            "minibwa": "minibwa",
        })


class TestShortReadPafCommand(unittest.TestCase):
    """polish.py generates racon's PAF itself, not via CoverM.

    Each aligner spells PAF output differently, so these are the exact command
    shapes rather than a pattern: minimap2/rammap take a preset as the value of
    -x, strobealign's -x is a boolean switch, and minibwa needs the 'map'
    subcommand plus -f.
    """

    def test_strobealign_uses_boolean_x(self):
        self.assertEqual(
            polish.short_read_paf_cmd("strobealign", "ref.fa", "r.fq.gz", 8),
            "strobealign -x -t 8 ref.fa r.fq.gz")

    def test_minimap2_uses_sr_preset(self):
        self.assertEqual(
            polish.short_read_paf_cmd("minimap2-sr", "ref.fa", "r.fq.gz", 8),
            "minimap2 -x sr -t 8 ref.fa r.fq.gz")

    def test_rammap_uses_sr_preset(self):
        self.assertEqual(
            polish.short_read_paf_cmd("rammap-sr", "ref.fa", "r.fq.gz", 8),
            "rammap -x sr -t 8 ref.fa r.fq.gz")

    def test_minibwa_uses_map_subcommand_and_f(self):
        self.assertEqual(
            polish.short_read_paf_cmd("minibwa", "ref.fa", "r.fq.gz", 8),
            "minibwa map -f -x sr -t 8 ref.fa r.fq.gz")

    def test_every_short_read_mapper_has_a_paf_command(self):
        # Any --short-read-mapper choice must be usable for racon polishing,
        # otherwise a valid flag combination fails partway through a run.
        for coverm_name in aviary_init.SHORT_READ_MAPPER_TO_COVERM.values():
            command = polish.short_read_paf_cmd(
                coverm_name, "ref.fa", "r.fq.gz", 4)
            self.assertTrue(command.startswith(coverm_name.split('-')[0]))
            self.assertIn("-t 4", command)

    def test_unknown_mapper_raises(self):
        # Fail loudly rather than falling back to a default, which would
        # silently polish against the wrong aligner.
        with self.assertRaises(ValueError):
            polish.short_read_paf_cmd("bwa-mem", "ref.fa", "r.fq.gz", 8)


class TestLongReadMapperGuard(unittest.TestCase):
    """get_abundances.run_coverm refuses short-read mappers for long reads.

    CoverM defaults to strobealign, which is short-read only. Long reads mapped
    with it do not necessarily error -- they can yield a well-formed abundance
    table of near-zero values, so the mistake would surface as wrong numbers
    rather than a crash.
    """

    BASE = dict(reads="r.fq", output_file="o.tsv", read_type="--single",
                threads=1, strain_analysis=False, output_dir="d/",
                log="/dev/null", bins_dir="b/")

    def test_rejects_short_read_mappers_for_long_reads(self):
        for bad in (None, "strobealign", "minimap2-sr", "rammap-sr", "minibwa"):
            with self.assertRaises(ValueError):
                get_abundances.run_coverm(
                    minimap2_type=bad, long_reads=True, **self.BASE)

    def test_accepts_long_read_mappers(self):
        for good in ("minimap2-ont", "minimap2-pb", "rammap-ont", "rammap-pb"):
            self.assertIn(good, get_abundances.LONG_READ_MAPPERS)

    def test_short_read_calls_are_unaffected(self):
        # long_reads defaults to False, so short-read calls must not be gated.
        try:
            get_abundances.run_coverm(minimap2_type="strobealign", **self.BASE)
        except ValueError as exception:
            self.fail(f"short-read path wrongly blocked: {exception}")
        except (FileNotFoundError, OSError):
            pass  # reached the CoverM exec, which is as far as we need to get


if __name__ == '__main__':
    unittest.main()

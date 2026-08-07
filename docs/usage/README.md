---
title: CLI reference
---

# CLI reference

Aviary exposes eight subcommands. The installed command's `--help` output is
the final authority for the installed version.

| Command | Purpose |
| --- | --- |
| [`assemble`](/usage/assemble) | Quality-control reads and assemble contigs |
| [`recover`](/usage/recover) | Recover and assess MAGs from an assembly |
| [`annotate`](/usage/annotate) | Annotate a directory of genome FASTA files |
| [`complete`](/usage/complete) | Run the applicable metagenome stages end to end |
| [`cluster`](/usage/cluster) | Dereplicate genomes across completed runs |
| [`isolate`](/usage/isolate) | Assemble reads from a cultured isolate |
| [`configure`](/usage/configure) | Store reference-data paths and request downloads |
| `build` | Build dependency environments; add `--gpu` for GPU environments |

Shared workflow and resource options are explained in
[centralised commands](centralised_commands.md).

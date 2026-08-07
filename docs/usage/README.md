---
title: CLI reference
---

# CLI reference

Aviary exposes eight subcommands. The installed command's `--help` output is
the final authority for the installed version.

| Command | Purpose |
| --- | --- |
| [`assemble`](assemble.md) | Quality-control reads and assemble contigs |
| [`recover`](recover.md) | Recover and assess MAGs from an assembly |
| [`annotate`](annotate.md) | Annotate a directory of genome FASTA files |
| [`complete`](complete.md) | Run the applicable metagenome stages end to end |
| [`cluster`](cluster.md) | Dereplicate genomes across completed runs |
| [`isolate`](isolate.md) | Assemble reads from a cultured isolate |
| [`configure`](configure.md) | Store reference-data paths and request downloads |
| `build` | Build dependency environments; add `--gpu` for GPU environments |

Shared workflow and resource options are explained in
[centralised commands](centralised_commands.md).

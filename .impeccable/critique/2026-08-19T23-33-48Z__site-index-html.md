---
target: site (aviary docs homepage)
total_score: 29
max_score: 40
na_heuristics: 
p0_count: 1
p1_count: 2
timestamp: 2026-08-19T23-33-48Z
slug: site-index-html
---
Method: dual-agent (A: general-purpose · B: general-purpose)

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Scroll-progress hairline + active-nav rail give good position feedback; no loading state needed since MkDocs search is near-instant |
| 2 | Match System / Real World | 4 | Domain-correct terms (MAGs, ANI, GTDB-Tk) used without over-explaining, matches bioinformatics audience |
| 3 | User Control and Freedom | 3 | No breadcrumbs beyond TOC/prev-next; deep CLI reference pages (e.g. `usage/recover.md`, 409 lines) rely only on right-hand TOC to navigate |
| 4 | Consistency and Standards | 2 | Committed `site/` build and current `docs/` source have diverged into two different designs (see Design Specificity Verdict) |
| 5 | Error Prevention | 3 | `installation.md` proactively warns to run `aviary complete --full-help` before large DB downloads; deprecated `--keep-percent` flagged inline |
| 6 | Recognition Rather Than Recall | 3 | CLI flag lists are long and flat (recover.md: 15+ options before QC section) with only `##` headers, moderate recall burden |
| 7 | Flexibility and Efficiency | 3 | PDF manual export serves power users; `content.code.copy` enabled on every code block |
| 8 | Aesthetic and Minimalist Design | 3 | Documented restraint (motion and gradient/grain decoration removed twice per CSS comments); undercut by flat option-dumps on reference pages |
| 9 | Error Recovery | 2 | `faqs.md` exists and quickstart points to `sample_aviary/logs/`, but no worked example of an actual failed-rule error message |
| 10 | Help and Documentation | 3 | Comprehensive CLI reference exists, but `admonition`/`pymdownx.details` are configured yet used in only 2 of ~30 doc files |
| **Total** | | **29/40** | **Good** |

## Design Specificity Verdict

**LLM assessment**: The `docs/` source is genuinely bespoke, not template-interchangeable: brand green sampled from the actual logo with worked-through per-theme WCAG contrast math, a hand-authored hero with an SVG flight-path motif, reduced-motion-by-default JS, and CSS comments documenting iterations that were tried and rejected (a scrollytelling command section, a mesh-gradient/grain background) with the reasoning for rejecting them. That is real design authorship.

**But the target reviewed (`site/index.html`, the committed built output) is a stale snapshot** that does not reflect any of that work. `site/stylesheets/extra.css` (53 lines, `--aviary-accent`/`--aviary-blue` tokens) and current `docs/stylesheets/extra.css` (152 lines, `--aviary-brand-green` tokens, `.aviary-hero__eyebrow`, `.aviary-commands`) are different stylesheets entirely. The `site/` hero markup ("From sequencing reads to microbial genomes." + a stat strip) does not match the current `docs/index.md` hero (eyebrow + terminal + 6-command list). No `.github/workflows/*.yml` builds or deploys mkdocs at all — only `python-publish.yml` and `test-aviary.yml` exist — so there is no visible mechanism keeping `site/` in sync with `docs/`, and it's unclear whether the live site (`snh-star.github.io/aviary/`) is running the current design or this older one.

**Deterministic scan**: The bundled detector ran against the full `site/` tree in degraded mode (no `htmlparser2`/`css-select`/`css-tree`/`domutils` — regex fallback only). It returned 22 warnings: 18 `em-dash-overuse` findings across content pages and 4 `layout-transition` findings in `main.342714a4.min.css`.

**Both categories are false positives.** The `layout-transition` hits are inside the bundled/minified MkDocs-Material vendor CSS, not project-authored code — not actionable. The `em-dash-overuse` findings are a regex artifact: the fallback matcher treats literal `--` (double-hyphen) as an em-dash, and this is CLI documentation dense with `--flag-name` syntax. Direct inspection of the two highest-count files confirms it: `usage/recover.md` and `usage/complete/index.html` were each flagged with 98 "em-dashes," but true `—` characters number 3 in each, against 125 literal `--` occurrences from flag names (`--nested`, `--min-cov-long`, `--semibin-mode`, etc.). Actual em-dash usage in the sampled prose is near zero.

**Visual overlays**: Not available. Neither assessment had browser/screenshot tooling exposed in this session (no Playwright/Puppeteer/browser-canvas tool). No local server was started for either assessment, so nothing needed to be stopped. This critique is based on direct source/markup inspection only — no live visual confirmation of layout, responsive behavior, or console errors.

## Overall Impression

The `docs/` source shows real design maturity for a scientific-tool documentation site: worked accessibility math, a landing page that argues itself out of decorative motion, and copy that speaks fluently to its bioinformatics audience. The single biggest opportunity, though, isn't a design tweak — it's that the artifact you pointed this critique at (`site/`) is not the same design the source now describes. Before anything else gets polished, it's worth confirming what's actually deployed.

## What's Working

- **Per-theme contrast math, not a copy-pasted palette** (`docs/stylesheets/extra.css` lines 12-20): light mode deepens the brand green to 4.93:1 for text; dark mode uses the true 8.35:1 green. That's deliberate accessibility work, not a default.
- **Editorial restraint on the homepage command list** (`docs/index.md` lines 64-114): CSS comments show a scrollytelling version was tried and explicitly rejected ("forced ~5 screens of scrolling... a reader arriving here wants to compare the six and leave") in favor of a scannable list. Real iteration, not decoration for its own sake.
- **Reduced-motion-first posture** (`docs/javascripts/reveal.js` + CSS): animation only activates after JS confirms the user has *not* set `prefers-reduced-motion: reduce` — the accessible default is the default, not an afterthought.

## Priority Issues

**[P0] The committed `site/` build has drifted from the current `docs/` source**
- **Why it matters**: If `site/` is what's deployed, every later accessibility, contrast, and motion fix in `docs/` is not live for real users. If it isn't deployed, it's 6.8MB of dead, misleading weight in the repo that risks being mistaken for the current design (as this critique nearly was, since it was the requested target).
- **Fix**: Confirm the actual deploy mechanism — there is currently no `mkdocs gh-deploy`/build workflow in `.github/workflows/`. Either add CI that builds and deploys `site/` automatically, or delete the committed `site/` directory and add it to `.gitignore` so `docs/` is the single source of truth.
- **Suggested command**: `/impeccable document` (once the deploy story is settled, to record the current `docs/` design as DESIGN.md)

**[P1] Interacting numeric flags have no visual aid** (`docs/usage/recover.md` lines 74-92)
- **Why it matters**: Five contig-inclusion/exclusion thresholds (`--min-cov-long`, `--min-cov-short`, `--exclude-contig-cov`, `--exclude-contig-size`, `--include-contig-size`) are documented as five sequential bold-flag paragraphs with no table or worked example. This is exactly the kind of flag set a user gets wrong on a real run — one that then wastes HPC walltime before the mistake surfaces.
- **Fix**: Add a small comparison table or one worked example showing how the five thresholds compose together.
- **Suggested command**: `/impeccable clarify`

**[P1] Admonitions are configured but barely used** (`mkdocs.yml` enables `admonition`/`pymdownx.details`; used in only `docs/pdf.md` and `docs/reference/inputs.md`)
- **Why it matters**: Load-bearing warnings — the deprecated `--keep-percent` flag (`usage/recover.md` lines 108-110) and the large-database-download caution (`installation.md` lines 82-83) — sit in plain prose, easy to skim past at exactly the moments they matter most.
- **Fix**: Convert genuinely load-bearing warnings/deprecations to `!!! warning` blocks so they're visually distinct from routine flag documentation.
- **Suggested command**: `/impeccable clarify`

**[P2] Sidebar still surfaces ~14 top-level items on short viewports**
- **Why it matters**: The `mkdocs.yml` comments themselves admit that whichever nav section is expanded can still push the list past viewport height on a short window, even after an earlier fix collapsed sections.
- **Fix**: Consider `navigation.indexes` plus shallower top-level grouping — e.g. fold Performance/Reproducibility/HPC under a single "Advanced" parent — to bring the top-level count under ~10.
- **Suggested command**: `/impeccable layout`

**[P3] No worked example of a real failure**
- **Why it matters**: `faqs.md` exists and `quickstart.md` points to `sample_aviary/logs/` on failure, but nothing shows an actual failed-rule Snakemake message, so a first-time user hitting a real error has no pattern to match it against.
- **Fix**: Add one annotated example of a Snakemake rule failure and where in `logs/` to find the relevant trace.
- **Suggested command**: `/impeccable onboard`

## Persona Red Flags

**Jordan (First-Timer, new to Snakemake/pixi/HPC)**: `docs/usage/recover.md` line 22 references "`--semibin-mode multi`" and terms like "differential-coverage binning" with no glossary link or pointer back to `docs/concepts.md`, even though that page exists in the nav. A first-timer hits unexplained domain fluency exactly where they need the most guidance.

**Alex (Power User)**: Generally well served by the single-command hero and PDF manual export. But `installation.md` buries the fastest path (bioconda, lines 11-18) under equal-weight prose about Pixi and pip immediately after, with only one sentence of "recommended" signal at line 8 — a skimmer can easily land on the slower install path.

**Sam (Accessibility-dependent)**: Mixed. Real effort is visible (`aria-labelledby` pattern on the hero SVG, `<title>`/`<desc>` inside it, reduced-motion-first CSS, documented contrast ratios). But `.md-source__facts { display: none; }` (`extra.css` lines 263-265) hides GitHub star/fork counts via `display:none` rather than removing the markup — worth checking with a screen reader whether it's still an announced, tabbable empty stop. And if the deployed site is actually the stale `site/` build (P0 above), none of this accessibility work is live at all.

## Minor Observations

- `docs/overrides/main.html` line 12 hardcodes `theme-color` to `#009688` (Material's stock teal), inconsistent with the chosen brand green (`#4ac58e`/`#1a7a58`) used everywhere else — likely a leftover from before the palette override.
- `docs/index.md` line 32 links to an absolute `https://snh-star.github.io/aviary/pdf/aviary-manual.pdf` rather than a relative `pdf.md` link used elsewhere — worth confirming it doesn't break under local `mkdocs serve`.
- CSS comments carry dates across 2026-08-10 to 2026-08-13 describing bugs found and fixed — a good engineering diary, but also evidence the design has been actively churning very recently, raising the stakes on keeping `site/` in sync.
- Table styling (`extra.css` lines 449-462, 1033-1044) — zebra striping, sunken header, hover state — is well executed and directly serves the flag-table-heavy CLI reference.
- The bundled detector ran in degraded/regex-fallback mode (missing `htmlparser2`/`css-select`/`css-tree`/`domutils`); its 22 findings were the em-dash/layout-transition false positives noted above, not new issues.

## Questions to Consider

- If `site/` isn't the deploy artifact, why is it committed at all — and if it is, how have the last several "Doc Updates" commits never made it live?
- Is there an actual CI step that runs `mkdocs gh-deploy`, or is deployment currently a manual, undocumented step run from someone's own machine?
- `recover.md` alone has 15+ interacting numeric flags before the QC section even starts — has anyone tried using this page cold, mid-run, under time pressure, or has it only ever been read top-to-bottom while writing it?
- The homepage explicitly rejected animation-heavy and decorative patterns — has that same discipline reached the CLI reference pages, or did the design effort concentrate entirely on the one page most people screenshot?

# Educational playground: implementation and verification

**2026-11-05. Website/software record, not biological validation.**

The site now connects the project's public research record to an educational
playground and its [long-term vision](virtual-human-vision.md). Current tools,
synthetic experiments and future ambitions have separate labels. The complete
Pilot 001 record remains expandable; its current owner decisions link to the
roadmap. Preliminary cohort/score values withheld by the site's existing policy
remain withheld. No private records or patient-derived inferences were used.

## Public-record refresh — 6 November 2026

This website-only update reflects Project Asma main at
`4f365cc098baac4461d1e45a075f947fe8fb6c23` (through PR #64) and
Virtual Human main at `6b10b458704e36cd592552ab8165d55ce5fe64ec`
(through PR #7). It summarises existing merged reports; it does not execute
new research or change core methods, registries or execution gates.

| Public work now represented | Site treatment |
| --- | --- |
| Asma #57, #64: [HLA-II source map](cdr2-hla-ii-evidence-map-2026-11-06.md) and [named-sequence check](cdr2l-sequence-adjudication-2026-11-06.md) | Updated frontier card and a four-step evidence diagram distinguish catalog detection, bounded sequence matching, receptor recognition and injury. The broader search remains incomplete. |
| Asma #60: [trial-landscape audit](trial-landscape-2026-11-05.md) | A dated research card and expandable aggregate table explain overlapping keyword counts and their limits. The retrieval date is 5 November in Chicago, 6 November UTC. |
| Asma #61–62: [exploratory plan](../protocols/pilot-001-exploratory-subset-plan.md) | A research card and notebook entry distinguish executed offline design calculations from an unexecuted study-data analysis. Preliminary Pilot numbers remain withheld. |
| Asma #53–56, #63: [first-run preparation](pilot-001-first-run-runbook.md) and platform checks | The notebook reflects implemented amendment code paths and artificial-input checks, while keeping authorization, host checks and data-use conditions open. |
| Virtual Human #4–7 | Capability summary and pinned report links cover the SBML importer, ovarian parameter ledger, dated research guide and optional evidence bindings. Unchecked SBML units and unpropagated uncertainty are explicit. |

The newer merged runbook records amendment implementation on artificial
fixtures; older roadmap/amendment passages still describe implementation as
outstanding. The site follows the runbook for software capability and retains
the execution conditions. This refresh does not reconcile those core records.
The duplicate Rosen card is consolidated, with both existing fragment links
preserved. The fragile hard-coded claim total is replaced by a direct ledger
invitation.

Refresh verification, separate from the original build checks below:

- Repository validator and all **372 Python unit tests** passed. Implementation
  hashes were current or covered by the same two pre-existing stale allowances.
- Existing JavaScript mathematics checks passed all 10,000 artificial slider
  combinations. Both reference models and static previews passed offline checks.
- The existing `tools/test_site_browser.cjs` passed: model switching, lab controls,
  failure fallback, themes, compact navigation, no-JavaScript view, GitHub Pages
  project paths and nested 404 links.
- A supplementary local browser check expanded all notebook sections at
  **320, 390, 640, 768, 980 and 1440 pixels**, in both themes. The new blocks had
  no horizontal overflow; all IDs were unique. The four evidence stages and
  trial table remained readable without JavaScript. Browser checks observed no
  page errors or off-site runtime requests.
- All 26 distinct public Asma document links in the page resolve to files in
  the checkout. Pinned Virtual Human additions were read against their reports.
  Desktop evidence/research views and mobile evidence/table views were inspected.
- A separate GPT-6 Astra agent reviewed the website changes against the public
  sources and found no material scientific or implementation issue. This is
  internal review, not external scientific peer review.

Browser versions match the original record below. These checks establish
presentation and software behaviour in the exercised environment; they do not
replay the research, establish clinical validity, or constitute a full
screen-reader audit. No new study-source acquisition, private-data access or
deployment was performed for this refresh.

## What runs in the browser

- Two measured reference structures, selected human insulin and synthetic DNA,
  with pointer/touch/keyboard rotation, zoom, reset and representation switching.
  The [structure record](site-structure-sources.md) describes primary sources,
  CC0 terms, selections, missing atoms and conversion checks. Curved chain guides
  are illustrations through representative atoms, not additional chemical bonds.
- A two-state assumption experiment with two sliders and two removal rules.
  Its equations follow the [Rosen-inspired exact experiment](research/rosen-treatment-sequence-assumptions.md).
  Browser arithmetic uses floating point and displays rounded values. It does
  not run Virtual Human's numerical engine or simulate a patient.
- Plain HTML explanations, conceptual biological scales, proof-versus-evidence
  distinctions, and source links remain available without JavaScript. The
  numerical example and coordinate-derived static image remain visible then.

Three.js is bundled locally with its MIT licence; its exact version and build
instructions are in [the vendor record](../assets/vendor/README.md). The viewer
loads local coordinate JSON, not a remote molecule service. The page uses system
fonts, no analytics and no external runtime dependencies. Rendering is on demand;
there is no automatic rotation or continuous idle animation. The site retains
light/dark themes and the existing motion preference controls.

## Checks actually performed

| Check | Observed result and limit |
| --- | --- |
| Existing Python suite | 247 tests passed; source/link validator passed. These are scaffold checks, not clinical evaluation. |
| Artificial JavaScript experiment | Hand-calculated cases, caps, null boundaries, malformed inputs and all 10,000 integer slider combinations passed. This verifies the intended restricted mathematics. |
| Coordinate integrity | Both model files and SVG fallbacks pass offline identity, topology, finite-coordinate, connectivity, source-pin, sequence and omission checks. Primary archive/PDB-format cross-checks are documented separately. |
| Viewer interaction | Both structures and representations render; drag and keyboard rotation/zoom/reset work. Idle frames stop. Reduced-motion handling, HTTP failure, missing WebGL and context loss retain an explanation/fallback. |
| Whole page | Lab inputs/reset, theme switching, compact navigation, no-JavaScript fallback and no horizontal overflow checked at widths 320, 390, 768 and 1440 pixels. Design review also checked 1280 pixels and expanded notebook sections. |
| Hosting paths | A locally intercepted GitHub Pages project path and nested 404 verified relative module/data assets, home links and the skip-link target. No live deployment was needed or claimed. |
| Requests and errors | Same-origin runtime requests only; no browser page errors in the exercised flows. |

An independent Astra review found no major scientific or usability issue. Its
two minor observations were corrected: the static legend now describes the
atom/connectivity projection, and a failed structure replacement restores the
selector to the structure still shown. The blank canvas starts outside the tab
order and accessibility tree; it is enabled after a successful frame.

Browser checks used Chromium 154.0.8037.57, Node 24.19.0 and Playwright Core 1.57.0
in this environment. Headless software WebGL was used; this is not a guarantee
of rendering on every GPU, browser or assistive technology. Keyboard/fallback
checks are not a full manual screen-reader audit. Reference coordinates and
correct rendering do not reproduce the original crystallography, predict
molecular dynamics or demonstrate clinical benefit.

## Reproduce

From the repository root:

```sh
python3 tools/validate.py
python3 -m unittest discover -s tests -v
python3 tools/check_implementation_hashes.py
node tools/test_research_lab.cjs
python3 tools/check_site_models.py
```

The existing CI workflow includes the JavaScript mathematics and offline model
checks. Browser tests are optional and need a separately installed Playwright
Core package and a Chromium executable; they introduce no site build step.
Start a local server in a separate terminal:

```sh
python3 -m http.server 8800 --bind 127.0.0.1
```

Then supply the installation paths for that host:

```sh
PLAYWRIGHT_MODULE=/path/to/playwright-core CHROMIUM_PATH=/path/to/chromium \
  SITE_URL=http://127.0.0.1:8800 node tools/test_molecular_viewer.cjs
PLAYWRIGHT_MODULE=/path/to/playwright-core CHROMIUM_PATH=/path/to/chromium \
  SITE_URL=http://127.0.0.1:8800 node tools/test_site_browser.cjs
```

The whole-page test stores screenshots in the system temporary directory under
`asma-site-preview`, or the directory named by `ASMA_PREVIEW_DIR`. The molecular
test also creates temporary diagnostic screenshots. Its reset-image comparison
allows at most two 8-bit channel values of compositor quantisation difference.
No screenshots or external source downloads are required to serve the site.

Prepared by multiple GPT-6 Astra agents for data, rendering, design and independent
review, with coordinating Codex integration and earlier supporting code/content
agents. This was internal review, not external scientific peer review.

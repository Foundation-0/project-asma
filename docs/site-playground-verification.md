# Educational playground: implementation and verification

**2026-11-05. Website/software record, not biological validation.**

The site now connects the project's public research record to an educational
playground and its [long-term vision](virtual-human-vision.md). Current tools,
synthetic experiments and future ambitions have separate labels. The complete
Pilot 001 record remains expandable; its current owner decisions link to the
roadmap. Preliminary cohort/score values withheld by the site's existing policy
remain withheld. No private records or patient-derived inferences were used.

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

# Clean Enterprise Banner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current TrustLens README banner with a polished 1200 x 300 light enterprise banner generated with GPT Image and finished with deterministic typography.

**Architecture:** GPT Image produces a text-free premium BI verification scene with intentional negative space on the left. A local compositing step crops and finishes that scene at the exact banner dimensions, adds the product name and tagline with system fonts, and exports the final PNG consumed by the existing README.

**Tech Stack:** GPT Image built-in generation, Python Pillow for deterministic raster compositing, GitHub README PNG asset.

## Global Constraints

- Final canvas is exactly 1200 x 300 pixels.
- The visible copy is exactly `TrustLens` and `The insights agent you can actually trust`.
- Use a white and cool-gray foundation, graphite typography, restrained cobalt accents, and one small emerald verification accent.
- Do not include neon, cyberpunk styling, a dark dominant background, visual clutter, watermarks, third-party logos, invented metrics, or illegible pseudo-text.
- Preserve the existing README structure and banner alt text.

---

### Task 1: Generate and compose the banner

**Files:**
- Modify: `assets/banner.png`
- Delete: `assets/banner.svg`

**Interfaces:**
- Consumes: the approved design in `docs/superpowers/specs/2026-06-22-clean-enterprise-banner-design.md`
- Produces: a 1200 x 300 RGBA PNG at `assets/banner.png`, referenced by `README.md`

- [ ] **Step 1: Generate the text-free visual**

Use the built-in GPT Image tool with this production prompt:

```text
Use case: ads-marketing
Asset type: GitHub README banner background for a premium enterprise BI product
Primary request: Create a refined, light enterprise data-verification scene for TrustLens. Show a precise transparent optical lens on the right inspecting a restrained stream of elegant charts, table cells, and numeric data; verified data emerges with one subtle emerald confirmation signal.
Scene/backdrop: bright white to cool-gray studio environment, spacious and minimal
Style/medium: premium 3D editorial product visualization, credible enterprise software branding, precise glass and brushed-metal details
Composition/framing: very wide banner composition; reserve the left 55 percent as clean low-detail negative space for typography; place the visual focus in the right 40 percent; keep all essential objects away from the edges
Lighting/mood: soft high-key studio lighting, calm, trustworthy, analytical
Color palette: white, cool gray, graphite, restrained cobalt blue, tiny emerald accent
Constraints: no text, no letters, no logos, no brands, no readable numbers, no watermark; sophisticated and restrained
Avoid: dark background, neon, cyberpunk, gradients as the main device, dashboard screenshot, clutter, glowing sci-fi HUD, illegible pseudo-text
```

Expected result: a clean landscape image with a low-detail left half and a premium verification scene on the right.

- [ ] **Step 2: Inspect the generated image**

Open the result at original resolution and reject it if it contains malformed text, a dark dominant background, central visual clutter, or insufficient negative space for the wordmark.

Expected result: all constraints pass before compositing.

- [ ] **Step 3: Composite exact typography**

Use Pillow to fit the generated scene to 1200 x 300 and add:

```text
TrustLens
The insights agent you can actually trust
```

Place both lines in the left negative-space area. Use a dark graphite sans-serif for `TrustLens`, cool gray for the tagline, and a short cobalt-to-emerald verification rule or check accent that does not compete with the image. Export as RGBA PNG to `assets/banner.png`.

Expected result: exact copy, crisp typography, generous whitespace, and no overlap with the generated scene.

- [ ] **Step 4: Remove the stale vector source**

Run:

```bash
rm assets/banner.svg
```

Expected result: only the current generated/composited banner remains as the source of truth.

- [ ] **Step 5: Commit the asset**

```bash
git add assets/banner.png assets/banner.svg
git commit -m "docs: replace README banner with clean enterprise visual"
```

Expected result: one asset-focused commit.

### Task 2: Validate and publish

**Files:**
- Verify: `README.md`
- Verify: `assets/banner.png`

**Interfaces:**
- Consumes: `assets/banner.png` from Task 1
- Produces: a verified banner rendered through the existing README image reference

- [ ] **Step 1: Validate dimensions and format**

Run:

```bash
file assets/banner.png
sips -g pixelWidth -g pixelHeight assets/banner.png
```

Expected: PNG image data with `pixelWidth: 1200` and `pixelHeight: 300`.

- [ ] **Step 2: Verify the README reference**

Run:

```bash
rg -n '<img src="assets/banner.png".*width="100%">' README.md
```

Expected: one match on the existing banner line, with its alt text unchanged.

- [ ] **Step 3: Inspect at full and reduced size**

Open `assets/banner.png` at original size, then create a temporary 720-pixel-wide preview and inspect it.

Expected: title and tagline remain legible, the verification scene remains recognizable, and no elements overlap or crop awkwardly.

- [ ] **Step 4: Check repository state**

Run:

```bash
git diff --check
git status --short --branch
```

Expected: no whitespace errors and no unintended changes.

- [ ] **Step 5: Push to GitHub**

```bash
git push origin main
```

Expected: local `main` and `origin/main` point to the same banner commit.

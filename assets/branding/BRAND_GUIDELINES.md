# Elenchus (ἔλεγχος) — Brand Guidelines

> Official visual identity and design guidelines for Elenchus. This document defines logo usage, clear space, minimum sizing, color tokens, and approved surfaces for developers, designers, and contributors.

---

## 1. The Logo & Brand Concept

- **Concept**: **The Faceted Caliper (`ἔ`)**
  Elenchus is named after the Classical Greek method of dialectic refutation (*elenctic method* / ἔλεγχος). The logo is a precision geometric monogram of the lowercase Greek polytonic epsilon (`ἔ`), crowned with the smooth breathing arc (*psili*) and acute refutation spark (*oxia*). Its outer profile is shaped with 45-degree architectural chamfers, evoking CNC-milled obsidian hardware instruments and relentless dialectic precision.
- **Versions**:
  - **Horizontal Lockup (Primary)**: Symbol on the left, `elenchus` lowercase wordmark on the right. Used in web navigation headers, documentation banners, and GitHub repository headers.
  - **Stacked Lockup**: Centered symbol positioned above the wordmark. Used for badges, signage, splash screens, and square containers.
  - **Symbol-Only**: Standalone monogram. Used for app icons, favicons, taskbar tiles, and avatars.
  - **Wordmark-Only**: Standalone vector typography for inline typographic titles.

---

## 2. Clear Space

Always maintain a clear space exclusion zone around the logo on all four sides. No text, graphic elements, window frames, or borders may intrude into this zone.

$$\text{Clear Space} = 1 \times X$$

Where $X$ is defined as the height of the central diacritic spark (*oxia* shard).
- For the horizontal lockup, the exclusion zone around the perimeter must equal at least the full height of the letter *e* in the wordmark.
- The minimum distance between the right edge of the symbol and the left edge of the wordmark is locked at $1.5 \times X$.

---

## 3. Minimum Sizing & Scale Thresholds

To preserve optical clarity, legibility, and geometric precision, adhere strictly to the following minimum size limits:

| Asset | Digital (Screen) | Physical (Print) | File to Use |
|---|---|---|---|
| **Horizontal Lockup** | Min width: `120 px` | Min width: `30 mm` | `kit/elenchus-lockup-horizontal-*.svg` |
| **Stacked Lockup** | Min width: `80 px` | Min width: `20 mm` | `kit/elenchus-lockup-stacked-*.svg` |
| **Standard Symbol** | Min width: `48 px` | Min width: `12 mm` | `kit/elenchus-symbol-*.svg` |
| **Micro-Icon / Favicon** | Min width: `16 px` | Min width: `5 mm` | `kit/favicon.ico` / `kit/favicon.svg` |
| **App Icon / Touch Tile**| Min width: `32 px` | Min width: `8 mm` | `kit/apple-touch-icon.png` / `kit/icon-192.png` |

> [!TIP]
> The official Elenchus Favicon and App Icon use a **Reversed-Color Squircle** format: a square curved-corner tile (radius $\approx 21\%$) filled with solid black (`#000000`), containing the pure white (`#ffffff`) Faceted Caliper mark centered inside. This ensures exceptional contrast across both light-mode and dark-mode browser chrome, taskbars, and launcher docks.

---

## 4. Official Color System

The Elenchus palette reflects the **Hyperstudio Obsidian** aesthetic: deep carbon blacks, mineral graphite strokes, crisp chalk type, and high-visibility instrument accents.

| Role | Color Name | HEX | RGB | CMYK | Pantone (Approx.) |
|---|---|---|---|---|---|
| **Base Surface** | Obsidian Black | `#101010` | `16, 16, 16` | `75, 68, 67, 90` | Black 6 C |
| **Canvas Deep** | Carbon | `#080808` | `8, 8, 8` | `80, 72, 70, 95` | Black 7 C |
| **Hairline Borders**| Graphite | `#212121` | `33, 33, 33` | `71, 65, 64, 80` | Cool Gray 11 C |
| **Primary Type** | Chalk White | `#f3f3f3` | `243, 243, 243` | `0, 0, 0, 5` | Bright White |
| **Active Accent** | Pulse Green | `#98ff38` | `152, 255, 56` | `40, 0, 78, 0` | 802 C (Fluorescent) |
| **Dialectic Accent**| Compass Gold | `#6f6759` | `111, 103, 89` | `0, 7, 20, 56` | 7531 C |
| **Warning / Flaw** | Status Red | `#ef4444` | `239, 68, 68` | `0, 72, 72, 6` | Warm Red C |

### Approved Combinations
1. **Dark Surfaces (Default)**: Solid Chalk `#f3f3f3` or pure White `#ffffff` logo on Obsidian `#101010` / Carbon `#080808`.
2. **Light Surfaces / Print**: Solid Obsidian Black `#000000` / `#101010` logo on White `#ffffff`.
3. **Active State**: Pulse Green `#98ff38` symbol on Obsidian `#101010` background (matches HUD listening LED and audio waveform).
4. **Editorial / Archival**: Compass Gold `#6f6759` on Carbon `#080808`.

---

## 5. Typography

- **Wordmark & Headings**: `General Sans` (Weight: 400 Regular). Clean, modern geometric grotesk with humanist open apertures.
- **Data & Telemetry / HUD**: `JetBrains Mono` or `Input Mono` (Weight: 400 / 500). Used for latency statistics, fallacy pill tags, and terminal CLI output.
- **Web Stack Fallback**: `ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.

---

## 6. Logo Don'ts (Unacceptable Misuse)

- **Do NOT** stretch, distort, shear, or horizontally compress the logo.
- **Do NOT** rotate the mark or diacritics away from their calibrated 45-degree angle.
- **Do NOT** add artificial drop shadows, glow halos, 3D extrusions, or bevels.
- **Do NOT** recolor the mark in non-brand gradient colors (e.g. rainbow, pastel purple).
- **Do NOT** separate the diacritics from the mirrored-3 body.
- **Do NOT** re-type the wordmark using default system serif or sans fonts; always use the outlined vector master files.

---

## 7. Asset Master Registry

All vector and raster masters are located in `assets/branding/`:
- **Master Symbol**: [`assets/branding/elenchus-symbol.svg`](file:///C:/Users/sayye/dev/active/elechus/assets/branding/elenchus-symbol.svg)
- **Small-Scale Cut**: [`assets/branding/elenchus-symbol-small.svg`](file:///C:/Users/sayye/dev/active/elechus/assets/branding/elenchus-symbol-small.svg)
- **Horizontal Lockup**: [`assets/branding/elenchus-lockup-horizontal.svg`](file:///C:/Users/sayye/dev/active/elechus/assets/branding/elenchus-lockup-horizontal.svg)
- **Stacked Lockup**: [`assets/branding/elenchus-lockup-stacked.svg`](file:///C:/Users/sayye/dev/active/elechus/assets/branding/elenchus-lockup-stacked.svg)
- **Production Distribution Kit**: [`assets/branding/kit/`](file:///C:/Users/sayye/dev/active/elechus/assets/branding/kit/)
- **Client Presentation Board**: [`assets/branding/presentation.html`](file:///C:/Users/sayye/dev/active/elechus/assets/branding/presentation.html)

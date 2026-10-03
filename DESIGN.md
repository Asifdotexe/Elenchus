---
name: Elenchus
description: Socratic debate analysis & fallacy detection engine
colors:
  obsidian: "#101010"
  carbon: "#080808"
  chalk: "#f3f3f3"
  smoke: "#9c9c9c"
  ash: "#c1c1c1"
  graphite: "#212121"
  iron: "#474747"
  signal-white: "#ffffff"
  compass-gold: "#6f6759"
  card-slate: "#3b3d45"
  pulse-green: "#98ff38"
  surface: "#141414"
  surface-hover: "#1c1c1c"
  status-busy: "#d97706"
  status-alert: "#ef4444"
typography:
  display:
    fontFamily: "General Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "72px"
    fontWeight: 400
    lineHeight: 1.02
    letterSpacing: "-1.4px"
  heading-lg:
    fontFamily: "General Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "44px"
    fontWeight: 400
    lineHeight: 1.07
    letterSpacing: "-0.31px"
  heading:
    fontFamily: "General Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "34px"
    fontWeight: 400
    lineHeight: 1.03
    letterSpacing: "normal"
  heading-sm:
    fontFamily: "General Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "23px"
    fontWeight: 400
    lineHeight: 1.07
    letterSpacing: "normal"
  subheading:
    fontFamily: "General Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "21px"
    fontWeight: 400
    lineHeight: 1.35
    letterSpacing: "-0.2px"
  body:
    fontFamily: "General Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  caption:
    fontFamily: "General Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "normal"
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, SF Mono, Menlo, monospace"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "-0.022em"
rounded:
  tags: "4px"
  cards: "8px"
  icons: "99px"
  buttons: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
  xxl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.signal-white}"
    textColor: "{colors.obsidian}"
    rounded: "{rounded.buttons}"
    padding: "12px 24px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.chalk}"
    rounded: "{rounded.cards}"
    padding: "10px 20px"
  button-ghost-pill:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.smoke}"
    rounded: "{rounded.buttons}"
    padding: "12px 24px"
---

## Overview
Hyperstudio editorial-tech design system: a blueprint scratched into obsidian. Type and hairline borders carve negative space from pure black, with the occasional gold compass-mark to show the way. Typography does the heavy lifting through oversized 400-weight headlines with negative tracking, communicating quiet authority rather than bold shouting.

## Colors
- **Canvas Obsidian (`#101010`)**: Page canvas, full-bleed dark matte background.
- **Depth Carbon (`#080808`)**: Deepest surface level, cards, and overlay backgrounds.
- **Primary Chalk (`#f3f3f3`)**: High-contrast headings and primary text.
- **Secondary Smoke (`#9c9c9c`)**: Subheadings, helper labels, captions.
- **Structural Graphite (`#212121`)**: 1px hairline border color for cards, grids, and dividers.
- **Signal White (`#ffffff`)**: Single high-contrast action color for primary pill CTAs.
- **Compass Gold (`#6f6759`)**: Icon strokes, Socratic spark nexus, and subtle accents.
- **Pulse Green (`#98ff38`)**: Active listening indicators and verified status badges.

## Typography
- **Primary (`Inter` / `Aeonik`)**: Weight 400 across all sizes is the signature rule. Scale and negative tracking establish hierarchy without bold shouting.
- **Code & Metadata (`JetBrains Mono` / `Input`)**: Utilitarian monospace feel for terminal commands, status badges, and technical metrics.

## Elevation
No box shadows. Elevation is achieved purely through contrast steps (`#080808` on `#101010`) and crisp 1px `#212121` hairline borders.

## Components
- **Pill Buttons (`9999px` radius)**: Primary CTA filled in Signal White with Obsidian text; secondary actions outlined in Graphite.
- **HUD Overlay Wireframe**: Translucent dark container with monochromatic energy meter, latency pills, and Socratic flaw cards.
- **ASCII Art Centerpiece**: Rasterized diamond-dot scanline Creation of Adam hands artwork with an interactive Compass Gold Socratic spark.

## Do's and Don'ts
- **DO** use 400-weight typography for display headlines with negative letter-spacing.
- **DO** use 1px hairline borders (`#212121`) to separate content sections.
- **DO** maintain strict WCAG AA contrast (≥4.5:1) for all text and metadata.
- **DON'T** use multi-color neon gradients, gradient text, or drop-shadows.
- **DON'T** use bold (700) shouting in headlines.
- **DON'T** add decorative glassmorphism blurs without structural purpose.

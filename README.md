# tofurengo

**tofurengo** is a Python toolkit that provides a unified "Glyph Tag" abstraction layer for handling large-scale Japanese glyph systems, such as **MJ** (using `MJxxxxxx` glyph tags) and **MJ+** (which extends MJ by adding administrative glyphs tagged as `GJxxxxxx`). Both systems are widely used in Japanese government and public sector applications.

### Problem & Key Objective
Traditionally, many Japanese personal names and place names containing variant kanji relied on proprietary custom characters (**Gaiji**). When exchanging data between different systems, Gaiji leads to corrupted text and a loss of precise glyph information.

**tofurengo** enables system compliance with Japan's Moji Joho Kiban (Character Information Infrastructure) and the Unicode IVS international standard. By representing glyphs through standard Glyph Tags (`MJxxxxxx` / `GJxxxxxx`), it eliminates reliance on Gaiji and ensures accurate, lossless glyph data exchange across systems.


### Resources & Links

* [GitHub Repository (`jp-rad/tofurengo`)](https://github.com/jp-rad/tofurengo)
* [Glyph Tag Specification (Japanese)](https://jp-rad.github.io/tofurengo/specification.ja.html) - 
For detailed rules, formats, and normalization behavior of Glyph Tags,
please refer to the "Glyph Tag Specification". The specification is
written in Japanese only.


## Features

- **Unified Glyph Abstraction (Glyph Tag)**  
  Handles diverse representations (`glyph-name` like `MJxxxxxx`/`GJxxxxxx`, `UCSSeq`, and `IVS`) in a single, standard Glyph Tag format.

- **Lossless Data Exchange Across Environments**  
  Ensures reliable glyph management and exchange even in systems or environments that do not natively support IVS/VDS, eliminating character corruption.

- **Extensible & Customizable Glyph Systems**  
  Provides built-in datasets for MJ (`MJxxxxxx`) and MJ+ (`GJxxxxxx`), while allowing users to easily define and extend their own custom `glyph-name` schemes.

## Namespace Package Layout

The project utilizes **PEP 420** namespace packages. It is organized into two primary namespaces: `tofurengo` (the core engine modules) and `tofurengo_data` (independently versioned dataset modules).

```text
tofurengo
├── builder
├── glyph_normalizer
├── glyph_renderer
├── replacer
├── resource
├── tag_parser
└── ucs

tofurengo_data
├── mj
│   ├── v6_02_201/         # contains GLYPH_TABLE
│   └── v6_02_201_onka/    # contains GLYPH_TABLE
├── mj_plus
│   └── v4_10/             # contains GLYPH_TABLE
└── mj_plusx
    └── v1_20/             # contains GLYPH_TABLE

```

Each module under `tofurengo_data.*` represents an independently versioned dataset exposing its glyph table through the `GLYPH_TABLE` symbol.

*(Note: A `template` module is available in the source repository for creating custom dataset packages, though it is not included in published distributions.)*

## Installation

There are **two installation methods** available depending on your requirements:

### 1. Install from GitHub Pages (Recommended)

Uses a PEP 503–compatible simple index hosted on GitHub Pages. Pip downloads pre-built wheel files for fast installation without requiring local build tools.

```bash
pip3 install --upgrade --no-deps --index-url https://jp-rad.github.io/tofurengo/simple/ \
    tofurengo \
    tofurengo-data-mj-plus-v4-10 \
    tofurengo-data-mj-plusx-v1-20 \
    tofurengo-data-mj-v6-02-201 \
    tofurengo-data-mj-v6-02-201-onka

```

### 2. Install Directly from Git Repository

Pulls source code directly from GitHub to build packages locally. Ideal for development versions, testing unreleased changes, or source-level debugging.

```bash
pip3 install --upgrade --no-deps \
    tofurengo@git+https://github.com/jp-rad/tofurengo.git@main#subdirectory=tofurengo \
    tofurengo-data-mj-plus-v4-10@git+https://github.com/jp-rad/tofurengo.git@main#subdirectory=glyph/mj_plus_v4_10 \
    tofurengo-data-mj-plusx-v1-20@git+https://github.com/jp-rad/tofurengo.git@main#subdirectory=glyph/mj_plusx_v1_20 \
    tofurengo-data-mj-v6-02-201@git+https://github.com/jp-rad/tofurengo.git@main#subdirectory=glyph/mj_v6_02_201 \
    tofurengo-data-mj-v6-02-201-onka@git+https://github.com/jp-rad/tofurengo.git@main#subdirectory=glyph/mj_v6_02_201_onka

```

## Check Installed Version

Verify all installed `tofurengo` core and dataset packages:

```bash
pip3 list | grep tofurengo

```

## Uninstallation

Remove the core engine and all installed dataset packages in one command:

```bash
pip3 uninstall -y \
    tofurengo \
    tofurengo-data-mj-plus-v4-10 \
    tofurengo-data-mj-plusx-v1-20 \
    tofurengo-data-mj-v6-02-201 \
    tofurengo-data-mj-v6-02-201-onka

```

## Usage Example

The following example demonstrates how to build a `GlyphNormalizer` and `GlyphRenderer`, normalize Hentaigana (variant kana) Glyph Tags in text, and render them into plain Unicode characters.

```python
from tofurengo.builder import build_normalizer, build_renderer

# Input text containing an MJ Hentaigana Glyph Tag (An-no-A)
text = "'{MJ090001}'"

# ------------------------------------------------------------
# 1. Build Normalizer and Renderer
# ------------------------------------------------------------
# Load the MJ dataset (version 6.02.201) and create a normalizer
normalizer = build_normalizer("mj", "6.02.201")

# Create a renderer (use_base=False uses IVS/UCSSeq, use_base=True uses base character)
renderer = build_renderer(use_base=False, tofu="U+25A1")

# ------------------------------------------------------------
# 2. Normalize Glyph Tags
# ------------------------------------------------------------
normalized = normalizer.normalize(text)
print(normalized.text)
# Output: '{MJ090001 b=U+5B89 v=U+1B002 set=mj}'

# ------------------------------------------------------------
# 3. Render Text to Unicode
# ------------------------------------------------------------
rendered = renderer.render(normalized.text)
print(rendered)
# Output: Hentaigana character (Kana Supplement U+1B002)

# Using base Kanji fallback:
base_renderer = build_renderer(use_base=True)
print(base_renderer.render(normalized.text))
# Output: Base Kanji character (U+5B89)

# ------------------------------------------------------------
# 4. Handle Escape Sequences (Section 4 of Specification)
# ------------------------------------------------------------
# Escaping '{' using '{{' prevents tag parsing and outputs a literal '{'
text_with_escape = "Literal bracket: {{MJ090001}"
normalized_esc = normalizer.normalize(text_with_escape)
print(normalized_esc.text)
# Output: "Literal bracket: {{MJ090001}"

rendered_esc = renderer.render(normalized_esc.text)
print(rendered_esc)
# Output: "Literal bracket: {MJ090001}"

```

## Data Sources

This project uses materials published by the following official data sources and organizations:

* [IPA MJ List](https://moji.or.jp/mojikiban/mjlist/)
* Digital Wide area Promotion Institute (DWPI) - [DWPI Mincho](https://www.digitalwidearea.org/dwpi_mincho)

All dataset materials are used solely as source data for generating unified glyph tables. All original copyrights remain with their respective publisher organizations.

## License

Released under the MIT License.

All underlying datasets retain their original copyright notices.

## Notes

* Each dataset module under `tofurengo_data.*` provides its own `GLYPH_TABLE` and `VERSION`.
* Dataset packages are versioned independently from the core engine.
* The core `tofurengo` engine does not embed any heavy datasets out of the box.
* Namespace packages allow multiple dataset versions to coexist without conflicts.


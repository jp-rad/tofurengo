# tofurengo_js

Client-side JavaScript library for parsing, normalizing, and rendering glyph tags in Japanese character set conversion workflows.

## Overview

`tofurengo_js` provides lightweight utilities to process glyph tags (such as `{MJ000001 b=U+845B v=U+845B_U+E0102}`) directly in browser and Node.js environments.

### Key Features

* **Tag Parsing:** Parse raw tag syntax and extract properties safely.
* **Glyph Normalization:** Validate tags against dataset dictionaries and normalize structure.
* **Glyph Rendering:** Resolve normalized tags into actual Unicode character sequences.
* **Zero Dependencies:** Pure JavaScript implementation optimized for fast execution.

## Installation

Download the latest `tofurengo.min.js` file from the repository's GitHub Releases page:

1. Navigate to the **Releases** section on the GitHub repository.
2. Select the latest version tag.
3. Download `tofurengo.min.js` from the release assets.

Include the downloaded script in your web page:

```html
<script src="path/to/tofurengo.min.js"></script>

```

## Quick Start

```javascript
import { normalizeAndRender, render } from "tofurengo_js";

// Sample glyph dataset dictionary
const glyphTable = {
  MJ000001: { active: true, b: "U+845B", v: "U+845B U+E0102" },
};

const input = "Sample text with tag {MJ000001}.";

// 1. Normalize and Render in one step
const result = normalizeAndRender(input, glyphTable, "mj");
console.log(result.text);
// Output: "Sample text with tag 葛󠄂."

// 2. Render pre-normalized text directly
const rendered = render("{MJ000001 b=U+845B v=U+845B_U+E0102}");
console.log(rendered);

```

## API Reference

### High-Level API

#### `normalize(text, glyphTable, setName)`

Normalizes tags present in the input text using the provided glyph table.

* **`text`** (`string`): Raw text containing glyph tags.
* **`glyphTable`** (`Record<string, Object>`): Mapping dictionary of glyph entries.
* **`setName`** (`string`): Name of the dataset (e.g., `'mj'`).
* **Returns:** `{ text: string, issues: TagIssue[] }`

#### `render(text, [useBase=false], [tofu="U+25A1"])`

Renders tags within text into Unicode characters.

* **`text`** (`string`): Input text containing glyph tags.
* **`useBase`** (`boolean`): If `true`, prioritizes base character (`b=`) over variant (`v=`). Default: `false`.
* **`tofu`** (`string`): Fallback Unicode character or hex string for unmapped tags. Default: `"U+25A1"`.
* **Returns:** `string`

#### `normalizeAndRender(text, glyphTable, setName, [useBase=false], [tofu="U+25A1"])`

Combines normalization and rendering in a single pipeline execution.

### Low-Level Modules

For advanced customization, internal pipeline classes are exported:

* **`TagParser`**: Low-level parser for tokenizing tag strings and handling double-brace escaping (`{{`).
* **`GlyphNormalizer`**: Custom normalization rule executor.
* **`GlyphRenderer`**: Configurable rendering pipeline engine.

## Escaping Syntax

To output literal brace characters without triggering tag parsing, escape them using double braces:

```text
Input:  "Use {{MJ000001}} syntax."
Output: "Use {MJ000001} syntax."

```

## License

MIT License

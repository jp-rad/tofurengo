/**
 * Sentence-only tests for dist bundle (normalizeAndRender)
 * ASCII-only comments only.
 */

import { describe, test, expect } from "vitest";

// Import from built ESM bundle
import { normalizeAndRender } from "../dist/tofurengo.bundle.js";

// Minimal glyph table for sentence tests
const glyphTable = {
  MJ000001: { b: "U+3005", v: "U+3005", active: true },
  MJ022335: { b: "U+845B", v: "U+845B U+E0102", active: true },
  MJ999999: { active: false },
};

describe("Sentence Processing Tests (dist bundle)", () => {

  test("Nara Katsuragi City MJ022335", () => {
    const sentence = "Nara Katsuragi City {MJ022335}";
    const out = normalizeAndRender(sentence, glyphTable, "mj");

    console.log("Rendered:", out.text);

    expect(out.text).toBe("Nara Katsuragi City \u{845B}\u{E0102}");
  });

  test("escaped literal braces", () => {
    const sentence = "Format {{KEY}}: Use {MJ000001} here.";
    const out = normalizeAndRender(sentence, glyphTable, "mj");

    console.log("Rendered:", out.text);

    expect(out.text).toBe("Format {KEY}}: Use \u{3005} here.");
  });

  test("inactive glyph produces tofu", () => {
    const sentence = "Unknown {MJ999999}";
    const out = normalizeAndRender(sentence, glyphTable, "mj");

    console.log("Rendered:", out.text, "Issues:", out.issues);

    expect(out.text).toBe("Unknown \u{25A1}");
    expect(out.issues.length).toBe(1);
  });

  test("multiline paragraph", () => {
    const paragraph = "Line 1: {MJ000001}\nLine 2: {MJ022335}";
    const out = normalizeAndRender(paragraph, glyphTable, "mj");

    console.log("Rendered:", out.text);

    expect(out.text).toBe("Line 1: \u{3005}\nLine 2: \u{845B}\u{E0102}");
  });
});


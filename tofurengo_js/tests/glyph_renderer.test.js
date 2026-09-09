/**
 * Unit tests for GlyphRenderer (string rendering version)
 * ASCII-only comments only.
 */

import { describe, test, expect } from "vitest";

import { GlyphRenderer, ucsToGlyph } from "../src/glyph_renderer.js";
import { TagParser, ParsedTag } from "../src/tag_parser.js";

//
// Tests for ucsToGlyph
//
describe("ucsToGlyph", () => {
  test("single code point", () => {
    const out = ucsToGlyph("U+3005");
    expect(out).toBe("\u{3005}");
  });

  test("multiple code points", () => {
    const out = ucsToGlyph("U+845B U+E0102");
    expect(out).toBe("\u{845B}\u{E0102}");
  });

  test("literal character passthrough", () => {
    const out = ucsToGlyph("ABC");
    expect(out).toBe("ABC");
  });

  test("invalid hex returns original", () => {
    const out = ucsToGlyph("U+ZZZZ");
    expect(out).toBe("U+ZZZZ");
  });

  test("empty input returns empty string", () => {
    const out = ucsToGlyph("");
    expect(out).toBe("");
  });
});

//
// Tests for GlyphRenderer.render
//
describe("GlyphRenderer.render", () => {
  const renderer = new GlyphRenderer(false, "U+25A1"); // useBase=false

  test("empty text returns empty string", () => {
    const out = renderer.render("");
    expect(out).toBe("");
  });

  test("basic variant rendering", () => {
    const text = "A {MJ000001 b=U+3005 v=U+3005}";
    const out = renderer.render(text);
    expect(out).toBe("A \u{3005}");
  });

  test("variant preferred over base when useBase=false", () => {
    const text = "{MJ022335 b=U+845B v=U+845B U+E0102}";
    const out = renderer.render(text);
    expect(out).toBe("\u{845B}\u{E0102}");
  });

  test("base preferred when useBase=true", () => {
    const renderer2 = new GlyphRenderer(true, "U+25A1");
    const text = "{MJ022335 b=U+845B v=U+845B U+E0102}";
    const out = renderer2.render(text);
    expect(out).toBe("\u{845B}");
  });

  test("fallback tofu used when no b or v", () => {
    const text = "{MJ999999}";
    const out = renderer.render(text);
    expect(out).toBe("\u{25A1}");
  });

  test("temporary override of useBase", () => {
    const text = "{MJ022335 b=U+845B v=U+845B U+E0102}";
    const out = renderer.render(text, true);
    expect(out).toBe("\u{845B}");
  });

  test("temporary override of tofu", () => {
    const text = "{MJ999999}";
    const out = renderer.render(text, null, "U+3005");
    expect(out).toBe("\u{3005}");
  });

  test("double braces '{{' unescaped to '{'", () => {
    const text = "Start {{X}}";
    const out = renderer.render(text);
    expect(out).toBe("Start {X}}");
  });

  test("multiple tags mixed", () => {
    const text =
      "A {MJ000001 b=U+3005 v=U+3005} B {MJ022335 b=U+845B v=U+845B U+E0102}";
    const out = renderer.render(text);
    expect(out).toBe("A \u{3005} B \u{845B}\u{E0102}");
  });

  test("extra braces preserved", () => {
    const text = "{MJ000001 b=U+3005}}}";
    const out = renderer.render(text);
    expect(out.endsWith("}}")).toBe(true);
  });
});


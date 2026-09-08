/**
 * Unit tests for glyph_tag.js (tofurengo_js)
 * ASCII-only comments only.
 */

import { describe, test, expect } from "vitest";

import {
  normalize,
  render,
  normalizeAndRender,
} from "../src/glyph_tag.js";

import { TagIssue } from "../src/tag_parser.js";

// Minimal glyph table for real behavior tests
const glyphTable = {
  MJ000001: { b: "U+3005", v: "U+3005", active: true },
  MJ022335: { b: "U+845B", v: "U+845B U+E0102", active: true },
  MJ999999: { active: false },
};

//
// Tests for normalize()
//
describe("normalize()", () => {
  test("basic normalization", () => {
    const out = normalize("A {MJ000001}", glyphTable, "mj");

    expect(out.text).toBe("A {MJ000001 b=U+3005 v=U+3005 set=mj}");
    expect(out.issues.length).toBe(0);
  });

  test("inactive glyph produces issues but keeps tag", () => {
    const out = normalize("{MJ999999}", glyphTable, "mj");

    // normalize() does NOT convert to tofu
    expect(out.text).toBe("{MJ999999}");
    expect(out.issues.length).toBeGreaterThan(0);
    expect(out.issues[0]).toBeInstanceOf(TagIssue);
  });

  test("unknown glyph produces issues but keeps tag", () => {
    const out = normalize("{MJXXXXX}", glyphTable, "mj");

    expect(out.text).toBe("{MJXXXXX}");
    expect(out.issues.length).toBeGreaterThan(0);
  });

  test("escaped braces preserved when unescape=false", () => {
    const out = normalize("Start {{X}} {MJ000001}", glyphTable, "mj", false);

    expect(out.text.startsWith("Start {{X}}")).toBe(true);
  });
});

//
// Tests for render()
//
describe("render()", () => {
  test("empty text returns empty string", () => {
    const out = render("");
    expect(out).toBe("");
  });

  test("basic rendering", () => {
    const out = render("A {MJ000001 b=U+3005 v=U+3005}");
    expect(out).toBe("A \u{3005}");
  });

  test("useBase=true overrides variant", () => {
    const out = render("{MJ022335 b=U+845B v=U+845B U+E0102}", true);
    expect(out).toBe("\u{845B}");
  });

  test("tofu override works", () => {
    const out = render("{MJ999999}", false, "U+3005");
    expect(out).toBe("\u{3005}");
  });

  test("double braces '{{' unescaped to '{'", () => {
    const out = render("Start {{X}}");

    // Renderer behavior: '{{' -> '{', but '}}' stays '}}'
    expect(out).toBe("Start {X}}");
  });
});

//
// Tests for normalizeAndRender()
//
describe("normalizeAndRender()", () => {
  test("basic normalize + render", () => {
    const out = normalizeAndRender(
      "A {MJ000001} B {MJ022335}",
      glyphTable,
      "mj"
    );

    expect(out.text).toBe("A \u{3005} B \u{845B}\u{E0102}");
  });

  test("inactive glyph produces tofu", () => {
    const out = normalizeAndRender("{MJ999999}", glyphTable, "mj");

    expect(out.text).toBe("\u{25A1}");
    expect(out.issues.length).toBeGreaterThan(0);
  });

  test("useBase=true overrides variant", () => {
    const out = normalizeAndRender("{MJ022335}", glyphTable, "mj", true);

    expect(out.text).toBe("\u{845B}");
  });

  test("tofu override works", () => {
    const out = normalizeAndRender("{MJ999999}", glyphTable, "mj", false, "U+3005");

    expect(out.text).toBe("\u{3005}");
  });

  test("unescape=false preserves '{{'", () => {
    const out = normalizeAndRender(
      "Start {{X}} {MJ000001}",
      glyphTable,
      "mj",
      false,
      "U+25A1"
    );

    // '{{' -> '{', but '}}' stays '}}'
    expect(out.text.startsWith("Start {X}}")).toBe(true);
  });

  test("issues propagate from normalizer", () => {
    const out = normalizeAndRender("{MJ999999}", glyphTable, "mj");

    expect(out.issues.length).toBeGreaterThan(0);
    expect(out.issues[0]).toBeInstanceOf(TagIssue);
  });
});


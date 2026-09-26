/**
 * Unit tests for GlyphSimplifier
 */

import { describe, test, expect, beforeEach } from "vitest";

import { GlyphSimplifier } from "../src/glyph_simplifier.js";

describe("GlyphSimplifier", () => {
  let simplifier;

  beforeEach(() => {
    simplifier = new GlyphSimplifier();
  });

  test("should return empty string for null, undefined, or empty input", () => {
    expect(simplifier.simplify("")).toBe("");
    expect(simplifier.simplify(null)).toBe("");
    expect(simplifier.simplify(undefined)).toBe("");
  });

  test("should simplify GlyphTags by removing attributes", () => {
    const input = "Sample {MJ000001 b=U+30F1 v=U+30F1} text";
    const expected = "Sample {MJ000001} text";
    expect(simplifier.simplify(input)).toBe(expected);
  });

  test("preserve '{{' without converting to '{'", () => {
    const input = "Escaped {{brace} and tag {MJ000001 b=U+30F1}";
    const expected = "Escaped {{brace} and tag {MJ000001}";
    expect(simplifier.simplify(input)).toBe(expected);
  });
});

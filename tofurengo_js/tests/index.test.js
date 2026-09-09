/**
 * Unit tests for index.js (tofurengo_js)
 * ASCII-only comments only.
 */

import { describe, test, expect } from "vitest";

// Import from index.js (the re-export hub)
import {
  normalize,
  render,
  normalizeAndRender,

  MARK_LB,
  TAG_PATTERN,
  IssueLevel,
  TagIssue,
  ParsedTag,
  TagParser,

  makeReplaceFn,
  NormalizationResult,
  GlyphNormalizer,

  GlyphRenderer,
  ucsToGlyph,
} from "../src/index.js";

// Import original modules to compare identity
import * as glyphTag from "../src/glyph_tag.js";
import * as tagParser from "../src/tag_parser.js";
import * as glyphNormalizer from "../src/glyph_normalizer.js";
import * as glyphRenderer from "../src/glyph_renderer.js";

//
// High-level API re-export tests
//
describe("index.js high-level API re-exports", () => {
  test("normalize is re-exported correctly", () => {
    expect(normalize).toBe(glyphTag.normalize);
  });

  test("render is re-exported correctly", () => {
    expect(render).toBe(glyphTag.render);
  });

  test("normalizeAndRender is re-exported correctly", () => {
    expect(normalizeAndRender).toBe(glyphTag.normalizeAndRender);
  });
});

//
// Low-level tag_parser.js re-exports
//
describe("index.js tag_parser re-exports", () => {
  test("MARK_LB", () => {
    expect(MARK_LB).toBe(tagParser.MARK_LB);
  });

  test("TAG_PATTERN", () => {
    expect(TAG_PATTERN).toBe(tagParser.TAG_PATTERN);
  });

  test("IssueLevel", () => {
    expect(IssueLevel).toBe(tagParser.IssueLevel);
  });

  test("TagIssue", () => {
    expect(TagIssue).toBe(tagParser.TagIssue);
  });

  test("ParsedTag", () => {
    expect(ParsedTag).toBe(tagParser.ParsedTag);
  });

  test("TagParser", () => {
    expect(TagParser).toBe(tagParser.TagParser);
  });
});

//
// Low-level glyph_normalizer.js re-exports
//
describe("index.js glyph_normalizer re-exports", () => {
  test("makeReplaceFn", () => {
    expect(makeReplaceFn).toBe(glyphNormalizer.makeReplaceFn);
  });

  test("NormalizationResult", () => {
    expect(NormalizationResult).toBe(glyphNormalizer.NormalizationResult);
  });

  test("GlyphNormalizer", () => {
    expect(GlyphNormalizer).toBe(glyphNormalizer.GlyphNormalizer);
  });
});

//
// Low-level glyph_renderer.js re-exports
//
describe("index.js glyph_renderer re-exports", () => {
  test("GlyphRenderer", () => {
    expect(GlyphRenderer).toBe(glyphRenderer.GlyphRenderer);
  });

  test("ucsToGlyph", () => {
    expect(ucsToGlyph).toBe(glyphRenderer.ucsToGlyph);
  });
});

//
// Basic sanity tests for primitives
//
describe("index.js primitive behavior sanity checks", () => {
  test("MARK_LB is correct", () => {
    expect(MARK_LB).toBe("\u0002");
  });

  test("TAG_PATTERN matches basic tag", () => {
    const m = "{MJ000001}".match(TAG_PATTERN);
    expect(m).not.toBeNull();
  });

  test("ucsToGlyph works", () => {
    expect(ucsToGlyph("U+3005")).toBe("\u{3005}");
    expect(ucsToGlyph("ABC")).toBe("ABC");
  });
});


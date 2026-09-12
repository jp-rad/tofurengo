/**
 * @file index.js - Entry point for tofurengo_js library.
 * Client-side glyph tag parsing, normalization, and rendering toolkit.
 *
 * @module tofurengo_js
 */

// ============================================================================
// Primary High-Level API Functions
// ============================================================================

export {
  normalize,
  render,
  normalizeAndRender,
} from "./glyph_tag.js";

// ============================================================================
// Low-Level Modules and Primitives for Custom Extensions
// ============================================================================

/**
 * Tag parsing primitive constants, types, and classes.
 */
export {
  MARK_LB,
  TAG_PATTERN_SOURCE,
  IssueLevel,
  TagIssue,
  ParsedTag,
  TagParser,
} from "./tag_parser.js";

/**
 * Glyph normalization utilities and classes.
 */
export {
  makeReplaceFn,
  NormalizationResult,
  GlyphNormalizer,
} from "./glyph_normalizer.js";

/**
 * Glyph rendering utilities and classes.
 */
export {
  GlyphRenderer,
  ucsToGlyph,
} from "./glyph_renderer.js";

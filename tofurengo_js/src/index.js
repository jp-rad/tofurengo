/**
 * tofurengo_js - Client-side glyph tag parsing, normalization, and rendering toolkit.
 *
 * @module tofurengo_js
 */

// Primary High-Level API Functions
export { normalize, render, normalizeAndRender } from "./glyph_tag.js";

// Low-Level Modules and Primitives for Custom Extensions
export {
    MARK_LB,
    TAG_PATTERN,
    IssueLevel,
    TagIssue,
    ParsedTag,
    TagParser,
} from "./tag_parser.js";

export {
    makeReplaceFn,
    NormalizationResult,
    GlyphNormalizer,
} from "./glyph_normalizer.js";

export {
    GlyphRenderer,
    ucsToGlyph,
} from "./glyph_renderer.js";


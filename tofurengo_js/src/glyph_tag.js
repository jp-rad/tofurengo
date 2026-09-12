import { GlyphNormalizer } from "./glyph_normalizer.js";
import { GlyphRenderer } from "./glyph_renderer.js";

/**
 * @typedef {Object} NormalizationResult
 * @property {string} text - The normalized text string.
 * @property {Array<import("./tag_parser.js").TagIssue>} issues - List of parsing and normalization issues found.
 */

/**
 * Normalizes glyph tags within the provided raw input text using a specified dataset table.
 *
 * @param {string} text - Raw input text containing glyph tags to normalize.
 * @param {Record<string, Object>} glyphTable - Dataset table mapping glyph IDs to their respective attributes.
 * @param {string} setName - Dataset identifier (e.g., 'mj').
 * @returns {NormalizationResult} Result object containing normalized text and encountered issues.
 */
export function normalize(text, glyphTable, setName) {
  const normalizer = new GlyphNormalizer(glyphTable, setName);
  return normalizer.normalize(text);
}

/**
 * Renders text containing normalized glyph tags directly into Unicode character strings.
 *
 * @param {string} text - Input text containing normalized or raw glyph tags.
 * @param {boolean} [useBase=false] - Whether to prioritize base character attributes (`b=`).
 * @param {string} [tofu="U+25A1"] - Fallback UCS code point string or literal character for unmapped tags.
 * @returns {string} Rendered Unicode output text string.
 */
export function render(text, useBase = false, tofu = "U+25A1") {
  const renderer = new GlyphRenderer(useBase, tofu);
  return renderer.render(text);
}

/**
 * Helper function to normalize and immediately render raw text into a Unicode string.
 *
 * @param {string} text - Raw input text containing glyph tags.
 * @param {Record<string, Object>} glyphTable - Dataset table mapping glyph IDs to their attributes.
 * @param {string} setName - Dataset identifier (e.g., 'mj').
 * @param {boolean} [useBase=false] - Whether to prioritize base character attributes (`b=`).
 * @param {string} [tofu="U+25A1"] - Fallback UCS code point string or literal character.
 * @returns {NormalizationResult} Result object containing rendered text and encountered issues.
 */
export function normalizeAndRender(text, glyphTable, setName, useBase = false, tofu = "U+25A1") {
  const normalizationResult = normalize(text, glyphTable, setName);
  const renderedText = render(normalizationResult.text, useBase, tofu);
  return {
    text: renderedText,
    issues: normalizationResult.issues,
  };
}

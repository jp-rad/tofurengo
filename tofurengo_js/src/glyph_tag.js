import { GlyphNormalizer } from "./glyph_normalizer.js";
import { GlyphRenderer } from "./glyph_renderer.js";

/**
 * Normalizes glyph tags in raw input text using a dataset table.
 *
 * @param {string} text - Raw input text with glyph tags.
 * @param {Object.<string, Object>} glyphTable - Dataset table mapping glyph IDs to attributes.
 * @param {string} setName - Dataset identifier (e.g., 'mj').
 * @returns {{ text: string, issues: Array<import("./tag_parser.js").TagIssue> }} Object containing normalized text and encountered issues.
 */
export function normalize(text, glyphTable, setName) {
    const normalizer = new GlyphNormalizer(glyphTable, setName);
    return normalizer.normalize(text);
}

/**
 * Directly renders text containing normalized glyph tags into Unicode character strings.
 *
 * @param {string} text - Input text containing normalized or raw glyph tags.
 * @param {boolean} [useBase=false] - If true, prioritizes base character attributes (`b=`).
 * @param {string} [tofu="U+25A1"] - Fallback UCS sequence or literal character.
 * @returns {string} Rendered Unicode output text.
 */
export function render(text, useBase = false, tofu = "U+25A1") {
    const renderer = new GlyphRenderer(useBase, tofu);
    return renderer.render(text);
}

/**
 * Convenient all-in-one helper function to normalize and immediately render text into Unicode string.
 *
 * @param {string} text - Raw input text with glyph tags.
 * @param {Object.<string, Object>} glyphTable - Dataset table mapping glyph IDs to attributes.
 * @param {string} setName - Dataset identifier (e.g., 'mj').
 * @param {boolean} [useBase=false] - If true, prioritizes base character attributes (`b=`).
 * @param {string} [tofu="U+25A1"] - Fallback UCS sequence or literal character.
 * @returns {{ text: string, issues: Array<import("./tag_parser.js").TagIssue> }} Object containing rendered text and encountered issues.
 */
export function normalizeAndRender(text, glyphTable, setName, useBase = false, tofu = "U+25A1") {
    const normalizationResult = normalize(text, glyphTable, setName);
    const renderedText = render(normalizationResult.text, useBase, tofu);

    return {
        text: renderedText,
        issues: normalizationResult.issues,
    };
}


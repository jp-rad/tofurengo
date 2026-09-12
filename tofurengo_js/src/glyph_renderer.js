/**
 * Glyph Tag renderer module for the tofurengo library.
 *
 * Provides the `GlyphRenderer` class, which converts normalized Glyph Tags
 * into resolved Unicode character strings or fallback placeholder representations (tofu).
 */

import { TagParser } from "./tag_parser.js";

/**
 * Converts a Unicode code point hex string (e.g., 'U+845B' or 'U+845B U+E0102')
 * or a literal character into an actual JavaScript string.
 *
 * @param {string} ucsSequence - Space-separated hex code point string or literal text.
 * @returns {string} Converted Unicode character string.
 */
export function ucsToGlyph(ucsSequence) {
  if (!ucsSequence) return "";

  // If it contains "U+", parse hex code points
  if (ucsSequence.includes("U+")) {
    try {
      return ucsSequence
        .trim()
        .split(/\s+/)
        .map((hex) => {
          const cleanHex = hex.replace(/^U\+?/i, "");
          return String.fromCodePoint(parseInt(cleanHex, 16));
        })
        .join("");
    } catch (e) {
      return ucsSequence;
    }
  }

  // Return as literal character string
  return ucsSequence;
}

/**
 * Rendering engine for resolving normalized Glyph Tags into Unicode strings.
 *
 * Converts tags containing base (`b=`) or variant (`v=`) UCS attributes into
 * actual characters. If specified glyph sequences cannot be resolved, a fallback
 * string (tofu) is rendered instead.
 */
export class GlyphRenderer {
  /**
   * Initialize the GlyphRenderer.
   *
   * @param {boolean} [useBase=false] - If true, prioritizes base character attributes (`b=`)
   *     over implementation-specific variant attributes (`v=`). Defaults to false.
   * @param {string} [tofu="U+25A1"] - Fallback UCS sequence or literal character used when a glyph
   *     cannot be resolved. Defaults to "U+25A1" (White Square).
   */
  constructor(useBase = false, tofu = "U+25A1") {
    /** @type {boolean} */
    this.useBase = useBase;
    
    /** @type {string} */
    this.tofu = tofu;
  }

  /**
   * Render normalized text into a final Unicode string.
   *
   * Resolves Glyph Tags to characters based on prioritization rules and
   * unescapes double-brace sequences (`{{`) into literal single braces (`{`).
   *
   * @param {string} text - Normalized input text containing Glyph Tags.
   * @param {boolean|null} [useBase=null] - Temporarily override the instance `useBase` preference.
   * @param {string|null} [tofu=null] - Temporarily override the instance `tofu` fallback string.
   * @returns {string} Rendered output text with resolved Unicode characters and unescaped braces.
   */
  render(text, useBase = null, tofu = null) {
    if (!text) {
      return "";
    }

    const actualUseBase = useBase !== null ? useBase : this.useBase;
    const actualTofu = tofu !== null ? tofu : this.tofu;

    /**
     * @param {import("./tag_parser.js").ParsedTag} tag
     * @param {Array<import("./tag_parser.js").TagIssue>} issues
     * @returns {string}
     */
    const renderTag = (tag, issues) => {
      let targetSeq = "";
      if (actualUseBase) {
        targetSeq = tag.b || actualTofu;
      } else {
        targetSeq = tag.v || tag.b || actualTofu;
      }
      return ucsToGlyph(targetSeq);
    };

    // Execute processing pipeline with unescaping enabled (unescape=true)
    return TagParser.processPipeline(text, renderTag, true);
  }
}

/**
 * Glyph Tag simplifier module for the tofurengo library.
 *
 * Provides the `GlyphSimplifier` class, which converts normalized Glyph Tags
 * into simplified tag representations by stripping attributes.
 */
import { TagParser } from "./tag_parser.js";

/**
 * High-level service class for simplifying glyph tags in text strings.
 */
export class GlyphSimplifier {
  /**
   * Simplify normalized text containing Glyph Tags.
   *
   * Strips attributes from Glyph Tags and unescapes double-brace sequences (`{{`)
   * into literal single braces (`{`).
   *
   * @param {string} text - Normalized input text containing Glyph Tags.
   * @returns {string} Simplified output text with stripped tag attributes and unescaped braces.
   */
  simplify(text) {
    if (!text) {
      return "";
    }

    return TagParser.processPipeline(
      text,
      (tag) => `{${tag.glyphName}}`,
      false,  // unescape=false
    );
  }
}

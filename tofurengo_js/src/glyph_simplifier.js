/**
 * GlyphTag simplifier module for the tofurengo library.
 *
 * Provides the `GlyphSimplifier` class, which converts normalized GlyphTags
 * into simplified tag representations by stripping attributes.
 */
import { TagParser } from "./tag_parser.js";

/**
 * High-level service class for simplifying GlyphTags in text strings.
 */
export class GlyphSimplifier {
  /**
   * Simplify normalized text containing GlyphTags.
   *
   * Strips attributes from GlyphTags and unescapes double-brace sequences (`{{`)
   * into literal single braces (`{`).
   *
   * @param {string} text - Normalized input text containing GlyphTags.
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

/**
 * Tag parsing, replacement protocols, and placeholder escaping utilities for client-side JavaScript.
 *
 * Provides core parsing logic, token escaping, issue collection data structures,
 * and high-level string transformation pipeline functionality.
 */

// Control character used as a temporary placeholder for escaped opening braces '{{'
export const MARK_LB = "\u0002";

// Pattern string for matching a single tag enclosed in single braces: {glyph_name key=value ...}
// Disallows newlines inside tags and captures raw content inside group 1.
// Note: Defined as a plain string to avoid shared mutable RegExp state (lastIndex).
export const TAG_PATTERN_SOURCE =
  "\\{([ \\t]*[A-Za-z0-9_\\-]+(?:[ \\t]+[^}\\r\\n]+)?)\\}";

/**
 * Severity levels for tag processing diagnostics.
 *
 * @readonly
 * @enum {string}
 */
export const IssueLevel = {
  WARNING: "warning",
  ERROR: "error",
};

/**
 * Represents a warning or error encountered during tag processing.
 */
export class TagIssue {
  /**
   * @param {string} code - Machine-readable issue category identifier.
   * @param {string} message - Human-readable failure explanation.
   * @param {string} [level=IssueLevel.ERROR] - Severity level of the issue.
   * @param {Record<string, any>} [details={}] - Additional contextual metadata.
   */
  constructor(code, message, level = IssueLevel.ERROR, details = {}) {
    /** @type {string} */
    this.code = code;

    /** @type {string} */
    this.message = message;

    /** @type {string} */
    this.level = level;

    /** @type {Record<string, any>} */
    this.details = details;
  }
}

/**
 * Structured representation of a parsed glyph tag's contents.
 */
export class ParsedTag {
  /**
   * @param {string} glyphName - Primary glyph identifier.
   * @param {Record<string, string>} [properties={}] - Extracted key-value pairs.
   * @param {string} [rawContent=""] - Original unparsed tag content inside braces.
   */
  constructor(glyphName, properties = {}, rawContent = "") {
    /** @type {string} */
    this.glyphName = glyphName;

    /** @type {Record<string, string>} */
    this.properties = properties;

    /** @type {string} */
    this.rawContent = rawContent;

    // Shortcut accessors
    /** @type {string|null} */
    this.b = properties["b"] || null;

    /** @type {string|null} */
    this.v = properties["v"] || null;

    /** @type {string|null} */
    this.set = properties["set"] || null;
  }

  /**
   * Construct a ParsedTag instance directly from raw tag inner content.
   *
   * @param {string} content - Raw inner string extracted from inside a tag.
   * @returns {ParsedTag} Newly created ParsedTag instance.
   */
  static fromContent(content) {
    const rawStr = content.trim();
    const tokens = rawStr.split(/[ \t]+/);

    if (tokens.length === 0 || tokens[0] === "") {
      return new ParsedTag("", {}, rawStr);
    }

    let glyphName = "";
    let attrTokens = [];

    // Check if the first token is a key-value pair (missing glyph_name)
    if (tokens[0].includes("=")) {
      glyphName = "";
      attrTokens = tokens;
    } else {
      glyphName = tokens[0];
      attrTokens = tokens.slice(1);
    }

    const properties = {};
    let lastKey = null;

    for (const token of attrTokens) {
      if (token.includes("=")) {
        const eqIndex = token.indexOf("=");
        const key = token.slice(0, eqIndex);
        const value = token.slice(eqIndex + 1);
        properties[key] = value;
        lastKey = key;
      } else if (lastKey !== null) {
        // Append multi-token values (e.g., space-separated UCS sequences like 'U+845B U+E0103')
        properties[lastKey] = `${properties[lastKey]} ${token}`;
      }
    }

    return new ParsedTag(glyphName, properties, rawStr);
  }
}

/**
 * Utility class for handling brace escaping, restoration, and tag parsing pipelines.
 */
export class TagParser {
  /**
   * Replace escaped double-brace sequences with a temporary control character placeholder.
   *
   * @param {string} text - Input text containing double braces `{{`.
   * @returns {string} Text with double braces replaced by placeholder tokens.
   */
  static escapeTokens(text) {
    return text.replace(/\{\{/g, MARK_LB);
  }

  /**
   * Restore internal placeholders back to double-brace escape sequences (`{{`).
   *
   * @param {string} text - Text containing temporary placeholder tokens.
   * @returns {string} Text with placeholders restored to literal `{{`.
   */
  static restoreTokensPreserveEscape(text) {
    return text.replace(new RegExp(MARK_LB, "g"), "{{");
  }

  /**
   * Restore internal placeholders to single unescaped braces (`{`).
   *
   * @param {string} text - Text containing temporary placeholder tokens.
   * @returns {string} Text with placeholders converted to single `{`.
   */
  static restoreTokensUnescape(text) {
    return text.replace(new RegExp(MARK_LB, "g"), "{");
  }

  /**
   * Execute the full transformation pipeline: escape -> substitute -> restore.
   *
   * @param {string} text - Target text to process.
   * @param {function(ParsedTag, Array<TagIssue>): string} replacer - Callback receiving parsed tag and issues array.
   * @param {boolean} [unescape=true] - Convert preserved placeholders to single '{' if true.
   * @param {Array<TagIssue>|null} [issues=null] - Optional mutable array to collect encountered issues.
   * @returns {string} Transformed output text.
   */
  static processPipeline(text, replacer, unescape = true, issues = null) {
    const issueList = issues !== null ? issues : [];
    const escaped = this.escapeTokens(text);

    // Instantiate a fresh RegExp locally with global flag 'g' using the pattern string
    const globalPattern = new RegExp(TAG_PATTERN_SOURCE, "g");
    const substituted = escaped.replace(globalPattern, (match, content) => {
      const tag = ParsedTag.fromContent(content);
      return replacer(tag, issueList);
    });

    if (unescape) {
      return this.restoreTokensUnescape(substituted);
    }
    return this.restoreTokensPreserveEscape(substituted);
  }
}

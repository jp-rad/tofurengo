/**
 * Tag parsing, replacement protocols, and placeholder escaping utilities for client-side JavaScript.
 */

// Control character used as a temporary placeholder for escaped opening braces '{{'
export const MARK_LB = "\u0002";

// Matches a single tag enclosed in single braces: {glyph_name key=value ...}
// Disallows newlines inside tags and captures raw content inside group 1.
export const TAG_PATTERN = /\{([ \t]*[A-Za-z0-9_\-]+(?:[ \t]+[^}\r\n]+)?)\}/g;

/**
 * Severity levels for tag processing diagnostics.
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
     * @param {string} [level=IssueLevel.ERROR] - Severity level.
     * @param {Object} [details={}] - Additional contextual metadata.
     */
    constructor(code, message, level = IssueLevel.ERROR, details = {}) {
        this.code = code;
        this.message = message;
        this.level = level;
        this.details = details;
    }
}

/**
 * Structured representation of a parsed glyph tag's contents.
 */
export class ParsedTag {
    /**
     * @param {string} glyphName - Primary glyph identifier.
     * @param {Object.<string, string>} [properties={}] - Extracted key-value pairs.
     * @param {string} [rawContent=""] - Original unparsed tag content.
     */
    constructor(glyphName, properties = {}, rawContent = "") {
        this.glyphName = glyphName;
        this.properties = properties;
        this.rawContent = rawContent;

        // Shortcut accessors
        this.b = properties["b"] || null;
        this.v = properties["v"] || null;
        this.set = properties["set"] || null;
    }

    /**
     * Construct a ParsedTag instance directly from raw tag inner content.
     * @param {string} content - Raw inner string extracted from inside a tag.
     * @returns {ParsedTag}
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
 * Utility class for handling brace escaping, restoration, and tag parsing.
 */
export class TagParser {
    /**
     * Replace escaped double-brace sequences with a temporary control character.
     * @param {string} text
     * @returns {string}
     */
    static escapeTokens(text) {
        return text.replace(/\{\{/g, MARK_LB);
    }

    /**
     * Restore internal placeholders back to double-brace escape sequences ('{{').
     * @param {string} text
     * @returns {string}
     */
    static restoreTokensPreserveEscape(text) {
        return text.replace(new RegExp(MARK_LB, "g"), "{{");
    }

    /**
     * Restore internal placeholders to single unescaped braces ('{').
     * @param {string} text
     * @returns {string}
     */
    static restoreTokensUnescape(text) {
        return text.replace(new RegExp(MARK_LB, "g"), "{");
    }

    /**
     * Execute the full transformation pipeline: escape -> substitute -> restore.
     * @param {string} text - Target text to process.
     * @param {function(ParsedTag, Array<TagIssue>): string} replacer - Callback receiving (parsedTag, issues).
     * @param {boolean} [unescape=true] - Convert preserved placeholders to '{' if true.
     * @param {Array<TagIssue>|null} [issues=null] - Mutable array to collect encountered issues.
     * @returns {string} Transformed output text.
     */
    static processPipeline(text, replacer, unescape = true, issues = null) {
        const issueList = issues !== null ? issues : [];
        const escaped = this.escapeTokens(text);

        // Reset regex state before executing replacement
        TAG_PATTERN.lastIndex = 0;

        const substituted = escaped.replace(TAG_PATTERN, (match, content) => {
            const tag = ParsedTag.fromContent(content);
            return replacer(tag, issueList);
        });

        if (unescape) {
            return this.restoreTokensUnescape(substituted);
        }
        return this.restoreTokensPreserveEscape(substituted);
    }
}


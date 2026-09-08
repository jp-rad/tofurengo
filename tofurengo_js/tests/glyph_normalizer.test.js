/**
 * Unit tests for glyph_normalizer.js
 * ASCII-only comments only.
 */

import { describe, test, expect } from "vitest";

import {
    makeReplaceFn,
    NormalizationResult,
    GlyphNormalizer,
} from "../src/glyph_normalizer.js";

import {
    TagParser,
    ParsedTag,
    TagIssue,
    IssueLevel,
} from "../src/tag_parser.js";

describe("makeReplaceFn", () => {
    const GLYPH_TABLE = {
        MJ000001: { b: "U+3005", v: "U+3005", active: true },
        MJ000012: { b: "U+FFFF", v: "U+FFFF", active: false },
        MJ022335: { b: "U+845B", v: "U+845B U+E0102", active: true },
    };

    test("missing glyphName", () => {
        const fn = makeReplaceFn(GLYPH_TABLE, "mj");
        const tag = new ParsedTag("", {}, "");
        const issues = [];

        const out = fn(tag, issues);

        expect(out).toBe("{}");
        expect(issues.length).toBe(1);
        expect(issues[0].code).toBe("error.glyph.missing");
    });

    test("glyph not found", () => {
        const fn = makeReplaceFn(GLYPH_TABLE, "mj");
        const tag = new ParsedTag("UNKNOWN", {}, "UNKNOWN");
        const issues = [];

        const out = fn(tag, issues);

        expect(out).toBe("{UNKNOWN}");
        expect(issues.length).toBe(1);
        expect(issues[0].code).toBe("error.glyph.not_found");
    });

    test("glyph inactive", () => {
        const fn = makeReplaceFn(GLYPH_TABLE, "mj");
        const tag = new ParsedTag("MJ000012", {}, "MJ000012");
        const issues = [];

        const out = fn(tag, issues);

        expect(out).toBe("{MJ000012}");
        expect(issues.length).toBe(1);
        expect(issues[0].code).toBe("error.glyph.archived");
    });

    test("glyph active and normalized", () => {
        const fn = makeReplaceFn(GLYPH_TABLE, "mj");
        const tag = new ParsedTag("MJ022335", {}, "MJ022335");
        const issues = [];

        const out = fn(tag, issues);

        expect(out).toBe("{MJ022335 b=U+845B v=U+845B U+E0102 set=mj}");
        expect(issues.length).toBe(0);
    });
});

describe("GlyphNormalizer.normalize", () => {
    const GLYPH_TABLE = {
        MJ000001: { b: "U+3005", v: "U+3005", active: true },
        MJ000012: { b: "U+FFFF", v: "U+FFFF", active: false },
        MJ022335: { b: "U+845B", v: "U+845B U+E0102", active: true },
    };

    test("basic normalization", () => {
        const norm = new GlyphNormalizer(GLYPH_TABLE, "mj");
        const result = norm.normalize("A {MJ000001} B");

        expect(result instanceof NormalizationResult).toBe(true);
        expect(result.text).toBe("A {MJ000001 b=U+3005 v=U+3005 set=mj} B");
        expect(result.issues.length).toBe(0);
        expect(result.hasErrors()).toBe(false);
    });

    test("inactive glyph produces error", () => {
        const norm = new GlyphNormalizer(GLYPH_TABLE, "mj");
        const result = norm.normalize("A {MJ000012} B");

        expect(result.text).toBe("A {MJ000012} B");
        expect(result.issues.length).toBe(1);
        expect(result.issues[0].code).toBe("error.glyph.archived");
        expect(result.hasErrors()).toBe(true);
    });

    test("unknown glyph produces error", () => {
        const norm = new GlyphNormalizer(GLYPH_TABLE, "mj");
        const result = norm.normalize("A {UNKNOWN} B");

        expect(result.text).toBe("A {UNKNOWN} B");
        expect(result.issues.length).toBe(1);
        expect(result.issues[0].code).toBe("error.glyph.not_found");
        expect(result.hasErrors()).toBe(true);
    });

    test("escape '{{' then unescape to '{'", () => {
        const norm = new GlyphNormalizer(GLYPH_TABLE, "mj");
        const result = norm.normalize("Start {{X}} {MJ000001}");

        expect(result.text.startsWith("Start {{X}} {MJ000001 ")).toBe(true);
        expect(result.text.includes("MJ000001")).toBe(true);
    });

    test("unescape=false preserves '{{'", () => {
        const norm = new GlyphNormalizer(GLYPH_TABLE, "mj");
        const result = norm.normalize("Start {{X}} {MJ000001}", false);

        expect(result.text.startsWith("Start {{X}}")).toBe(true);
    });

    test("multiple tags mixed", () => {
        const norm = new GlyphNormalizer(GLYPH_TABLE, "mj");
        const result = norm.normalize(
            "A {MJ000001} B {UNKNOWN} C {MJ000012} D {MJ022335}"
        );

        expect(result.text.includes("MJ000001 b=U+3005")).toBe(true);
        expect(result.text.includes("{UNKNOWN}")).toBe(true);
        expect(result.text.includes("{MJ000012}")).toBe(true);
        expect(result.text.includes("MJ022335 b=U+845B")).toBe(true);

        expect(result.issues.length).toBe(2);
        expect(result.hasErrors()).toBe(true);
    });
});


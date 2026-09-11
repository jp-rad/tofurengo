/**
 * Unit tests for tag_parser.js
 * ASCII-only comments only.
 */

import { describe, test, expect } from "vitest";

import {
    MARK_LB,
    TAG_PATTERN_SOURCE,
    IssueLevel,
    TagIssue,
    ParsedTag,
    TagParser,
} from "../src/tag_parser.js";

describe("ParsedTag.fromContent", () => {
    test("basic glyph with properties", () => {
        const tag = ParsedTag.fromContent("MJ000001 b=U+3005 v=U+3005 set=mj");
        expect(tag.glyphName).toBe("MJ000001");
        expect(tag.b).toBe("U+3005");
        expect(tag.v).toBe("U+3005");
        expect(tag.set).toBe("mj");
    });

    test("multi-token value", () => {
        const tag = ParsedTag.fromContent("MJ022336 v=U+845B U+E0103");
        expect(tag.v).toBe("U+845B U+E0103");
    });

    test("missing glyphName", () => {
        const tag = ParsedTag.fromContent("b=U+3005 v=U+3005");
        expect(tag.glyphName).toBe("");
        expect(tag.b).toBe("U+3005");
        expect(tag.v).toBe("U+3005");
    });

    test("rawContent preserved", () => {
        const tag = ParsedTag.fromContent("MJ000001 b=U+3005");
        expect(tag.rawContent).toBe("MJ000001 b=U+3005");
    });
});

describe("TagParser escape and restore", () => {
    test("escape '{{' into MARK_LB", () => {
        const out = TagParser.escapeTokens("Start {{X}}");
        expect(out).toBe(`Start ${MARK_LB}X}}`);
    });

    test("restore preserve '{{'", () => {
        const out = TagParser.restoreTokensPreserveEscape(`A ${MARK_LB} B`);
        expect(out).toBe("A {{ B");
    });

    test("restore unescape '{'", () => {
        const out = TagParser.restoreTokensUnescape(`A ${MARK_LB} B`);
        expect(out).toBe("A { B");
    });
});

describe("TAG_PATTERN_SOURCE", () => {
    test("matches simple tag", () => {
        const text = "A {MJ000001} B";
        const matches = [...text.matchAll(new RegExp(TAG_PATTERN_SOURCE, "g"))];
        expect(matches.length).toBe(1);
        expect(matches[0][1]).toBe("MJ000001");
    });

    test("matches tag with properties", () => {
        const text = "A {MJ000001 b=U+3005} B";
        const matches = [...text.matchAll(new RegExp(TAG_PATTERN_SOURCE, "g"))];
        expect(matches.length).toBe(1);
        expect(matches[0][1]).toBe("MJ000001 b=U+3005");
    });

    test("does not match newline inside tag", () => {
        const text = "A {MJ000001\nb=U+3005} B";
        const matches = [...text.matchAll(new RegExp(TAG_PATTERN_SOURCE, "g"))];
        expect(matches.length).toBe(0);
    });
});

describe("TagParser processPipeline", () => {
    test("basic replacement", () => {
        const replacer = (tag) => `[${tag.glyphName}]`;
        const out = TagParser.processPipeline("A {MJ000001} B", replacer);
        expect(out).toBe("A [MJ000001] B");
    });

    test("escape then replace then unescape", () => {
        const replacer = (tag) => tag.glyphName;
        const out = TagParser.processPipeline("{{X}} {MJ000001}", replacer);
        expect(out.startsWith("{X}")).toBe(true);
        expect(out.includes("MJ000001")).toBe(true);
    });

    test("extra braces preserved", () => {
        const replacer = (tag) => tag.glyphName;
        const out = TagParser.processPipeline("{MJ000001}}}", replacer);
        expect(out).toBe("MJ000001}}");
    });

    test("issues collected", () => {
        const issues = [];
        const replacer = (tag, issuesArr) => {
            issuesArr.push(new TagIssue("test.issue", "dummy"));
            return tag.glyphName;
        };

        TagParser.processPipeline("{MJ000001}", replacer, true, issues);
        expect(issues.length).toBe(1);
        expect(issues[0].code).toBe("test.issue");
    });

    test("unescape=false preserves '{{'", () => {
        const replacer = (tag) => tag.glyphName;
        const out = TagParser.processPipeline("{{X}} {MJ000001}", replacer, false);
        expect(out.startsWith("{{X}}")).toBe(true);
    });
});


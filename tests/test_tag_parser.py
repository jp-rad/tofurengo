import pytest
from tofurengo.tag_parser import (
    TagParser,
    ParsedTag,
    TagIssue,
    IssueLevel,
)

# Reference:
# MJ022335 (KATSU)
# Basic code point: U+845B
# IVS code point:   U+E0102
# Official info URL:
# https://moji.or.jp/mojikibansearch/info?MJ%E6%96%87%E5%AD%97%E5%9B%B3%E5%BD%A2%E5%90%8D=MJ022335


# ------------------------------------------------------------
# ParsedTag.from_content
# ------------------------------------------------------------

def test_parsed_tag_basic():
    tag = ParsedTag.from_content("MJ022335 b=U+845B v=U+845B U+E0102 set=mj")
    assert tag.glyph_name == "MJ022335"
    assert tag.b == "U+845B"
    assert tag.v == "U+845B U+E0102"
    assert tag.set == "mj"
    assert tag.properties["b"] == "U+845B"
    assert tag.properties["v"] == "U+845B U+E0102"


def test_parsed_tag_empty():
    tag = ParsedTag.from_content("")
    assert tag.glyph_name == ""
    assert tag.properties == {}


def test_parsed_tag_no_properties():
    tag = ParsedTag.from_content("MJ022335")
    assert tag.glyph_name == "MJ022335"
    assert tag.properties == {}


def test_parsed_tag_missing_glyph_name():
    # First token is key=value → glyph_name must be empty
    tag = ParsedTag.from_content("b=U+845B v=U+E0102")
    assert tag.glyph_name == ""
    assert tag.b == "U+845B"
    assert tag.v == "U+E0102"


def test_parsed_tag_multi_token_value():
    tag = ParsedTag.from_content("MJ022335 v=U+845B U+E0102 U+E0103")
    assert tag.v == "U+845B U+E0102 U+E0103"


def test_parsed_tag_trailing_spaces():
    tag = ParsedTag.from_content("   MJ022335    b=U+845B   ")
    assert tag.glyph_name == "MJ022335"
    assert tag.b == "U+845B"


def test_parsed_tag_invalid_property_format():
    # Token without "=" and without previous key → ignored
    tag = ParsedTag.from_content("MJ022335 X Y Z")
    assert tag.properties == {}


def test_parsed_tag_property_chain():
    # Multi-token chain appended to last key
    tag = ParsedTag.from_content("MJ022335 v=U+845B U+E0102 U+E0103 U+E0104")
    assert tag.v == "U+845B U+E0102 U+E0103 U+E0104"


# ------------------------------------------------------------
# TAG_PATTERN behavior
# ------------------------------------------------------------

def test_tag_pattern_basic():
    out = TagParser.process_pipeline("{MJ022335}", lambda t, i: "X")
    assert out == "X"


def test_tag_pattern_leading_whitespace():
    out = TagParser.process_pipeline("{   MJ022335}", lambda t, i: "X")
    assert out == "X"


def test_tag_pattern_reject_newline_inside():
    text = "{MJ022335\nb=U+845B}"
    out = TagParser.process_pipeline(text, lambda t, i: "X")
    assert out == text  # No replacement


def test_tag_pattern_identifier_rules():
    text = "{MJ-022335}"
    out = TagParser.process_pipeline(text, lambda t, i: "OK")
    assert out == "OK"


def test_tag_pattern_invalid_identifier():
    # Identifier must match [A-Za-z0-9_-]+
    text = "{@@@}"
    out = TagParser.process_pipeline(text, lambda t, i: "X")
    assert out == text  # No replacement


# ------------------------------------------------------------
# TagParser.escape / restore
# ------------------------------------------------------------

def test_escape_tokens():
    text = "{{MJ022335}}"
    escaped = TagParser.escape_tokens(text)
    assert "\u0002" in escaped


def test_restore_preserve_escape():
    text = "\u0002MJ022335\u0002"
    restored = TagParser.restore_tokens_preserve_escape(text)
    assert restored == "{{MJ022335{{"


def test_restore_unescape():
    text = "\u0002MJ022335\u0002"
    restored = TagParser.restore_tokens_unescape(text)
    assert restored == "{MJ022335{"


# ------------------------------------------------------------
# TagParser.process_pipeline basic replacement
# ------------------------------------------------------------

def test_process_pipeline_basic():
    def replacer(tag, issues):
        return "[OK:" + tag.glyph_name + "]"

    out = TagParser.process_pipeline("{MJ022335}", replacer)
    assert out == "[OK:MJ022335]"


def test_process_pipeline_multiple_tags():
    def replacer(tag, issues):
        return "<" + tag.glyph_name + ">"

    text = "A {MJ022335} B {MJ000001} C"
    out = TagParser.process_pipeline(text, replacer)
    assert out == "A <MJ022335> B <MJ000001> C"


# ------------------------------------------------------------
# Escaping behavior
# ------------------------------------------------------------

def test_process_pipeline_with_escape():
    def replacer(tag, issues):
        return "[X]"

    text = "{{{MJ022335}}"
    out = TagParser.process_pipeline(text, replacer)
    assert out == "{[X]}"

    text = "{{{MJ022335}}}"
    out = TagParser.process_pipeline(text, replacer)
    assert out == "{[X]}}"


def test_process_pipeline_preserve_escape():
    def replacer(tag, issues):
        return "[" + tag.glyph_name + "]"

    text = "Start {{X}} and {MJ022335}"
    out = TagParser.process_pipeline(text, replacer, unescape=False)
    assert out == "Start {{X}} and [MJ022335]"


# ------------------------------------------------------------
# Issue collection
# ------------------------------------------------------------

def test_process_pipeline_collect_issues():
    def replacer(tag, issues):
        issues.append(TagIssue(code="t", message="test", level=IssueLevel.WARNING))
        return "Z"

    issues = []
    text = "Sentence {MJ022335} test"
    out = TagParser.process_pipeline(text, replacer, issues=issues)

    assert out == "Sentence Z test"
    assert len(issues) == 1
    assert issues[0].level == IssueLevel.WARNING


# ------------------------------------------------------------
# Sentence without tags
# ------------------------------------------------------------

def test_process_pipeline_no_tags():
    def replacer(tag, issues):
        return "X"

    text = "No tags here."
    out = TagParser.process_pipeline(text, replacer)
    assert out == "No tags here."


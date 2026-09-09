import pytest
from tofurengo.replacer import make_replace_fn
from tofurengo.tag_parser import TagParser, TagIssue


# Dummy glyph table for testing
GLYPH_TABLE = {
    "MJ022335": {"b": "U+845B", "v": "U+845B U+E0102", "active": True},
    "MJ999999": {"b": "U+FFFF", "v": "U+FFFF", "active": False},
}


# ------------------------------------------------------------
# Basic normalization
# ------------------------------------------------------------

def test_replacer_basic():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    issues = []
    out = TagParser.process_pipeline("{MJ022335}", fn, issues=issues)

    assert out == "{MJ022335 b=U+845B v=U+845B U+E0102 set=mj}"
    assert issues == []


# ------------------------------------------------------------
# Glyph not found
# ------------------------------------------------------------

def test_replacer_glyph_not_found():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    issues = []
    out = TagParser.process_pipeline("{UNKNOWN}", fn, issues=issues)

    assert out == "{UNKNOWN}"
    assert len(issues) == 1
    assert isinstance(issues[0], TagIssue)
    assert issues[0].code == "error.glyph.not_found"


# ------------------------------------------------------------
# Glyph inactive
# ------------------------------------------------------------

def test_replacer_glyph_inactive():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    issues = []
    out = TagParser.process_pipeline("{MJ999999}", fn, issues=issues)

    assert out == "{MJ999999}"
    assert len(issues) == 1
    assert isinstance(issues[0], TagIssue)
    assert issues[0].code == "error.glyph.archived"


# ------------------------------------------------------------
# Empty tag content
# ------------------------------------------------------------

def test_replacer_empty_content():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    issues = []
    out = TagParser.process_pipeline("{}", fn, issues=issues)

    assert out == "{}"
    assert issues == []


# ------------------------------------------------------------
# Multiple tags in sentence
# ------------------------------------------------------------

def test_replacer_multiple_tags():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    issues = []
    text = "A {MJ022335} B {UNKNOWN} C"

    out = TagParser.process_pipeline(text, fn, issues=issues)

    assert out.startswith("A {MJ022335 b=U+845B")
    assert "{UNKNOWN}" in out
    assert len(issues) == 1
    assert issues[0].code == "error.glyph.not_found"


# ------------------------------------------------------------
# Escaped braces
# ------------------------------------------------------------

def test_replacer_escape_behavior():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    issues = []

    text = "{{{MJ022335}}}"
    out = TagParser.process_pipeline(text, fn, issues=issues)

    # "{{" becomes "{"
    assert out.startswith("{")
    assert "MJ022335" in out


# ------------------------------------------------------------
# No tags
# ------------------------------------------------------------

def test_replacer_no_tags():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    issues = []

    out = TagParser.process_pipeline("No tags here.", fn, issues=issues)

    assert out == "No tags here."
    assert issues == []


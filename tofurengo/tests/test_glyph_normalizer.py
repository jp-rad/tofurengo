import pytest
from tofurengo.glyph_normalizer import GlyphNormalizer, NormalizeResult
from tofurengo.replacer import make_replace_fn
from tofurengo.tag_parser import TagIssue, IssueLevel


# Dummy glyph table
GLYPH_TABLE = {
    "GJ000002": {"b": None, "v": "U+100001", "active": True},
    "MJ022335": {"b": "U+845B", "v": "U+845B U+E0102", "active": True},
    "MJ999999": {"b": "U+FFFF", "v": "U+FFFF", "active": False},
}


# ------------------------------------------------------------
# Basic normalization
# ------------------------------------------------------------

def test_normalizer_basic():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    norm = GlyphNormalizer(fn)

    result = norm.normalize("{MJ022335}")

    assert isinstance(result, NormalizeResult)
    assert result.success is True
    assert result.text == "{MJ022335 b=U+845B v=U+845B U+E0102 set=mj}"
    assert result.issues == []

def test_normalizer_no_base_glyph():
    fn = make_replace_fn(GLYPH_TABLE, "gj")
    norm = GlyphNormalizer(fn)

    result = norm.normalize("{GJ000002}")

    assert isinstance(result, NormalizeResult)
    assert result.success is True
    assert result.text == "{GJ000002 b= v=U+100001 set=gj}"

    assert len(result.issues) == 1
    issue = result.issues[0]
    assert issue.code == "warning.glyph.b_missing"
    assert issue.level == IssueLevel.WARNING
    assert issue.details == {"glyph": "GJ000002"}

# ------------------------------------------------------------
# Glyph not found
# ------------------------------------------------------------

def test_normalizer_glyph_not_found():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    norm = GlyphNormalizer(fn)

    result = norm.normalize("{UNKNOWN}")

    assert result.success is False
    assert len(result.errors) == 1
    assert isinstance(result.errors[0], TagIssue)
    assert result.text == "{UNKNOWN}"


# ------------------------------------------------------------
# Glyph inactive
# ------------------------------------------------------------

def test_normalizer_glyph_inactive():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    norm = GlyphNormalizer(fn)

    result = norm.normalize("{MJ999999}")

    assert result.success is False
    assert len(result.errors) == 1
    assert result.errors[0].code == "error.glyph.archived"
    assert result.text == "{MJ999999}"


# ------------------------------------------------------------
# Empty text
# ------------------------------------------------------------

def test_normalizer_empty_text():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    norm = GlyphNormalizer(fn)

    result = norm.normalize("")

    assert result.success is True
    assert result.text == ""
    assert result.issues == []


# ------------------------------------------------------------
# Missing replace_fn
# ------------------------------------------------------------

def test_normalizer_missing_replace_fn():
    norm = GlyphNormalizer(None)

    with pytest.raises(ValueError):
        norm.normalize("{MJ022335}")


# ------------------------------------------------------------
# Multiple tags
# ------------------------------------------------------------

def test_normalizer_multiple_tags():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    norm = GlyphNormalizer(fn)

    text = "A {MJ022335} B {UNKNOWN} C"
    result = norm.normalize(text)

    assert result.success is False
    assert len(result.errors) == 1
    assert "{MJ022335 b=U+845B" in result.text
    assert "{UNKNOWN}" in result.text


# ------------------------------------------------------------
# Escape sequences '{{'
# ------------------------------------------------------------

def test_normalizer_escape_sequences():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    norm = GlyphNormalizer(fn)

    text = "{{{MJ022335}}}"
    result = norm.normalize(text)

    # '{{' preserved
    assert result.text.startswith("{")
    assert "MJ022335" in result.text


# ------------------------------------------------------------
# to_dict serialization
# ------------------------------------------------------------

def test_normalizer_to_dict():
    fn = make_replace_fn(GLYPH_TABLE, "mj")
    norm = GlyphNormalizer(fn)

    result = norm.normalize("{UNKNOWN}")
    d = result.to_dict()

    assert d["success"] is False
    assert "issues" in d
    assert isinstance(d["issues"], list)


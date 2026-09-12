import pytest
from unittest.mock import patch

from tofurengo.builder import build_normalizer_from_table, build_normalizer, build_renderer, build_simplifier
from tofurengo.glyph_normalizer import GlyphNormalizer
from tofurengo.glyph_renderer import GlyphRenderer
from tofurengo.glyph_simplifier import GlyphSimplifier


# ------------------------------------------------------------
# build_normalizer
# ------------------------------------------------------------

def test_build_normalizer_from_table_example():
    glyph_table = {
        "MJ013044": {"b": "U+6589", "v": "U+6589 U+E0102"},
        "MJ013049": {"b": "U+6589", "v": "U+658E U+E0102"},
        "MJ013050": {"b": "U+6589", "v": "U+658E U+E0103"},
        "MJ030058": {"b": "U+6589", "v": "U+9F4A U+E0103"},
        "MJ030059": {"b": "U+6589", "v": "U+9F4A U+E0102"},
    }

    normalizer = build_normalizer_from_table(glyph_table=glyph_table, set_name="sai")
    result = normalizer.normalize("Sample {MJ013050}")

    assert result.text == "Sample {MJ013050 b=U+6589 v=U+658E U+E0103 set=sai}"

@patch("tofurengo.builder.get_resource")
def test_build_normalizer_basic(mock_get_resource):
    # Fake dataset resource
    mock_get_resource.return_value = {
        "GLYPH_TABLE": {
            "MJ022335": {"b": "U+845B", "v": "U+845B U+E0102", "active": True}
        },
        "VERSION": "v6_02_201",
        "LIBRARY_NAME": "dummy-lib",
    }

    norm = build_normalizer("mj", "6.02.201")

    assert isinstance(norm, GlyphNormalizer)
    assert norm.replace_fn is not None


@patch("tofurengo.builder.get_resource")
def test_build_normalizer_set_name_override(mock_get_resource):
    mock_get_resource.return_value = {
        "GLYPH_TABLE": {"MJ000001": {"b": "U+4E00", "v": "U+4E00 U+E0101", "active": True}},
        "VERSION": "v1",
        "LIBRARY_NAME": "dummy",
    }

    norm = build_normalizer("mj", "1.0", set_name="custom")

    assert isinstance(norm, GlyphNormalizer)
    # ReplaceFn should embed "custom" as set name
    out = norm.normalize("{MJ000001}")
    assert "set=custom" in out.text


# ------------------------------------------------------------
# build_renderer
# ------------------------------------------------------------

def test_build_renderer_basic():
    renderer = build_renderer()

    assert isinstance(renderer, GlyphRenderer)
    assert renderer.use_base is False
    assert renderer.tofu == "U+25A1"


def test_build_renderer_override():
    renderer = build_renderer(use_base=True, tofu="U+FFFD")

    assert renderer.use_base is True
    assert renderer.tofu == "U+FFFD"


# ------------------------------------------------------------
# build_simplifier
# ------------------------------------------------------------

def test_build_simplifier():
    """Test build_simplifier returns a GlyphSimplifier instance without arguments."""
    simplifier = build_simplifier()

    assert isinstance(simplifier, GlyphSimplifier)

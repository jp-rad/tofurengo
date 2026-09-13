import pytest
from tofurengo.glyph_simplifier import GlyphSimplifier


class TestGlyphSimplifier:
    """Test suite for GlyphSimplifier."""

    def test_simplify_basic_tag(self) -> None:
        """Test stripping attributes from a normalized tag."""
        simplifier = GlyphSimplifier()
        input_text = "{MJ022335 b=U+845B v=U+845B U+E0102 set=mj}"
        expected = "{MJ022335}"
        assert simplifier.simplify(input_text) == expected

    def test_simplify_tag_without_attributes(self) -> None:
        """Test processing a tag that already has no attributes."""
        simplifier = GlyphSimplifier()
        input_text = "{MJ022335}"
        expected = "{MJ022335}"
        assert simplifier.simplify(input_text) == expected

    def test_simplify_multiple_tags_in_text(self) -> None:
        """Test simplifying multiple tags within surrounding text."""
        simplifier = GlyphSimplifier()
        input_text = "Tag1:{MJ022335 b=U+845B set=mj} Tag2:{MJ010526 v=U+8FBB U+E0101}"
        expected = "Tag1:{MJ022335} Tag2:{MJ010526}"
        assert simplifier.simplify(input_text) == expected

    def test_simplify_retains_double_brace_escape(self) -> None:
        """Test that double braces '{{' are preserved and not unescaped."""
        simplifier = GlyphSimplifier()
        input_text = "Escaped {{MJ022335 b=U+845B} and normal {MJ022335 b=U+845B}"
        expected = "Escaped {{MJ022335 b=U+845B} and normal {MJ022335}"
        assert simplifier.simplify(input_text) == expected

    def test_simplify_empty_and_plain_string(self) -> None:
        """Test edge cases with empty strings or text without tags."""
        simplifier = GlyphSimplifier()
        assert simplifier.simplify("") == ""
        assert simplifier.simplify("Plain text without tags.") == "Plain text without tags."

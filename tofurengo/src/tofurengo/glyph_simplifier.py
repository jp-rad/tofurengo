"""GlyphTag simplifier module for the tofurengo library.

This module provides the `GlyphSimplifier` class, which simplifies GlyphTags
in text by stripping all attributes and reducing tags to their base `{<glyph-name>}` format.
"""

from tofurengo.tag_parser import ParsedTag, TagIssue, TagParser


class GlyphSimplifier:
    """Simplification engine for stripping attributes from GlyphTags.

    Converts GlyphTags containing attributes (such as `b=`, `v=`, or `set=`)
    back into their simplified `{<glyph-name>}` representation.
    """

    def __init__(self) -> None:
        """Initialize the GlyphSimplifier."""
        pass

    def simplify(self, text: str) -> str:
        """Simplify GlyphTags in the input text by stripping all attributes.

        Args:
            text (str): Input text containing GlyphTags.

        Returns:
            str: Simplified output text with `{<glyph-name>}` format tags.
        """
        if not text:
            return ""

        def _simplify_tag(tag: ParsedTag, issues: list[TagIssue]) -> str:
            return f"{{{tag.glyph_name}}}"

        # Execute processing pipeline
        return TagParser.process_pipeline(
            text=text,
            replacer=_simplify_tag,
            unescape=False,  # Retain '{{' escape sequences during simplification
        )


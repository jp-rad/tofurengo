"""
Glyph Tag renderer module for the tofurengo library.

This module provides the `GlyphRenderer` class, which converts normalized Glyph Tags
into resolved Unicode character strings or fallback placeholder representations (tofu).
"""

from typing import Optional

from tofurengo.tag_parser import ParsedTag, TagIssue, TagParser
from tofurengo.ucs import ucs_to_glyph


class GlyphRenderer:
    """
    Rendering engine for resolving normalized Glyph Tags into Unicode strings.

    Converts tags containing base (`b=`) or variant (`v=`) UCS attributes into
    actual characters. If specified glyph sequences cannot be resolved, a fallback
    string (tofu) is rendered instead.
    """

    def __init__(
        self,
        use_base: bool = False,
        tofu: str = "U+25A1",
    ) -> None:
        """
        Initialize the GlyphRenderer.

        Args:
            use_base (bool): If True, prioritizes base character attributes (`b=`)
                over implementation-specific variant attributes (`v=`). Defaults to False.
            tofu (str): Fallback UCS sequence or literal character used when a glyph
                cannot be resolved. Defaults to "U+25A1" (White Square □).
        """
        self.use_base = use_base
        self.tofu = tofu

    def render(
        self,
        text: str,
        use_base: Optional[bool] = None,
        tofu: Optional[str] = None,
    ) -> str:
        """
        Render normalized text into a final Unicode string.

        Resolves Glyph Tags to characters based on prioritization rules and
        unescapes double-brace sequences (`{{`) into literal single braces (`{`).

        Args:
            text (str): Normalized input text containing Glyph Tags.
            use_base (Optional[bool]): Temporarily override the instance `use_base` preference.
            tofu (Optional[str]): Temporarily override the instance `tofu` fallback string.

        Returns:
            str: Rendered output text with resolved Unicode characters and unescaped braces.
        """
        if not text:
            return ""

        actual_use_base = self.use_base if use_base is None else use_base
        actual_tofu = self.tofu if tofu is None else tofu

        def _render_tag(tag: ParsedTag, issues: list[TagIssue]) -> str:
            if actual_use_base:
                target_seq = tag.b or actual_tofu
            else:
                target_seq = tag.v or tag.b or actual_tofu

            return ucs_to_glyph(target_seq)

        # Execute processing pipeline with unescaping enabled (unescape=True)
        return TagParser.process_pipeline(text, _render_tag, unescape=True)


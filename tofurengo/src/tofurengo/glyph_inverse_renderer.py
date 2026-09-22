"""
Inverse Glyph Tag renderer module for the tofurengo library.

This module provides the `GlyphInverseRenderer` class, which performs the
reverse operation of `GlyphRenderer`. It converts Unicode text into
normalized Glyph Tags, applying brace escaping and customizable glyph
conversion logic.

This version uses Unicode grapheme cluster segmentation so that characters
with Ideographic Variation Sequences (IVS) are treated as single units.
"""

import re
from typing import List, Optional, Protocol


class GlyphConverter(Protocol):
    """
    Protocol definition for glyph conversion callbacks.

    Implementations are callable objects that accept a single Unicode
    grapheme cluster and return the corresponding glyph name if the
    cluster can be mapped. If the cluster cannot be converted, the
    implementation must return None.

    Signature:
        (ch: str) -> Optional[str]
    """

    def __call__(self, ch: str) -> Optional[str]:
        """
        Convert a Unicode grapheme cluster into a glyph name.

        Args:
            ch (str): A Unicode grapheme cluster.

        Returns:
            Optional[str]: The glyph name if conversion is possible,
            otherwise None.
        """
        ...


class GlyphInverseRenderer:
    """
    Inverse rendering engine for converting Unicode grapheme clusters into
    normalized Glyph Tags.

    This class performs the conceptual reverse of `GlyphRenderer.render()`,
    scanning text grapheme-by-grapheme and converting eligible clusters
    into "{GlyphName}" tags. Literal brace characters ("{") are always
    escaped into "{{" when no glyph conversion is performed.
    """

    def __init__(
        self,
        glyph_converter: Optional[GlyphConverter] = None,
    ) -> None:
        """
        Initialize the inverse renderer.

        Args:
            glyph_converter (GlyphConverter | None):
                Custom glyph conversion function. If omitted, clusters
                are not converted into tags.
        """
        self.glyph_converter = glyph_converter

    @staticmethod
    def _escape_left_brace(ch: str) -> str:
        """
        Escape a literal left brace.

        Converts a single "{" character into "{{", ensuring that literal
        braces are preserved during later tag parsing stages.

        Args:
            ch (str): A grapheme cluster.

        Returns:
            str: "{{" if the input is "{", otherwise the original cluster.
        """
        if ch == "{":
            return "{{"
        return ch

    @staticmethod
    def _split_grapheme_clusters(text: str) -> List[str]:
        pattern = re.compile(
            r".(?:[\U000E0100-\U000E01EF]|[\u3099\u309A]|[\u0300-\u036F])*",
            re.DOTALL
        )

        return pattern.findall(text)

    def inverse_text(self, text: str) -> str:
        """
        Convert Unicode text into tag-containing text.

        Behavior:
        - If glyph_converter is provided and returns a glyph name,
          the cluster is converted into "{GlyphName}".
        - If glyph_converter is provided but returns None,
          the cluster is preserved, except "{" which is escaped.
        - If glyph_converter is not provided at all,
          no conversion is performed; only "{" is escaped.

        Grapheme cluster segmentation ensures that sequences such as
        "U+845B U+E0102" (IVS) are treated as single units.

        Args:
            text (str): Input Unicode string.

        Returns:
            str: Output string containing normalized Glyph Tags.
        """
        out: list[str] = []

        # Split into grapheme clusters (IVS becomes 1 unit)
        chars = self._split_grapheme_clusters(text)
        for ch in chars:
            # 1. Try glyph conversion
            if self.glyph_converter is not None:
                glyph_name = self.glyph_converter(ch)
                if glyph_name is not None:
                    out.append(f"{{{glyph_name}}}")
                    continue

            # 2. No conversion -> escape brace if needed
            out.append(self._escape_left_brace(ch))

        return "".join(out)

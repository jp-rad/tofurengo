"""
Factory module for initializing Glyph Normalizer, Renderer, and Simplifier instances.

This module provides factory functions to instantiate `GlyphNormalizer`,
`GlyphRenderer`, and `GlyphSimplifier` configured with resources loaded from `tofurengo.resource`.
"""

from typing import Any

from tofurengo.glyph_normalizer import GlyphNormalizer
from tofurengo.glyph_renderer import GlyphRenderer
from tofurengo.glyph_simplifier import GlyphSimplifier
from tofurengo.replacer import make_replace_fn
from tofurengo.resource import get_resource


def build_normalizer_from_table(
    glyph_table: dict[str, Any],
    set_name: str,
) -> GlyphNormalizer:
    """
    Build a `GlyphNormalizer` instance directly using a provided glyph table.

    Args:
        glyph_table: Dictionary mapping glyph keys to their attributes.
        set_name: Name tag for the set attribute (e.g., 'mj').

    Returns:
        GlyphNormalizer: Fully configured normalizer instance ready for processing.

    Example:
        >>> glyph_table = {
        ...     "MJ013044": {"b": "U+6589", "v": "U+6589 U+E0102"},
        ...     "MJ013049": {"b": "U+6589", "v": "U+658E U+E0102"},
        ...     "MJ013050": {"b": "U+6589", "v": "U+658E U+E0103"},
        ...     "MJ030058": {"b": "U+6589", "v": "U+9F4A U+E0103"},
        ...     "MJ030059": {"b": "U+6589", "v": "U+9F4A U+E0102"},
        ... }
        >>> normalizer = build_normalizer_from_table(glyph_table=glyph_table, set_name="sai")
        >>> result = normalizer.normalize("Sample {MJ013050}")
        >>> print(result.text)
    """
    replace_fn = make_replace_fn(glyph_table, set_name)
    return GlyphNormalizer(replace_fn=replace_fn)


def build_normalizer(
    glyph_set: str,
    version: str,
    set_name: str | None = None,
    base: str = "tofurengo_data",
) -> GlyphNormalizer:
    """
    Build a `GlyphNormalizer` instance initialized with glyph mapping resources.

    Loads the dataset resource corresponding to the given glyph set and version,
    and constructs the replacement closure required for tag normalization.

    Args:
        glyph_set: Identifier of the target glyph set (e.g., 'mj').
        version: Dataset version string (e.g., '6.02.201').
        set_name: Optional explicit name tag for the set attribute. If `None`, defaults to the value of `glyph_set`.
        base: Package base path for locating dataset resources. Defaults to `'tofurengo.data'`.

    Returns:
        GlyphNormalizer: Fully configured normalizer instance ready for processing.

    Example:
        >>> normalizer = build_normalizer(glyph_set="mj", version="6.02.201")
        >>> result = normalizer.normalize("Sample {MJ000001}")
        >>> print(result.text)
    """
    effective_set_name = set_name if set_name is not None else glyph_set
    resource: dict[str, Any] = get_resource(glyph_set, version, base=base)
    glyph_table: dict[str, Any] = resource["GLYPH_TABLE"]

    return build_normalizer_from_table(
        glyph_table=glyph_table,
        set_name=effective_set_name,
    )


def build_renderer(
    use_base: bool = False,
    tofu: str = "U+25A1",
) -> GlyphRenderer:
    """
    Build a `GlyphRenderer` instance with specified fallback and mapping preferences.

    The renderer resolves normalized Glyph Tags into Unicode characters based on base (`b=`) or variant (`v=`) attributes.

    Args:
        use_base: If `True`, prioritizes base UCS attributes (`b=`) over variant attributes (`v=`). Defaults to `False`.
        tofu: Fallback UCS sequence string or literal character used when a glyph cannot be resolved. Defaults to `'U+25A1'` (White Square □).

    Returns:
        GlyphRenderer: Configured renderer instance.

    Example:
        >>> renderer = build_renderer(use_base=True, tofu="U+FFFD")
        >>> rendered_text = renderer.render("Sample {MJ000001 b=U+30F1}")
    """
    return GlyphRenderer(use_base=use_base, tofu=tofu)


def build_simplifier() -> GlyphSimplifier:
    """
    Build a `GlyphSimplifier` instance.

    Returns:
        GlyphSimplifier: Configured simplifier instance.

    Example:
        >>> simplifier = build_simplifier()
    """
    return GlyphSimplifier()

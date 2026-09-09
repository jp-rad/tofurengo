"""
Replacer and normalization closures for glyph tags.

This module provides factory functions such as `make_replace_fn` to generate
substitution callbacks compatible with `ReplaceFn` used during tag normalization pipelines.
"""

from typing import Any

from tofurengo.tag_parser import ParsedTag, ReplaceFn, TagIssue


def make_replace_fn(
    glyph_table: dict[str, dict[str, Any]],
    set_name: str,
) -> ReplaceFn:
    """
    Factory that creates a normalization replacement callback for parsed tags.

    The generated closure inspects `ParsedTag` objects, looks up glyph entries in
    the provided `glyph_table`, validates their active status and presence of glyph_name,
    and formats them into canonical tag strings: `{<glyph> b=<b> v=<v> set=<set_name>}`.

    If validation fails (glyph missing, empty, or inactive), an appropriate `TagIssue`
    is appended to the mutable `issues` list, and the original raw tag is returned unmodified.

    Args:
        glyph_table (dict[str, dict[str, Any]]): Dictionary mapping glyph identifiers
            to property maps containing `b`, `v`, and `active` keys.
        set_name (str): The target dataset/set identifier assigned to normalized tags.

    Returns:
        ReplaceFn: A closure with signature `(ParsedTag, list[TagIssue]) -> str`.

    Examples:
        >>> table = {"MJ012345": {"b": "U+4E00", "v": "U+4E00 U+E0100", "active": True}}
        >>> replace_fn = make_replace_fn(table, set_name="mj")
        >>> issues = []
        >>> tag = ParsedTag.from_content("MJ012345")
        >>> replace_fn(tag, issues)
        '{MJ012345 b=U+4E00 v=U+4E00 U+E0100 set=mj}'
    """

    def replace_fn(tag: ParsedTag, issues: list[TagIssue]) -> str:
        """
        Process a parsed tag object, performing lookup, validation, and tag normalization.

        Args:
            tag (ParsedTag): Structured representation of the parsed tag.
            issues (list[TagIssue]): Mutable list to store encountered validation issues.

        Returns:
            str: Normalized tag string if valid; original raw tag text otherwise.
        """
        glyph = tag.glyph_name

        # 1. Empty glyph name validation
        if not glyph:
            code = "error.glyph.missing"
            msg = "Glyph name is missing in the tag."
            issues.append(
                TagIssue(
                    code=code,
                    message=f"{code}: {msg}",
                    details={"raw_content": tag.raw_content, "set": set_name},
                )
            )
            return f"{{{tag.raw_content}}}"

        # 2. Glyph existence validation
        if glyph not in glyph_table:
            code = "error.glyph.not_found"
            msg = f"Glyph '{glyph}' does not exist in dataset '{set_name}'."
            issues.append(
                TagIssue(
                    code=code,
                    message=f"{code}: {msg}",
                    details={"glyph": glyph, "set": set_name},
                )
            )
            return f"{{{tag.raw_content}}}"

        entry = glyph_table[glyph]

        # 3. Glyph active status validation
        if not entry.get("active", True):
            code = "error.glyph.archived"
            msg = f"Glyph '{glyph}' is archived or inactive."
            issues.append(
                TagIssue(
                    code=code,
                    message=f"{code}: {msg}",
                    details={"glyph": glyph, "set": set_name},
                )
            )
            return f"{{{tag.raw_content}}}"

        # 4. Canonical tag formatting
        b_val = entry.get("b", "")
        v_val = entry.get("v", "")

        return f"{{{glyph} b={b_val} v={v_val} set={set_name}}}"

    return replace_fn


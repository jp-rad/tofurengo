"""
Tag parsing, replacement protocols, and placeholder escaping utilities.

This module provides data models and utilities for tag-based string processing,
including `TagIssue` for capturing validation warnings and errors, `ParsedTag` for
structured tag attribute access, `ReplaceFn` for substitution callbacks,
and `TagParser` for managing double-brace escaping.
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Protocol

# Control character used as a placeholder for escaped opening braces '{{'
MARK_LB: str = "\u0002"

# Matches a single tag enclosed in single braces: {glyph_name key=value ...}
# Allows optional leading horizontal whitespace before the glyph name,
# requires a valid glyph name identifier, disallows newlines, and captures
# the raw tag body inside the "content" named group.
TAG_PATTERN: re.Pattern[str] = re.compile(
    r"\{"
    r"(?P<content>[ \t]*[A-Za-z0-9_\-]+(?:[ \t]+[^}\r\n]+)?)"
    r"\}",
)


class IssueLevel(str, Enum):
    """
    Severity levels for tag processing diagnostics.
    """

    WARNING = "warning"
    ERROR = "error"


@dataclass
class TagIssue:
    """
    Represents a warning or error encountered during tag processing.

    Attributes:
        code (str): Machine-readable issue category identifier.
        message (str): Human-readable message explaining failure details.
        level (IssueLevel): Severity level (`IssueLevel.WARNING` or `IssueLevel.ERROR`).
        details (dict[str, Any]): Additional contextual metadata regarding the issue.
    """

    code: str
    message: str
    level: IssueLevel = IssueLevel.ERROR
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the issue instance into a JSON-serializable dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of the tag issue.
        """
        return {
            "code": self.code,
            "message": self.message,
            "level": self.level.value,
            "details": self.details,
        }


@dataclass
class ParsedTag:
    """
    Structured representation of a parsed glyph tag's contents.

    Attributes:
        glyph_name (str): The primary glyph identifier (e.g., 'MJ000001').
        b (str | None): Value of the 'b' (base UCS) property if present.
        v (str | None): Value of the 'v' (variation) property if present.
        set (str | None): Value of the 'set' property if present.
        properties (dict[str, str]): All extracted key-value pairs.
        raw_content (str): The original unparsed tag inner content string.
    """

    glyph_name: str
    b: str | None = None
    v: str | None = None
    set: str | None = None
    properties: dict[str, str] = field(default_factory=dict)
    raw_content: str = ""

    @classmethod
    def from_content(cls, content: str) -> "ParsedTag":
        """
        Construct a `ParsedTag` instance directly from raw tag inner content.

        Args:
            content (str): Raw string extracted from inside a tag.

        Returns:
            ParsedTag: Structured object with shortcut accessors for b, v, and set.
        """
        raw_str = content.strip()
        tokens = raw_str.split()
        if not tokens:
            return cls(glyph_name="", raw_content=raw_str)

        # Check if the first token is actually a key-value pair (missing glyph_name)
        if "=" in tokens[0]:
            glyph_name = ""
            attr_tokens = tokens
        else:
            glyph_name = tokens[0]
            attr_tokens = tokens[1:]

        properties: dict[str, str] = {}
        last_key: str | None = None

        for token in attr_tokens:
            if "=" in token:
                key, value = token.split("=", 1)
                properties[key] = value
                last_key = key
            elif last_key is not None:
                # Append multi-token values (e.g., space-separated UCS sequences like 'U+845B U+E0103')
                properties[last_key] = f"{properties[last_key]} {token}"

        return cls(
            glyph_name=glyph_name,
            b=properties.get("b"),
            v=properties.get("v"),
            set=properties.get("set"),
            properties=properties,
            raw_content=raw_str,
        )


class ReplaceFn(Protocol):
    """
    Protocol definition for tag match-replacement closures.

    Implementations are callable objects that accept a structured `ParsedTag`
    and a mutable issue list, returning a replacement string while appending any
    encountered issues.
    """

    def __call__(self, tag: ParsedTag, issues: list[TagIssue]) -> str:
        """
        Process a parsed tag object and record any non-fatal processing issues.

        Args:
            tag (ParsedTag): Structured representation of the tag to process.
            issues (list[TagIssue]): Mutable list to collect encountered issues.

        Returns:
            str: The replacement string to substitute into target text.
        """
        ...


class TagParser:
    """
    Utility class for handling brace escaping, restoration, and tag parsing.

    Provides mechanisms to temporarily protect escaped braces (`{{`), parse
    and substitute tag matches, and restore the preserved sequences into either
    unescaped (`{`) or original escaped (`{{`) representations.
    """

    @staticmethod
    def escape_tokens(text: str) -> str:
        """
        Replace escaped double-brace sequences with a temporary control character.

        Args:
            text (str): Input text containing potential `{{` escape sequences.

        Returns:
            str: Text with `{{` replaced by the internal placeholder character.
        """
        return text.replace("{{", MARK_LB)

    @staticmethod
    def restore_tokens_preserve_escape(text: str) -> str:
        """
        Restore internal placeholders back to double-brace escape sequences (`{{`).

        Args:
            text (str): Processed text containing placeholder characters.

        Returns:
            str: Text with placeholders restored to `{{`.
        """
        return text.replace(MARK_LB, "{{")

    @staticmethod
    def restore_tokens_unescape(text: str) -> str:
        """
        Restore internal placeholders to single unescaped braces (`{`).

        Args:
            text (str): Processed text containing placeholder characters.

        Returns:
            str: Text with placeholders converted to `{`.
        """
        return text.replace(MARK_LB, "{")

    @classmethod
    def process_pipeline(
        cls,
        text: str,
        replacer: ReplaceFn,
        unescape: bool = True,
        issues: list[TagIssue] | None = None,
    ) -> str:
        """
        Execute the full transformation pipeline: escape -> substitute -> restore.

        Args:
            text (str): Target text to process.
            replacer (ReplaceFn): Replacement callback implementing `ReplaceFn`.
            unescape (bool): If `True`, converts preserved placeholders to `{`.
                If `False`, preserves them as `{{`. Defaults to `True`.
            issues (list[TagIssue] | None): Optional mutable list to collect issues
                encountered during substitution. If `None`, an internal list is used.

        Returns:
            str: Transformed output text after tag substitution and brace restoration.
        """
        issue_list = issues if issues is not None else []
        escaped = cls.escape_tokens(text)

        def sub_callback(match: re.Match[str]) -> str:
            content = match.group("content")
            tag = ParsedTag.from_content(content)
            return replacer(tag, issue_list)

        substituted = TAG_PATTERN.sub(sub_callback, escaped)

        if unescape:
            return cls.restore_tokens_unescape(substituted)
        return cls.restore_tokens_preserve_escape(substituted)


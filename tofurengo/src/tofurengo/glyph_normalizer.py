"""
Glyph Tag normalization models and processing engine for the tofurengo library.

This module provides data models for tracking normalization results (`NormalizeResult`)
and the `GlyphNormalizer` class, which handles the normalization phase of Glyph Tags
using a delegated callback function (`ReplaceFn`).
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from tofurengo.tag_parser import IssueLevel, ReplaceFn, TagIssue, TagParser


@dataclass
class NormalizeResult:
    """
    Encapsulates the final outcome of a tag normalization pipeline operation.

    Attributes:
        success (bool): Indicates whether the process completed without error-level issues.
        text (str): The transformed or normalized output string.
        issues (list[TagIssue]): List of collected warnings and errors.
    """

    success: bool
    text: str
    issues: list[TagIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[TagIssue]:
        """
        Filter and return only error-level issues.

        Returns:
            list[TagIssue]: List of issues with `IssueLevel.ERROR`.
        """
        return [i for i in self.issues if i.level == IssueLevel.ERROR]

    @property
    def warnings(self) -> list[TagIssue]:
        """
        Filter and return only warning-level issues.

        Returns:
            list[TagIssue]: List of issues with `IssueLevel.WARNING`.
        """
        return [i for i in self.issues if i.level == IssueLevel.WARNING]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the result object and its collected issues into a dictionary.

        Returns:
            dict[str, Any]: Serialized dictionary containing status, output text,
                and issue dictionaries.
        """
        return {
            "success": self.success,
            "text": self.text,
            "issues": [i.to_dict() for i in self.issues],
        }


class GlyphNormalizer:
    """
    Stateless normalization engine for processing text containing Glyph Tags.

    Delegates tag lookup and attribute reconstruction details to a `ReplaceFn` callback.
    The `replace_fn` can be provided either during initialization or dynamically
    during the `normalize()` method call.
    """

    def __init__(self, replace_fn: Optional[ReplaceFn] = None) -> None:
        """
        Initialize the GlyphNormalizer.

        Args:
            replace_fn (Optional[ReplaceFn]): Default replacement callback function.
        """
        self.replace_fn = replace_fn

    def normalize(
        self,
        text: str,
        replace_fn: Optional[ReplaceFn] = None,
    ) -> NormalizeResult:
        """
        Execute normalization on the input text.

        Replaces Glyph Tags with their canonical attributes while preserving
        the opening escape tokens (`{{`).

        Args:
            text (str): Input text containing Glyph Tags.
            replace_fn (Optional[ReplaceFn]): Replacement callback to use for this call.
                Overrides instance `self.replace_fn` if provided.

        Returns:
            NormalizeResult: Result object containing the normalized text, success status,
                and any accumulated warnings or errors.

        Raises:
            ValueError: If no `replace_fn` is provided in either `__init__` or `normalize()`.
        """
        if not text:
            return NormalizeResult(success=True, text="", issues=[])

        fn = replace_fn or self.replace_fn
        if fn is None:
            raise ValueError("replace_fn is required in __init__ or normalize()")

        issues: list[TagIssue] = []

        normalized_text = TagParser.process_pipeline(
            text=text,
            replacer=fn,
            unescape=False,  # Retain '{{' escape sequences during normalization
            issues=issues,
        )

        has_errors = any(i.level == IssueLevel.ERROR for i in issues)

        return NormalizeResult(
            success=not has_errors,
            text=normalized_text,
            issues=issues,
        )


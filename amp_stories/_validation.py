"""Validation utilities for amp_stories.

ValidationError is raised immediately at construction time for structural
problems that would produce invalid AMP HTML.

AmpStoriesWarning is issued for likely mistakes that won't prevent rendering
but may degrade the viewer experience.
"""

from __future__ import annotations

import re
import warnings
from typing import Any, get_args

_DURATION_RE = re.compile(r"^\d+(\.\d+)?(ms|s)$")
_HTML_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\-:.]*$")
_ASPECT_RATIO_RE = re.compile(r"^\d+:\d+$")
_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_CSS_SIZE_RE = re.compile(r"^\d+(\.\d+)?(rem|px|pt|em)$")

# AMP Stories best-practice thresholds
TEXT_LENGTH_WARN_THRESHOLD = 200
PAGE_COUNT_MIN = 4
PAGE_COUNT_MAX = 30


class ValidationError(ValueError):
    """Raised when a component is constructed with invalid or missing data."""


class AmpStoriesWarning(UserWarning):
    """Issued for likely mistakes that produce valid but suboptimal AMP HTML."""


def warn(msg: str) -> None:
    """Emit an AmpStoriesWarning with a helpful stack level."""
    warnings.warn(msg, AmpStoriesWarning, stacklevel=4)


def validate_nonempty(value: str, field: str) -> None:
    """Raise if *value* is an empty string."""
    if not value.strip():
        raise ValidationError(f"{field} must not be empty.")


def validate_html_id(value: str, field: str) -> None:
    """Raise if *value* is not a valid HTML id attribute value."""
    validate_nonempty(value, field)
    if not _HTML_ID_RE.match(value):
        raise ValidationError(
            f"{field} must be a valid HTML id (start with a letter, "
            f"contain only letters, digits, '_', '-', ':', '.'). Got: {value!r}"
        )


def validate_duration(value: str, field: str) -> None:
    """Raise if *value* is not a valid CSS duration string (e.g. '0.5s', '300ms')."""
    if not _DURATION_RE.match(value):
        raise ValidationError(
            f"{field} must be a CSS duration like '0.5s' or '300ms'. Got: {value!r}"
        )


def validate_aspect_ratio(value: str, field: str) -> None:
    """Raise if *value* is not in 'W:H' format."""
    if not _ASPECT_RATIO_RE.match(value):
        raise ValidationError(
            f"{field} must be in 'W:H' format (e.g. '4:3'). Got: {value!r}"
        )


def validate_literal(value: str, field: str, literal_type: Any) -> None:
    """Raise if *value* is not a member of the given Literal type."""
    allowed = get_args(literal_type)
    if value not in allowed:
        raise ValidationError(
            f"{field} must be one of {list(allowed)}. Got: {value!r}"
        )


def validate_hex_color(value: str, field: str) -> None:
    """Raise if *value* is not a valid 6-digit hex color string (e.g. ``'#FF0000'``)."""
    if not _HEX_COLOR_RE.match(value):
        raise ValidationError(
            f"{field} must be a 6-digit hex color like '#FF0000'. Got: {value!r}"
        )


def validate_css_size(value: str, field: str) -> None:
    """Raise if *value* is not a valid CSS size (e.g. ``'1.6rem'``, ``'24px'``)."""
    if not _CSS_SIZE_RE.match(value):
        raise ValidationError(
            f"{field} must be a CSS size like '1.6rem' or '24px'. Got: {value!r}"
        )


def validate_poll_interval(value: int, field: str) -> None:
    """Raise if the live-story poll interval is below the AMP minimum of 15 000 ms."""
    if value < 15000:
        raise ValidationError(
            f"{field} must be at least 15000 ms (AMP minimum). Got: {value}"
        )


def warn_missing_alt(src: str) -> None:
    """Warn when an AmpImg has no alt text (accessibility issue)."""
    warn(
        f"AmpImg(src={src!r}) has no alt text. "
        "Add alt='' explicitly to suppress this warning, or provide a description."
    )


def warn_text_too_long(tag: str, length: int) -> None:
    """Warn when a text element exceeds the recommended 200-character limit."""
    warn(
        f"<{tag}> text is {length} characters, which exceeds the AMP Stories "
        f"recommendation of {TEXT_LENGTH_WARN_THRESHOLD}. Consider breaking it across pages."
    )


def warn_page_count_low(count: int) -> None:
    """Warn when a story has fewer than 4 pages (AMP recommendation)."""
    warn(
        f"Story has {count} page(s). AMP Stories recommend at least {PAGE_COUNT_MIN} pages "
        "for a complete story experience."
    )


def warn_page_count_high(count: int) -> None:
    """Warn when a story exceeds 30 pages (AMP recommendation)."""
    warn(
        f"Story has {count} pages. AMP Stories recommend no more than {PAGE_COUNT_MAX} pages "
        "to maintain reader engagement."
    )


def warn_fill_layer_multiple_children(count: int) -> None:
    """Warn when a fill layer has more than one child element."""
    warn(
        f"A 'fill' layer has {count} children. Fill layers should have exactly one "
        "background element (amp-img, amp-video, etc.)."
    )

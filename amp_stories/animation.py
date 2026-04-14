"""Animation support for AMP story elements.

The Animation dataclass captures all four animate-in attributes supported
by amp-story-grid-layer children. It is intentionally kept separate so that
elements can carry animation state as a plain value without inheritance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import get_args

from amp_stories._types import AnimateIn
from amp_stories._validation import ValidationError, validate_duration

# Tuple of all valid effect names, used for validation
_VALID_EFFECTS: tuple[str, ...] = get_args(AnimateIn)


@dataclass
class Animation:
    """Represents an AMP Story animate-in animation on a single element.

    Args:
        effect: The animation name (e.g. 'fly-in-bottom', 'fade-in').
        duration: CSS duration string (e.g. '0.5s', '300ms'). Overrides default.
        delay: CSS duration string for the delay before the animation starts.
        after: The ``id`` of another element; this animation triggers after
               that element's animation completes.
    """

    effect: AnimateIn
    duration: str | None = None
    delay: str | None = None
    after: str | None = None

    def __post_init__(self) -> None:
        if self.effect not in _VALID_EFFECTS:
            raise ValidationError(
                f"animate_in must be one of {list(_VALID_EFFECTS)}. "
                f"Got: {self.effect!r}"
            )
        if self.duration is not None:
            validate_duration(self.duration, "animate_in_duration")
        if self.delay is not None:
            validate_duration(self.delay, "animate_in_delay")

    def to_attrs(self) -> dict[str, str | bool | None]:
        """Return HTML attribute dict to merge into an element's attrs."""
        return {
            "animate-in": self.effect,
            "animate-in-duration": self.duration,
            "animate-in-delay": self.delay,
            "animate-in-after": self.after,
        }

"""Convenience helpers built on top of the core AMP Story primitives.

These are *library* utilities — they have no direct AMP HTML counterpart.
They exist to reduce boilerplate when constructing common element and layer
patterns.

Text element constructors (:func:`heading`, :func:`paragraph`, :func:`span`,
:func:`blockquote`) are thin wrappers around
:class:`~amp_stories.elements.TextElement`.

Layer factory functions (:func:`background_layer`, :func:`text_layer`) are
thin wrappers around :class:`~amp_stories.layer.Layer`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from typing import Literal

    from amp_stories._types import AnimateIn
    from amp_stories.elements import AmpImg, AmpVideo
    from amp_stories.layer import LayerChild

from amp_stories._validation import ValidationError
from amp_stories.elements import TextElement
from amp_stories.layer import Layer

# ---------------------------------------------------------------------------
# Text element constructors
# ---------------------------------------------------------------------------

def heading(
    text: str,
    level: int = 1,
    style: str | None = None,
    class_: str | None = None,
    id: str | None = None,
    animate_in: AnimateIn | None = None,
    animate_in_duration: str | None = None,
    animate_in_delay: str | None = None,
    animate_in_after: str | None = None,
) -> TextElement:
    """Create a heading element (``<h1>``–``<h6>``).

    Args:
        text: The heading text.
        level: Heading level, 1–6. Defaults to ``1``.
        style: Inline CSS style string.
        class_: CSS class name(s).
        id: HTML id for animation targeting.
        animate_in: Entry animation name.
        animate_in_duration: Duration of the entry animation.
        animate_in_delay: Delay before the animation starts.
        animate_in_after: Id of an element whose animation this follows.
    """
    if not 1 <= level <= 6:
        raise ValidationError(f"heading level must be 1–6. Got: {level}")
    tag = cast("Literal['h1', 'h2', 'h3', 'h4', 'h5', 'h6']", f"h{level}")
    return TextElement(
        tag=tag,
        text=text,
        style=style,
        class_=class_,
        id=id,
        animate_in=animate_in,
        animate_in_duration=animate_in_duration,
        animate_in_delay=animate_in_delay,
        animate_in_after=animate_in_after,
    )


def paragraph(
    text: str,
    style: str | None = None,
    class_: str | None = None,
    id: str | None = None,
    animate_in: AnimateIn | None = None,
    animate_in_duration: str | None = None,
    animate_in_delay: str | None = None,
    animate_in_after: str | None = None,
) -> TextElement:
    """Create a ``<p>`` element."""
    return TextElement(
        tag="p",
        text=text,
        style=style,
        class_=class_,
        id=id,
        animate_in=animate_in,
        animate_in_duration=animate_in_duration,
        animate_in_delay=animate_in_delay,
        animate_in_after=animate_in_after,
    )


def span(
    text: str,
    style: str | None = None,
    class_: str | None = None,
    id: str | None = None,
    animate_in: AnimateIn | None = None,
    animate_in_duration: str | None = None,
    animate_in_delay: str | None = None,
    animate_in_after: str | None = None,
) -> TextElement:
    """Create a ``<span>`` element."""
    return TextElement(
        tag="span",
        text=text,
        style=style,
        class_=class_,
        id=id,
        animate_in=animate_in,
        animate_in_duration=animate_in_duration,
        animate_in_delay=animate_in_delay,
        animate_in_after=animate_in_after,
    )


def blockquote(
    text: str,
    style: str | None = None,
    class_: str | None = None,
    id: str | None = None,
    animate_in: AnimateIn | None = None,
    animate_in_duration: str | None = None,
    animate_in_delay: str | None = None,
    animate_in_after: str | None = None,
) -> TextElement:
    """Create a ``<blockquote>`` element."""
    return TextElement(
        tag="blockquote",
        text=text,
        style=style,
        class_=class_,
        id=id,
        animate_in=animate_in,
        animate_in_duration=animate_in_duration,
        animate_in_delay=animate_in_delay,
        animate_in_after=animate_in_after,
    )


# ---------------------------------------------------------------------------
# Layer factory functions
# ---------------------------------------------------------------------------

def background_layer(media: AmpImg | AmpVideo) -> Layer:
    """Return a ``fill`` layer containing a single background media element.

    Shorthand for ``Layer('fill', children=[media])``.
    """
    return Layer("fill", children=[media])


def text_layer(*elements: LayerChild) -> Layer:
    """Return a ``vertical`` layer containing the given text elements.

    Shorthand for ``Layer('vertical', children=list(elements))``.
    """
    return Layer("vertical", children=list(elements))

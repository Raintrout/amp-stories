"""AMP Story content elements.

Every class in this module corresponds to an HTML element that can live inside
an amp-story-grid-layer. All animatable elements carry flat ``animate_in*``
kwargs rather than a nested Animation object, which is more ergonomic when
using the nested-constructor API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Union, get_args

from amp_stories._html import HtmlNode, NodeChild
from amp_stories._types import AnimateIn, ImageLayout
from amp_stories._validation import (
    ValidationError,
    validate_duration,
    validate_nonempty,
    warn_missing_alt,
    warn_relative_url,
    warn_text_too_long,
)

_VALID_ANIMATE_IN: tuple[str, ...] = get_args(AnimateIn)


def _animation_attrs(
    animate_in: AnimateIn | None,
    animate_in_duration: str | None,
    animate_in_delay: str | None,
    animate_in_after: str | None,
) -> dict[str, str | bool | None]:
    """Build the four animate-in attribute entries."""
    if animate_in is not None and animate_in not in _VALID_ANIMATE_IN:
        raise ValidationError(
            f"animate_in must be one of {list(_VALID_ANIMATE_IN)}. Got: {animate_in!r}"
        )
    if animate_in_duration is not None:
        validate_duration(animate_in_duration, "animate_in_duration")
    if animate_in_delay is not None:
        validate_duration(animate_in_delay, "animate_in_delay")
    return {
        "animate-in": animate_in,
        "animate-in-duration": animate_in_duration,
        "animate-in-delay": animate_in_delay,
        "animate-in-after": animate_in_after,
    }


@dataclass
class AmpImg:
    """An ``<amp-img>`` element.

    Defaults to a 900×1600 fill layout, which is appropriate for full-bleed
    story backgrounds. Override *width*, *height*, and *layout* for other uses.
    """

    src: str
    width: int = 900
    height: int = 1600
    alt: str | None = None
    layout: ImageLayout = "fill"
    id: str | None = None
    animate_in: AnimateIn | None = None
    animate_in_duration: str | None = None
    animate_in_delay: str | None = None
    animate_in_after: str | None = None
    object_fit: str | None = None
    object_position: str | None = None

    def __post_init__(self) -> None:
        validate_nonempty(self.src, "AmpImg.src")
        valid_layouts: tuple[str, ...] = get_args(ImageLayout)
        if self.layout not in valid_layouts:
            raise ValidationError(
                f"AmpImg.layout must be one of {list(valid_layouts)}. "
                f"Got: {self.layout!r}"
            )
        if not (
            self.src.startswith("http://")
            or self.src.startswith("https://")
            or self.src.startswith("/")
        ):
            warn_relative_url("AmpImg.src", self.src)
        if self.alt is None:
            warn_missing_alt(self.src)
        # Validate animation kwargs
        _animation_attrs(
            self.animate_in,
            self.animate_in_duration,
            self.animate_in_delay,
            self.animate_in_after,
        )

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "src": self.src,
            "width": str(self.width),
            "height": str(self.height),
            "alt": self.alt if self.alt is not None else "",
            "layout": self.layout,
            "id": self.id,
        }
        style_parts: list[str] = []
        if self.object_fit is not None:
            style_parts.append(f"object-fit:{self.object_fit}")
        if self.object_position is not None:
            style_parts.append(f"object-position:{self.object_position}")
        if style_parts:
            attrs["style"] = ";".join(style_parts)
        attrs.update(
            _animation_attrs(
                self.animate_in,
                self.animate_in_duration,
                self.animate_in_delay,
                self.animate_in_after,
            )
        )
        return HtmlNode("amp-img", attrs, void=False)


@dataclass
class VideoSource:
    """A ``<source>`` element for multi-format video.

    Use with :class:`AmpVideo` ``sources`` to provide multiple video formats.
    """

    src: str
    type: str   # e.g. "video/mp4", "video/webm"

    def __post_init__(self) -> None:
        validate_nonempty(self.src, "VideoSource.src")
        validate_nonempty(self.type, "VideoSource.type")

    def to_node(self) -> HtmlNode:
        return HtmlNode("source", {"src": self.src, "type": self.type}, void=True)


@dataclass
class AmpVideo:
    """An ``<amp-video>`` element for story pages.

    Supply either *src* (single-source) or *sources* (multi-format).  Exactly
    one must be provided.
    """

    src: str = ""
    width: int = 900
    height: int = 1600
    loop: bool = False
    autoplay: bool = True
    muted: bool = True
    poster: str | None = None
    layout: str = "fill"
    id: str | None = None
    sources: list[VideoSource] = field(default_factory=list)
    animate_in: AnimateIn | None = None
    animate_in_duration: str | None = None
    animate_in_delay: str | None = None
    animate_in_after: str | None = None

    def __post_init__(self) -> None:
        has_src = bool(self.src.strip())
        has_sources = bool(self.sources)
        if has_src and has_sources:
            raise ValidationError(
                "AmpVideo: provide either 'src' or 'sources', not both."
            )
        if not has_src and not has_sources:
            raise ValidationError(
                "AmpVideo: one of 'src' or 'sources' must be provided."
            )
        if has_src and not (
            self.src.startswith("http://")
            or self.src.startswith("https://")
            or self.src.startswith("/")
        ):
            warn_relative_url("AmpVideo.src", self.src)
        _animation_attrs(
            self.animate_in,
            self.animate_in_duration,
            self.animate_in_delay,
            self.animate_in_after,
        )

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "src": self.src if self.src else None,
            "width": str(self.width),
            "height": str(self.height),
            "layout": self.layout,
            "poster": self.poster,
            "loop": True if self.loop else None,
            "autoplay": True if self.autoplay else None,
            "muted": True if self.muted else None,
            "id": self.id,
        }
        attrs.update(
            _animation_attrs(
                self.animate_in,
                self.animate_in_duration,
                self.animate_in_delay,
                self.animate_in_after,
            )
        )
        children: list[NodeChild] = [s.to_node() for s in self.sources]
        return HtmlNode("amp-video", attrs, children=children)


@dataclass
class StoryPanningMedia:
    """An ``<amp-story-panning-media>`` element for parallax panning effects.

    Args:
        src: URL of the image (required).
        width: Element width in px. Defaults to 900.
        height: Element height in px. Defaults to 1600.
        layout: AMP layout. Defaults to ``'fill'``.
        id: HTML id attribute for animation targeting.
        animate_in: Entry animation name.
        animate_in_duration: Duration of the entry animation.
        animate_in_delay: Delay before the entry animation starts.
        animate_in_after: Id of an element whose animation this follows.
    """

    src: str
    width: int = 900
    height: int = 1600
    layout: str = "fill"
    id: str | None = None
    animate_in: AnimateIn | None = None
    animate_in_duration: str | None = None
    animate_in_delay: str | None = None
    animate_in_after: str | None = None

    def __post_init__(self) -> None:
        validate_nonempty(self.src, "StoryPanningMedia.src")
        _animation_attrs(
            self.animate_in,
            self.animate_in_duration,
            self.animate_in_delay,
            self.animate_in_after,
        )

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "src": self.src,
            "width": str(self.width),
            "height": str(self.height),
            "layout": self.layout,
            "id": self.id,
        }
        attrs.update(
            _animation_attrs(
                self.animate_in,
                self.animate_in_duration,
                self.animate_in_delay,
                self.animate_in_after,
            )
        )
        return HtmlNode("amp-story-panning-media", attrs)


@dataclass
class Story360:
    """An ``<amp-story-360>`` element for 360° panoramic media.

    Args:
        src: URL of the equirectangular image (required).
        width: Element width in px. Defaults to 900.
        height: Element height in px. Defaults to 1600.
        layout: AMP layout. Defaults to ``'fill'``.
        id: HTML id attribute.
    """

    src: str
    width: int = 900
    height: int = 1600
    layout: str = "fill"
    id: str | None = None

    def __post_init__(self) -> None:
        validate_nonempty(self.src, "Story360.src")

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "src": self.src,
            "width": str(self.width),
            "height": str(self.height),
            "layout": self.layout,
            "id": self.id,
        }
        return HtmlNode("amp-story-360", attrs)


@dataclass
class AmpAudio:
    """An ``<amp-audio>`` element for background audio on a page."""

    src: str
    autoplay: bool = True
    loop: bool = False
    id: str | None = None

    def __post_init__(self) -> None:
        validate_nonempty(self.src, "AmpAudio.src")
        if not (
            self.src.startswith("http://")
            or self.src.startswith("https://")
            or self.src.startswith("/")
        ):
            warn_relative_url("AmpAudio.src", self.src)

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "src": self.src,
            "autoplay": True if self.autoplay else None,
            "loop": True if self.loop else None,
            "id": self.id,
        }
        return HtmlNode("amp-audio", attrs)


@dataclass
class TextElement:
    """A text-bearing element: h1–h6, p, span, blockquote, or div.

    Prefer the convenience constructors :func:`heading`, :func:`paragraph`,
    :func:`span`, and :func:`blockquote` over instantiating this class directly.
    """

    tag: Literal["h1", "h2", "h3", "h4", "h5", "h6", "p", "span", "blockquote", "div"]
    text: str
    style: str | None = None
    class_: str | None = None
    id: str | None = None
    animate_in: AnimateIn | None = None
    animate_in_duration: str | None = None
    animate_in_delay: str | None = None
    animate_in_after: str | None = None

    _VALID_TAGS: tuple[str, ...] = field(
        default=(
            "h1", "h2", "h3", "h4", "h5", "h6",
            "p", "span", "blockquote", "div",
        ),
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if self.tag not in self._VALID_TAGS:
            raise ValidationError(
                f"TextElement.tag must be one of {list(self._VALID_TAGS)}. "
                f"Got: {self.tag!r}"
            )
        if len(self.text) > 200:
            warn_text_too_long(self.tag, len(self.text))
        _animation_attrs(
            self.animate_in,
            self.animate_in_duration,
            self.animate_in_delay,
            self.animate_in_after,
        )

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "class": self.class_,
            "style": self.style,
            "id": self.id,
        }
        attrs.update(
            _animation_attrs(
                self.animate_in,
                self.animate_in_duration,
                self.animate_in_delay,
                self.animate_in_after,
            )
        )
        return HtmlNode(self.tag, attrs, children=[self.text])


# ---------------------------------------------------------------------------
# Container element
# ---------------------------------------------------------------------------

# Type alias for anything that can be a child of DivElement
DivChild = Union[AmpImg, AmpVideo, AmpAudio, "AmpList", TextElement, "DivElement", str]


@dataclass
class DivElement:
    """A ``<div>`` container that can nest other elements.

    Unlike :class:`TextElement` with tag ``'div'``, this class holds a list
    of child elements rather than a text string, making it suitable for
    grouping animated sub-elements.
    """

    children: list[DivChild] = field(default_factory=list)
    style: str | None = None
    class_: str | None = None
    id: str | None = None
    animate_in: AnimateIn | None = None
    animate_in_duration: str | None = None
    animate_in_delay: str | None = None
    animate_in_after: str | None = None

    def __post_init__(self) -> None:
        _animation_attrs(
            self.animate_in,
            self.animate_in_duration,
            self.animate_in_delay,
            self.animate_in_after,
        )

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "style": self.style,
            "class": self.class_,
            "id": self.id,
        }
        attrs.update(
            _animation_attrs(
                self.animate_in,
                self.animate_in_duration,
                self.animate_in_delay,
                self.animate_in_after,
            )
        )
        child_nodes: list[NodeChild] = [
            c if isinstance(c, str) else c.to_node() for c in self.children
        ]
        return HtmlNode("div", attrs, children=child_nodes)

    def add_child(self, *children: DivChild) -> DivElement:
        """Append one or more children and return *self* for chaining."""
        self.children.extend(children)
        return self


# ---------------------------------------------------------------------------
# AmpList element (requires amp-list + amp-mustache extension scripts)
# ---------------------------------------------------------------------------

@dataclass
class AmpList:
    """An ``<amp-list>`` element for dynamic, data-driven story content.

    The *template* string should contain a Mustache template that will be
    wrapped in ``<template type="amp-mustache">``.

    Requires the ``amp-list`` and ``amp-mustache`` extension scripts, which
    are injected automatically by :class:`~amp_stories.story.Story`.
    """

    src: str
    width: int = 900
    height: int = 400
    layout: str = "fixed-height"
    template: str = ""
    id: str | None = None

    def __post_init__(self) -> None:
        validate_nonempty(self.src, "AmpList.src")

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "src": self.src,
            "width": str(self.width),
            "height": str(self.height),
            "layout": self.layout,
            "id": self.id,
        }
        children: list[NodeChild] = []
        if self.template:
            from amp_stories._html import RawHtmlNode
            template_node = HtmlNode(
                "template",
                {"type": "amp-mustache"},
                children=[RawHtmlNode(self.template)],
            )
            children.append(template_node)
        return HtmlNode("amp-list", attrs, children=children)

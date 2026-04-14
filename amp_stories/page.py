"""amp-story-page wrapper."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import TYPE_CHECKING

from amp_stories._html import HtmlNode, NodeChild
from amp_stories._validation import (
    ValidationError,
    validate_html_id,
    warn,
)

if TYPE_CHECKING:
    from amp_stories.layer import Layer

_page_counter = itertools.count(1)


def next_page_id() -> str:
    """Return the next auto-generated page id (``'page-1'``, ``'page-2'``, …).

    The counter is module-level and increments on every call. Generated ids
    are valid HTML ids and pass :func:`~amp_stories._validation.validate_html_id`.

    Example::

        from amp_stories import Page, Layer, AmpImg, next_page_id

        pages = [
            Page(next_page_id(), layers=[fill_layer]),
            Page(next_page_id(), layers=[fill_layer]),
        ]
        # pages[0].page_id == 'page-N', pages[1].page_id == 'page-N+1'
    """
    return f"page-{next(_page_counter)}"


@dataclass
class Page:
    """An ``<amp-story-page>`` element representing one screen of a story.

    Args:
        page_id: Unique HTML id for this page (required). Must be a valid
            HTML id: start with a letter, contain only letters, digits,
            ``_``, ``-``, ``:``, ``.``.
        layers: One or more :class:`~amp_stories.layer.Layer` objects composing
            this page's visual content (required).
        auto_advance_after: CSS duration (e.g. ``'5s'``) or a media element
            id after which this page auto-advances.
        background_audio: URL to an audio file played while this page is shown.
        outlink: A :class:`~amp_stories.outlink.PageOutlink` CTA button.
        attachment: A :class:`~amp_stories.attachment.PageAttachment` drawer
            (deprecated; mutually exclusive with *outlink*).
        data_sort_time: Unix ms timestamp for ordering pages in live stories.
    """

    page_id: str
    layers: list[Layer]
    auto_advance_after: str | None = None
    background_audio: str | None = None
    # Import at class level to avoid circular imports — type-check only
    outlink: object | None = None             # PageOutlink | None
    attachment: object | None = None          # PageAttachment | None
    shopping_attachment: object | None = None  # ShoppingAttachment | None
    data_sort_time: int | None = None

    def __post_init__(self) -> None:
        validate_html_id(self.page_id, "Page.page_id")

        if not self.layers:
            raise ValidationError(
                f"Page '{self.page_id}' must have at least one Layer."
            )

        if self.outlink is not None and self.attachment is not None:
            raise ValidationError(
                f"Page '{self.page_id}' cannot have both an outlink and an attachment. "
                "Use one or the other."
            )

        # Warn if there is no fill layer — pages without a fill layer have no
        # background and usually look broken.
        has_fill = any(layer.template == "fill" for layer in self.layers)
        if not has_fill:
            warn(
                f"Page '{self.page_id}' has no 'fill' layer. "
                "Consider adding a fill layer with a background image or video."
            )

    def __repr__(self) -> str:
        return f"Page(page_id={self.page_id!r}, layers={len(self.layers)})"

    def add_layer(self, *layers: Layer) -> Page:
        """Append one or more layers and return *self* for chaining."""
        self.layers.extend(layers)
        return self

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "id": self.page_id,
            "auto-advance-after": self.auto_advance_after,
            "background-audio": self.background_audio,
        }
        if self.data_sort_time is not None:
            attrs["data-sort-time"] = str(self.data_sort_time)

        children: list[NodeChild] = [layer.to_node() for layer in self.layers]

        if self.attachment is not None:
            from amp_stories.attachment import PageAttachment  # noqa: PLC0415

            assert isinstance(self.attachment, PageAttachment)
            children.append(self.attachment.to_node())

        if self.shopping_attachment is not None:
            from amp_stories.shopping import ShoppingAttachment  # noqa: PLC0415

            assert isinstance(self.shopping_attachment, ShoppingAttachment)
            children.append(self.shopping_attachment.to_node())

        if self.outlink is not None:
            from amp_stories.outlink import PageOutlink  # noqa: PLC0415

            assert isinstance(self.outlink, PageOutlink)
            children.append(self.outlink.to_node())

        return HtmlNode("amp-story-page", attrs, children=children)

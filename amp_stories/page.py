"""amp-story-page wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from amp_stories._html import HtmlNode
from amp_stories._validation import (
    ValidationError,
    validate_html_id,
    warn,
)

if TYPE_CHECKING:
    from amp_stories.layer import Layer


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
    outlink: object | None = None      # PageOutlink | None
    attachment: object | None = None   # PageAttachment | None
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

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "id": self.page_id,
            "auto-advance-after": self.auto_advance_after,
            "background-audio": self.background_audio,
        }
        if self.data_sort_time is not None:
            attrs["data-sort-time"] = str(self.data_sort_time)

        children: list[HtmlNode] = [layer.to_node() for layer in self.layers]

        if self.attachment is not None:
            from amp_stories.attachment import PageAttachment  # noqa: PLC0415

            assert isinstance(self.attachment, PageAttachment)
            children.append(self.attachment.to_node())

        if self.outlink is not None:
            from amp_stories.outlink import PageOutlink  # noqa: PLC0415

            assert isinstance(self.outlink, PageOutlink)
            children.append(self.outlink.to_node())

        return HtmlNode("amp-story-page", attrs, children=children)  # type: ignore[arg-type]

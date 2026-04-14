"""amp-story-page-attachment wrapper (deprecated but still functional).

Prefer :class:`~amp_stories.outlink.PageOutlink` for simple external links.
Use PageAttachment only when you need a swipe-up drawer with rich HTML content
or a list of internal/external links.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from amp_stories._html import HtmlNode, NodeChild
from amp_stories._validation import ValidationError, validate_nonempty
from amp_stories.elements import AmpImg, DivElement, TextElement

# Valid content child types for the attachment's HTML mode
AttachmentChild = TextElement | DivElement | AmpImg


@dataclass
class AttachmentLink:
    """A single link entry inside a link-list PageAttachment.

    Args:
        title: Display text for the link.
        url: Destination URL.
        image: Optional thumbnail image URL.
    """

    title: str
    url: str
    image: str | None = None

    def __post_init__(self) -> None:
        validate_nonempty(self.title, "AttachmentLink.title")
        validate_nonempty(self.url, "AttachmentLink.url")


@dataclass
class PageAttachment:
    """An ``<amp-story-page-attachment>`` element (deprecated).

    Supports two mutually exclusive content modes:

    - **Link-list mode**: populate *links* with :class:`AttachmentLink` items.
    - **HTML mode**: populate *html_content* with text/image elements.

    Mixing both modes raises :class:`~amp_stories._validation.ValidationError`.

    Args:
        cta_text: Label for the swipe-up button. Defaults to ``'Swipe up'``.
        theme: ``'light'`` or ``'dark'``.
        links: List of links for link-list mode.
        html_content: List of elements for HTML mode.
    """

    cta_text: str = "Swipe up"
    theme: Literal["light", "dark"] = "light"
    links: list[AttachmentLink] = field(default_factory=list)
    html_content: list[AttachmentChild] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.theme not in ("light", "dark"):
            raise ValidationError(
                f"PageAttachment.theme must be 'light' or 'dark'. Got: {self.theme!r}"
            )
        if self.links and self.html_content:
            raise ValidationError(
                "PageAttachment cannot mix link-list mode and HTML mode. "
                "Populate either 'links' or 'html_content', not both."
            )

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "layout": "nodisplay",
            "theme": self.theme,
            "cta-text": self.cta_text,
        }
        children: list[NodeChild] = []

        if self.links:
            for link in self.links:
                link_attrs: dict[str, str | bool | None] = {"href": link.url}
                if link.image:
                    link_attrs["data-img"] = link.image
                children.append(HtmlNode("a", link_attrs, children=[link.title]))
        else:
            for item in self.html_content:
                children.append(item.to_node())

        return HtmlNode("amp-story-page-attachment", attrs, children=children)

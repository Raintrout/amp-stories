"""amp-story-page-outlink wrapper (the preferred one-tap CTA component)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from amp_stories._html import HtmlNode
from amp_stories._validation import ValidationError, validate_nonempty


@dataclass
class PageOutlink:
    """An ``<amp-story-page-outlink>`` element.

    Renders a swipe-up / tap CTA button that navigates to an external URL.
    This is the current recommended way to link out from a story page;
    :class:`~amp_stories.attachment.PageAttachment` is the older alternative.

    Args:
        href: The destination URL (required).
        cta_text: Button label shown to the user. Defaults to ``'Swipe up'``.
        theme: Color scheme — ``'light'``, ``'dark'``, or ``'custom'``.
        cta_accent_color: Hex color required when ``theme='custom'``
            (e.g. ``'#FF0000'``).
        cta_accent_element: Which element receives the accent color —
            ``'text'`` or ``'background'``.
        cta_image: URL to a 32×32 px icon, or ``'none'`` to suppress the
            default link icon.
    """

    href: str
    cta_text: str = "Swipe up"
    theme: Literal["light", "dark", "custom"] = "light"
    cta_accent_color: str | None = None
    cta_accent_element: Literal["text", "background"] | None = None
    cta_image: str | None = None

    def __post_init__(self) -> None:
        validate_nonempty(self.href, "PageOutlink.href")
        if self.theme not in ("light", "dark", "custom"):
            raise ValidationError(
                f"PageOutlink.theme must be 'light', 'dark', or 'custom'. "
                f"Got: {self.theme!r}"
            )
        if self.theme == "custom" and self.cta_accent_color is None:
            raise ValidationError(
                "PageOutlink.cta_accent_color is required when theme='custom'."
            )
        if self.cta_accent_element is not None and self.cta_accent_element not in (
            "text",
            "background",
        ):
            raise ValidationError(
                "PageOutlink.cta_accent_element must be 'text' or 'background'. "
                f"Got: {self.cta_accent_element!r}"
            )

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "layout": "nodisplay",
            "theme": self.theme,
            "cta-text": self.cta_text if self.cta_text != "Swipe up" else None,
            "cta-accent-color": self.cta_accent_color,
            "cta-accent-element": self.cta_accent_element,
            "cta-image": self.cta_image,
        }
        link = HtmlNode("a", {"href": self.href}, children=[self.cta_text])
        return HtmlNode("amp-story-page-outlink", attrs, children=[link])  # type: ignore[arg-type]

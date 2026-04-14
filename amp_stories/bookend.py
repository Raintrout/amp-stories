"""amp-story-bookend wrapper.

The bookend is the end-card that appears after the last story page. It holds
sharing options and links to related content. AMP encodes bookend configuration
as JSON inside a <script type="application/json"> tag.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from amp_stories._html import HtmlNode, RawHtmlNode
from amp_stories._types import BookendComponentType, ShareProvider
from amp_stories._validation import ValidationError, validate_literal


@dataclass
class BookendShareProvider:
    """A social sharing platform entry in the bookend.

    Args:
        provider: Platform identifier (e.g. ``'twitter'``, ``'facebook'``).
        param: Provider-specific parameter (e.g. ``app_id`` for Facebook).
    """

    provider: ShareProvider
    param: str | None = None

    def __post_init__(self) -> None:
        validate_literal(self.provider, "BookendShareProvider.provider", ShareProvider)

    def to_dict(self) -> str | dict[str, str]:
        """Serialize to the format expected by the bookend JSON schema."""
        if self.param is None:
            return self.provider
        return {"provider": self.provider, "app_id": self.param}


@dataclass
class BookendComponent:
    """A single component entry in the bookend's ``components`` array.

    The required fields vary by *type*:

    - ``'heading'`` / ``'textbox'``: requires *text*
    - ``'small'``: requires *title* and *url*; optional *image*
    - ``'portrait'`` / ``'landscape'``: requires *title*, *url*, *image*;
      optional *category*
    - ``'cta-link'``: requires *title* and *url*

    Args:
        type: Component type string.
        text: Display text (heading/textbox).
        title: Link card title.
        url: Destination URL.
        image: Thumbnail image URL.
        category: Category label (portrait/landscape).
    """

    type: BookendComponentType
    text: str | None = None
    title: str | None = None
    url: str | None = None
    image: str | None = None
    category: str | None = None

    def __post_init__(self) -> None:
        validate_literal(self.type, "BookendComponent.type", BookendComponentType)
        self._validate_required_fields()

    def _validate_required_fields(self) -> None:
        t = self.type
        if t in ("heading", "textbox") and not self.text:
            raise ValidationError(
                f"BookendComponent of type '{t}' requires 'text'."
            )
        if t in ("small", "cta-link") and not self.url:
            raise ValidationError(
                f"BookendComponent of type '{t}' requires 'url'."
            )
        if t in ("portrait", "landscape") and not (self.url and self.image):
            raise ValidationError(
                f"BookendComponent of type '{t}' requires 'url' and 'image'."
            )

    def to_dict(self) -> dict[str, str]:
        """Serialize to the bookend JSON component format."""
        d: dict[str, str] = {"type": self.type}
        if self.text is not None:
            d["text"] = self.text
        if self.title is not None:
            d["title"] = self.title
        if self.url is not None:
            d["url"] = self.url
        if self.image is not None:
            d["image"] = self.image
        if self.category is not None:
            d["category"] = self.category
        return d


@dataclass
class Bookend:
    """An ``<amp-story-bookend>`` element.

    Renders as a ``<amp-story-bookend layout="nodisplay">`` element containing
    the bookend configuration encoded as a JSON ``<script>`` child.

    Args:
        share_providers: Social sharing platforms to display.
        components: Content cards and headings for the bookend screen.
    """

    share_providers: list[BookendShareProvider] = field(default_factory=list)
    components: list[BookendComponent] = field(default_factory=list)

    def to_json(self) -> str:
        """Serialize bookend configuration to the AMP bookend JSON format."""
        data: dict[str, object] = {"bookendVersion": "v1.0"}
        if self.share_providers:
            data["shareProviders"] = [p.to_dict() for p in self.share_providers]
        if self.components:
            data["components"] = [c.to_dict() for c in self.components]
        return json.dumps(data, indent=2)

    def to_node(self) -> HtmlNode:
        script_node = HtmlNode(
            "script",
            {"type": "application/json"},
            children=[RawHtmlNode(self.to_json())],
        )
        return HtmlNode(
            "amp-story-bookend",
            {"layout": "nodisplay"},
            children=[script_node],  # type: ignore[list-item]
        )

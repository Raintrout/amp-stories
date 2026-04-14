"""amp-story-auto-ads wrapper.

Provides the :class:`AutoAds` component for injecting programmatic ads into a
story. Requires the ``amp-story-auto-ads`` extension script, which is injected
automatically by :class:`~amp_stories.story.Story` when an :class:`AutoAds`
instance is set on :attr:`~amp_stories.story.Story.auto_ads`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from amp_stories._html import HtmlNode, RawHtmlNode
from amp_stories._validation import validate_nonempty


@dataclass
class AutoAds:
    """An ``<amp-story-auto-ads>`` monetization element.

    The AMP runtime periodically inserts ads into the story. Configuration is
    encoded as a JSON ``<script>`` child of the element.

    Args:
        ad_url: URL of the ad server endpoint (mapped to ``"src"`` in the
            ``"ad-attributes"`` JSON config).
        ad_attributes: Additional attributes passed verbatim inside the
            ``"ad-attributes"`` JSON object (e.g. ``{"type": "adsense"}``)
    """

    ad_url: str
    ad_attributes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_nonempty(self.ad_url, "AutoAds.ad_url")

    def to_json(self) -> str:
        """Serialize the ad configuration as a JSON string."""
        config: dict[str, object] = {
            "ad-attributes": {"src": self.ad_url, **self.ad_attributes}
        }
        return json.dumps(config, indent=2)

    def to_node(self) -> HtmlNode:
        script_node = HtmlNode(
            "script",
            {"type": "application/json"},
            children=[RawHtmlNode(self.to_json())],
        )
        return HtmlNode(
            "amp-story-auto-ads",
            {},
            children=[script_node],  # type: ignore[list-item]
        )

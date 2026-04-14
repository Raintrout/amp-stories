"""AMP Consent component for story-level consent management."""

from __future__ import annotations

import json as _json
from dataclasses import dataclass, field
from typing import Any

from amp_stories._html import HtmlNode, RawHtmlNode
from amp_stories._validation import ValidationError


@dataclass
class AmpConsent:
    """An ``<amp-consent>`` element for consent management.

    Uses a dict-based API consistent with ``Story.structured_data`` to
    avoid over-designing wrappers for a highly variable config format.

    Args:
        consents: Dict mapping consent id to consent config dict (required).
        post_prompt_ui: Optional id of a post-prompt UI element.
    """

    consents: dict[str, Any] = field(default_factory=dict)
    post_prompt_ui: str | None = None

    def __post_init__(self) -> None:
        if not self.consents:
            raise ValidationError("AmpConsent.consents must not be empty.")

    def to_json(self) -> dict[str, Any]:
        """Return the consent config as a dict for JSON serialization."""
        data: dict[str, Any] = {"consents": self.consents}
        if self.post_prompt_ui is not None:
            data["postPromptUI"] = self.post_prompt_ui
        return data

    def to_node(self) -> HtmlNode:
        json_child = HtmlNode(
            "script",
            {"type": "application/json"},
            children=[RawHtmlNode(_json.dumps(self.to_json()))],
        )
        return HtmlNode("amp-consent", {"layout": "nodisplay"}, children=[json_child])

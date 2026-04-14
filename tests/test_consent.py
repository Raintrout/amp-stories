"""Tests for consent.py."""

from __future__ import annotations

import json

import pytest

from amp_stories._validation import ValidationError
from amp_stories.consent import AmpConsent


class TestAmpConsent:
    def test_renders_amp_consent(self) -> None:
        consent = AmpConsent(consents={"my-consent": {"checkConsentHref": "/check"}})
        node = consent.to_node()
        assert node.tag == "amp-consent"

    def test_layout_nodisplay(self) -> None:
        consent = AmpConsent(consents={"c": {}})
        assert consent.to_node().attrs["layout"] == "nodisplay"

    def test_json_script_child(self) -> None:
        consent = AmpConsent(consents={"c": {"checkConsentHref": "/check"}})
        node = consent.to_node()
        assert len(node.children) == 1
        script = node.children[0]
        assert script.tag == "script"  # type: ignore[union-attr]
        assert script.attrs["type"] == "application/json"  # type: ignore[union-attr]

    def test_to_json_includes_consents(self) -> None:
        config = {"checkConsentHref": "/check"}
        consent = AmpConsent(consents={"my-consent": config})
        data = consent.to_json()
        assert data["consents"] == {"my-consent": config}

    def test_to_json_post_prompt_ui(self) -> None:
        consent = AmpConsent(consents={"c": {}}, post_prompt_ui="consent-ui")
        data = consent.to_json()
        assert data["postPromptUI"] == "consent-ui"

    def test_to_json_no_post_prompt_ui_omitted(self) -> None:
        consent = AmpConsent(consents={"c": {}})
        data = consent.to_json()
        assert "postPromptUI" not in data

    def test_empty_consents_raises(self) -> None:
        with pytest.raises(ValidationError, match="consents"):
            AmpConsent(consents={})

    def test_json_serialized_in_script_content(self) -> None:
        consent = AmpConsent(consents={"c": {"checkConsentHref": "/check"}})
        node = consent.to_node()
        script = node.children[0]
        raw = script.children[0]  # type: ignore[union-attr]
        expected = json.dumps({"consents": {"c": {"checkConsentHref": "/check"}}})
        assert raw.content == expected  # type: ignore[union-attr]

    def test_post_prompt_ui_in_serialized_json(self) -> None:
        consent = AmpConsent(consents={"c": {}}, post_prompt_ui="my-ui")
        node = consent.to_node()
        rendered_json = node.children[0].children[0].content  # type: ignore[union-attr]
        data = json.loads(rendered_json)
        assert data["postPromptUI"] == "my-ui"

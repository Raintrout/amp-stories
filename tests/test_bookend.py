"""Tests for bookend.py."""

from __future__ import annotations

import json

import pytest

from amp_stories._validation import ValidationError
from amp_stories.bookend import Bookend, BookendComponent, BookendShareProvider


class TestBookendShareProvider:
    def test_string_provider(self) -> None:
        p = BookendShareProvider("twitter")
        assert p.to_dict() == "twitter"

    def test_provider_with_param(self) -> None:
        p = BookendShareProvider("facebook", param="123456")
        result = p.to_dict()
        assert isinstance(result, dict)
        assert result["provider"] == "facebook"
        assert result["app_id"] == "123456"

    def test_invalid_provider_raises(self) -> None:
        with pytest.raises(ValidationError, match="provider"):
            BookendShareProvider("instagram")  # type: ignore[arg-type]

    def test_all_valid_providers(self) -> None:
        for provider in ("email", "twitter", "tumblr", "facebook",
                         "gplus", "linkedin", "whatsapp", "sms", "system"):
            BookendShareProvider(provider)  # type: ignore[arg-type]


class TestBookendComponent:
    def test_heading_type(self) -> None:
        c = BookendComponent(type="heading", text="More Stories")
        assert c.to_dict()["type"] == "heading"
        assert c.to_dict()["text"] == "More Stories"

    def test_heading_requires_text(self) -> None:
        with pytest.raises(ValidationError, match="text"):
            BookendComponent(type="heading")

    def test_small_type(self) -> None:
        c = BookendComponent(type="small", title="Article", url="https://example.com")
        d = c.to_dict()
        assert d["title"] == "Article"
        assert d["url"] == "https://example.com"

    def test_small_requires_url(self) -> None:
        with pytest.raises(ValidationError, match="url"):
            BookendComponent(type="small", title="Article")

    def test_portrait_requires_url_and_image(self) -> None:
        with pytest.raises(ValidationError, match="url.*image|image.*url"):
            BookendComponent(type="portrait", title="Art")

    def test_landscape_requires_url_and_image(self) -> None:
        with pytest.raises(ValidationError, match="url.*image|image.*url"):
            BookendComponent(type="landscape", title="Art", url="https://example.com")

    def test_cta_link_requires_url(self) -> None:
        with pytest.raises(ValidationError, match="url"):
            BookendComponent(type="cta-link", title="Click")

    def test_textbox_requires_text(self) -> None:
        with pytest.raises(ValidationError, match="text"):
            BookendComponent(type="textbox")

    def test_optional_fields_included_in_dict(self) -> None:
        c = BookendComponent(
            type="portrait",
            title="Art",
            url="https://example.com",
            image="img.jpg",
            category="Technology",
        )
        d = c.to_dict()
        assert d["category"] == "Technology"
        assert d["image"] == "img.jpg"

    def test_none_fields_not_in_dict(self) -> None:
        c = BookendComponent(type="heading", text="Title")
        d = c.to_dict()
        assert "url" not in d
        assert "image" not in d
        assert "category" not in d

    def test_invalid_type_raises(self) -> None:
        with pytest.raises(ValidationError, match="type"):
            BookendComponent(type="unknown")  # type: ignore[arg-type]


class TestBookend:
    def test_empty_bookend_json(self) -> None:
        b = Bookend()
        data = json.loads(b.to_json())
        assert data["bookendVersion"] == "v1.0"
        assert "shareProviders" not in data
        assert "components" not in data

    def test_share_providers_serialized(self) -> None:
        b = Bookend(share_providers=[
            BookendShareProvider("twitter"),
            BookendShareProvider("facebook", param="app123"),
        ])
        data = json.loads(b.to_json())
        assert data["shareProviders"][0] == "twitter"
        assert data["shareProviders"][1] == {"provider": "facebook", "app_id": "app123"}

    def test_components_serialized(self) -> None:
        b = Bookend(components=[
            BookendComponent(type="heading", text="Related"),
            BookendComponent(type="small", title="Article", url="https://example.com"),
        ])
        data = json.loads(b.to_json())
        assert len(data["components"]) == 2
        assert data["components"][0]["type"] == "heading"
        assert data["components"][1]["url"] == "https://example.com"

    def test_renders_amp_story_bookend_tag(self) -> None:
        b = Bookend()
        node = b.to_node()
        assert node.tag == "amp-story-bookend"

    def test_nodisplay_layout(self) -> None:
        b = Bookend()
        assert b.to_node().attrs["layout"] == "nodisplay"

    def test_json_in_script_child(self) -> None:
        b = Bookend()
        node = b.to_node()
        script = node.children[0]
        assert script.tag == "script"  # type: ignore[union-attr]
        assert script.attrs["type"] == "application/json"  # type: ignore[union-attr]

    def test_bookend_json_in_rendered_output(self) -> None:
        b = Bookend(share_providers=[BookendShareProvider("twitter")])
        rendered = b.to_node().render()
        assert "bookendVersion" in rendered
        assert "twitter" in rendered

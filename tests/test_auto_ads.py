"""Tests for auto_ads.py — amp-story-auto-ads component."""

from __future__ import annotations

import json

import pytest

from amp_stories._validation import ValidationError
from amp_stories.auto_ads import AutoAds
from amp_stories.elements import AmpImg
from amp_stories.layer import Layer
from amp_stories.page import Page
from amp_stories.story import Story


class TestAutoAds:
    def test_renders_auto_ads_tag(self) -> None:
        ads = AutoAds("https://ad-server.example.com/endpoint")
        assert ads.to_node().tag == "amp-story-auto-ads"

    def test_json_contains_src(self) -> None:
        ads = AutoAds("https://ad-server.example.com/endpoint")
        data = json.loads(ads.to_json())
        assert data["ad-attributes"]["src"] == "https://ad-server.example.com/endpoint"

    def test_ad_attributes_included(self) -> None:
        ads = AutoAds("https://ad-server.example.com", ad_attributes={"type": "adsense"})
        data = json.loads(ads.to_json())
        assert data["ad-attributes"]["type"] == "adsense"
        assert data["ad-attributes"]["src"] == "https://ad-server.example.com"

    def test_empty_ad_url_raises(self) -> None:
        with pytest.raises(ValidationError, match="ad_url"):
            AutoAds("")

    def test_whitespace_ad_url_raises(self) -> None:
        with pytest.raises(ValidationError, match="ad_url"):
            AutoAds("   ")

    def test_script_child_with_json(self) -> None:
        ads = AutoAds("https://ad-server.example.com")
        node = ads.to_node()
        script = node.children[0]
        assert script.tag == "script"  # type: ignore[union-attr]
        assert script.attrs["type"] == "application/json"  # type: ignore[union-attr]


def _make_page(page_id: str = "p1") -> Page:
    return Page(
        page_id=page_id,
        layers=[Layer("fill", children=[AmpImg("img.jpg", alt="")])],
    )


def _make_story(**kwargs: object) -> Story:
    defaults: dict[str, object] = {
        "title": "Test Story",
        "publisher": "Publisher",
        "publisher_logo_src": "https://example.com/logo.png",
        "poster_portrait_src": "https://example.com/poster.jpg",
        "canonical_url": "https://example.com/story.html",
        "pages": [_make_page()],
    }
    defaults.update(kwargs)
    return Story(**defaults)  # type: ignore[arg-type]


class TestAutoAdsStoryIntegration:
    def test_auto_ads_script_injected(self) -> None:
        ads = AutoAds("https://ad-server.example.com")
        pages = [_make_page(f"p{i}") for i in range(4)]
        story = _make_story(pages=pages, auto_ads=ads)
        assert "amp-story-auto-ads-0.1.js" in story.render()

    def test_auto_ads_rendered_before_pages(self) -> None:
        ads = AutoAds("https://ad-server.example.com")
        pages = [_make_page(f"p{i}") for i in range(4)]
        story = _make_story(pages=pages, auto_ads=ads)
        rendered = story.render()
        ads_pos = rendered.index("amp-story-auto-ads")
        page_pos = rendered.index("amp-story-page")
        assert ads_pos < page_pos

    def test_no_auto_ads_no_script(self) -> None:
        pages = [_make_page(f"p{i}") for i in range(4)]
        story = _make_story(pages=pages)
        assert "amp-story-auto-ads" not in story.render()

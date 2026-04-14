"""Tests for live story features."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.elements import AmpImg
from amp_stories.layer import Layer
from amp_stories.page import Page
from amp_stories.story import Story


def _make_page(page_id: str = "p1", sort_time: int | None = None) -> Page:
    return Page(
        page_id=page_id,
        layers=[Layer("fill", children=[AmpImg("img.jpg")])],
        data_sort_time=sort_time,
    )


def _make_story(**kwargs: object) -> Story:
    defaults: dict[str, object] = {
        "title": "Live Story",
        "publisher": "Publisher",
        "publisher_logo_src": "https://example.com/logo.png",
        "poster_portrait_src": "https://example.com/poster.jpg",
        "canonical_url": "https://example.com/story.html",
        "pages": [_make_page()],
    }
    defaults.update(kwargs)
    return Story(**defaults)  # type: ignore[arg-type]


class TestLiveStory:
    def test_live_story_attribute(self) -> None:
        story = _make_story(live_story=True, data_poll_interval=15000)
        rendered = story.render()
        assert "live-story" in rendered

    def test_live_story_not_present_by_default(self) -> None:
        story = _make_story()
        assert "live-story" not in story.render()

    def test_live_story_disabled_attr(self) -> None:
        story = _make_story(live_story_disabled=True)
        assert "live-story-disabled" in story.render()

    def test_poll_interval_in_rendered_output(self) -> None:
        story = _make_story(live_story=True, data_poll_interval=30000)
        assert "30000" in story.render()

    def test_poll_interval_below_minimum_raises(self) -> None:
        with pytest.raises(ValidationError, match="15000"):
            _make_story(live_story=True, data_poll_interval=10000)

    def test_poll_interval_exactly_minimum_allowed(self) -> None:
        story = _make_story(live_story=True, data_poll_interval=15000)
        assert story.data_poll_interval == 15000

    def test_data_sort_time_on_page(self) -> None:
        page = _make_page("p1", sort_time=1700000000000)
        node = page.to_node()
        assert node.attrs["data-sort-time"] == "1700000000000"

    def test_data_sort_time_absent_when_not_set(self) -> None:
        page = _make_page("p1")
        node = page.to_node()
        assert "data-sort-time" not in node.attrs

    def test_multiple_pages_with_sort_times(self) -> None:
        pages = [
            _make_page("p1", sort_time=1700000000000),
            _make_page("p2", sort_time=1700000001000),
            _make_page("p3", sort_time=1700000002000),
        ]
        story = _make_story(live_story=True, data_poll_interval=15000, pages=pages)
        rendered = story.render()
        assert "1700000000000" in rendered
        assert "1700000002000" in rendered

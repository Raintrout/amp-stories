"""Tests for page.py."""

from __future__ import annotations

import pytest

from amp_stories._validation import AmpStoriesWarning, ValidationError
from amp_stories.attachment import AttachmentLink, PageAttachment
from amp_stories.elements import AmpImg, heading
from amp_stories.layer import Layer
from amp_stories.outlink import PageOutlink
from amp_stories.page import Page


def _fill_layer() -> Layer:
    return Layer("fill", children=[AmpImg("img.jpg", alt="")])


def _vertical_layer() -> Layer:
    return Layer("vertical", children=[heading("Title")])


class TestPageConstruction:
    def test_valid_page(self) -> None:
        page = Page("cover", layers=[_fill_layer()])
        assert page.page_id == "cover"

    def test_empty_id_raises(self) -> None:
        with pytest.raises(ValidationError, match="page_id"):
            Page("", layers=[_fill_layer()])

    def test_id_starting_with_digit_raises(self) -> None:
        with pytest.raises(ValidationError, match="page_id"):
            Page("1bad", layers=[_fill_layer()])

    def test_id_with_spaces_raises(self) -> None:
        with pytest.raises(ValidationError, match="page_id"):
            Page("my page", layers=[_fill_layer()])

    def test_valid_id_with_hyphen(self) -> None:
        page = Page("my-page", layers=[_fill_layer()])
        assert page.page_id == "my-page"

    def test_valid_id_with_dot_and_colon(self) -> None:
        page = Page("page.1:a", layers=[_fill_layer()])
        assert page.page_id == "page.1:a"

    def test_empty_layers_raises(self) -> None:
        with pytest.raises(ValidationError, match="at least one Layer"):
            Page("cover", layers=[])

    def test_outlink_and_attachment_raises(self) -> None:
        with pytest.raises(ValidationError, match="cannot have both"):
            Page(
                "cover",
                layers=[_fill_layer()],
                outlink=PageOutlink(href="https://example.com"),
                attachment=PageAttachment(
                    links=[AttachmentLink("x", "https://example.com")]
                ),
            )

    def test_no_fill_layer_warns(self) -> None:
        with pytest.warns(AmpStoriesWarning, match="fill"):
            Page("cover", layers=[_vertical_layer()])

    def test_fill_layer_no_warning(self) -> None:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            Page("cover", layers=[_fill_layer()])  # should not warn


class TestPageRendering:
    def test_renders_amp_story_page_tag(self) -> None:
        page = Page("cover", layers=[_fill_layer()])
        node = page.to_node()
        assert node.tag == "amp-story-page"

    def test_id_attribute(self) -> None:
        page = Page("p-123", layers=[_fill_layer()])
        assert page.to_node().attrs["id"] == "p-123"

    def test_auto_advance_after_attr(self) -> None:
        page = Page("p", layers=[_fill_layer()], auto_advance_after="5s")
        assert page.to_node().attrs["auto-advance-after"] == "5s"

    def test_background_audio_attr(self) -> None:
        page = Page("p", layers=[_fill_layer()], background_audio="audio.mp3")
        assert page.to_node().attrs["background-audio"] == "audio.mp3"

    def test_layers_rendered_as_children(self) -> None:
        page = Page("p", layers=[_fill_layer(), _vertical_layer()])
        node = page.to_node()
        layer_tags = [c.tag for c in node.children]  # type: ignore[union-attr]
        assert layer_tags.count("amp-story-grid-layer") == 2

    def test_outlink_rendered_last(self) -> None:
        page = Page(
            "p",
            layers=[_fill_layer()],
            outlink=PageOutlink(href="https://example.com"),
        )
        node = page.to_node()
        last_child = node.children[-1]
        assert last_child.tag == "amp-story-page-outlink"  # type: ignore[union-attr]

    def test_attachment_rendered_last(self) -> None:
        page = Page(
            "p",
            layers=[_fill_layer()],
            attachment=PageAttachment(
                links=[AttachmentLink("Read", "https://example.com")]
            ),
        )
        node = page.to_node()
        last_child = node.children[-1]
        assert last_child.tag == "amp-story-page-attachment"  # type: ignore[union-attr]

    def test_data_sort_time_attr(self) -> None:
        page = Page("p", layers=[_fill_layer()], data_sort_time=1700000000000)
        assert page.to_node().attrs["data-sort-time"] == "1700000000000"


class TestPageAddLayer:
    def test_add_layer_returns_self(self) -> None:
        page = Page("p", layers=[_fill_layer()])
        result = page.add_layer(_vertical_layer())
        assert result is page
        assert len(page.layers) == 2

    def test_add_layer_appends(self) -> None:
        fill = _fill_layer()
        page = Page("p", layers=[fill])
        vert = _vertical_layer()
        page.add_layer(vert)
        assert page.layers[-1] is vert

    def test_add_layer_multiple_at_once(self) -> None:
        page = Page("p", layers=[_fill_layer()])
        page.add_layer(_vertical_layer(), _vertical_layer())
        assert len(page.layers) == 3


class TestPageRepr:
    def test_repr_includes_page_id(self) -> None:
        page = Page("cover", layers=[_fill_layer()])
        assert "cover" in repr(page)

    def test_repr_includes_layer_count(self) -> None:
        page = Page("p", layers=[_fill_layer(), _vertical_layer()])
        assert "layers=2" in repr(page)

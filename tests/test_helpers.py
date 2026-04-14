"""Tests for amp_stories/helpers.py — text constructors and layer factories."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.elements import AmpImg, AmpVideo
from amp_stories.helpers import (
    background_layer,
    blockquote,
    heading,
    paragraph,
    positioned_layer,
    span,
    text_layer,
)
from amp_stories.layer import Layer


class TestHeading:
    def test_default_level(self) -> None:
        el = heading("Hello")
        assert el.tag == "h1"
        assert el.text == "Hello"

    def test_level_3(self) -> None:
        assert heading("x", level=3).tag == "h3"

    def test_all_valid_levels(self) -> None:
        for lvl in range(1, 7):
            assert heading("x", level=lvl).tag == f"h{lvl}"

    def test_invalid_level_raises(self) -> None:
        with pytest.raises(ValidationError, match="level"):
            heading("x", level=7)

    def test_invalid_level_zero_raises(self) -> None:
        with pytest.raises(ValidationError, match="level"):
            heading("x", level=0)

    def test_style_forwarded(self) -> None:
        el = heading("Title", style="color:red")
        assert el.style == "color:red"

    def test_class_forwarded(self) -> None:
        el = heading("Title", class_="my-heading")
        assert el.class_ == "my-heading"

    def test_id_forwarded(self) -> None:
        el = heading("Title", id="h1-id")
        assert el.id == "h1-id"

    def test_animation_forwarded(self) -> None:
        el = heading("Title", animate_in="fade-in", animate_in_duration="0.5s")
        assert el.animate_in == "fade-in"
        assert el.animate_in_duration == "0.5s"

    def test_animate_in_after_forwarded(self) -> None:
        el = heading("Title", animate_in="fade-in", animate_in_after="hero")
        assert el.animate_in_after == "hero"

    def test_renders_correctly(self) -> None:
        node = heading("My Title", level=2).to_node()
        assert node.tag == "h2"
        assert node.children == ["My Title"]


class TestParagraph:
    def test_tag(self) -> None:
        el = paragraph("body")
        assert el.tag == "p"
        assert el.text == "body"

    def test_style_forwarded(self) -> None:
        assert paragraph("text", style="font-size:1rem").style == "font-size:1rem"

    def test_class_forwarded(self) -> None:
        assert paragraph("text", class_="intro").class_ == "intro"

    def test_animation_forwarded(self) -> None:
        el = paragraph("text", animate_in="drop", animate_in_duration="0.3s")
        node = el.to_node()
        assert node.attrs["animate-in"] == "drop"
        assert node.attrs["animate-in-duration"] == "0.3s"


class TestSpan:
    def test_tag(self) -> None:
        el = span("inline")
        assert el.tag == "span"
        assert el.text == "inline"

    def test_class_forwarded(self) -> None:
        assert span("x", class_="highlight").class_ == "highlight"

    def test_animation_forwarded(self) -> None:
        el = span("x", animate_in="fade-in")
        assert el.animate_in == "fade-in"


class TestBlockquote:
    def test_tag(self) -> None:
        el = blockquote("quote")
        assert el.tag == "blockquote"
        assert el.text == "quote"

    def test_class_forwarded(self) -> None:
        assert blockquote("q", class_="pull-quote").class_ == "pull-quote"

    def test_style_forwarded(self) -> None:
        assert blockquote("q", style="border-left:4px solid").style == "border-left:4px solid"


class TestBackgroundLayer:
    def test_fill_template(self) -> None:
        img = AmpImg("bg.jpg", alt="background")
        layer = background_layer(img)
        assert layer.template == "fill"

    def test_child_is_media(self) -> None:
        img = AmpImg("bg.jpg", alt="")
        layer = background_layer(img)
        assert layer.children == [img]

    def test_with_video(self) -> None:
        video = AmpVideo("bg.mp4")
        layer = background_layer(video)
        assert layer.template == "fill"
        assert layer.children == [video]

    def test_renders_to_fill_grid_layer(self) -> None:
        img = AmpImg("bg.jpg", alt="")
        node = background_layer(img).to_node()
        assert node.tag == "amp-story-grid-layer"
        assert node.attrs["template"] == "fill"


class TestTextLayer:
    def test_vertical_template(self) -> None:
        layer = text_layer()
        assert layer.template == "vertical"

    def test_no_args_empty_children(self) -> None:
        assert text_layer().children == []

    def test_children_passed_through(self) -> None:
        h = heading("Title")
        p = paragraph("Body")
        layer = text_layer(h, p)
        assert layer.children == [h, p]

    def test_renders_to_vertical_grid_layer(self) -> None:
        node = text_layer(heading("Hi")).to_node()
        assert node.tag == "amp-story-grid-layer"
        assert node.attrs["template"] == "vertical"


class TestPositionedLayer:
    def test_returns_layer(self) -> None:
        assert isinstance(positioned_layer("fill", "5%", "10%", "50%", "auto"), Layer)

    def test_position_is_absolute(self) -> None:
        layer = positioned_layer("fill", "5%", "10%", "50%", "auto")
        assert layer.position == "absolute"

    def test_style_contains_left(self) -> None:
        layer = positioned_layer("fill", "5%", "10%", "50%", "auto")
        assert layer.style is not None
        assert "left:5%" in layer.style

    def test_style_contains_top(self) -> None:
        layer = positioned_layer("fill", "5%", "10%", "50%", "auto")
        assert layer.style is not None
        assert "top:10%" in layer.style

    def test_style_contains_width(self) -> None:
        layer = positioned_layer("fill", "5%", "10%", "50%", "auto")
        assert layer.style is not None
        assert "width:50%" in layer.style

    def test_style_contains_height(self) -> None:
        layer = positioned_layer("fill", "5%", "10%", "50%", "auto")
        assert layer.style is not None
        assert "height:auto" in layer.style

    def test_children_forwarded(self) -> None:
        img = AmpImg("/img.jpg", alt="")
        layer = positioned_layer("fill", "0", "0", "100%", "100%", children=[img])
        assert layer.children == [img]

    def test_no_children_empty_list(self) -> None:
        layer = positioned_layer("fill", "0", "0", "100%", "100%")
        assert layer.children == []

    def test_template_forwarded(self) -> None:
        layer = positioned_layer("vertical", "0", "0", "100%", "100%")
        assert layer.template == "vertical"

    def test_style_in_rendered_node(self) -> None:
        layer = positioned_layer("fill", "5%", "10%", "50%", "auto")
        node = layer.to_node()
        assert node.attrs.get("style") is not None
        assert node.attrs.get("position") == "absolute"

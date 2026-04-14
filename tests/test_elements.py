"""Tests for elements.py."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.elements import (
    AmpAudio,
    AmpImg,
    AmpList,
    AmpVideo,
    DivElement,
    TextElement,
    blockquote,
    heading,
    paragraph,
    span,
)


class TestAmpImg:
    def test_renders_amp_img_tag(self) -> None:
        img = AmpImg("https://example.com/img.jpg")
        node = img.to_node()
        assert node.tag == "amp-img"

    def test_default_attrs(self) -> None:
        img = AmpImg("https://example.com/img.jpg", alt="desc")
        node = img.to_node()
        assert node.attrs["src"] == "https://example.com/img.jpg"
        assert node.attrs["width"] == "900"
        assert node.attrs["height"] == "1600"
        assert node.attrs["layout"] == "fill"
        assert node.attrs["alt"] == "desc"

    def test_custom_dimensions(self) -> None:
        img = AmpImg("img.jpg", width=400, height=300, layout="fixed")
        node = img.to_node()
        assert node.attrs["width"] == "400"
        assert node.attrs["height"] == "300"
        assert node.attrs["layout"] == "fixed"

    def test_empty_src_raises(self) -> None:
        with pytest.raises(ValidationError, match="src"):
            AmpImg("")

    def test_invalid_layout_raises(self) -> None:
        with pytest.raises(ValidationError, match="layout"):
            AmpImg("img.jpg", layout="bad-layout")  # type: ignore[arg-type]

    def test_animation_attrs_included(self) -> None:
        img = AmpImg("img.jpg", animate_in="fade-in", animate_in_delay="0.5s")
        node = img.to_node()
        assert node.attrs["animate-in"] == "fade-in"
        assert node.attrs["animate-in-delay"] == "0.5s"

    def test_animation_after_attr(self) -> None:
        img = AmpImg("img.jpg", animate_in="fade-in", animate_in_after="hero")
        node = img.to_node()
        assert node.attrs["animate-in-after"] == "hero"

    def test_invalid_animate_in_raises(self) -> None:
        with pytest.raises(ValidationError, match="animate_in"):
            AmpImg("img.jpg", animate_in="spin-around")  # type: ignore[arg-type]

    def test_invalid_duration_raises(self) -> None:
        with pytest.raises(ValidationError, match="animate_in_duration"):
            AmpImg("img.jpg", animate_in="fade-in", animate_in_duration="fast")

    def test_id_attr(self) -> None:
        img = AmpImg("img.jpg", id="hero-img")
        node = img.to_node()
        assert node.attrs["id"] == "hero-img"


class TestAmpVideo:
    def test_renders_amp_video_tag(self) -> None:
        video = AmpVideo("video.mp4")
        assert video.to_node().tag == "amp-video"

    def test_default_booleans(self) -> None:
        video = AmpVideo("video.mp4")
        node = video.to_node()
        assert node.attrs["autoplay"] is True
        assert node.attrs["muted"] is True
        assert node.attrs.get("loop") is None  # False → None

    def test_loop_enabled(self) -> None:
        video = AmpVideo("video.mp4", loop=True)
        assert video.to_node().attrs["loop"] is True

    def test_poster_attr(self) -> None:
        video = AmpVideo("video.mp4", poster="poster.jpg")
        assert video.to_node().attrs["poster"] == "poster.jpg"

    def test_empty_src_raises(self) -> None:
        with pytest.raises(ValidationError, match="src"):
            AmpVideo("")

    def test_animation_on_video(self) -> None:
        video = AmpVideo("v.mp4", animate_in="zoom-in")
        assert video.to_node().attrs["animate-in"] == "zoom-in"


class TestAmpAudio:
    def test_renders_amp_audio_tag(self) -> None:
        audio = AmpAudio("audio.mp3")
        assert audio.to_node().tag == "amp-audio"

    def test_empty_src_raises(self) -> None:
        with pytest.raises(ValidationError, match="src"):
            AmpAudio("")

    def test_autoplay_default(self) -> None:
        audio = AmpAudio("audio.mp3")
        assert audio.to_node().attrs["autoplay"] is True


class TestTextElement:
    def test_heading_tag(self) -> None:
        el = TextElement("h1", "Title")
        assert el.to_node().tag == "h1"
        assert el.to_node().children == ["Title"]

    def test_paragraph_tag(self) -> None:
        el = TextElement("p", "Body text")
        assert el.to_node().tag == "p"

    def test_invalid_tag_raises(self) -> None:
        with pytest.raises(ValidationError, match="tag"):
            TextElement("script", "bad")  # type: ignore[arg-type]

    def test_style_attr(self) -> None:
        el = TextElement("p", "text", style="color:red")
        assert el.to_node().attrs["style"] == "color:red"

    def test_animation_attrs(self) -> None:
        el = TextElement("h2", "title", animate_in="fly-in-left", animate_in_delay="1s")
        node = el.to_node()
        assert node.attrs["animate-in"] == "fly-in-left"
        assert node.attrs["animate-in-delay"] == "1s"

    def test_no_animation_attrs_absent(self) -> None:
        el = TextElement("p", "text")
        node = el.to_node()
        assert node.attrs.get("animate-in") is None


class TestConvenienceConstructors:
    def test_heading_default_level(self) -> None:
        el = heading("Hello")
        assert el.tag == "h1"
        assert el.text == "Hello"

    def test_heading_level_3(self) -> None:
        assert heading("x", level=3).tag == "h3"

    def test_heading_invalid_level(self) -> None:
        with pytest.raises(ValidationError, match="level"):
            heading("x", level=7)

    def test_paragraph(self) -> None:
        el = paragraph("body")
        assert el.tag == "p"
        assert el.text == "body"

    def test_span(self) -> None:
        el = span("inline")
        assert el.tag == "span"

    def test_blockquote(self) -> None:
        el = blockquote("quote")
        assert el.tag == "blockquote"

    def test_convenience_passes_animation(self) -> None:
        el = paragraph("text", animate_in="drop", animate_in_duration="0.3s")
        node = el.to_node()
        assert node.attrs["animate-in"] == "drop"
        assert node.attrs["animate-in-duration"] == "0.3s"


class TestDivElement:
    def test_renders_div(self) -> None:
        el = DivElement()
        assert el.to_node().tag == "div"

    def test_children_rendered(self) -> None:
        child = TextElement("p", "hello")
        div = DivElement(children=[child])
        node = div.to_node()
        assert len(node.children) == 1
        assert node.children[0].tag == "p"  # type: ignore[union-attr]

    def test_style_and_class(self) -> None:
        div = DivElement(style="color:red", class_="wrapper")
        node = div.to_node()
        assert node.attrs["style"] == "color:red"
        assert node.attrs["class"] == "wrapper"

    def test_animation_on_div(self) -> None:
        div = DivElement(animate_in="fade-in")
        assert div.to_node().attrs["animate-in"] == "fade-in"


class TestAmpList:
    def test_renders_amp_list(self) -> None:
        lst = AmpList("https://example.com/data.json")
        assert lst.to_node().tag == "amp-list"

    def test_empty_src_raises(self) -> None:
        with pytest.raises(ValidationError, match="src"):
            AmpList("")

    def test_default_attrs(self) -> None:
        lst = AmpList("https://example.com/data.json")
        node = lst.to_node()
        assert node.attrs["layout"] == "fixed-height"
        assert node.attrs["height"] == "400"

    def test_template_wrapped_in_template_tag(self) -> None:
        lst = AmpList("https://example.com/data.json", template="<p>{{item}}</p>")
        node = lst.to_node()
        assert len(node.children) == 1
        template_node = node.children[0]
        assert template_node.tag == "template"  # type: ignore[union-attr]
        assert template_node.attrs["type"] == "amp-mustache"  # type: ignore[union-attr]

    def test_no_template_no_children(self) -> None:
        lst = AmpList("https://example.com/data.json")
        assert lst.to_node().children == []

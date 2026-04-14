"""Tests for elements.py."""

from __future__ import annotations

import warnings

import pytest

from amp_stories._validation import AmpStoriesWarning, ValidationError
from amp_stories.elements import (
    AmpAudio,
    AmpImg,
    AmpList,
    AmpVideo,
    DivElement,
    Story360,
    StoryPanningMedia,
    TextElement,
    VideoSource,
    blockquote,
    heading,
    paragraph,
    span,
)


class TestAmpImg:
    def test_renders_amp_img_tag(self) -> None:
        img = AmpImg("https://example.com/img.jpg", alt="")
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
        img = AmpImg("img.jpg", alt="", width=400, height=300, layout="fixed")
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
        img = AmpImg("img.jpg", alt="", animate_in="fade-in", animate_in_delay="0.5s")
        node = img.to_node()
        assert node.attrs["animate-in"] == "fade-in"
        assert node.attrs["animate-in-delay"] == "0.5s"

    def test_animation_after_attr(self) -> None:
        img = AmpImg("img.jpg", alt="", animate_in="fade-in", animate_in_after="hero")
        node = img.to_node()
        assert node.attrs["animate-in-after"] == "hero"

    def test_invalid_animate_in_raises(self) -> None:
        with pytest.raises(ValidationError, match="animate_in"):
            AmpImg("img.jpg", animate_in="spin-around")  # type: ignore[arg-type]

    def test_invalid_duration_raises(self) -> None:
        with pytest.raises(ValidationError, match="animate_in_duration"):
            AmpImg("img.jpg", animate_in="fade-in", animate_in_duration="fast")

    def test_id_attr(self) -> None:
        img = AmpImg("img.jpg", alt="", id="hero-img")
        node = img.to_node()
        assert node.attrs["id"] == "hero-img"

    def test_no_alt_emits_warning(self) -> None:
        with pytest.warns(AmpStoriesWarning, match="no alt text"):
            AmpImg("img.jpg")

    def test_empty_alt_suppresses_warning(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            AmpImg("img.jpg", alt="")  # must not raise

    def test_explicit_alt_suppresses_warning(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            AmpImg("img.jpg", alt="A mountain peak")  # must not raise

    def test_none_alt_renders_empty_string(self) -> None:
        img = AmpImg("img.jpg")
        assert img.to_node().attrs["alt"] == ""


class TestVideoSource:
    def test_renders_source_tag(self) -> None:
        s = VideoSource("video.mp4", "video/mp4")
        node = s.to_node()
        assert node.tag == "source"
        assert node.attrs["src"] == "video.mp4"
        assert node.attrs["type"] == "video/mp4"

    def test_empty_src_raises(self) -> None:
        with pytest.raises(ValidationError, match="src"):
            VideoSource("", "video/mp4")

    def test_empty_type_raises(self) -> None:
        with pytest.raises(ValidationError, match="type"):
            VideoSource("video.mp4", "")


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
        with pytest.raises(ValidationError, match="src.*sources"):
            AmpVideo("")

    def test_no_src_no_sources_raises(self) -> None:
        with pytest.raises(ValidationError, match="src.*sources"):
            AmpVideo()  # type: ignore[call-arg]

    def test_both_src_and_sources_raises(self) -> None:
        with pytest.raises(ValidationError, match="not both"):
            AmpVideo("video.mp4", sources=[VideoSource("video.mp4", "video/mp4")])

    def test_multi_source_renders_source_children(self) -> None:
        video = AmpVideo(sources=[
            VideoSource("video.mp4", "video/mp4"),
            VideoSource("video.webm", "video/webm"),
        ])
        node = video.to_node()
        assert node.attrs.get("src") is None
        assert len(node.children) == 2
        assert node.children[0].tag == "source"  # type: ignore[union-attr]
        assert node.children[1].attrs["type"] == "video/webm"  # type: ignore[union-attr]

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

    def test_long_text_emits_warning(self) -> None:
        long_text = "x" * 201
        with pytest.warns(AmpStoriesWarning, match="201 characters"):
            TextElement("p", long_text)

    def test_exactly_200_chars_no_warning(self) -> None:
        text = "x" * 200
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            TextElement("p", text)  # must not raise


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

    def test_string_child_passthrough(self) -> None:
        div = DivElement(children=["raw text"])
        node = div.to_node()
        assert node.children[0] == "raw text"

    def test_mixed_children(self) -> None:
        div = DivElement(children=[TextElement("p", "hello"), "inline text"])
        node = div.to_node()
        assert node.children[0].tag == "p"  # type: ignore[union-attr]
        assert node.children[1] == "inline text"

    def test_add_child_returns_self(self) -> None:
        div = DivElement()
        child = TextElement("p", "hello")
        result = div.add_child(child)
        assert result is div
        assert child in div.children

    def test_add_child_appends(self) -> None:
        p = TextElement("p", "first")
        div = DivElement(children=[p])
        span_el = TextElement("span", "second")
        div.add_child(span_el)
        assert div.children[-1] is span_el

    def test_add_child_multiple_at_once(self) -> None:
        div = DivElement()
        a = TextElement("h1", "a")
        b = TextElement("h2", "b")
        div.add_child(a, b)
        assert len(div.children) == 2
        assert div.children[0] is a
        assert div.children[1] is b


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


class TestDivElementExpandedChildren:
    def test_div_with_amp_audio_child(self) -> None:
        audio = AmpAudio("audio.mp3")
        div = DivElement(children=[audio])
        node = div.to_node()
        assert node.children[0].tag == "amp-audio"  # type: ignore[union-attr]

    def test_div_with_amp_list_child(self) -> None:
        lst = AmpList("https://example.com/data.json")
        div = DivElement(children=[lst])
        node = div.to_node()
        assert node.children[0].tag == "amp-list"  # type: ignore[union-attr]


class TestStoryPanningMedia:
    def test_renders_panning_media_tag(self) -> None:
        m = StoryPanningMedia("img.jpg")
        assert m.to_node().tag == "amp-story-panning-media"

    def test_default_attrs(self) -> None:
        m = StoryPanningMedia("img.jpg")
        node = m.to_node()
        assert node.attrs["src"] == "img.jpg"
        assert node.attrs["width"] == "900"
        assert node.attrs["height"] == "1600"
        assert node.attrs["layout"] == "fill"

    def test_empty_src_raises(self) -> None:
        with pytest.raises(ValidationError, match="src"):
            StoryPanningMedia("")

    def test_animation_attrs(self) -> None:
        m = StoryPanningMedia("img.jpg", animate_in="fade-in", animate_in_delay="0.5s")
        node = m.to_node()
        assert node.attrs["animate-in"] == "fade-in"
        assert node.attrs["animate-in-delay"] == "0.5s"

    def test_id_attr(self) -> None:
        m = StoryPanningMedia("img.jpg", id="panning")
        assert m.to_node().attrs["id"] == "panning"

    def test_invalid_animate_in_raises(self) -> None:
        with pytest.raises(ValidationError, match="animate_in"):
            StoryPanningMedia("img.jpg", animate_in="spin-around")  # type: ignore[arg-type]


class TestStory360:
    def test_renders_story360_tag(self) -> None:
        m = Story360("img.jpg")
        assert m.to_node().tag == "amp-story-360"

    def test_default_attrs(self) -> None:
        m = Story360("img.jpg")
        node = m.to_node()
        assert node.attrs["src"] == "img.jpg"
        assert node.attrs["width"] == "900"
        assert node.attrs["height"] == "1600"
        assert node.attrs["layout"] == "fill"

    def test_empty_src_raises(self) -> None:
        with pytest.raises(ValidationError, match="src"):
            Story360("")

    def test_custom_dimensions(self) -> None:
        m = Story360("img.jpg", width=1920, height=960)
        node = m.to_node()
        assert node.attrs["width"] == "1920"
        assert node.attrs["height"] == "960"

    def test_id_attr(self) -> None:
        m = Story360("img.jpg", id="360-view")
        assert m.to_node().attrs["id"] == "360-view"

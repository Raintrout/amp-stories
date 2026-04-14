"""Tests for _serde.py — serialization / deserialization round-trips."""

from __future__ import annotations

import pytest

from amp_stories._serde import _deserialize, _get_registry, _serialize, from_dict
from amp_stories.attachment import AttachmentLink, PageAttachment
from amp_stories.auto_ads import AutoAds
from amp_stories.bookend import Bookend, BookendComponent, BookendShareProvider
from amp_stories.consent import AmpConsent
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
)
from amp_stories.interactive import (
    InteractiveBinaryPoll,
    InteractiveOption,
    InteractivePoll,
    InteractiveQuiz,
    InteractiveResults,
    InteractiveSlider,
)
from amp_stories.layer import Layer
from amp_stories.outlink import PageOutlink
from amp_stories.page import Page
from amp_stories.shopping import ShoppingTag, StoryShopping
from amp_stories.story import Story

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _img(alt: str = "") -> AmpImg:
    return AmpImg("https://example.com/img.jpg", alt=alt)


def _fill_layer() -> Layer:
    return Layer("fill", children=[_img()])


def _make_story(**kwargs: object) -> Story:
    defaults: dict[str, object] = {
        "title": "Test Story",
        "publisher": "Publisher",
        "publisher_logo_src": "https://example.com/logo.png",
        "poster_portrait_src": "https://example.com/poster.jpg",
        "canonical_url": "https://example.com/story.html",
        "pages": [Page("p1", layers=[_fill_layer()])],
    }
    defaults.update(kwargs)
    return Story(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _serialize primitives
# ---------------------------------------------------------------------------

class TestSerializePrimitives:
    def test_none(self) -> None:
        assert _serialize(None) is None

    def test_string(self) -> None:
        assert _serialize("hello") == "hello"

    def test_int(self) -> None:
        assert _serialize(42) == 42

    def test_float(self) -> None:
        assert _serialize(3.14) == 3.14

    def test_bool(self) -> None:
        assert _serialize(True) is True
        assert _serialize(False) is False

    def test_list(self) -> None:
        assert _serialize([1, "a", None]) == [1, "a", None]

    def test_nested_list(self) -> None:
        assert _serialize([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]

    def test_dict(self) -> None:
        assert _serialize({"a": 1, "b": "x"}) == {"a": 1, "b": "x"}


# ---------------------------------------------------------------------------
# _serialize dataclasses
# ---------------------------------------------------------------------------

class TestSerializeDataclasses:
    def test_type_key_added(self) -> None:
        img = _img()
        data = _serialize(img)
        assert data["__type__"] == "AmpImg"

    def test_fields_included(self) -> None:
        img = _img("desc")
        data = _serialize(img)
        assert data["src"] == "https://example.com/img.jpg"
        assert data["alt"] == "desc"
        assert data["layout"] == "fill"

    def test_none_fields_omitted(self) -> None:
        img = _img()
        data = _serialize(img)
        assert "animate_in" not in data
        assert "id" not in data

    def test_non_init_field_excluded(self) -> None:
        el = TextElement("h1", "Title")
        data = _serialize(el)
        assert "_VALID_TAGS" not in data

    def test_nested_dataclass(self) -> None:
        layer = _fill_layer()
        data = _serialize(layer)
        assert data["__type__"] == "Layer"
        assert data["children"][0]["__type__"] == "AmpImg"

    def test_string_child_preserved(self) -> None:
        layer = Layer("vertical", children=["raw text"])
        data = _serialize(layer)
        assert data["children"][0] == "raw text"

    def test_empty_list_included(self) -> None:
        bookend = Bookend()
        data = _serialize(bookend)
        assert data["share_providers"] == []
        assert data["components"] == []


# ---------------------------------------------------------------------------
# _deserialize
# ---------------------------------------------------------------------------

class TestDeserialize:
    def test_none(self) -> None:
        assert _deserialize(None) is None

    def test_scalar(self) -> None:
        assert _deserialize("hello") == "hello"
        assert _deserialize(42) == 42
        assert _deserialize(True) is True

    def test_list(self) -> None:
        assert _deserialize([1, 2, 3]) == [1, 2, 3]

    def test_known_type(self) -> None:
        data = {"__type__": "AmpImg", "src": "img.jpg", "alt": ""}
        obj = _deserialize(data)
        assert isinstance(obj, AmpImg)
        assert obj.src == "img.jpg"

    def test_unknown_type_returns_plain_dict(self) -> None:
        data = {"__type__": "UnknownFutureClass", "field": 42}
        result = _deserialize(data)
        assert isinstance(result, dict)
        assert result["__type__"] == "UnknownFutureClass"
        assert result["field"] == 42

    def test_plain_dict_no_type(self) -> None:
        data = {"checkConsentHref": "/check", "clientConfig": {}}
        result = _deserialize(data)
        assert result == data

    def test_dict_with_non_registry_type_preserved(self) -> None:
        # AutoAds.ad_attributes can contain a "type" key (plain data, not discriminator)
        data = {
            "__type__": "AutoAds",
            "ad_url": "https://ads.example.com",
            "ad_attributes": {"type": "adsense", "slot": "123"},
        }
        obj = _deserialize(data)
        assert isinstance(obj, AutoAds)
        assert obj.ad_attributes == {"type": "adsense", "slot": "123"}


# ---------------------------------------------------------------------------
# Registry caching
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_registry_cached(self) -> None:
        r1 = _get_registry()
        r2 = _get_registry()
        assert r1 is r2

    def test_registry_contains_core_types(self) -> None:
        reg = _get_registry()
        assert "Story" in reg
        assert "Page" in reg
        assert "Layer" in reg
        assert "AmpImg" in reg


# ---------------------------------------------------------------------------
# Round-trip tests
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_minimal_story(self) -> None:
        story = _make_story()
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()

    def test_story_to_dict_type(self) -> None:
        story = _make_story()
        assert story.to_dict()["__type__"] == "Story"

    def test_from_dict_wrong_type_raises(self) -> None:
        page_data = _serialize(Page("p", layers=[_fill_layer()]))
        with pytest.raises(ValueError, match="Story"):
            Story.from_dict(page_data)

    def test_module_level_from_dict(self) -> None:
        story = _make_story()
        story2 = from_dict(story.to_dict())
        assert isinstance(story2, Story)

    def test_module_level_from_dict_page(self) -> None:
        page = Page("p", layers=[_fill_layer()])
        page2 = from_dict(_serialize(page))
        assert isinstance(page2, Page)
        assert page2.page_id == "p"


class TestElementRoundTrips:
    def test_amp_video_src(self) -> None:
        video = AmpVideo("video.mp4", loop=True)
        data = _serialize(video)
        obj = _deserialize(data)
        assert isinstance(obj, AmpVideo)
        assert obj.src == "video.mp4"
        assert obj.loop is True

    def test_amp_video_sources(self) -> None:
        video = AmpVideo(sources=[VideoSource("v.mp4", "video/mp4")])
        data = _serialize(video)
        obj = _deserialize(data)
        assert isinstance(obj, AmpVideo)
        assert len(obj.sources) == 1
        assert obj.sources[0].src == "v.mp4"

    def test_text_element(self) -> None:
        el = TextElement("h2", "Hello", style="color:red")
        data = _serialize(el)
        obj = _deserialize(data)
        assert isinstance(obj, TextElement)
        assert obj.tag == "h2"
        assert obj.style == "color:red"

    def test_div_element_nested(self) -> None:
        div = DivElement(children=[TextElement("p", "text"), "raw"])
        data = _serialize(div)
        obj = _deserialize(data)
        assert isinstance(obj, DivElement)
        assert isinstance(obj.children[0], TextElement)
        assert obj.children[1] == "raw"

    def test_amp_audio(self) -> None:
        audio = AmpAudio("audio.mp3", loop=True)
        data = _serialize(audio)
        obj = _deserialize(data)
        assert isinstance(obj, AmpAudio)
        assert obj.loop is True

    def test_amp_list(self) -> None:
        lst = AmpList("https://example.com/data.json", template="<p>{{x}}</p>")
        data = _serialize(lst)
        obj = _deserialize(data)
        assert isinstance(obj, AmpList)
        assert obj.template == "<p>{{x}}</p>"

    def test_story_panning_media(self) -> None:
        m = StoryPanningMedia("img.jpg", animate_in="fade-in")
        data = _serialize(m)
        obj = _deserialize(data)
        assert isinstance(obj, StoryPanningMedia)
        assert obj.animate_in == "fade-in"

    def test_story360(self) -> None:
        m = Story360("img.jpg", width=1920, height=960)
        data = _serialize(m)
        obj = _deserialize(data)
        assert isinstance(obj, Story360)
        assert obj.width == 1920

    def test_animated_element(self) -> None:
        img2 = AmpImg(
            "img.jpg", alt="desc",
            animate_in="fly-in-bottom",
            animate_in_duration="0.5s",
            animate_in_delay="0.2s",
            animate_in_after="hero",
        )
        data = _serialize(img2)
        obj = _deserialize(data)
        assert isinstance(obj, AmpImg)
        assert obj.animate_in == "fly-in-bottom"
        assert obj.animate_in_after == "hero"


class TestOptionalFieldRoundTrips:
    def test_outlink(self) -> None:
        page = Page(
            "p",
            layers=[_fill_layer()],
            outlink=PageOutlink(
                href="https://example.com",
                theme="custom",
                cta_accent_color="#FF0000",
                cta_accent_element="text",
            ),
        )
        story = _make_story(pages=[page])
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()

    def test_attachment(self) -> None:
        page = Page(
            "p",
            layers=[_fill_layer()],
            attachment=PageAttachment(
                links=[AttachmentLink("Read more", "https://example.com")]
            ),
        )
        story = _make_story(pages=[page])
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()

    def test_bookend(self) -> None:
        bookend = Bookend(
            share_providers=[BookendShareProvider("twitter")],
            components=[BookendComponent("heading", text="Read more")],
        )
        story = _make_story(bookend=bookend)
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()

    def test_auto_ads(self) -> None:
        ads = AutoAds("https://ads.example.com", ad_attributes={"type": "adsense"})
        story = _make_story(auto_ads=ads)
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()

    def test_shopping(self) -> None:
        shopping = StoryShopping(tags=[
            ShoppingTag("p1", "Widget", "Acme", 9.99, "USD", ["img.jpg"]),
        ])
        story = _make_story(shopping=shopping)
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()

    def test_consent(self) -> None:
        consent = AmpConsent(
            consents={"c": {"checkConsentHref": "/check"}},
            post_prompt_ui="my-ui",
        )
        story = _make_story(consent=consent)
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()

    def test_structured_data(self) -> None:
        data = {"@context": "https://schema.org", "@type": "Article"}
        story = _make_story(structured_data=data)
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()


class TestInteractiveRoundTrips:
    def test_binary_poll(self) -> None:
        poll = InteractiveBinaryPoll("Yes", "No")
        data = _serialize(poll)
        obj = _deserialize(data)
        assert isinstance(obj, InteractiveBinaryPoll)
        assert obj.option_1_text == "Yes"

    def test_poll(self) -> None:
        poll = InteractivePoll([InteractiveOption("A"), InteractiveOption("B")])
        data = _serialize(poll)
        obj = _deserialize(data)
        assert isinstance(obj, InteractivePoll)
        assert len(obj.options) == 2

    def test_quiz(self) -> None:
        quiz = InteractiveQuiz([
            InteractiveOption("Right", correct=True),
            InteractiveOption("Wrong"),
        ])
        data = _serialize(quiz)
        obj = _deserialize(data)
        assert isinstance(obj, InteractiveQuiz)
        assert obj.options[0].correct is True

    def test_slider(self) -> None:
        slider = InteractiveSlider(emoji_start="😐", emoji_end="😍", id="s1")
        data = _serialize(slider)
        obj = _deserialize(data)
        assert isinstance(obj, InteractiveSlider)
        assert obj.id == "s1"

    def test_results(self) -> None:
        results = InteractiveResults([
            InteractiveOption("Outcome A"),
            InteractiveOption("Outcome B"),
        ])
        data = _serialize(results)
        obj = _deserialize(data)
        assert isinstance(obj, InteractiveResults)

    def test_interactive_in_story(self) -> None:
        page = Page(
            "p",
            layers=[
                _fill_layer(),
                Layer("vertical", children=[InteractiveBinaryPoll("Yes", "No")]),
            ],
        )
        story = _make_story(pages=[page])
        story2 = Story.from_dict(story.to_dict())
        assert story2.render() == story.render()


class TestJsonCompatibility:
    def test_to_dict_is_json_serializable(self) -> None:
        import json
        story = _make_story()
        json_str = json.dumps(story.to_dict())
        assert isinstance(json_str, str)

    def test_from_dict_after_json_roundtrip(self) -> None:
        import json
        story = _make_story()
        story2 = Story.from_dict(json.loads(json.dumps(story.to_dict())))
        assert story2.render() == story.render()

"""Tests for story.py — the root document renderer."""

from __future__ import annotations

import pathlib

import pytest

from amp_stories._validation import AmpStoriesWarning, ValidationError
from amp_stories.elements import AmpAudio, AmpImg, AmpList, AmpVideo
from amp_stories.layer import Layer
from amp_stories.page import Page
from amp_stories.story import Story


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


class TestStoryConstruction:
    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValidationError, match="title"):
            _make_story(title="")

    def test_empty_publisher_raises(self) -> None:
        with pytest.raises(ValidationError, match="publisher"):
            _make_story(publisher="")

    def test_empty_logo_raises(self) -> None:
        with pytest.raises(ValidationError, match="publisher_logo_src"):
            _make_story(publisher_logo_src="")

    def test_empty_poster_raises(self) -> None:
        with pytest.raises(ValidationError, match="poster_portrait_src"):
            _make_story(poster_portrait_src="")

    def test_empty_canonical_url_raises(self) -> None:
        with pytest.raises(ValidationError, match="canonical_url"):
            _make_story(canonical_url="")

    def test_no_pages_raises(self) -> None:
        with pytest.raises(ValidationError, match="at least one Page"):
            _make_story(pages=[])

    def test_duplicate_page_ids_raise_on_render(self) -> None:
        story = _make_story(pages=[_make_page("dup"), _make_page("dup")])
        with pytest.raises(ValidationError, match="Duplicate page id"):
            story.render()

    def test_poll_interval_too_low_raises(self) -> None:
        with pytest.raises(ValidationError, match="15000"):
            _make_story(live_story=True, data_poll_interval=5000)

    def test_live_story_without_poll_interval_raises(self) -> None:
        with pytest.raises(ValidationError, match="data_poll_interval"):
            _make_story(live_story=True)


class TestStoryRendering:
    def test_render_returns_string(self, minimal_story: Story) -> None:
        result = minimal_story.render()
        assert isinstance(result, str)

    def test_starts_with_doctype(self, minimal_story: Story) -> None:
        assert minimal_story.render().startswith("<!doctype html>")

    def test_html_has_amp_attribute(self, minimal_story: Story) -> None:
        rendered = minimal_story.render()
        assert "<html ⚡" in rendered

    def test_lang_attribute(self) -> None:
        story = _make_story(lang="fr")
        rendered = story.render()
        assert 'lang="fr"' in rendered

    def test_charset_meta(self, minimal_story: Story) -> None:
        rendered = minimal_story.render()
        assert 'charset="utf-8"' in rendered

    def test_canonical_link(self) -> None:
        story = _make_story(canonical_url="https://example.com/my-story.html")
        rendered = story.render()
        assert "https://example.com/my-story.html" in rendered
        assert 'rel="canonical"' in rendered

    def test_viewport_meta(self, minimal_story: Story) -> None:
        assert "width=device-width" in minimal_story.render()

    def test_amp_boilerplate_css(self, minimal_story: Story) -> None:
        rendered = minimal_story.render()
        assert "amp-boilerplate" in rendered
        assert "-amp-start" in rendered

    def test_title_in_head(self) -> None:
        story = _make_story(title="Amazing Story")
        assert "<title>Amazing Story</title>" in story.render()

    def test_amp_story_script_always_present(self, minimal_story: Story) -> None:
        rendered = minimal_story.render()
        assert "amp-story-1.0.js" in rendered

    def test_amp_runtime_script_present(self, minimal_story: Story) -> None:
        assert "cdn.ampproject.org/v0.js" in minimal_story.render()

    def test_amp_story_element_attrs(self) -> None:
        story = _make_story(
            title="My Story",
            publisher="Pub",
            publisher_logo_src="logo.png",
            poster_portrait_src="poster.jpg",
        )
        rendered = story.render()
        assert "standalone" in rendered
        assert 'title="My Story"' in rendered
        assert 'publisher="Pub"' in rendered
        assert 'publisher-logo-src="logo.png"' in rendered
        assert 'poster-portrait-src="poster.jpg"' in rendered

    def test_optional_poster_attrs(self) -> None:
        story = _make_story(
            poster_square_src="square.jpg",
            poster_landscape_src="landscape.jpg",
        )
        rendered = story.render()
        assert "poster-square-src" in rendered
        assert "poster-landscape-src" in rendered

    def test_supports_landscape_attr(self) -> None:
        story = _make_story(supports_landscape=True)
        assert "supports-landscape" in story.render()

    def test_supports_landscape_absent_when_false(self) -> None:
        story = _make_story(supports_landscape=False)
        assert "supports-landscape" not in story.render()

    def test_live_story_attr(self) -> None:
        story = _make_story(live_story=True, data_poll_interval=20000)
        rendered = story.render()
        assert "live-story" in rendered
        assert "20000" in rendered

    def test_custom_css_injected(self) -> None:
        story = _make_story(custom_css="body { color: red; }")
        rendered = story.render()
        assert "amp-custom" in rendered
        assert "color: red;" in rendered

    def test_entity_attrs(self) -> None:
        story = _make_story(
            entity="My Platform",
            entity_logo_src="platform-logo.png",
            entity_url="https://platform.example.com",
        )
        rendered = story.render()
        assert 'entity="My Platform"' in rendered
        assert "platform-logo.png" in rendered

    def test_background_audio_attr(self) -> None:
        story = _make_story(background_audio="theme.mp3")
        assert "theme.mp3" in story.render()


class TestScriptInjection:
    def test_no_extra_scripts_by_default(self, minimal_story: Story) -> None:
        rendered = minimal_story.render()
        assert "amp-story-bookend" not in rendered
        assert "amp-story-page-outlink" not in rendered
        assert "amp-video" not in rendered

    def test_amp_video_script_injected(self) -> None:
        page = Page(
            "p",
            layers=[Layer("fill", children=[AmpVideo("video.mp4")])],
        )
        story = _make_story(pages=[page])
        assert "amp-video-0.1.js" in story.render()

    def test_amp_audio_script_injected(self) -> None:
        page = Page(
            "p",
            layers=[
                Layer("fill", children=[AmpImg("img.jpg", alt="")]),
                Layer("vertical", children=[AmpAudio("audio.mp3")]),
            ],
        )
        story = _make_story(pages=[page])
        assert "amp-audio-0.1.js" in story.render()

    def test_amp_list_and_mustache_scripts_injected(self) -> None:
        page = Page(
            "p",
            layers=[
                Layer("fill", children=[AmpImg("img.jpg", alt="")]),
                Layer("vertical", children=[AmpList("https://example.com/data.json")]),
            ],
        )
        story = _make_story(pages=[page])
        rendered = story.render()
        assert "amp-list-0.1.js" in rendered
        assert "amp-mustache-0.2.js" in rendered

    def test_bookend_script_injected(self) -> None:
        from amp_stories.bookend import Bookend
        story = _make_story(bookend=Bookend())
        assert "amp-story-bookend-0.1.js" in story.render()

    def test_outlink_script_injected(self) -> None:
        from amp_stories.outlink import PageOutlink
        page = Page(
            "p",
            layers=[Layer("fill", children=[AmpImg("img.jpg", alt="")])],
            outlink=PageOutlink(href="https://example.com"),
        )
        story = _make_story(pages=[page])
        assert "amp-story-page-outlink-0.1.js" in story.render()

    def test_attachment_script_injected(self) -> None:
        from amp_stories.attachment import AttachmentLink, PageAttachment
        page = Page(
            "p",
            layers=[Layer("fill", children=[AmpImg("img.jpg", alt="")])],
            attachment=PageAttachment(links=[AttachmentLink("Read", "https://ex.com")]),
        )
        story = _make_story(pages=[page])
        assert "amp-story-page-attachment-0.1.js" in story.render()


class TestStoryRepr:
    def test_repr_includes_title(self) -> None:
        story = _make_story(title="My Story")
        assert "My Story" in repr(story)

    def test_repr_includes_page_count(self) -> None:
        story = _make_story(pages=[_make_page("p1"), _make_page("p2")])
        assert "pages=2" in repr(story)


class TestStoryValidate:
    def test_validate_passes_on_valid_story(self) -> None:
        pages = [_make_page(f"p{i}") for i in range(4)]
        story = _make_story(pages=pages)
        story.validate()  # must not raise

    def test_validate_raises_on_duplicate_ids(self) -> None:
        story = _make_story(pages=[_make_page("dup"), _make_page("dup")])
        with pytest.raises(ValidationError, match="Duplicate page id"):
            story.validate()

    def test_validate_warns_too_few_pages(self) -> None:
        story = _make_story(pages=[_make_page()])
        with pytest.warns(AmpStoriesWarning, match="at least 4"):
            story.validate()

    def test_validate_warns_too_many_pages(self) -> None:
        pages = [_make_page(f"p{i}") for i in range(31)]
        story = _make_story(pages=pages)
        with pytest.warns(AmpStoriesWarning, match="no more than"):
            story.validate()

    def test_exactly_4_pages_no_page_count_warning(self) -> None:
        import warnings
        pages = [_make_page(f"p{i}") for i in range(4)]
        story = _make_story(pages=pages)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            story.validate()
        page_count_warnings = [
            w for w in caught if issubclass(w.category, AmpStoriesWarning)
            and ("fewer" in str(w.message) or "more than" in str(w.message))
        ]
        assert page_count_warnings == []

    def test_render_calls_validate(self) -> None:
        story = _make_story(pages=[_make_page("dup"), _make_page("dup")])
        with pytest.raises(ValidationError, match="Duplicate page id"):
            story.render()


class TestPageCountWarnings:
    def test_1_page_warns_too_few(self) -> None:
        story = _make_story(pages=[_make_page()])
        with pytest.warns(AmpStoriesWarning, match="at least 4"):
            story.render()

    def test_31_pages_warns_too_many(self) -> None:
        pages = [_make_page(f"p{i}") for i in range(31)]
        story = _make_story(pages=pages)
        with pytest.warns(AmpStoriesWarning, match="no more than 30"):
            story.render()


class TestStructuredData:
    def test_structured_data_injected_in_head(self) -> None:
        story = _make_story(structured_data={"@context": "https://schema.org", "@type": "Article"})
        rendered = story.render()
        assert "application/ld+json" in rendered
        assert "schema.org" in rendered

    def test_structured_data_none_not_injected(self) -> None:
        story = _make_story()
        assert "ld+json" not in story.render()

    def test_structured_data_serialized_as_json(self) -> None:
        import json
        data = {"@context": "https://schema.org", "name": "My Story"}
        story = _make_story(structured_data=data)
        rendered = story.render()
        assert json.dumps(data) in rendered


class TestStoryAddPage:
    def test_add_page_returns_self(self) -> None:
        story = _make_story(pages=[_make_page("p1")])
        result = story.add_page(_make_page("p2"))
        assert result is story
        assert len(story.pages) == 2

    def test_add_page_appends(self) -> None:
        story = _make_story(pages=[_make_page("p1")])
        p2 = _make_page("p2")
        story.add_page(p2)
        assert story.pages[-1] is p2

    def test_add_page_multiple_at_once(self) -> None:
        story = _make_story(pages=[_make_page("p1")])
        story.add_page(_make_page("p2"), _make_page("p3"))
        assert len(story.pages) == 3


class TestNewComponentScriptInjection:
    def test_panning_media_script_injected(self) -> None:
        from amp_stories.elements import StoryPanningMedia
        page = Page(
            "p",
            layers=[Layer("fill", children=[StoryPanningMedia("img.jpg")])],
        )
        story = _make_story(pages=[page])
        assert "amp-story-panning-media-0.1.js" in story.render()

    def test_story360_script_injected(self) -> None:
        from amp_stories.elements import Story360
        page = Page(
            "p",
            layers=[Layer("fill", children=[Story360("img.jpg")])],
        )
        story = _make_story(pages=[page])
        assert "amp-story-360-0.1.js" in story.render()

    def test_shopping_script_injected(self) -> None:
        from amp_stories.shopping import ShoppingTag, StoryShopping
        shopping = StoryShopping(tags=[
            ShoppingTag("p1", "Widget", "Acme", 9.99, "USD", ["img.jpg"]),
        ])
        story = _make_story(shopping=shopping)
        assert "amp-story-shopping-0.1.js" in story.render()

    def test_consent_script_injected(self) -> None:
        from amp_stories.consent import AmpConsent
        consent = AmpConsent(consents={"c": {"checkConsentHref": "/check"}})
        story = _make_story(consent=consent)
        assert "amp-consent-0.1.js" in story.render()

    def test_shopping_rendered_in_body(self) -> None:
        from amp_stories.shopping import ShoppingTag, StoryShopping
        shopping = StoryShopping(tags=[
            ShoppingTag("p1", "Widget", "Acme", 9.99, "USD", ["img.jpg"]),
        ])
        story = _make_story(shopping=shopping)
        assert "amp-story-shopping" in story.render()

    def test_consent_rendered_in_body(self) -> None:
        from amp_stories.consent import AmpConsent
        consent = AmpConsent(consents={"c": {}})
        story = _make_story(consent=consent)
        assert "amp-consent" in story.render()


class TestInteractiveScriptInjection:
    def test_interactive_script_injected_for_binary_poll(self) -> None:
        from amp_stories.interactive import InteractiveBinaryPoll
        page = Page(
            "p",
            layers=[
                Layer("fill", children=[AmpImg("img.jpg", alt="")]),
                Layer("vertical", children=[InteractiveBinaryPoll("Yes", "No")]),
            ],
        )
        story = _make_story(pages=[page])
        assert "amp-story-interactive-0.1.js" in story.render()

    def test_interactive_script_injected_for_poll(self) -> None:
        from amp_stories.interactive import InteractiveOption, InteractivePoll
        page = Page(
            "p",
            layers=[
                Layer("fill", children=[AmpImg("img.jpg", alt="")]),
                Layer("vertical", children=[
                    InteractivePoll([InteractiveOption("A"), InteractiveOption("B")]),
                ]),
            ],
        )
        story = _make_story(pages=[page])
        assert "amp-story-interactive-0.1.js" in story.render()

    def test_interactive_script_not_injected_without_interactive(self) -> None:
        story = _make_story()
        assert "amp-story-interactive" not in story.render()


class TestStoryReprHtml:
    def test_returns_iframe(self, minimal_story: Story) -> None:
        html = minimal_story._repr_html_()
        assert "<iframe" in html
        assert "</iframe>" in html

    def test_contains_srcdoc(self, minimal_story: Story) -> None:
        html = minimal_story._repr_html_()
        assert "srcdoc=" in html

    def test_contains_story_content(self, minimal_story: Story) -> None:
        html = minimal_story._repr_html_()
        # The rendered story HTML should be embedded (escaped) in the srcdoc
        assert "amp-story" in html

    def test_dimensions_present(self, minimal_story: Story) -> None:
        html = minimal_story._repr_html_()
        assert "360" in html
        assert "640" in html


class TestStorySerialize:
    def test_to_dict_returns_dict(self, minimal_story: Story) -> None:
        assert isinstance(minimal_story.to_dict(), dict)

    def test_to_dict_type_key(self, minimal_story: Story) -> None:
        assert minimal_story.to_dict()["__type__"] == "Story"

    def test_from_dict_roundtrip(self, minimal_story: Story) -> None:
        story2 = Story.from_dict(minimal_story.to_dict())
        assert story2.render() == minimal_story.render()

    def test_from_dict_wrong_type_raises(self, minimal_story: Story) -> None:
        data = minimal_story.to_dict()
        data["__type__"] = "Page"
        with pytest.raises(ValueError, match="Story"):
            Story.from_dict(data)

    def test_from_dict_preserves_title(self) -> None:
        story = _make_story(title="Round-trip Title")
        story2 = Story.from_dict(story.to_dict())
        assert story2.title == "Round-trip Title"


class TestStoryValidateWarnings:
    def test_landscape_no_poster_warns(self) -> None:
        story = _make_story(supports_landscape=True)
        with pytest.warns(AmpStoriesWarning, match="poster_landscape_src"):
            story.validate()

    def test_landscape_with_poster_no_warn(self) -> None:
        import warnings
        story = _make_story(
            supports_landscape=True,
            poster_landscape_src="https://example.com/landscape.jpg",
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            story.validate()
        landscape_warnings = [
            w for w in caught
            if issubclass(w.category, AmpStoriesWarning)
            and "poster_landscape_src" in str(w.message)
        ]
        assert landscape_warnings == []

    def test_landscape_false_no_poster_warn(self) -> None:
        import warnings
        story = _make_story(supports_landscape=False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            story.validate()
        landscape_warnings = [
            w for w in caught
            if issubclass(w.category, AmpStoriesWarning)
            and "poster_landscape_src" in str(w.message)
        ]
        assert landscape_warnings == []

    def test_css_over_75kb_warns(self) -> None:
        big_css = "a" * 75_001
        story = _make_story(custom_css=big_css)
        with pytest.warns(AmpStoriesWarning, match="KB"):
            story.validate()

    def test_css_exactly_75000_bytes_no_warn(self) -> None:
        import warnings
        exact_css = "a" * 75_000
        story = _make_story(custom_css=exact_css)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            story.validate()
        size_warnings = [
            w for w in caught
            if issubclass(w.category, AmpStoriesWarning) and "KB" in str(w.message)
        ]
        assert size_warnings == []

    def test_custom_css_none_no_warn(self) -> None:
        import warnings
        story = _make_story(custom_css=None)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            story.validate()
        size_warnings = [
            w for w in caught
            if issubclass(w.category, AmpStoriesWarning) and "KB" in str(w.message)
        ]
        assert size_warnings == []

    def test_outlink_on_non_last_page_warns(self) -> None:
        from amp_stories.outlink import PageOutlink
        p1 = Page(
            "p1",
            layers=[Layer("fill", children=[AmpImg("img.jpg", alt="")])],
            outlink=PageOutlink(href="https://example.com"),
        )
        p2 = _make_page("p2")
        story = _make_story(pages=[p1, p2])
        with pytest.warns(AmpStoriesWarning, match="p1"):
            story.validate()

    def test_outlink_on_last_page_no_warn(self) -> None:
        import warnings  # noqa: PLC0415

        from amp_stories.outlink import PageOutlink
        p1 = _make_page("p1")
        p2 = Page(
            "p2",
            layers=[Layer("fill", children=[AmpImg("img.jpg", alt="")])],
            outlink=PageOutlink(href="https://example.com"),
        )
        story = _make_story(pages=[p1, p2])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            story.validate()
        outlink_warnings = [
            w for w in caught
            if issubclass(w.category, AmpStoriesWarning) and "PageOutlink" in str(w.message)
        ]
        assert outlink_warnings == []


class TestFontLinks:
    def test_default_font_links_empty(self) -> None:
        story = _make_story()
        assert story.font_links == []

    def test_single_font_link_in_html(self) -> None:
        url = "https://fonts.googleapis.com/css2?family=Roboto"
        story = _make_story(font_links=[url])
        rendered = story.render()
        assert url in rendered
        assert 'rel="stylesheet"' in rendered

    def test_multiple_font_links_all_present(self) -> None:
        urls = [
            "https://fonts.googleapis.com/css2?family=Roboto",
            "https://fonts.googleapis.com/css2?family=Montserrat",
        ]
        story = _make_story(font_links=urls)
        rendered = story.render()
        for url in urls:
            assert url in rendered

    def test_font_link_is_link_tag(self) -> None:
        url = "https://fonts.googleapis.com/css2?family=Roboto&display=swap"
        story = _make_story(font_links=[url])
        rendered = story.render()
        assert "<link" in rendered

    def test_serde_round_trip(self) -> None:
        url = "https://fonts.googleapis.com/css2?family=Roboto"
        story = _make_story(font_links=[url])
        story2 = Story.from_dict(story.to_dict())
        assert story2.font_links == [url]


class TestGenerateStructuredData:
    def test_returns_dict(self) -> None:
        story = _make_story()
        result = story.generate_structured_data()
        assert isinstance(result, dict)

    def test_context_field(self) -> None:
        story = _make_story()
        result = story.generate_structured_data()
        assert result["@context"] == "https://schema.org"

    def test_type_field(self) -> None:
        story = _make_story()
        result = story.generate_structured_data()
        assert result["@type"] == "WebStory"

    def test_headline_field(self) -> None:
        story = _make_story(title="My Great Story")
        result = story.generate_structured_data()
        assert result["headline"] == "My Great Story"

    def test_url_field(self) -> None:
        story = _make_story(canonical_url="https://example.com/story.html")
        result = story.generate_structured_data()
        assert result["url"] == "https://example.com/story.html"

    def test_publisher_name(self) -> None:
        story = _make_story(publisher="My Publisher")
        result = story.generate_structured_data()
        assert result["publisher"]["name"] == "My Publisher"

    def test_publisher_logo(self) -> None:
        story = _make_story(publisher_logo_src="https://example.com/logo.png")
        result = story.generate_structured_data()
        assert result["publisher"]["logo"]["url"] == "https://example.com/logo.png"

    def test_image_field(self) -> None:
        story = _make_story(poster_portrait_src="https://example.com/poster.jpg")
        result = story.generate_structured_data()
        assert result["image"]["url"] == "https://example.com/poster.jpg"

    def test_assign_and_render_emits_json_ld(self) -> None:
        story = _make_story()
        story.structured_data = story.generate_structured_data()
        rendered = story.render()
        assert "application/ld+json" in rendered
        assert "WebStory" in rendered


class TestStorySave:
    def test_save_writes_file(self, minimal_story: Story, tmp_path: pathlib.Path) -> None:
        output = tmp_path / "story.html"
        minimal_story.save(output)
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "<!doctype html>" in content

    def test_save_accepts_string_path(
        self, minimal_story: Story, tmp_path: pathlib.Path
    ) -> None:
        output = str(tmp_path / "story.html")
        minimal_story.save(output)
        assert pathlib.Path(output).exists()

    def test_saved_content_matches_render(
        self, minimal_story: Story, tmp_path: pathlib.Path
    ) -> None:
        output = tmp_path / "story.html"
        minimal_story.save(output)
        assert output.read_text(encoding="utf-8") == minimal_story.render()

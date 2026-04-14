"""Tests for amp_stories/templates.py."""

from __future__ import annotations

import warnings

import pytest

from amp_stories._validation import AmpStoriesWarning, ValidationError
from amp_stories.elements import AmpImg, AmpVideo, DivElement, TextElement
from amp_stories.layer import Layer
from amp_stories.outlink import PageOutlink
from amp_stories.page import Page
from amp_stories.story import Story
from amp_stories.templates import (
    ChartRow,
    _background_layers,
    breaking_page,
    chapter_page,
    comparison_page,
    cta_page,
    data_chart_page,
    deal_page,
    itinerary_page,
    listicle_page,
    photo_page,
    product_page,
    quote_page,
    stat_page,
    text_page,
    title_page,
    trip_page,
    update_page,
    video_page,
)
from amp_stories.themes import SLATE_THEME, Theme

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _renderable_story(pages: list[Page]) -> Story:
    """Wrap pages in a minimal Story that suppresses page-count warnings."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", AmpStoriesWarning)
        return Story(
            title="Test",
            publisher="Test",
            publisher_logo_src="https://example.com/logo.png",
            poster_portrait_src="https://example.com/poster.jpg",
            canonical_url="https://example.com/story.html",
            custom_css=SLATE_THEME.generate_css(),
            pages=pages,
        )


# ---------------------------------------------------------------------------
# _background_layers helper
# ---------------------------------------------------------------------------

class TestBackgroundLayers:
    def test_no_image_returns_one_layer(self) -> None:
        layers = _background_layers(None, SLATE_THEME)
        assert len(layers) == 1

    def test_no_image_fill_layer(self) -> None:
        layers = _background_layers(None, SLATE_THEME)
        assert layers[0].template == "fill"

    def test_no_image_div_child(self) -> None:
        layers = _background_layers(None, SLATE_THEME)
        assert isinstance(layers[0].children[0], DivElement)

    def test_no_image_div_has_ast_bg_class(self) -> None:
        layers = _background_layers(None, SLATE_THEME)
        assert layers[0].children[0].class_ == "ast-bg"  # type: ignore[union-attr]

    def test_with_image_returns_two_layers(self) -> None:
        layers = _background_layers("img.jpg", SLATE_THEME)
        assert len(layers) == 2

    def test_with_image_first_layer_fill(self) -> None:
        layers = _background_layers("img.jpg", SLATE_THEME)
        assert layers[0].template == "fill"

    def test_with_image_first_layer_has_ampimg(self) -> None:
        layers = _background_layers("img.jpg", SLATE_THEME)
        assert isinstance(layers[0].children[0], AmpImg)

    def test_with_image_second_layer_is_overlay(self) -> None:
        layers = _background_layers("img.jpg", SLATE_THEME)
        assert isinstance(layers[1].children[0], DivElement)
        assert layers[1].children[0].class_ == "ast-overlay"  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# title_page
# ---------------------------------------------------------------------------

class TestTitlePage:
    def test_returns_page(self) -> None:
        p = title_page("cover", "Hello World")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = title_page("my-cover", "Title")
        assert p.page_id == "my-cover"

    def test_minimal_no_image_has_two_layers(self) -> None:
        p = title_page("p", "Title")
        assert len(p.layers) == 2  # bg + text

    def test_minimal_no_image_first_layer_fill(self) -> None:
        p = title_page("p", "Title")
        assert p.layers[0].template == "fill"

    def test_minimal_no_image_text_layer_vertical(self) -> None:
        p = title_page("p", "Title")
        assert p.layers[-1].template == "vertical"

    def test_with_image_has_three_layers(self) -> None:
        p = title_page("p", "Title", background_src="img.jpg")
        assert len(p.layers) == 3  # fill + overlay + text

    def test_with_image_overlay_present(self) -> None:
        p = title_page("p", "Title", background_src="img.jpg")
        overlay_div = p.layers[1].children[0]
        assert isinstance(overlay_div, DivElement)
        assert overlay_div.class_ == "ast-overlay"

    def test_title_element_present(self) -> None:
        p = title_page("p", "My Title")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-title"]
        assert len(titles) == 1
        assert titles[0].text == "My Title"

    def test_title_is_h1(self) -> None:
        p = title_page("p", "Title")
        text_layer = p.layers[-1]
        h1s = [c for c in text_layer.children
               if isinstance(c, TextElement) and c.tag == "h1"]
        assert len(h1s) == 1

    def test_no_subtitle_by_default(self) -> None:
        p = title_page("p", "Title")
        text_layer = p.layers[-1]
        subtitles = [c for c in text_layer.children
                     if isinstance(c, TextElement) and c.class_ == "ast-subtitle"]
        assert len(subtitles) == 0

    def test_subtitle_added_when_provided(self) -> None:
        p = title_page("p", "Title", subtitle="Sub")
        text_layer = p.layers[-1]
        subtitles = [c for c in text_layer.children
                     if isinstance(c, TextElement) and c.class_ == "ast-subtitle"]
        assert len(subtitles) == 1
        assert subtitles[0].text == "Sub"

    def test_eyebrow_added_when_provided(self) -> None:
        p = title_page("p", "Title", eyebrow="Category")
        text_layer = p.layers[-1]
        eyebrows = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-eyebrow"]
        assert len(eyebrows) == 1
        assert eyebrows[0].text == "Category"

    def test_eyebrow_is_first_in_text_layer(self) -> None:
        p = title_page("p", "Title", eyebrow="Cat")
        text_layer = p.layers[-1]
        assert isinstance(text_layer.children[0], TextElement)
        assert text_layer.children[0].class_ == "ast-eyebrow"

    def test_title_has_heading_animate_in(self) -> None:
        p = title_page("p", "Title")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in == SLATE_THEME.heading_animate_in

    def test_subtitle_has_body_animate_in(self) -> None:
        p = title_page("p", "Title", subtitle="Sub")
        text_layer = p.layers[-1]
        sub = next(c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-subtitle")
        assert sub.animate_in == SLATE_THEME.body_animate_in

    def test_auto_advance_after(self) -> None:
        p = title_page("p", "Title", auto_advance_after="5s")
        assert p.auto_advance_after == "5s"

    def test_custom_theme_respected(self) -> None:
        theme = Theme(heading_animate_in="fade-in", body_animate_in="fly-in-top",
                      bg_color="#000000", text_color="#ffffff",
                      accent_color="#ff0000", muted_color="#888888")
        p = title_page("p", "Title", theme=theme)
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in == "fade-in"

    def test_title_no_animation_when_none(self) -> None:
        theme = Theme(heading_animate_in=None, body_animate_in=None,
                      bg_color="#000000", text_color="#ffffff",
                      accent_color="#ff0000", muted_color="#888888")
        p = title_page("p", "Title", theme=theme)
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in is None

    def test_title_with_eyebrow_has_delay_on_title(self) -> None:
        p = title_page("p", "Title", eyebrow="Cat")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_title_without_eyebrow_has_no_delay(self) -> None:
        p = title_page("p", "Title")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in_delay is None

    def test_renderable(self) -> None:
        p = title_page("p1", "My Story", subtitle="A tale", background_src="img.jpg")
        story = _renderable_story([p])
        html = story.render()
        assert "My Story" in html
        assert "A tale" in html


# ---------------------------------------------------------------------------
# quote_page
# ---------------------------------------------------------------------------

class TestQuotePage:
    def test_returns_page(self) -> None:
        p = quote_page("q", "To be or not to be.")
        assert isinstance(p, Page)

    def test_no_image_two_layers(self) -> None:
        p = quote_page("q", "Quote text")
        assert len(p.layers) == 2

    def test_with_image_three_layers(self) -> None:
        p = quote_page("q", "Quote text", background_src="img.jpg")
        assert len(p.layers) == 3

    def test_quote_mark_present(self) -> None:
        p = quote_page("q", "Quote")
        text_layer = p.layers[-1]
        marks = [c for c in text_layer.children
                 if isinstance(c, TextElement) and c.class_ == "ast-quote-mark"]
        assert len(marks) == 1

    def test_quote_text_present(self) -> None:
        p = quote_page("q", "To be or not to be.")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 1
        assert bodies[0].text == "To be or not to be."

    def test_quote_uses_blockquote_tag(self) -> None:
        p = quote_page("q", "Quote")
        text_layer = p.layers[-1]
        blockquotes = [c for c in text_layer.children
                       if isinstance(c, TextElement) and c.tag == "blockquote"]
        assert len(blockquotes) == 1

    def test_no_attribution_by_default(self) -> None:
        p = quote_page("q", "Quote")
        text_layer = p.layers[-1]
        attribs = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-attribution"]
        assert len(attribs) == 0

    def test_attribution_added_when_provided(self) -> None:
        p = quote_page("q", "Quote", attribution="— Author")
        text_layer = p.layers[-1]
        attribs = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-attribution"]
        assert len(attribs) == 1
        assert attribs[0].text == "— Author"

    def test_renderable(self) -> None:
        p = quote_page("q1", "Be the change.", attribution="— Gandhi")
        story = _renderable_story([p])
        html = story.render()
        assert "Be the change." in html
        assert "Gandhi" in html


# ---------------------------------------------------------------------------
# stat_page
# ---------------------------------------------------------------------------

class TestStatPage:
    def test_returns_page(self) -> None:
        p = stat_page("s", "92%", "success rate")
        assert isinstance(p, Page)

    def test_no_image_two_layers(self) -> None:
        p = stat_page("s", "92%", "success")
        assert len(p.layers) == 2

    def test_with_image_three_layers(self) -> None:
        p = stat_page("s", "92%", "success", background_src="img.jpg")
        assert len(p.layers) == 3

    def test_stat_number_present(self) -> None:
        p = stat_page("s", "1.4B", "users")
        text_layer = p.layers[-1]
        numbers = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-stat-number"]
        assert len(numbers) == 1
        assert numbers[0].text == "1.4B"

    def test_stat_label_present(self) -> None:
        p = stat_page("s", "1.4B", "active users worldwide")
        text_layer = p.layers[-1]
        labels = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-stat-label"]
        assert len(labels) == 1
        assert labels[0].text == "active users worldwide"

    def test_no_context_by_default(self) -> None:
        p = stat_page("s", "42%", "label")
        text_layer = p.layers[-1]
        contexts = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(contexts) == 0

    def test_context_added_when_provided(self) -> None:
        p = stat_page("s", "42%", "label", context="As of Q4 2024")
        text_layer = p.layers[-1]
        contexts = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(contexts) == 1
        assert contexts[0].text == "As of Q4 2024"

    def test_renderable(self) -> None:
        p = stat_page("s1", "92%", "of users agree")
        story = _renderable_story([p])
        html = story.render()
        assert "92%" in html


# ---------------------------------------------------------------------------
# chapter_page
# ---------------------------------------------------------------------------

class TestChapterPage:
    def test_returns_page(self) -> None:
        p = chapter_page("ch", "Introduction")
        assert isinstance(p, Page)

    def test_no_image_two_layers(self) -> None:
        p = chapter_page("ch", "Introduction")
        assert len(p.layers) == 2

    def test_with_image_three_layers(self) -> None:
        p = chapter_page("ch", "Introduction", background_src="img.jpg")
        assert len(p.layers) == 3

    def test_chapter_title_present(self) -> None:
        p = chapter_page("ch", "The Beginning")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-chapter-title"]
        assert len(titles) == 1
        assert titles[0].text == "The Beginning"

    def test_chapter_title_is_h1(self) -> None:
        p = chapter_page("ch", "Chapter Title")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-chapter-title"]
        assert titles[0].tag == "h1"

    def test_no_chapter_number_by_default(self) -> None:
        p = chapter_page("ch", "Title")
        text_layer = p.layers[-1]
        numbers = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-chapter-number"]
        assert len(numbers) == 0

    def test_integer_chapter_number_formatted(self) -> None:
        p = chapter_page("ch", "Title", chapter_number=3)
        text_layer = p.layers[-1]
        numbers = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-chapter-number"]
        assert len(numbers) == 1
        assert numbers[0].text == "Part 3"

    def test_string_chapter_number_used_as_is(self) -> None:
        p = chapter_page("ch", "Title", chapter_number="Part I")
        text_layer = p.layers[-1]
        numbers = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-chapter-number"]
        assert numbers[0].text == "Part I"

    def test_chapter_number_is_first_element(self) -> None:
        p = chapter_page("ch", "Title", chapter_number=1)
        text_layer = p.layers[-1]
        assert isinstance(text_layer.children[0], TextElement)
        assert text_layer.children[0].class_ == "ast-chapter-number"

    def test_title_has_delay_when_chapter_number_present(self) -> None:
        p = chapter_page("ch", "Title", chapter_number=1)
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-chapter-title")
        assert title_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_title_has_no_delay_without_chapter_number(self) -> None:
        p = chapter_page("ch", "Title")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-chapter-title")
        assert title_el.animate_in_delay is None

    def test_renderable(self) -> None:
        p = chapter_page("ch1", "The Beginning", chapter_number=1)
        story = _renderable_story([p])
        html = story.render()
        assert "The Beginning" in html
        assert "Part 1" in html


# ---------------------------------------------------------------------------
# photo_page
# ---------------------------------------------------------------------------

class TestPhotoPage:
    def test_returns_page(self) -> None:
        p = photo_page("ph", "photo.jpg")
        assert isinstance(p, Page)

    def test_one_layer_when_no_caption_no_eyebrow(self) -> None:
        p = photo_page("ph", "photo.jpg")
        assert len(p.layers) == 1

    def test_fill_layer_has_ampimg(self) -> None:
        p = photo_page("ph", "photo.jpg")
        assert isinstance(p.layers[0].children[0], AmpImg)

    def test_ampimg_src(self) -> None:
        p = photo_page("ph", "photo.jpg")
        assert p.layers[0].children[0].src == "photo.jpg"  # type: ignore[union-attr]

    def test_no_overlay(self) -> None:
        p = photo_page("ph", "photo.jpg", caption="Caption")
        # No fill layer with overlay div — second layer is vertical text layer
        assert p.layers[1].template == "vertical"

    def test_two_layers_with_caption(self) -> None:
        p = photo_page("ph", "photo.jpg", caption="A nice photo")
        assert len(p.layers) == 2

    def test_caption_present(self) -> None:
        p = photo_page("ph", "photo.jpg", caption="A nice photo")
        text_layer = p.layers[-1]
        captions = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-caption"]
        assert len(captions) == 1
        assert captions[0].text == "A nice photo"

    def test_eyebrow_present(self) -> None:
        p = photo_page("ph", "photo.jpg", eyebrow="Nature")
        text_layer = p.layers[-1]
        eyebrows = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-eyebrow"]
        assert len(eyebrows) == 1
        assert eyebrows[0].text == "Nature"

    def test_eyebrow_before_caption(self) -> None:
        p = photo_page("ph", "photo.jpg", eyebrow="Cat", caption="Caption")
        text_layer = p.layers[-1]
        assert text_layer.children[0].class_ == "ast-eyebrow"  # type: ignore[union-attr]
        assert text_layer.children[1].class_ == "ast-caption"  # type: ignore[union-attr]

    def test_two_layers_with_eyebrow_only(self) -> None:
        p = photo_page("ph", "photo.jpg", eyebrow="Cat")
        assert len(p.layers) == 2

    def test_renderable(self) -> None:
        p = photo_page("ph1", "photo.jpg", caption="Beautiful sunset")
        story = _renderable_story([p])
        html = story.render()
        assert "Beautiful sunset" in html


# ---------------------------------------------------------------------------
# text_page
# ---------------------------------------------------------------------------

class TestTextPage:
    def test_returns_page(self) -> None:
        p = text_page("t", "Heading", "Body text here.")
        assert isinstance(p, Page)

    def test_no_image_two_layers(self) -> None:
        p = text_page("t", "Heading", "Body")
        assert len(p.layers) == 2

    def test_with_image_three_layers(self) -> None:
        p = text_page("t", "Heading", "Body", background_src="img.jpg")
        assert len(p.layers) == 3

    def test_heading_present(self) -> None:
        p = text_page("t", "My Heading", "Body text")
        text_layer = p.layers[-1]
        headings = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-subtitle"]
        assert len(headings) == 1
        assert headings[0].text == "My Heading"

    def test_heading_is_h2(self) -> None:
        p = text_page("t", "Heading", "Body")
        text_layer = p.layers[-1]
        h2s = [c for c in text_layer.children
               if isinstance(c, TextElement) and c.tag == "h2"]
        assert len(h2s) == 1

    def test_body_present(self) -> None:
        p = text_page("t", "Heading", "The body text.")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 1
        assert bodies[0].text == "The body text."

    def test_body_has_animate_in_delay(self) -> None:
        p = text_page("t", "Heading", "Body")
        text_layer = p.layers[-1]
        body_el = next(c for c in text_layer.children
                       if isinstance(c, TextElement) and c.class_ == "ast-body")
        assert body_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_renderable(self) -> None:
        p = text_page("t1", "Key Facts", "Here is what you need to know.")
        story = _renderable_story([p])
        html = story.render()
        assert "Key Facts" in html
        assert "Here is what you need to know." in html


# ---------------------------------------------------------------------------
# trip_page
# ---------------------------------------------------------------------------

class TestTripPage:
    def test_returns_page(self) -> None:
        p = trip_page("t1", 1, "Patagonia")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = trip_page("trip-1", 1, "Patagonia")
        assert p.page_id == "trip-1"

    def test_no_image_two_layers(self) -> None:
        p = trip_page("t1", 1, "Patagonia")
        assert len(p.layers) == 2

    def test_with_image_three_layers(self) -> None:
        p = trip_page("t1", 1, "Patagonia", background_src="img.jpg")
        assert len(p.layers) == 3

    def test_eyebrow_formatted_as_trip_number(self) -> None:
        p = trip_page("t1", 3, "Patagonia")
        text_layer = p.layers[-1]
        eyebrows = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-eyebrow"]
        assert len(eyebrows) == 1
        assert eyebrows[0].text == "TRIP 03"

    def test_single_digit_number_zero_padded(self) -> None:
        p = trip_page("t1", 1, "Patagonia")
        text_layer = p.layers[-1]
        eyebrow = next(c for c in text_layer.children
                       if isinstance(c, TextElement) and c.class_ == "ast-eyebrow")
        assert eyebrow.text == "TRIP 01"

    def test_double_digit_number(self) -> None:
        p = trip_page("t1", 10, "Patagonia")
        text_layer = p.layers[-1]
        eyebrow = next(c for c in text_layer.children
                       if isinstance(c, TextElement) and c.class_ == "ast-eyebrow")
        assert eyebrow.text == "TRIP 10"

    def test_location_present_as_h1(self) -> None:
        p = trip_page("t1", 1, "Big Sur")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-title"]
        assert len(titles) == 1
        assert titles[0].text == "Big Sur"
        assert titles[0].tag == "h1"

    def test_location_has_delay(self) -> None:
        p = trip_page("t1", 1, "Big Sur")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_no_region_by_default(self) -> None:
        p = trip_page("t1", 1, "Patagonia")
        text_layer = p.layers[-1]
        subtitles = [c for c in text_layer.children
                     if isinstance(c, TextElement) and c.class_ == "ast-subtitle"]
        assert len(subtitles) == 0

    def test_region_added_when_provided(self) -> None:
        p = trip_page("t1", 1, "Patagonia", region="Chile")
        text_layer = p.layers[-1]
        subtitles = [c for c in text_layer.children
                     if isinstance(c, TextElement) and c.class_ == "ast-subtitle"]
        assert len(subtitles) == 1
        assert subtitles[0].text == "Chile"

    def test_no_highlight_by_default(self) -> None:
        p = trip_page("t1", 1, "Patagonia")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 0

    def test_highlight_added_when_provided(self) -> None:
        p = trip_page("t1", 1, "Patagonia", highlight="Stunning glaciers")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 1
        assert bodies[0].text == "Stunning glaciers"

    def test_all_optional_fields(self) -> None:
        p = trip_page("t1", 5, "Yosemite", region="California",
                      highlight="Half Dome sunrise", background_src="img.jpg")
        assert len(p.layers) == 3
        text_layer = p.layers[-1]
        classes = [c.class_ for c in text_layer.children if isinstance(c, TextElement)]
        assert "ast-eyebrow" in classes
        assert "ast-title" in classes
        assert "ast-subtitle" in classes
        assert "ast-body" in classes

    def test_auto_advance_after(self) -> None:
        p = trip_page("t1", 1, "Patagonia", auto_advance_after="8s")
        assert p.auto_advance_after == "8s"

    def test_custom_theme_respected(self) -> None:
        theme = Theme(heading_animate_in="fade-in", body_animate_in="fly-in-top",
                      bg_color="#000000", text_color="#ffffff",
                      accent_color="#ff0000", muted_color="#888888")
        p = trip_page("t1", 1, "Patagonia", theme=theme)
        text_layer = p.layers[-1]
        eyebrow = next(c for c in text_layer.children
                       if isinstance(c, TextElement) and c.class_ == "ast-eyebrow")
        assert eyebrow.animate_in == "fade-in"

    def test_renderable(self) -> None:
        p = trip_page("t1", 1, "Big Sur", region="California",
                      highlight="First solo trip", background_src="img.jpg")
        story = _renderable_story([p])
        html = story.render()
        assert "TRIP 01" in html
        assert "Big Sur" in html
        assert "California" in html


# ---------------------------------------------------------------------------
# cta_page
# ---------------------------------------------------------------------------

class TestCtaPage:
    def test_returns_page(self) -> None:
        p = cta_page("cta", "Read more", cta_url="https://example.com")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = cta_page("my-cta", "Explore", cta_url="https://example.com")
        assert p.page_id == "my-cta"

    def test_no_image_two_layers(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com")
        assert len(p.layers) == 2

    def test_with_image_three_layers(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com",
                     background_src="img.jpg")
        assert len(p.layers) == 3

    def test_heading_present_as_h1(self) -> None:
        p = cta_page("cta", "Discover more", cta_url="https://example.com")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-title"]
        assert len(titles) == 1
        assert titles[0].text == "Discover more"
        assert titles[0].tag == "h1"

    def test_no_body_by_default(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 0

    def test_body_added_when_provided(self) -> None:
        p = cta_page("cta", "Heading", body="Some details here.",
                     cta_url="https://example.com")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 1
        assert bodies[0].text == "Some details here."

    def test_body_has_animate_in_delay(self) -> None:
        p = cta_page("cta", "Heading", body="Body text.",
                     cta_url="https://example.com")
        text_layer = p.layers[-1]
        body_el = next(c for c in text_layer.children
                       if isinstance(c, TextElement) and c.class_ == "ast-body")
        assert body_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_outlink_attached(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com")
        assert p.outlink is not None
        assert isinstance(p.outlink, PageOutlink)

    def test_outlink_href(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com/story")
        assert p.outlink is not None
        assert p.outlink.href == "https://example.com/story"

    def test_outlink_default_cta_text(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com")
        assert p.outlink is not None
        assert p.outlink.cta_text == "Read more"

    def test_outlink_custom_cta_text(self) -> None:
        p = cta_page("cta", "Heading", cta_text="Visit site",
                     cta_url="https://example.com")
        assert p.outlink is not None
        assert p.outlink.cta_text == "Visit site"

    def test_outlink_uses_theme_accent_color(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com")
        assert p.outlink is not None
        assert p.outlink.cta_accent_color == SLATE_THEME.accent_color

    def test_outlink_custom_theme_accent(self) -> None:
        theme = Theme(bg_color="#000000", text_color="#ffffff",
                      accent_color="#ff6600", muted_color="#aaaaaa")
        p = cta_page("cta", "Heading", cta_url="https://example.com", theme=theme)
        assert p.outlink is not None
        assert p.outlink.cta_accent_color == "#ff6600"

    def test_outlink_theme_custom(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com")
        assert p.outlink is not None
        assert p.outlink.theme == "custom"

    def test_outlink_accent_element_background(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com")
        assert p.outlink is not None
        assert p.outlink.cta_accent_element == "background"

    def test_auto_advance_after(self) -> None:
        p = cta_page("cta", "Heading", cta_url="https://example.com",
                     auto_advance_after="10s")
        assert p.auto_advance_after == "10s"

    def test_renderable(self) -> None:
        p = cta_page("cta", "Want more?",
                     body="Check out the full story.",
                     cta_text="Read it",
                     cta_url="https://example.com/story",
                     background_src="img.jpg")
        story = _renderable_story([p])
        html = story.render()
        assert "Want more?" in html
        assert "Check out the full story." in html
        assert "Read it" in html


# ---------------------------------------------------------------------------
# Integration — multi-page story with theme CSS
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_themed_story_renders(self) -> None:
        pages = [
            title_page("p1", "Story Title", subtitle="Subtitle",
                       background_src="hero.jpg"),
            quote_page("p2", "A great quote.", attribution="— Source"),
            stat_page("p3", "99%", "uptime", context="2024 average"),
            chapter_page("p4", "The Beginning", chapter_number=1),
            photo_page("p5", "photo.jpg", caption="A caption"),
            text_page("p6", "More Info", "Body text here."),
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", AmpStoriesWarning)
            story = Story(
                title="Themed Story",
                publisher="Test",
                publisher_logo_src="https://example.com/logo.png",
                poster_portrait_src="https://example.com/poster.jpg",
                canonical_url="https://example.com/story.html",
                custom_css=SLATE_THEME.generate_css(),
                pages=pages,
            )
        html = story.render()
        assert "Story Title" in html
        assert "ast-title" in html
        assert "ast-overlay" in html
        assert ".ast-bg" in html  # from generate_css()

    def test_custom_theme_in_integration(self) -> None:
        theme = Theme(
            bg_color="#000000",
            text_color="#ffffff",
            accent_color="#ff6600",
            muted_color="#aaaaaa",
        )
        pages = [
            title_page("p1", "Dark Story", theme=theme),
            quote_page("p2", "Quote here.", theme=theme),
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", AmpStoriesWarning)
            story = Story(
                title="Dark Story",
                publisher="Test",
                publisher_logo_src="https://example.com/logo.png",
                poster_portrait_src="https://example.com/poster.jpg",
                canonical_url="https://example.com/story.html",
                custom_css=theme.generate_css(),
                pages=pages,
            )
        html = story.render()
        assert "#000000" in html  # bg_color in CSS
        assert "Dark Story" in html


# ---------------------------------------------------------------------------
# video_page
# ---------------------------------------------------------------------------

class TestVideoPage:
    def test_returns_page(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = video_page("my-video", "https://example.com/v.mp4")
        assert p.page_id == "my-video"

    def test_single_fill_layer_no_text(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4")
        assert len(p.layers) == 1
        assert p.layers[0].template == "fill"

    def test_fill_layer_contains_amp_video(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4")
        assert isinstance(p.layers[0].children[0], AmpVideo)

    def test_video_src_forwarded(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4")
        video = p.layers[0].children[0]
        assert isinstance(video, AmpVideo)
        assert video.src == "https://example.com/v.mp4"

    def test_default_autoplay_true(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4")
        video = p.layers[0].children[0]
        assert isinstance(video, AmpVideo)
        assert video.autoplay is True

    def test_default_loop_true(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4")
        video = p.layers[0].children[0]
        assert isinstance(video, AmpVideo)
        assert video.loop is True

    def test_default_muted_true(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4")
        video = p.layers[0].children[0]
        assert isinstance(video, AmpVideo)
        assert video.muted is True

    def test_poster_forwarded(self) -> None:
        p = video_page(
            "v1", "https://example.com/v.mp4",
            poster="https://example.com/poster.jpg",
        )
        video = p.layers[0].children[0]
        assert isinstance(video, AmpVideo)
        assert video.poster == "https://example.com/poster.jpg"

    def test_no_poster_is_none(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4")
        video = p.layers[0].children[0]
        assert isinstance(video, AmpVideo)
        assert video.poster is None

    def test_caption_adds_text_layer(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4", caption="A great clip")
        assert len(p.layers) == 2
        assert p.layers[1].template == "vertical"

    def test_eyebrow_adds_text_layer(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4", eyebrow="BREAKING")
        assert len(p.layers) == 2

    def test_caption_element_present(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4", caption="Nice shot")
        text_layer = p.layers[1]
        captions = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-caption"]
        assert len(captions) == 1
        assert captions[0].text == "Nice shot"

    def test_eyebrow_element_present(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4", eyebrow="WATCH")
        text_layer = p.layers[1]
        eyebrows = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-eyebrow"]
        assert len(eyebrows) == 1
        assert eyebrows[0].text == "WATCH"

    def test_eyebrow_before_caption_same_layer(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4",
                       eyebrow="CAT", caption="A caption")
        assert len(p.layers) == 2
        text_layer = p.layers[1]
        assert text_layer.children[0].class_ == "ast-eyebrow"  # type: ignore[union-attr]
        assert text_layer.children[1].class_ == "ast-caption"  # type: ignore[union-attr]

    def test_autoplay_false_forwarded(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4", autoplay=False)
        video = p.layers[0].children[0]
        assert isinstance(video, AmpVideo)
        assert video.autoplay is False

    def test_loop_false_forwarded(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4", loop=False)
        video = p.layers[0].children[0]
        assert isinstance(video, AmpVideo)
        assert video.loop is False

    def test_auto_advance_after_forwarded(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4", auto_advance_after="10s")
        assert p.auto_advance_after == "10s"

    def test_custom_theme_caption_animation(self) -> None:
        theme = Theme(
            heading_animate_in="fade-in",
            body_animate_in="fly-in-top",
            bg_color="#000000",
            text_color="#ffffff",
            accent_color="#ff0000",
            muted_color="#888888",
        )
        p = video_page("v1", "https://example.com/v.mp4", caption="Hello", theme=theme)
        text_layer = p.layers[1]
        caption_el = next(c for c in text_layer.children
                          if isinstance(c, TextElement) and c.class_ == "ast-caption")
        assert caption_el.animate_in == "fly-in-top"

    def test_renderable(self) -> None:
        p = video_page("v1", "https://example.com/v.mp4", caption="Great clip")
        story = _renderable_story([p])
        html = story.render()
        assert "Great clip" in html
        assert "amp-video" in html


# ---------------------------------------------------------------------------
# photo_page — overlay parameter
# ---------------------------------------------------------------------------

class TestPhotoPageOverlay:
    def test_overlay_false_no_overlay_layer(self) -> None:
        p = photo_page("ph", "photo.jpg", overlay=False)
        # Only the fill image layer; no overlay div
        for layer in p.layers:
            for child in layer.children:
                if isinstance(child, DivElement):
                    assert child.class_ != "ast-overlay"

    def test_overlay_true_inserts_overlay_layer(self) -> None:
        p = photo_page("ph", "photo.jpg", overlay=True)
        overlay_divs = [
            child for layer in p.layers
            for child in layer.children
            if isinstance(child, DivElement) and child.class_ == "ast-overlay"
        ]
        assert len(overlay_divs) == 1

    def test_overlay_layer_order_image_then_overlay(self) -> None:
        p = photo_page("ph", "photo.jpg", overlay=True)
        # first layer = image fill, second = overlay fill
        assert isinstance(p.layers[0].children[0], AmpImg)
        assert p.layers[1].template == "fill"
        assert isinstance(p.layers[1].children[0], DivElement)
        assert p.layers[1].children[0].class_ == "ast-overlay"

    def test_overlay_with_no_text_two_layers(self) -> None:
        p = photo_page("ph", "photo.jpg", overlay=True)
        assert len(p.layers) == 2

    def test_overlay_with_caption_three_layers(self) -> None:
        p = photo_page("ph", "photo.jpg", overlay=True, caption="A caption")
        assert len(p.layers) == 3


# ---------------------------------------------------------------------------
# listicle_page
# ---------------------------------------------------------------------------

class TestListiclePage:
    def test_returns_page(self) -> None:
        p = listicle_page("lst", "My List", ["Item A", "Item B"])
        assert isinstance(p, Page)

    def test_empty_items_raises(self) -> None:
        with pytest.raises(ValidationError):
            listicle_page("lst", "Title", [])

    def test_page_id(self) -> None:
        p = listicle_page("my-list", "Title", ["X"])
        assert p.page_id == "my-list"

    def test_single_item_no_error(self) -> None:
        p = listicle_page("lst", "Title", ["Only item"])
        assert isinstance(p, Page)

    def test_bullet_prefix_on_items(self) -> None:
        p = listicle_page("lst", "Title", ["Alpha", "Beta"])
        text_layer = p.layers[-1]
        bullets = [
            c for c in text_layer.children
            if isinstance(c, TextElement) and c.class_ == "ast-body"
        ]
        assert all(c.text.startswith("\u2022") for c in bullets)

    def test_item_text_preserved(self) -> None:
        p = listicle_page("lst", "Title", ["Hello world"])
        text_layer = p.layers[-1]
        bullets = [
            c for c in text_layer.children
            if isinstance(c, TextElement) and c.class_ == "ast-body"
        ]
        assert any("Hello world" in c.text for c in bullets)

    def test_title_is_h2_ast_subtitle(self) -> None:
        p = listicle_page("lst", "My Heading", ["Item"])
        text_layer = p.layers[-1]
        titles = [
            c for c in text_layer.children
            if isinstance(c, TextElement) and c.class_ == "ast-subtitle"
        ]
        assert len(titles) == 1
        assert titles[0].tag == "h2"
        assert titles[0].text == "My Heading"

    def test_no_background_two_layers(self) -> None:
        p = listicle_page("lst", "Title", ["Item A"])
        assert len(p.layers) == 2

    def test_with_background_three_layers(self) -> None:
        p = listicle_page("lst", "Title", ["Item A"], background_src="bg.jpg")
        assert len(p.layers) == 3

    def test_renderable(self) -> None:
        p = listicle_page("lst1", "Top Things", ["First", "Second", "Third"])
        story = _renderable_story([p])
        html = story.render()
        assert "Top Things" in html
        assert "First" in html


# ---------------------------------------------------------------------------
# comparison_page
# ---------------------------------------------------------------------------

class TestComparisonPage:
    def _get_vertical_layer(self, p: Page) -> Layer:
        verticals = [lyr for lyr in p.layers if lyr.template == "vertical"]
        assert len(verticals) == 1
        return verticals[0]

    def _get_row(self, p: Page) -> DivElement:
        layer = self._get_vertical_layer(p)
        rows = [c for c in layer.children if isinstance(c, DivElement) and c.class_ == "ast-comparison-row"]
        assert len(rows) == 1
        return rows[0]

    def test_returns_page(self) -> None:
        p = comparison_page("cmp", "80%", "Satisfied", "20%", "Unsatisfied")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = comparison_page("my-cmp", "A", "left", "B", "right")
        assert p.page_id == "my-cmp"

    def test_has_single_vertical_layer(self) -> None:
        p = comparison_page("cmp", "80%", "Satisfied", "20%", "Unsatisfied")
        verticals = [lyr for lyr in p.layers if lyr.template == "vertical"]
        assert len(verticals) == 1

    def test_no_thirds_layers(self) -> None:
        p = comparison_page("cmp", "80%", "Left", "20%", "Right")
        thirds = [lyr for lyr in p.layers if lyr.template == "thirds"]
        assert len(thirds) == 0

    def test_row_has_two_comparison_cols(self) -> None:
        row = self._get_row(comparison_page("cmp", "80%", "Left", "20%", "Right"))
        cols = [c for c in row.children if isinstance(c, DivElement) and c.class_ == "ast-comparison-col"]
        assert len(cols) == 2

    def test_left_stat_in_left_col(self) -> None:
        row = self._get_row(comparison_page("cmp", "80%", "Satisfied", "20%", "Unsatisfied"))
        cols = [c for c in row.children if isinstance(c, DivElement) and c.class_ == "ast-comparison-col"]
        left_texts = [c for c in cols[0].children if isinstance(c, TextElement)]
        assert any("80%" in t.text for t in left_texts)

    def test_right_stat_in_right_col(self) -> None:
        row = self._get_row(comparison_page("cmp", "80%", "Satisfied", "20%", "Unsatisfied"))
        cols = [c for c in row.children if isinstance(c, DivElement) and c.class_ == "ast-comparison-col"]
        right_texts = [c for c in cols[-1].children if isinstance(c, TextElement)]
        assert any("20%" in t.text for t in right_texts)

    def test_versus_shown_in_centre_div(self) -> None:
        row = self._get_row(comparison_page("cmp", "80%", "Left", "20%", "Right", versus="VS"))
        vs_divs = [c for c in row.children if isinstance(c, DivElement) and c.class_ == "ast-comparison-vs"]
        assert len(vs_divs) == 1
        texts = [c for c in vs_divs[0].children if isinstance(c, TextElement)]
        assert any("VS" in t.text for t in texts)

    def test_empty_versus_omits_centre_div(self) -> None:
        row = self._get_row(comparison_page("cmp", "80%", "Left", "20%", "Right", versus=""))
        vs_divs = [c for c in row.children if isinstance(c, DivElement) and c.class_ == "ast-comparison-vs"]
        assert len(vs_divs) == 0

    def test_custom_versus_text(self) -> None:
        row = self._get_row(comparison_page("cmp", "A", "left", "B", "right", versus="OR"))
        vs_divs = [c for c in row.children if isinstance(c, DivElement) and c.class_ == "ast-comparison-vs"]
        texts = [c for c in vs_divs[0].children if isinstance(c, TextElement)]
        assert any("OR" in t.text for t in texts)

    def test_eyebrow_in_vertical_layer(self) -> None:
        p = comparison_page("cmp", "A", "left_label", "B", "right_label", eyebrow="Compare")
        layer = self._get_vertical_layer(p)
        eyebrow_texts = [
            c for c in layer.children
            if isinstance(c, TextElement) and c.class_ == "ast-eyebrow"
        ]
        assert len(eyebrow_texts) == 1
        assert eyebrow_texts[0].text == "Compare"

    def test_no_eyebrow_layer_has_only_row(self) -> None:
        p = comparison_page("cmp", "A", "left_label", "B", "right_label")
        layer = self._get_vertical_layer(p)
        # Only child should be the comparison row DivElement
        assert len(layer.children) == 1
        assert isinstance(layer.children[0], DivElement)
        assert layer.children[0].class_ == "ast-comparison-row"

    def test_stat_uses_comparison_stat_class(self) -> None:
        row = self._get_row(comparison_page("cmp", "80%", "Left", "20%", "Right"))
        cols = [c for c in row.children if isinstance(c, DivElement) and c.class_ == "ast-comparison-col"]
        stat_els = [c for c in cols[0].children if isinstance(c, TextElement) and c.class_ == "ast-comparison-stat"]
        assert len(stat_els) == 1

    def test_with_background_has_image_layer(self) -> None:
        p = comparison_page("cmp", "A", "left_label", "B", "right_label", background_src="bg.jpg")
        fill_layers = [lyr for lyr in p.layers if lyr.template == "fill"]
        has_img = any(
            isinstance(c, AmpImg)
            for lyr in fill_layers
            for c in lyr.children
        )
        assert has_img

    def test_renderable(self) -> None:
        p = comparison_page("cmp1", "80%", "Yes", "20%", "No", eyebrow="Results")
        story = _renderable_story([p])
        html = story.render()
        assert "80%" in html
        assert "Yes" in html


# ---------------------------------------------------------------------------
# breaking_page
# ---------------------------------------------------------------------------

class TestBreakingPage:
    def test_returns_page(self) -> None:
        p = breaking_page("b1", "Major event unfolds")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = breaking_page("news-1", "Headline")
        assert p.page_id == "news-1"

    def test_default_badge_is_breaking(self) -> None:
        p = breaking_page("b1", "Headline")
        text_layer = p.layers[-1]
        badges = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-badge"]
        assert len(badges) == 1
        assert badges[0].text == "BREAKING"

    def test_custom_badge(self) -> None:
        p = breaking_page("b1", "Headline", badge="LIVE")
        text_layer = p.layers[-1]
        badges = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-badge"]
        assert badges[0].text == "LIVE"

    def test_headline_is_h1_ast_title(self) -> None:
        p = breaking_page("b1", "Big News")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-title"]
        assert len(titles) == 1
        assert titles[0].tag == "h1"
        assert titles[0].text == "Big News"

    def test_headline_has_delay(self) -> None:
        p = breaking_page("b1", "Headline")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_no_body_text_layer_has_two_children(self) -> None:
        p = breaking_page("b1", "Headline")
        assert len(p.layers[-1].children) == 2

    def test_with_body_text_layer_has_three_children(self) -> None:
        p = breaking_page("b1", "Headline", body="Some context here.")
        assert len(p.layers[-1].children) == 3

    def test_body_is_ast_body(self) -> None:
        p = breaking_page("b1", "Headline", body="Details follow.")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 1
        assert bodies[0].text == "Details follow."

    def test_no_background_one_bg_layer(self) -> None:
        p = breaking_page("b1", "Headline")
        fill_layers = [lyr for lyr in p.layers if lyr.template == "fill"]
        assert len(fill_layers) == 1

    def test_with_background_two_bg_layers(self) -> None:
        p = breaking_page("b1", "Headline", background_src="https://example.com/img.jpg")
        fill_layers = [lyr for lyr in p.layers if lyr.template == "fill"]
        assert len(fill_layers) == 2

    def test_auto_advance_after(self) -> None:
        p = breaking_page("b1", "Headline", auto_advance_after="8s")
        assert p.auto_advance_after == "8s"

    def test_renderable(self) -> None:
        p = breaking_page("b1", "Market crash begins",
                          badge="ALERT", body="Stocks fell 5% today.")
        story = _renderable_story([p])
        html = story.render()
        assert "Market crash begins" in html
        assert "ALERT" in html
        assert "Stocks fell 5% today." in html


# ---------------------------------------------------------------------------
# update_page
# ---------------------------------------------------------------------------

class TestUpdatePage:
    def test_returns_page(self) -> None:
        p = update_page("u1", 1, "Headline", "Body text.")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = update_page("upd-3", 3, "Third update", "More details.")
        assert p.page_id == "upd-3"

    def test_eyebrow_formatted(self) -> None:
        p = update_page("u1", 5, "Headline", "Body")
        text_layer = p.layers[-1]
        eyebrows = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-eyebrow"]
        assert len(eyebrows) == 1
        assert eyebrows[0].text == "UPDATE 5"

    def test_headline_is_h1_ast_title(self) -> None:
        p = update_page("u1", 1, "The Story So Far", "Body")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-title"]
        assert len(titles) == 1
        assert titles[0].tag == "h1"
        assert titles[0].text == "The Story So Far"

    def test_body_is_ast_body(self) -> None:
        p = update_page("u1", 1, "Headline", "The body paragraph.")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 1
        assert bodies[0].text == "The body paragraph."

    def test_text_layer_always_three_children(self) -> None:
        p = update_page("u1", 2, "Headline", "Body")
        assert len(p.layers[-1].children) == 3

    def test_headline_has_delay(self) -> None:
        p = update_page("u1", 1, "Headline", "Body")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_no_background_two_layers(self) -> None:
        p = update_page("u1", 1, "Headline", "Body")
        assert len(p.layers) == 2

    def test_with_background_three_layers(self) -> None:
        p = update_page("u1", 1, "Headline", "Body",
                        background_src="https://example.com/img.jpg")
        assert len(p.layers) == 3

    def test_renderable(self) -> None:
        p = update_page("u1", 2, "Crisis deepens", "Officials have responded.")
        story = _renderable_story([p])
        html = story.render()
        assert "UPDATE 2" in html
        assert "Crisis deepens" in html
        assert "Officials have responded." in html


# ---------------------------------------------------------------------------
# itinerary_page
# ---------------------------------------------------------------------------

class TestItineraryPage:
    def test_returns_page(self) -> None:
        p = itinerary_page("it1", 1, "Paris")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = itinerary_page("stop-2", 2, "Rome")
        assert p.page_id == "stop-2"

    def test_integer_day_formats_as_day_n(self) -> None:
        p = itinerary_page("it1", 3, "Tokyo")
        text_layer = p.layers[-1]
        day_els = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-chapter-number"]
        assert len(day_els) == 1
        assert day_els[0].text == "DAY 3"

    def test_string_day_used_verbatim(self) -> None:
        p = itinerary_page("it1", "Final Stop", "Nairobi")
        text_layer = p.layers[-1]
        day_els = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-chapter-number"]
        assert day_els[0].text == "Final Stop"

    def test_destination_is_h1_ast_chapter_title(self) -> None:
        p = itinerary_page("it1", 1, "Kyoto")
        text_layer = p.layers[-1]
        dests = [c for c in text_layer.children
                 if isinstance(c, TextElement) and c.class_ == "ast-chapter-title"]
        assert len(dests) == 1
        assert dests[0].tag == "h1"
        assert dests[0].text == "Kyoto"

    def test_no_details_text_layer_has_two_children(self) -> None:
        p = itinerary_page("it1", 1, "Lisbon")
        assert len(p.layers[-1].children) == 2

    def test_with_two_details_text_layer_has_four_children(self) -> None:
        p = itinerary_page("it1", 1, "Lisbon", details=["Fado music", "Pastéis de nata"])
        assert len(p.layers[-1].children) == 4

    def test_details_are_ast_body(self) -> None:
        p = itinerary_page("it1", 1, "Berlin", details=["Visit the Wall", "Try currywurst"])
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 2
        assert bodies[0].text == "Visit the Wall"
        assert bodies[1].text == "Try currywurst"

    def test_no_background_two_layers(self) -> None:
        p = itinerary_page("it1", 1, "Oslo")
        assert len(p.layers) == 2

    def test_with_background_three_layers(self) -> None:
        p = itinerary_page("it1", 1, "Oslo",
                           background_src="https://example.com/oslo.jpg")
        assert len(p.layers) == 3

    def test_renderable(self) -> None:
        p = itinerary_page("it1", 4, "Barcelona",
                           details=["Sagrada Família", "La Barceloneta"])
        story = _renderable_story([p])
        html = story.render()
        assert "DAY 4" in html
        assert "Barcelona" in html
        assert "Sagrada" in html


# ---------------------------------------------------------------------------
# ChartRow
# ---------------------------------------------------------------------------

class TestChartRow:
    def test_label_and_value_required(self) -> None:
        row = ChartRow("Python", 45.0)
        assert row.label == "Python"
        assert row.value == 45.0

    def test_display_defaults_to_none(self) -> None:
        row = ChartRow("Go", 30.0)
        assert row.display is None

    def test_all_three_fields(self) -> None:
        row = ChartRow("Rust", 25.0, display="25%")
        assert row.label == "Rust"
        assert row.value == 25.0
        assert row.display == "25%"


# ---------------------------------------------------------------------------
# data_chart_page
# ---------------------------------------------------------------------------

class TestDataChartPage:
    def test_returns_page(self) -> None:
        p = data_chart_page("dc1", "Languages", [ChartRow("Python", 50)])
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = data_chart_page("my-chart", "Title", [ChartRow("A", 1)])
        assert p.page_id == "my-chart"

    def test_empty_rows_raises(self) -> None:
        with pytest.raises(ValidationError):
            data_chart_page("dc1", "Title", [])

    def test_single_row_layer_has_two_children(self) -> None:
        p = data_chart_page("dc1", "Chart", [ChartRow("A", 10)])
        chart_layer = p.layers[-1]
        # title element + 1 row div
        assert len(chart_layer.children) == 2

    def test_three_rows_layer_has_four_children(self) -> None:
        rows = [ChartRow("A", 10), ChartRow("B", 20), ChartRow("C", 30)]
        p = data_chart_page("dc1", "Chart", rows)
        assert len(p.layers[-1].children) == 4

    def test_title_element_class(self) -> None:
        p = data_chart_page("dc1", "My Chart", [ChartRow("X", 1)])
        chart_layer = p.layers[-1]
        title_el = chart_layer.children[0]
        assert isinstance(title_el, TextElement)
        assert title_el.class_ == "ast-chart-title"
        assert title_el.text == "My Chart"

    def test_row_div_class(self) -> None:
        p = data_chart_page("dc1", "Chart", [ChartRow("Alpha", 75)])
        chart_layer = p.layers[-1]
        row_div = chart_layer.children[1]
        assert isinstance(row_div, DivElement)
        assert row_div.class_ == "ast-chart-row"

    def test_bar_width_computed(self) -> None:
        rows = [ChartRow("A", 50), ChartRow("B", 100)]
        p = data_chart_page("dc1", "Chart", rows)
        chart_layer = p.layers[-1]
        # First row: 50/100 * 100 = 50%
        row_div = chart_layer.children[1]
        assert isinstance(row_div, DivElement)
        track = row_div.children[1]
        assert isinstance(track, DivElement)
        bar = track.children[0]
        assert isinstance(bar, TextElement)
        assert "50%" in (bar.style or "")

    def test_bar_width_capped_at_100(self) -> None:
        rows = [ChartRow("A", 150)]
        p = data_chart_page("dc1", "Chart", rows, max_value=100)
        chart_layer = p.layers[-1]
        row_div = chart_layer.children[1]
        assert isinstance(row_div, DivElement)
        track = row_div.children[1]
        assert isinstance(track, DivElement)
        bar = track.children[0]
        assert isinstance(bar, TextElement)
        assert "100%" in (bar.style or "")

    def test_custom_max_value(self) -> None:
        rows = [ChartRow("A", 25)]
        p = data_chart_page("dc1", "Chart", rows, max_value=50)
        chart_layer = p.layers[-1]
        row_div = chart_layer.children[1]
        assert isinstance(row_div, DivElement)
        track = row_div.children[1]
        assert isinstance(track, DivElement)
        bar = track.children[0]
        assert isinstance(bar, TextElement)
        assert "50%" in (bar.style or "")

    def test_display_field_used_when_set(self) -> None:
        p = data_chart_page("dc1", "Chart", [ChartRow("A", 42, display="42 pts")])
        chart_layer = p.layers[-1]
        row_div = chart_layer.children[1]
        assert isinstance(row_div, DivElement)
        value_el = row_div.children[2]
        assert isinstance(value_el, TextElement)
        assert value_el.text == "42 pts"

    def test_display_defaults_to_4g_format(self) -> None:
        p = data_chart_page("dc1", "Chart", [ChartRow("A", 42.0)])
        chart_layer = p.layers[-1]
        row_div = chart_layer.children[1]
        assert isinstance(row_div, DivElement)
        value_el = row_div.children[2]
        assert isinstance(value_el, TextElement)
        assert value_el.text == "42"

    def test_no_background_two_layers(self) -> None:
        p = data_chart_page("dc1", "Chart", [ChartRow("A", 1)])
        assert len(p.layers) == 2

    def test_with_background_three_layers(self) -> None:
        p = data_chart_page("dc1", "Chart", [ChartRow("A", 1)],
                            background_src="https://example.com/bg.jpg")
        assert len(p.layers) == 3

    def test_renderable(self) -> None:
        rows = [ChartRow("Python", 45, display="45%"),
                ChartRow("JavaScript", 35, display="35%")]
        p = data_chart_page("dc1", "Top Languages", rows)
        story = _renderable_story([p])
        html = story.render()
        assert "Top Languages" in html
        assert "Python" in html
        assert "45%" in html


# ---------------------------------------------------------------------------
# product_page
# ---------------------------------------------------------------------------

class TestProductPage:
    def test_returns_page(self) -> None:
        p = product_page("prod1", "Wireless Headphones")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = product_page("my-product", "Widget")
        assert p.page_id == "my-product"

    def test_product_name_is_h2_ast_subtitle(self) -> None:
        p = product_page("p1", "Super Widget")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-subtitle"]
        assert len(titles) == 1
        assert titles[0].tag == "h2"
        assert titles[0].text == "Super Widget"

    def test_no_brand_no_eyebrow(self) -> None:
        p = product_page("p1", "Widget")
        text_layer = p.layers[-1]
        eyebrows = [c for c in text_layer.children
                    if isinstance(c, TextElement) and c.class_ == "ast-eyebrow"]
        assert len(eyebrows) == 0

    def test_with_brand_eyebrow_is_first(self) -> None:
        p = product_page("p1", "Widget", brand="Acme")
        text_layer = p.layers[-1]
        first = text_layer.children[0]
        assert isinstance(first, TextElement)
        assert first.class_ == "ast-eyebrow"
        assert first.text == "Acme"

    def test_title_has_delay_when_brand_present(self) -> None:
        p = product_page("p1", "Widget", brand="Acme")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-subtitle")
        assert title_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_title_no_delay_without_brand(self) -> None:
        p = product_page("p1", "Widget")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-subtitle")
        assert title_el.animate_in_delay is None

    def test_no_price_no_stat_number(self) -> None:
        p = product_page("p1", "Widget")
        text_layer = p.layers[-1]
        prices = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-stat-number"]
        assert len(prices) == 0

    def test_with_price_stat_number_present(self) -> None:
        p = product_page("p1", "Widget", price="$49.99")
        text_layer = p.layers[-1]
        prices = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-stat-number"]
        assert len(prices) == 1
        assert prices[0].text == "$49.99"

    def test_was_price_before_price(self) -> None:
        p = product_page("p1", "Widget", price="$49.99", was_price="$79.99")
        text_layer = p.layers[-1]
        was_els = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-price-was"]
        price_els = [c for c in text_layer.children
                     if isinstance(c, TextElement) and c.class_ == "ast-stat-number"]
        assert len(was_els) == 1
        assert len(price_els) == 1
        was_idx = text_layer.children.index(was_els[0])
        price_idx = text_layer.children.index(price_els[0])
        assert was_idx < price_idx

    def test_no_image_one_bg_layer(self) -> None:
        p = product_page("p1", "Widget")
        fill_layers = [lyr for lyr in p.layers if lyr.template == "fill"]
        assert len(fill_layers) == 1

    def test_with_image_two_bg_layers(self) -> None:
        p = product_page("p1", "Widget", image_src="https://example.com/prod.jpg")
        fill_layers = [lyr for lyr in p.layers if lyr.template == "fill"]
        assert len(fill_layers) == 2

    def test_renderable(self) -> None:
        p = product_page("p1", "Noise-Cancelling Headphones",
                         brand="SoundCo",
                         price="$199",
                         was_price="$299",
                         image_src="https://example.com/headphones.jpg")
        story = _renderable_story([p])
        html = story.render()
        assert "Noise-Cancelling Headphones" in html
        assert "SoundCo" in html
        assert "$199" in html
        assert "$299" in html


# ---------------------------------------------------------------------------
# deal_page
# ---------------------------------------------------------------------------

class TestDealPage:
    def test_returns_page(self) -> None:
        p = deal_page("d1", "Weekend Sale")
        assert isinstance(p, Page)

    def test_page_id(self) -> None:
        p = deal_page("my-deal", "Big Deal")
        assert p.page_id == "my-deal"

    def test_no_badge_first_child_is_title(self) -> None:
        p = deal_page("d1", "Great Deal")
        text_layer = p.layers[-1]
        first = text_layer.children[0]
        assert isinstance(first, TextElement)
        assert first.class_ == "ast-title"

    def test_with_badge_first_child_is_badge(self) -> None:
        p = deal_page("d1", "Big Sale", badge="SALE")
        text_layer = p.layers[-1]
        first = text_layer.children[0]
        assert isinstance(first, TextElement)
        assert first.class_ == "ast-badge"
        assert first.text == "SALE"

    def test_title_is_h1_ast_title(self) -> None:
        p = deal_page("d1", "Flash Sale")
        text_layer = p.layers[-1]
        titles = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-title"]
        assert len(titles) == 1
        assert titles[0].tag == "h1"
        assert titles[0].text == "Flash Sale"

    def test_title_has_delay_when_badge_present(self) -> None:
        p = deal_page("d1", "Title", badge="OFFER")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in_delay == SLATE_THEME.animate_in_delay

    def test_title_no_delay_without_badge(self) -> None:
        p = deal_page("d1", "Title")
        text_layer = p.layers[-1]
        title_el = next(c for c in text_layer.children
                        if isinstance(c, TextElement) and c.class_ == "ast-title")
        assert title_el.animate_in_delay is None

    def test_description_as_ast_body(self) -> None:
        p = deal_page("d1", "Title", description="Hurry, limited stock!")
        text_layer = p.layers[-1]
        bodies = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-body"]
        assert len(bodies) == 1
        assert bodies[0].text == "Hurry, limited stock!"

    def test_was_price_present(self) -> None:
        p = deal_page("d1", "Title", was_price="$100")
        text_layer = p.layers[-1]
        was_els = [c for c in text_layer.children
                   if isinstance(c, TextElement) and c.class_ == "ast-price-was"]
        assert len(was_els) == 1
        assert was_els[0].text == "$100"

    def test_price_present(self) -> None:
        p = deal_page("d1", "Title", price="$50")
        text_layer = p.layers[-1]
        prices = [c for c in text_layer.children
                  if isinstance(c, TextElement) and c.class_ == "ast-stat-number"]
        assert len(prices) == 1
        assert prices[0].text == "$50"

    def test_all_optional_fields_present(self) -> None:
        p = deal_page("d1", "Title", badge="SALE", description="Desc",
                      was_price="$100", price="$50")
        text_layer = p.layers[-1]
        assert len(text_layer.children) == 5

    def test_no_background_one_bg_layer(self) -> None:
        p = deal_page("d1", "Title")
        fill_layers = [lyr for lyr in p.layers if lyr.template == "fill"]
        assert len(fill_layers) == 1

    def test_with_background_two_bg_layers(self) -> None:
        p = deal_page("d1", "Title", background_src="https://example.com/bg.jpg")
        fill_layers = [lyr for lyr in p.layers if lyr.template == "fill"]
        assert len(fill_layers) == 2

    def test_renderable(self) -> None:
        p = deal_page("d1", "Laptop Clearance",
                      badge="50% OFF",
                      description="While stocks last.",
                      was_price="$1000",
                      price="$499")
        story = _renderable_story([p])
        html = story.render()
        assert "Laptop Clearance" in html
        assert "50% OFF" in html
        assert "$499" in html

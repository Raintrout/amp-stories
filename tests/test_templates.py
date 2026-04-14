"""Tests for amp_stories/templates.py."""

from __future__ import annotations

import warnings

from amp_stories._validation import AmpStoriesWarning
from amp_stories.elements import AmpImg, DivElement, TextElement
from amp_stories.page import Page
from amp_stories.story import Story
from amp_stories.templates import (
    _background_layers,
    chapter_page,
    photo_page,
    quote_page,
    stat_page,
    text_page,
    title_page,
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

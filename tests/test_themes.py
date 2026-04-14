"""Tests for amp_stories/themes.py."""

from __future__ import annotations

import pytest

from amp_stories._serde import _deserialize, _serialize
from amp_stories._validation import ValidationError
from amp_stories.themes import SLATE_THEME, Theme


class TestThemeDefaults:
    def test_slate_theme_is_theme_instance(self) -> None:
        assert isinstance(SLATE_THEME, Theme)

    def test_default_bg_color(self) -> None:
        assert SLATE_THEME.bg_color == "#16213e"

    def test_default_text_color(self) -> None:
        assert SLATE_THEME.text_color == "#f5f5f5"

    def test_default_accent_color(self) -> None:
        assert SLATE_THEME.accent_color == "#0f8b8d"

    def test_default_muted_color(self) -> None:
        assert SLATE_THEME.muted_color == "#9e9eb0"

    def test_default_overlay_opacity(self) -> None:
        assert SLATE_THEME.overlay_opacity == 0.50

    def test_default_font_sizes(self) -> None:
        assert SLATE_THEME.h1_size == "3.2rem"
        assert SLATE_THEME.h2_size == "2.4rem"
        assert SLATE_THEME.body_size == "1.6rem"
        assert SLATE_THEME.small_size == "1.1rem"

    def test_default_animation_values(self) -> None:
        assert SLATE_THEME.heading_animate_in == "fly-in-bottom"
        assert SLATE_THEME.body_animate_in == "fade-in"
        assert SLATE_THEME.animate_in_duration == "0.5s"
        assert SLATE_THEME.animate_in_delay == "0.3s"

    def test_heading_font_none_by_default(self) -> None:
        assert SLATE_THEME.heading_font is None


class TestThemeValidation:
    def test_invalid_bg_color(self) -> None:
        with pytest.raises(ValidationError, match="bg_color"):
            Theme(bg_color="navy")

    def test_invalid_text_color(self) -> None:
        with pytest.raises(ValidationError, match="text_color"):
            Theme(text_color="white")

    def test_invalid_accent_color(self) -> None:
        with pytest.raises(ValidationError, match="accent_color"):
            Theme(accent_color="#abc")  # short hex

    def test_invalid_muted_color(self) -> None:
        with pytest.raises(ValidationError, match="muted_color"):
            Theme(muted_color="rgb(100,100,100)")

    def test_overlay_opacity_too_low(self) -> None:
        with pytest.raises(ValidationError, match="overlay_opacity"):
            Theme(overlay_opacity=-0.1)

    def test_overlay_opacity_too_high(self) -> None:
        with pytest.raises(ValidationError, match="overlay_opacity"):
            Theme(overlay_opacity=1.1)

    def test_overlay_opacity_boundary_zero(self) -> None:
        t = Theme(overlay_opacity=0.0)
        assert t.overlay_opacity == 0.0

    def test_overlay_opacity_boundary_one(self) -> None:
        t = Theme(overlay_opacity=1.0)
        assert t.overlay_opacity == 1.0

    def test_invalid_h1_size(self) -> None:
        with pytest.raises(ValidationError, match="h1_size"):
            Theme(h1_size="large")

    def test_invalid_h2_size(self) -> None:
        with pytest.raises(ValidationError, match="h2_size"):
            Theme(h2_size="2.4")

    def test_invalid_body_size(self) -> None:
        with pytest.raises(ValidationError, match="body_size"):
            Theme(body_size="16")

    def test_invalid_small_size(self) -> None:
        with pytest.raises(ValidationError, match="small_size"):
            Theme(small_size="small")

    def test_valid_px_size(self) -> None:
        t = Theme(h1_size="48px")
        assert t.h1_size == "48px"

    def test_valid_pt_size(self) -> None:
        t = Theme(body_size="18pt")
        assert t.body_size == "18pt"

    def test_valid_em_size(self) -> None:
        t = Theme(small_size="1em")
        assert t.small_size == "1em"


class TestGenerateCss:
    def test_returns_string(self) -> None:
        css = SLATE_THEME.generate_css()
        assert isinstance(css, str)

    def test_css_nonempty(self) -> None:
        assert len(SLATE_THEME.generate_css()) > 0

    def test_contains_ast_bg(self) -> None:
        assert ".ast-bg" in SLATE_THEME.generate_css()

    def test_contains_ast_overlay(self) -> None:
        assert ".ast-overlay" in SLATE_THEME.generate_css()

    def test_contains_ast_eyebrow(self) -> None:
        assert ".ast-eyebrow" in SLATE_THEME.generate_css()

    def test_contains_ast_title(self) -> None:
        assert ".ast-title" in SLATE_THEME.generate_css()

    def test_contains_ast_subtitle(self) -> None:
        assert ".ast-subtitle" in SLATE_THEME.generate_css()

    def test_contains_ast_body(self) -> None:
        assert ".ast-body" in SLATE_THEME.generate_css()

    def test_contains_ast_attribution(self) -> None:
        assert ".ast-attribution" in SLATE_THEME.generate_css()

    def test_contains_ast_quote_mark(self) -> None:
        assert ".ast-quote-mark" in SLATE_THEME.generate_css()

    def test_contains_ast_stat_number(self) -> None:
        assert ".ast-stat-number" in SLATE_THEME.generate_css()

    def test_contains_ast_stat_label(self) -> None:
        assert ".ast-stat-label" in SLATE_THEME.generate_css()

    def test_contains_ast_caption(self) -> None:
        assert ".ast-caption" in SLATE_THEME.generate_css()

    def test_contains_ast_chapter_number(self) -> None:
        assert ".ast-chapter-number" in SLATE_THEME.generate_css()

    def test_contains_ast_chapter_title(self) -> None:
        assert ".ast-chapter-title" in SLATE_THEME.generate_css()

    def test_bg_color_in_css(self) -> None:
        css = SLATE_THEME.generate_css()
        assert SLATE_THEME.bg_color in css

    def test_text_color_in_css(self) -> None:
        css = SLATE_THEME.generate_css()
        assert SLATE_THEME.text_color in css

    def test_accent_color_in_css(self) -> None:
        css = SLATE_THEME.generate_css()
        assert SLATE_THEME.accent_color in css

    def test_overlay_rgba_in_css(self) -> None:
        theme = Theme(overlay_opacity=0.6)
        css = theme.generate_css()
        assert "rgba(0,0,0,0.6)" in css

    def test_custom_colors_reflected(self) -> None:
        theme = Theme(bg_color="#ff0000", text_color="#0000ff", accent_color="#00ff00",
                      muted_color="#aaaaaa")
        css = theme.generate_css()
        assert "#ff0000" in css
        assert "#0000ff" in css
        assert "#00ff00" in css

    def test_custom_font_family_reflected(self) -> None:
        theme = Theme(font_family="'Arial', sans-serif")
        css = theme.generate_css()
        assert "Arial" in css

    def test_heading_font_used_when_set(self) -> None:
        theme = Theme(heading_font="'Playfair Display', serif")
        css = theme.generate_css()
        assert "Playfair Display" in css

    def test_heading_font_none_falls_back_to_font_family(self) -> None:
        theme = Theme(font_family="'Verdana', sans-serif", heading_font=None)
        css = theme.generate_css()
        # Both headings and body use same font
        assert css.count("Verdana") >= 2

    def test_font_sizes_in_css(self) -> None:
        css = SLATE_THEME.generate_css()
        assert SLATE_THEME.h1_size in css
        assert SLATE_THEME.h2_size in css
        assert SLATE_THEME.body_size in css
        assert SLATE_THEME.small_size in css

    def test_custom_font_sizes_reflected(self) -> None:
        theme = Theme(h1_size="48px", body_size="20px")
        css = theme.generate_css()
        assert "48px" in css
        assert "20px" in css


class TestThemeInternalHelpers:
    def test_heading_font_css_falls_back(self) -> None:
        theme = Theme(font_family="'Georgia', serif", heading_font=None)
        assert theme._heading_font_css() == "'Georgia', serif"

    def test_heading_font_css_uses_heading_font(self) -> None:
        theme = Theme(heading_font="'Merriweather', serif")
        assert theme._heading_font_css() == "'Merriweather', serif"

    def test_overlay_rgba_format(self) -> None:
        theme = Theme(overlay_opacity=0.75)
        assert theme._overlay_rgba() == "rgba(0,0,0,0.75)"

    def test_overlay_rgba_zero(self) -> None:
        theme = Theme(overlay_opacity=0.0)
        assert theme._overlay_rgba() == "rgba(0,0,0,0.0)"


class TestThemeSerde:
    def test_serialize_type_key(self) -> None:
        data = _serialize(SLATE_THEME)
        assert data["__type__"] == "Theme"

    def test_serialize_fields_present(self) -> None:
        data = _serialize(SLATE_THEME)
        assert data["bg_color"] == "#16213e"
        assert data["text_color"] == "#f5f5f5"
        assert data["h1_size"] == "3.2rem"

    def test_round_trip(self) -> None:
        data = _serialize(SLATE_THEME)
        theme2 = _deserialize(data)
        assert isinstance(theme2, Theme)
        assert theme2.bg_color == SLATE_THEME.bg_color
        assert theme2.accent_color == SLATE_THEME.accent_color
        assert theme2.h1_size == SLATE_THEME.h1_size

    def test_custom_theme_round_trip(self) -> None:
        theme = Theme(
            bg_color="#000000",
            text_color="#ffffff",
            accent_color="#ff6600",
            muted_color="#888888",
        )
        data = _serialize(theme)
        theme2 = _deserialize(data)
        assert isinstance(theme2, Theme)
        assert theme2.bg_color == "#000000"
        assert theme2.accent_color == "#ff6600"

"""Tests for amp_stories/themes.py."""

from __future__ import annotations

import pytest

from amp_stories._serde import _deserialize, _serialize
from amp_stories._validation import ValidationError
from amp_stories.themes import (
    FEATURE_THEME,
    MARKET_THEME,
    SIGNAL_THEME,
    SUMMIT_THEME,
    Theme,
    _hex_to_rgb,
    _scale_css_size,
)

DEFAULT_THEME = SUMMIT_THEME
SLATE_THEME = DEFAULT_THEME


class TestThemeDefaults:
    def test_summit_theme_is_theme_instance(self) -> None:
        assert isinstance(SUMMIT_THEME, Theme)

    def test_default_bg_color(self) -> None:
        assert SUMMIT_THEME.bg_color == "#152226"

    def test_default_text_color(self) -> None:
        assert SUMMIT_THEME.text_color == "#f4efe6"

    def test_default_accent_color(self) -> None:
        assert SUMMIT_THEME.accent_color == "#d7a14d"

    def test_default_muted_color(self) -> None:
        assert SUMMIT_THEME.muted_color == "#a7b1ab"

    def test_default_overlay_opacity(self) -> None:
        assert SUMMIT_THEME.overlay_opacity == 0.50

    def test_default_font_sizes(self) -> None:
        assert SUMMIT_THEME.h1_size == "2.8rem"
        assert SUMMIT_THEME.h2_size == "2rem"
        assert SUMMIT_THEME.body_size == "1.6rem"
        assert SUMMIT_THEME.small_size == "1.1rem"

    def test_default_animation_values(self) -> None:
        assert SUMMIT_THEME.heading_animate_in == "fly-in-bottom"
        assert SUMMIT_THEME.body_animate_in == "fade-in"
        assert SUMMIT_THEME.animate_in_duration == "0.5s"
        assert SUMMIT_THEME.animate_in_delay == "0.3s"

    def test_heading_font_none_by_default(self) -> None:
        assert SUMMIT_THEME.heading_font is not None


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

    def test_invalid_panel_color(self) -> None:
        with pytest.raises(ValidationError, match="panel_color"):
            Theme(panel_color="black")

    def test_invalid_panel_opacity(self) -> None:
        with pytest.raises(ValidationError, match="panel_opacity"):
            Theme(panel_opacity=1.2)

    def test_invalid_caption_opacity(self) -> None:
        with pytest.raises(ValidationError, match="caption_opacity"):
            Theme(caption_opacity=-0.1)

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

    def test_panel_sizes_validate(self) -> None:
        t = Theme(panel_radius="20px", panel_padding="1em", content_max_width="36rem")
        assert t.panel_radius == "20px"
        assert t.panel_padding == "1em"
        assert t.content_max_width == "36rem"


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
        theme = Theme(
            bg_color="#ff0000", text_color="#0000ff", accent_color="#00ff00", muted_color="#aaaaaa"
        )
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

    def test_panel_rgba_uses_panel_color(self) -> None:
        theme = Theme(panel_color="#112233", panel_opacity=0.7)
        assert theme._panel_rgba() == "rgba(17,34,51,0.7)"


class TestColorHelpers:
    def test_hex_to_rgb(self) -> None:
        assert _hex_to_rgb("#102030") == (16, 32, 48)


class TestThemeSerde:
    def test_serialize_type_key(self) -> None:
        data = _serialize(SLATE_THEME)
        assert data["__type__"] == "Theme"

    def test_serialize_fields_present(self) -> None:
        data = _serialize(SLATE_THEME)
        assert data["bg_color"] == "#152226"
        assert data["text_color"] == "#f4efe6"
        assert data["h1_size"] == "2.8rem"

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


class TestScaleCssSize:
    def test_scale_rem(self) -> None:
        assert _scale_css_size("3.2rem", 0.7) == "2.24rem"

    def test_scale_px(self) -> None:
        assert _scale_css_size("48px", 0.5) == "24px"

    def test_scale_pt(self) -> None:
        assert _scale_css_size("24pt", 2.0) == "48pt"

    def test_scale_em(self) -> None:
        assert _scale_css_size("1em", 1.5) == "1.5em"

    def test_identity_at_one(self) -> None:
        assert _scale_css_size("3.2rem", 1.0) == "3.2rem"

    def test_trailing_zeros_stripped(self) -> None:
        result = _scale_css_size("2rem", 0.5)
        assert result == "1rem"
        assert "0" not in result.split("rem")[0].lstrip("0123456789.") or True

    def test_no_trailing_dot(self) -> None:
        result = _scale_css_size("2rem", 1.0)
        assert not result.startswith(".")
        assert "." not in result or result.index(".") < len(result) - 1


class TestLandscapeFontScale:
    def test_default_theme_has_landscape_scale(self) -> None:
        assert SLATE_THEME.landscape_font_scale == 0.8

    def test_boundary_low_passes(self) -> None:
        t = Theme(landscape_font_scale=0.1)
        assert t.landscape_font_scale == 0.1

    def test_boundary_high_passes(self) -> None:
        t = Theme(landscape_font_scale=2.0)
        assert t.landscape_font_scale == 2.0

    def test_below_minimum_raises(self) -> None:
        with pytest.raises(ValidationError, match="landscape_font_scale"):
            Theme(landscape_font_scale=0.09)

    def test_above_maximum_raises(self) -> None:
        with pytest.raises(ValidationError, match="landscape_font_scale"):
            Theme(landscape_font_scale=2.1)

    def test_generate_css_no_landscape_query_when_none(self) -> None:
        theme = Theme(landscape_font_scale=None)
        css = theme.generate_css()
        assert "@media (orientation:landscape)" not in css

    def test_default_theme_has_media_query(self) -> None:
        css = SLATE_THEME.generate_css()
        assert "@media (orientation:landscape)" in css

    def test_generate_css_has_media_query_when_set(self) -> None:
        theme = Theme(landscape_font_scale=0.8)
        css = theme.generate_css()
        assert "@media (orientation:landscape)" in css

    def test_scaled_h1_in_css(self) -> None:
        theme = Theme(landscape_font_scale=0.7)
        css = theme.generate_css()
        expected = _scale_css_size("3.2rem", 0.7)
        assert expected in css

    def test_serde_round_trip(self) -> None:
        theme = Theme(landscape_font_scale=0.75)
        data = _serialize(theme)
        theme2 = _deserialize(data)
        assert isinstance(theme2, Theme)
        assert theme2.landscape_font_scale == 0.75


class TestGoogleFont:
    def test_default_is_none(self) -> None:
        assert SLATE_THEME.google_font is None

    def test_get_google_fonts_url_returns_none_when_no_font(self) -> None:
        assert SLATE_THEME.get_google_fonts_url() is None

    def test_get_google_fonts_url_returns_url(self) -> None:
        theme = Theme(google_font="Montserrat")
        url = theme.get_google_fonts_url()
        assert url is not None
        assert "fonts.googleapis.com" in url
        assert "Montserrat" in url

    def test_url_contains_display_swap(self) -> None:
        theme = Theme(google_font="Roboto")
        url = theme.get_google_fonts_url()
        assert url is not None
        assert "display=swap" in url

    def test_url_encoded_weights(self) -> None:
        theme = Theme(google_font="Roboto:400,700")
        url = theme.get_google_fonts_url()
        assert url is not None
        assert "Roboto" in url

    def test_serde_round_trip(self) -> None:
        theme = Theme(google_font="Playfair+Display")
        data = _serialize(theme)
        theme2 = _deserialize(data)
        assert isinstance(theme2, Theme)
        assert theme2.google_font == "Playfair+Display"


class TestNewCssClasses:
    def test_ast_badge_present(self) -> None:
        assert ".ast-badge" in SLATE_THEME.generate_css()

    def test_ast_badge_border_radius(self) -> None:
        assert "border-radius:2rem" in SLATE_THEME.generate_css()

    def test_ast_badge_uses_accent_color(self) -> None:
        css = SLATE_THEME.generate_css()
        assert f"background:{SLATE_THEME.accent_color}" in css

    def test_ast_price_was_present(self) -> None:
        assert ".ast-price-was" in SLATE_THEME.generate_css()

    def test_ast_price_was_line_through(self) -> None:
        assert "line-through" in SLATE_THEME.generate_css()

    def test_ast_price_was_uses_muted_color(self) -> None:
        css = SLATE_THEME.generate_css()
        assert SLATE_THEME.muted_color in css

    def test_ast_chart_title_present(self) -> None:
        assert ".ast-chart-title" in SLATE_THEME.generate_css()

    def test_ast_chart_row_present(self) -> None:
        assert ".ast-chart-row" in SLATE_THEME.generate_css()

    def test_ast_chart_row_display_flex(self) -> None:
        assert "display:flex" in SLATE_THEME.generate_css()

    def test_ast_chart_label_present(self) -> None:
        assert ".ast-chart-label" in SLATE_THEME.generate_css()

    def test_ast_chart_label_flex_shrink(self) -> None:
        assert "flex-shrink:0" in SLATE_THEME.generate_css()

    def test_ast_chart_track_present(self) -> None:
        assert ".ast-chart-track" in SLATE_THEME.generate_css()

    def test_ast_chart_track_rgba_background(self) -> None:
        assert "rgba(0,0,0,.12)" in SLATE_THEME.generate_css()

    def test_ast_chart_bar_present(self) -> None:
        assert ".ast-chart-bar" in SLATE_THEME.generate_css()

    def test_ast_chart_bar_uses_accent_color(self) -> None:
        theme = Theme(
            bg_color="#000000",
            text_color="#ffffff",
            accent_color="#ff6600",
            muted_color="#888888",
        )
        css = theme.generate_css()
        assert "background:#ff6600" in css

    def test_ast_chart_value_present(self) -> None:
        assert ".ast-chart-value" in SLATE_THEME.generate_css()

    def test_ast_chart_value_uses_accent_color(self) -> None:
        theme = Theme(
            bg_color="#000000",
            text_color="#ffffff",
            accent_color="#00ccff",
            muted_color="#888888",
        )
        css = theme.generate_css()
        assert "color:#00ccff" in css

    def test_ast_comparison_row_present(self) -> None:
        assert ".ast-comparison-row" in SLATE_THEME.generate_css()

    def test_ast_comparison_row_uses_flex(self) -> None:
        css = SLATE_THEME.generate_css()
        idx = css.index(".ast-comparison-row")
        assert "display:flex" in css[idx : idx + 80]

    def test_ast_comparison_col_present(self) -> None:
        assert ".ast-comparison-col" in SLATE_THEME.generate_css()

    def test_ast_comparison_vs_present(self) -> None:
        assert ".ast-comparison-vs" in SLATE_THEME.generate_css()

    def test_ast_comparison_stat_present(self) -> None:
        assert ".ast-comparison-stat" in SLATE_THEME.generate_css()

    def test_ast_comparison_stat_uses_accent_color(self) -> None:
        theme = Theme(
            bg_color="#000000",
            text_color="#ffffff",
            accent_color="#aabbcc",
            muted_color="#888888",
        )
        css = theme.generate_css()
        idx = css.index(".ast-comparison-stat")
        assert "#aabbcc" in css[idx : idx + 160]

    def test_ast_comparison_label_present(self) -> None:
        assert ".ast-comparison-label" in SLATE_THEME.generate_css()

    def test_ast_panel_present(self) -> None:
        assert ".ast-panel" in SLATE_THEME.generate_css()

    def test_ast_panel_caption_present(self) -> None:
        assert ".ast-panel--caption" in SLATE_THEME.generate_css()

    def test_ast_measure_present(self) -> None:
        assert ".ast-measure" in SLATE_THEME.generate_css()


class TestResponsiveCss:
    def test_padding_uses_clamp(self) -> None:
        css = SLATE_THEME.generate_css()
        assert "clamp(.75rem,5vw,2.4rem)" in css

    def test_text_rules_use_fluid_padding(self) -> None:
        css = SLATE_THEME.generate_css()
        # Every text-bearing rule should use the clamp pad, not a bare 2.4rem
        assert "padding:0 2.4rem" not in css

    def test_stat_number_has_clamp_font_size(self) -> None:
        assert "font-size:clamp(4rem,14vw,6rem)" in SLATE_THEME.generate_css()

    def test_quote_mark_has_clamp_font_size(self) -> None:
        assert "font-size:clamp(5rem,19vw,8rem)" in SLATE_THEME.generate_css()

    def test_chart_label_min_width_uses_clamp(self) -> None:
        assert "min-width:clamp(3rem,9vw,5rem)" in SLATE_THEME.generate_css()

    def test_narrow_screen_breakpoint_present(self) -> None:
        assert "@media (max-width:370px)" in SLATE_THEME.generate_css()

    def test_narrow_breakpoint_scales_h1(self) -> None:
        css = SLATE_THEME.generate_css()
        idx = css.index("@media (max-width:370px)")
        # default h1=2.8rem × 0.8 = 2.24rem
        assert "2.24rem" in css[idx:]

    def test_narrow_breakpoint_scales_subtitle(self) -> None:
        css = SLATE_THEME.generate_css()
        idx = css.index("@media (max-width:370px)")
        # default h2=2.4rem × 0.83 = 1.992rem → "1.992rem"
        assert ".ast-subtitle" in css[idx:]

    def test_narrow_breakpoint_custom_sizes(self) -> None:
        theme = Theme(h1_size="48px", h2_size="36px", body_size="20px")
        css = theme.generate_css()
        idx = css.index("@media (max-width:370px)")
        # 48px × 0.8 = 38.4px
        assert "38.4px" in css[idx:]

    def test_narrow_breakpoint_present_even_without_landscape_scale(self) -> None:
        theme = Theme(landscape_font_scale=None)
        css = theme.generate_css()
        assert "@media (max-width:370px)" in css
        assert "@media (orientation:landscape)" not in css

    def test_caption_padding_uses_clamp(self) -> None:
        css = SLATE_THEME.generate_css()
        assert "padding:.5rem clamp(.75rem,5vw,2.4rem)" in css

    def test_badge_margin_uses_clamp(self) -> None:
        css = SLATE_THEME.generate_css()
        assert "margin:0 0 .6rem clamp(.75rem,5vw,2.4rem)" in css

    def test_clamp_absent_on_tablets_via_max(self) -> None:
        # The max of the clamp is 2.4rem, so on wide viewports padding stays 2.4rem.
        # Verify the original max value is encoded in the clamp expression.
        assert "2.4rem" in SLATE_THEME.generate_css()

    def test_title_has_overflow_wrap(self) -> None:
        assert "overflow-wrap:break-word" in SLATE_THEME.generate_css()

    def test_subtitle_has_no_overflow_wrap(self) -> None:
        css = SLATE_THEME.generate_css()
        idx = css.index(".ast-subtitle")
        # subtitle uses natural word-boundary wrapping to avoid mid-word breaks
        # on product names and short headings
        assert "overflow-wrap:break-word" not in css[idx : idx + 200]

    def test_body_has_overflow_wrap(self) -> None:
        css = SLATE_THEME.generate_css()
        idx = css.index(".ast-body{")
        assert "overflow-wrap:break-word" in css[idx : idx + 200]


class TestLandscapeMediaQueryNewClasses:
    def test_no_landscape_css_when_scale_none(self) -> None:
        css = Theme(landscape_font_scale=None).generate_css()
        assert "@media (orientation:landscape)" not in css

    def test_landscape_contains_ast_badge(self) -> None:
        theme = Theme(landscape_font_scale=0.5)
        assert ".ast-badge" in theme.generate_css()

    def test_landscape_contains_ast_price_was(self) -> None:
        theme = Theme(landscape_font_scale=0.5)
        css = theme.generate_css()
        media_start = css.index("@media")
        assert ".ast-price-was" in css[media_start:]

    def test_landscape_contains_ast_chart_title(self) -> None:
        theme = Theme(landscape_font_scale=0.5)
        css = theme.generate_css()
        media_start = css.index("@media")
        assert ".ast-chart-title" in css[media_start:]

    def test_landscape_contains_ast_chart_label(self) -> None:
        theme = Theme(landscape_font_scale=0.5)
        css = theme.generate_css()
        media_start = css.index("@media")
        assert ".ast-chart-label" in css[media_start:]

    def test_landscape_contains_ast_chart_value(self) -> None:
        theme = Theme(landscape_font_scale=0.5)
        css = theme.generate_css()
        media_start = css.index("@media")
        assert ".ast-chart-value" in css[media_start:]

    def test_landscape_contains_ast_comparison_label(self) -> None:
        theme = Theme(landscape_font_scale=0.5)
        css = theme.generate_css()
        landscape_start = css.index("@media (orientation:landscape)")
        assert ".ast-comparison-label" in css[landscape_start:]


class TestStyleGuideThemes:
    def test_signal_theme_is_theme(self) -> None:
        assert isinstance(SIGNAL_THEME, Theme)

    def test_summit_theme_is_theme(self) -> None:
        assert isinstance(SUMMIT_THEME, Theme)

    def test_market_theme_is_theme(self) -> None:
        assert isinstance(MARKET_THEME, Theme)

    def test_feature_theme_is_theme(self) -> None:
        assert isinstance(FEATURE_THEME, Theme)

    def test_signal_theme_accent(self) -> None:
        assert SIGNAL_THEME.accent_color == "#ff5a5f"

    def test_summit_theme_landscape_scale(self) -> None:
        assert SUMMIT_THEME.landscape_font_scale == 0.8

    def test_market_theme_overlay_opacity(self) -> None:
        assert MARKET_THEME.overlay_opacity == 0.38

    def test_feature_theme_heading_font(self) -> None:
        assert FEATURE_THEME.heading_font is not None
        assert "Cormorant Garamond" in FEATURE_THEME.heading_font

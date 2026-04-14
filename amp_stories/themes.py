"""Theme system for amp_stories.

A :class:`Theme` controls the colour palette, typography, and default
animations used by the page-factory functions in :mod:`amp_stories.templates`.
Call :meth:`Theme.generate_css` to get a stylesheet string ready to pass to
``Story.custom_css``::

    from amp_stories import Story, title_page, SLATE_THEME

    story = Story(
        ...,
        custom_css=SLATE_THEME.generate_css(),
        pages=[title_page("cover", "Hello World", background_src="hero.jpg")],
    )
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from amp_stories._validation import (
    ValidationError,
    validate_css_size,
    validate_hex_color,
)

if TYPE_CHECKING:
    from amp_stories._types import AnimateIn

_CSS_SIZE_RE = re.compile(r"^(\d+(?:\.\d+)?)(rem|px|pt|em)$")


def _scale_css_size(size: str, scale: float) -> str:
    """Scale a CSS size string by *scale*.

    Parses a validated CSS size like ``'3.2rem'`` or ``'24px'``, multiplies the
    numeric part by *scale*, and returns the formatted result with the same unit.
    """
    m = _CSS_SIZE_RE.match(size)
    assert m  # size was already validated via validate_css_size
    value = float(m.group(1)) * scale
    unit = m.group(2)
    return f"{value:.4f}".rstrip("0").rstrip(".") + unit


@dataclass
class Theme:
    """Visual theme controlling colours, typography, and animation defaults.

    Args:
        bg_color: Solid background colour used when no image is given.
        text_color: Primary text colour.
        accent_color: Accent colour for eyebrows, stats, quote marks, etc.
        muted_color: Secondary / muted text colour (attributions, captions).
        overlay_opacity: Darkness of the semi-transparent overlay placed over
            background images (0.0 = transparent, 1.0 = opaque).
        font_family: CSS font-family stack for body text.
        heading_font: CSS font-family for headings; falls back to *font_family*
            when ``None``.
        h1_size: CSS font-size for primary headings (e.g. ``'3.2rem'``).
        h2_size: CSS font-size for secondary headings.
        body_size: CSS font-size for body text.
        small_size: CSS font-size for small labels and captions.
        heading_animate_in: ``animate-in`` value applied to heading elements in
            page templates (``None`` disables animation).
        body_animate_in: ``animate-in`` value applied to body text in page
            templates.
        animate_in_duration: Duration applied to animated template elements.
        animate_in_delay: Delay applied to the *second* animated element on a
            page, creating a stagger effect.
    """

    # Colours
    bg_color: str = "#16213e"
    text_color: str = "#f5f5f5"
    accent_color: str = "#0f8b8d"
    muted_color: str = "#9e9eb0"
    overlay_opacity: float = 0.50

    # Typography
    font_family: str = "'Georgia', 'Times New Roman', serif"
    heading_font: str | None = None  # falls back to font_family

    # Font sizes (AMP recommends ≥ 24pt ≈ 1.5rem at 16px base)
    h1_size: str = "3.2rem"
    h2_size: str = "2.4rem"
    body_size: str = "1.6rem"
    small_size: str = "1.1rem"

    # Animation defaults used by page factory functions
    heading_animate_in: AnimateIn | None = "fly-in-bottom"
    body_animate_in: AnimateIn | None = "fade-in"
    animate_in_duration: str = "0.5s"
    animate_in_delay: str = "0.3s"

    # Desktop / landscape layout
    landscape_font_scale: float | None = None  # 0.1–2.0; None disables landscape CSS

    # Font loading
    google_font: str | None = None  # e.g. "Montserrat" or "Roboto:400,700"

    def __post_init__(self) -> None:
        validate_hex_color(self.bg_color, "Theme.bg_color")
        validate_hex_color(self.text_color, "Theme.text_color")
        validate_hex_color(self.accent_color, "Theme.accent_color")
        validate_hex_color(self.muted_color, "Theme.muted_color")
        if not 0.0 <= self.overlay_opacity <= 1.0:
            raise ValidationError(
                "Theme.overlay_opacity must be between 0.0 and 1.0. "
                f"Got: {self.overlay_opacity}"
            )
        validate_css_size(self.h1_size, "Theme.h1_size")
        validate_css_size(self.h2_size, "Theme.h2_size")
        validate_css_size(self.body_size, "Theme.body_size")
        validate_css_size(self.small_size, "Theme.small_size")
        if self.landscape_font_scale is not None and not 0.1 <= self.landscape_font_scale <= 2.0:
            raise ValidationError(
                "Theme.landscape_font_scale must be between 0.1 and 2.0. "
                f"Got: {self.landscape_font_scale}"
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _heading_font_css(self) -> str:
        return self.heading_font if self.heading_font is not None else self.font_family

    def _overlay_rgba(self) -> str:
        alpha = round(self.overlay_opacity, 3)
        return f"rgba(0,0,0,{alpha})"

    def get_google_fonts_url(self) -> str | None:
        """Return the Google Fonts CSS URL for this theme's font, or ``None``.

        Use the result with :attr:`~amp_stories.story.Story.font_links`::

            story = Story(..., font_links=[theme.get_google_fonts_url()])
        """
        if self.google_font is None:
            return None
        from urllib.parse import quote  # noqa: PLC0415

        return f"https://fonts.googleapis.com/css2?family={quote(self.google_font)}&display=swap"

    # ------------------------------------------------------------------
    # CSS generation
    # ------------------------------------------------------------------

    def generate_css(self) -> str:
        """Return a CSS string defining all ``.ast-*`` classes for this theme.

        The result should be passed to :attr:`~amp_stories.story.Story.custom_css`
        so that page-template elements render correctly.
        """
        hf = self._heading_font_css()
        bf = self.font_family
        tc = self.text_color
        ac = self.accent_color
        mc = self.muted_color
        bg = self.bg_color
        ov = self._overlay_rgba()
        h1 = self.h1_size
        h2 = self.h2_size
        bs = self.body_size
        sm = self.small_size

        rules: list[str] = [
            # Background div — used when no background image is provided
            f".ast-bg{{background-color:{bg}}}",
            # Overlay — darkens a background image for text legibility
            f".ast-overlay{{background:{ov}}}",
            # Eyebrow — small uppercase category label
            (
                f".ast-eyebrow{{font-family:{bf};font-size:{sm};"
                f"color:{ac};letter-spacing:.12em;text-transform:uppercase;"
                f"margin:0 0 .6rem;padding:0 2.4rem}}"
            ),
            # Primary heading
            (
                f".ast-title{{font-family:{hf};font-size:{h1};"
                f"font-weight:700;color:{tc};line-height:1.15;"
                f"margin:0;padding:0 2.4rem}}"
            ),
            # Secondary heading / subtitle
            (
                f".ast-subtitle{{font-family:{hf};font-size:{h2};"
                f"font-weight:400;color:{tc};line-height:1.2;"
                f"margin:.8rem 0 0;padding:0 2.4rem}}"
            ),
            # Body text
            (
                f".ast-body{{font-family:{bf};font-size:{bs};"
                f"color:{tc};line-height:1.55;margin:0;padding:0 2.4rem}}"
            ),
            # Attribution / author line
            (
                f".ast-attribution{{font-family:{bf};font-size:{sm};"
                f"color:{mc};font-style:italic;margin:1.2rem 0 0;padding:0 2.4rem}}"
            ),
            # Decorative opening quotation mark
            (
                f".ast-quote-mark{{font-family:{hf};font-size:8rem;"
                f"color:{ac};line-height:.8;margin:0;padding:0 2rem 0 2.4rem}}"
            ),
            # Large stat number
            (
                f".ast-stat-number{{font-family:{hf};font-size:6rem;"
                f"font-weight:900;color:{ac};line-height:1;"
                f"margin:0;padding:0 2.4rem}}"
            ),
            # Stat descriptor label
            (
                f".ast-stat-label{{font-family:{bf};font-size:{bs};"
                f"color:{tc};text-transform:uppercase;letter-spacing:.08em;"
                f"margin:.5rem 0 0;padding:0 2.4rem}}"
            ),
            # Image caption bar
            (
                f".ast-caption{{font-family:{bf};font-size:{sm};"
                f"color:{tc};background:rgba(0,0,0,.55);"
                f"padding:.5rem 2.4rem;margin:0}}"
            ),
            # Chapter / part number label
            (
                f".ast-chapter-number{{font-family:{bf};font-size:{sm};"
                f"color:{ac};letter-spacing:.2em;text-transform:uppercase;"
                f"margin:0 0 .6rem;padding:0 2.4rem}}"
            ),
            # Chapter divider heading
            (
                f".ast-chapter-title{{font-family:{hf};font-size:{h1};"
                f"font-weight:700;color:{tc};line-height:1.15;"
                f"margin:0;padding:0 2.4rem}}"
            ),
        ]

        if self.landscape_font_scale is not None:
            s = self.landscape_font_scale
            rules.append(
                "@media (orientation:landscape){"
                f".ast-title{{font-size:{_scale_css_size(h1, s)}}}"
                f".ast-chapter-title{{font-size:{_scale_css_size(h1, s)}}}"
                f".ast-subtitle{{font-size:{_scale_css_size(h2, s)}}}"
                f".ast-body{{font-size:{_scale_css_size(bs, s)}}}"
                f".ast-stat-label{{font-size:{_scale_css_size(bs, s)}}}"
                f".ast-eyebrow{{font-size:{_scale_css_size(sm, s)}}}"
                f".ast-attribution{{font-size:{_scale_css_size(sm, s)}}}"
                f".ast-caption{{font-size:{_scale_css_size(sm, s)}}}"
                f".ast-chapter-number{{font-size:{_scale_css_size(sm, s)}}}"
                "}"
            )

        return "".join(rules)


# ---------------------------------------------------------------------------
# Built-in theme
# ---------------------------------------------------------------------------

#: Dark slate/navy theme with near-white text and teal accent.
#: This is the default theme used by all page factory functions.
SLATE_THEME: Theme = Theme()

#: Clean light theme with white background, near-black text, and blue accent.
LIGHT_THEME: Theme = Theme(
    bg_color="#ffffff",
    text_color="#1a1a1a",
    accent_color="#2563eb",
    muted_color="#6b7280",
)

#: High-contrast editorial theme with near-black background, white text, and red accent.
EDITORIAL_THEME: Theme = Theme(
    bg_color="#0a0a0a",
    text_color="#f8f8f8",
    accent_color="#e63946",
    muted_color="#888888",
)

#: Warm theme with off-white background, rich brown text, and amber accent.
WARM_THEME: Theme = Theme(
    bg_color="#fdf6ec",
    text_color="#3d2b1f",
    accent_color="#d97706",
    muted_color="#a87c5f",
)

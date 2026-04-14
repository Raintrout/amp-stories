"""High-level page factory functions for common AMP Story page types.

Each function returns a ready-to-use :class:`~amp_stories.page.Page` styled
with the provided :class:`~amp_stories.themes.Theme`.  The pages use
``.ast-*`` CSS classes — you must apply the theme stylesheet to the story::

    from amp_stories import Story, SUMMIT_THEME, quote_page, title_page

    story = Story(
        title="My Story",
        publisher="Acme",
        publisher_logo_src="https://example.com/logo.png",
        poster_portrait_src="https://example.com/poster.jpg",
        canonical_url="https://example.com/story.html",
        custom_css=SUMMIT_THEME.generate_css(),
        pages=[
            title_page("cover", "Hello World",
                       subtitle="A great story",
                       background_src="https://example.com/hero.jpg"),
            quote_page("q1", "The only way to do great work is to love it.",
                       attribution="— Steve Jobs"),
            stat_page("s1", "92%", "of users prefer visual stories"),
        ],
    )
    story.save("story.html")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from amp_stories._validation import ValidationError
from amp_stories.elements import AmpImg, AmpVideo, DivElement, StoryPanningMedia, TextElement
from amp_stories.layer import Layer
from amp_stories.outlink import PageOutlink
from amp_stories.page import Page
from amp_stories.themes import SUMMIT_THEME, Theme

if TYPE_CHECKING:
    from collections.abc import Iterable

    from amp_stories._types import AnimateIn, LayerTemplate

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ChartRow:
    """One row in a :func:`data_chart_page` bar-chart visualization.

    Args:
        label: Left-side row label (e.g. ``"Python"``).
        value: Numeric value; bar width = ``value / max_value * 100%``.
        display: String shown after the bar.  Defaults to ``f"{value:.4g}"``.
    """

    label: str
    value: float
    display: str | None = None


@dataclass(frozen=True)
class MotionPreset:
    """Shared animation and media behavior for page templates."""

    name: str
    heading_animate_in: AnimateIn | None = None
    body_animate_in: AnimateIn | None = None
    animate_in_duration: str | None = None
    animate_in_delay: str | None = None
    background_media: Literal["static", "panning"] = "static"


@dataclass(frozen=True)
class LayoutPreset:
    """Shared layer placement and wrapper treatment for page templates."""

    name: str
    layer_template: LayerTemplate = "vertical"
    layer_style: str | None = None
    wrapper_class: str | None = None
    wrapper_style: str | None = None


EDITORIAL_SOFT_MOTION = MotionPreset("editorial-soft")
ADVENTURE_CINEMATIC_MOTION = MotionPreset(
    "adventure-cinematic",
)
COMMERCE_CRISP_MOTION = MotionPreset(
    "commerce-crisp",
)

BOTTOM_STACK_LAYOUT = LayoutPreset(
    "bottom-stack",
    layer_style="justify-content:end;align-content:end;padding:0 0 clamp(1.2rem,8vw,3rem)",
)
TOP_STACK_LAYOUT = LayoutPreset(
    "top-stack",
    layer_style="justify-content:start;align-content:start;padding:clamp(1.2rem,8vw,3rem) 0 0",
)
CENTER_FOCUS_LAYOUT = LayoutPreset(
    "center-focus",
    layer_style="justify-content:center;align-content:center",
)
CAPTION_BAND_LAYOUT = LayoutPreset(
    "caption-band",
    layer_style="justify-content:end;align-content:end;padding:0",
)
CARD_OVERLAY_LAYOUT = LayoutPreset(
    "card-overlay",
    layer_style=(
        "justify-content:end;align-content:end;"
        "padding:0 clamp(.75rem,5vw,2.4rem) clamp(1.2rem,8vw,3rem)"
    ),
    wrapper_class="ast-panel ast-panel--card ast-measure",
)
SPLIT_PANEL_LAYOUT = LayoutPreset(
    "split-panel",
    layer_style="justify-content:center;align-content:center",
)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _background_layers(
    background_src: str | None,
    theme: Theme,
    *,
    motion: MotionPreset | None = None,
    overlay: bool = True,
) -> list[Layer]:
    """Return the background layers for a page.

    - No image: one fill layer with a solid-colour ``.ast-bg`` div.
    - Image provided: a fill layer with the image, *plus* a fill layer with
      a semi-transparent ``.ast-overlay`` div for text legibility.
    """
    if background_src is None:
        return [Layer("fill", children=[DivElement(class_="ast-bg")])]
    background_child = (
        StoryPanningMedia(background_src)
        if motion is not None and motion.background_media == "panning"
        else AmpImg(background_src, alt="")
    )
    if not overlay:
        return [Layer("fill", children=[background_child])]
    return [
        Layer("fill", children=[background_child]),
        Layer("fill", children=[DivElement(class_="ast-overlay")]),
    ]


def _motion_heading(theme: Theme, motion: MotionPreset | None) -> AnimateIn | None:
    if motion is not None and motion.heading_animate_in is not None:
        return motion.heading_animate_in
    return theme.heading_animate_in


def _motion_body(theme: Theme, motion: MotionPreset | None) -> AnimateIn | None:
    if motion is not None and motion.body_animate_in is not None:
        return motion.body_animate_in
    return theme.body_animate_in


def _motion_duration(theme: Theme, motion: MotionPreset | None) -> str | None:
    if motion is not None and motion.animate_in_duration is not None:
        return motion.animate_in_duration
    return theme.animate_in_duration


def _motion_delay(theme: Theme, motion: MotionPreset | None) -> str | None:
    if motion is not None and motion.animate_in_delay is not None:
        return motion.animate_in_delay
    return theme.animate_in_delay


def _text(
    tag: Literal["h1", "h2", "p", "blockquote"],
    text: str,
    *,
    class_: str,
    role: Literal["heading", "body"],
    theme: Theme,
    motion: MotionPreset | None,
    delay: bool = False,
    style: str | None = None,
) -> TextElement:
    return TextElement(
        tag,
        text,
        class_=class_,
        style=style,
        animate_in=_motion_heading(theme, motion)
        if role == "heading"
        else _motion_body(theme, motion),
        animate_in_duration=_motion_duration(theme, motion),
        animate_in_delay=_motion_delay(theme, motion) if delay else None,
    )


def _content_layer(
    children: Iterable[TextElement | DivElement],
    *,
    layout: LayoutPreset,
) -> Layer:
    layer_children = list(children)
    if layout.wrapper_class is not None or layout.wrapper_style is not None:
        layer_children = [  # type: ignore[assignment]
            DivElement(
                children=list(layer_children),  # type: ignore[arg-type]
                class_=layout.wrapper_class,
                style=layout.wrapper_style,
            )
        ]
    return Layer(
        layout.layer_template,  # type: ignore[arg-type]
        children=list(layer_children),  # type: ignore[arg-type]
        style=layout.layer_style,
    )


# ---------------------------------------------------------------------------
# Page factories
# ---------------------------------------------------------------------------


def title_page(
    page_id: str,
    title: str,
    *,
    subtitle: str | None = None,
    eyebrow: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = ADVENTURE_CINEMATIC_MOTION,
) -> Page:
    """Create a cover / title page.

    Args:
        page_id: Unique page id.
        title: Main headline text.
        subtitle: Optional secondary line below the title.
        eyebrow: Optional small uppercase label above the title.
        background_src: URL of a background image.  When omitted, the theme's
            ``bg_color`` is used as a solid-colour background.
        auto_advance_after: CSS duration (e.g. ``'5s'``) after which the page
            auto-advances.
        theme: Visual theme to apply.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = []

    if eyebrow is not None:
        text_children.append(
            _text("p", eyebrow, class_="ast-eyebrow", role="heading", theme=theme, motion=motion)
        )

    text_children.append(
        _text(
            "h1",
            title,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=eyebrow is not None,
        )
    )

    if subtitle is not None:
        text_children.append(
            _text(
                "h2",
                subtitle,
                class_="ast-subtitle",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def quote_page(
    page_id: str,
    quote: str,
    *,
    attribution: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CENTER_FOCUS_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a pull-quote page.

    Args:
        page_id: Unique page id.
        quote: The quotation text.
        attribution: Optional author / source line.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = [
        TextElement("p", "\u201c", class_="ast-quote-mark"),
        _text("blockquote", quote, class_="ast-body", role="heading", theme=theme, motion=motion),
    ]

    if attribution is not None:
        text_children.append(
            _text(
                "p",
                attribution,
                class_="ast-attribution",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def stat_page(
    page_id: str,
    stat: str,
    label: str,
    *,
    context: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CENTER_FOCUS_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a statistic / data-point page.

    Args:
        page_id: Unique page id.
        stat: The headline figure (e.g. ``'92%'`` or ``'1.4B'``).
        label: Short descriptor for the stat.
        context: Optional additional sentence of context.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = [
        _text("p", stat, class_="ast-stat-number", role="heading", theme=theme, motion=motion),
        _text(
            "p", label, class_="ast-stat-label", role="body", theme=theme, motion=motion, delay=True
        ),
    ]

    if context is not None:
        text_children.append(
            _text(
                "p", context, class_="ast-body", role="body", theme=theme, motion=motion, delay=True
            )
        )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def chapter_page(
    page_id: str,
    chapter_title: str,
    *,
    chapter_number: int | str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CENTER_FOCUS_LAYOUT,
    motion: MotionPreset | None = ADVENTURE_CINEMATIC_MOTION,
) -> Page:
    """Create a chapter / section divider page.

    Args:
        page_id: Unique page id.
        chapter_title: The chapter or section title.
        chapter_number: Optional chapter number or label (e.g. ``1``, ``'Part I'``).
            When an integer is given it is formatted as ``'Part N'``.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = []

    if chapter_number is not None:
        label = f"Part {chapter_number}" if isinstance(chapter_number, int) else str(chapter_number)
        text_children.append(
            _text(
                "p", label, class_="ast-chapter-number", role="heading", theme=theme, motion=motion
            )
        )

    text_children.append(
        _text(
            "h1",
            chapter_title,
            class_="ast-chapter-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=chapter_number is not None,
        )
    )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def trip_page(
    page_id: str,
    number: int,
    location: str,
    *,
    region: str | None = None,
    highlight: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = ADVENTURE_CINEMATIC_MOTION,
) -> Page:
    """Create a numbered trip-card page.

    Designed for series of entries (expeditions, destinations, episodes) where
    each page follows the same structure: a sequential number, a place name,
    an optional region label, and an optional one-line highlight.

    Args:
        page_id: Unique page id.
        number: Trip / entry number (rendered as ``TRIP 01``, ``TRIP 02`` …).
        location: Primary location or trip name.
        region: Optional region or area label shown below the location.
        highlight: Optional one-sentence memorable detail.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = [
        _text(
            "p",
            f"TRIP {number:02d}",
            class_="ast-eyebrow",
            role="heading",
            theme=theme,
            motion=motion,
        ),
        _text(
            "h1",
            location,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=True,
        ),
    ]

    if region is not None:
        text_children.append(
            _text(
                "h2",
                region,
                class_="ast-subtitle",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    if highlight is not None:
        text_children.append(
            _text(
                "p",
                highlight,
                class_="ast-body",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def cta_page(
    page_id: str,
    heading_text: str,
    *,
    body: str | None = None,
    cta_text: str = "Read more",
    cta_url: str,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = COMMERCE_CRISP_MOTION,
) -> Page:
    """Create a call-to-action finale page with a swipe-up link button.

    The page shows a heading and optional body text, with a
    :class:`~amp_stories.outlink.PageOutlink` button styled using the theme's
    accent colour.

    Args:
        page_id: Unique page id.
        heading_text: Primary CTA heading.
        body: Optional supporting sentence below the heading.
        cta_text: Label on the outlink button.  Defaults to ``'Read more'``.
        cta_url: Destination URL for the button (required).
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = [
        _text("h1", heading_text, class_="ast-title", role="heading", theme=theme, motion=motion),
    ]

    if body is not None:
        text_children.append(
            _text("p", body, class_="ast-body", role="body", theme=theme, motion=motion, delay=True)
        )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))

    outlink = PageOutlink(
        href=cta_url,
        cta_text=cta_text,
        theme="custom",
        cta_accent_color=theme.accent_color,
        cta_accent_element="background",
    )

    return Page(
        page_id,
        layers=layers,
        outlink=outlink,
        auto_advance_after=auto_advance_after,
    )


def photo_page(
    page_id: str,
    image_src: str,
    *,
    overlay: bool = False,
    caption: str | None = None,
    eyebrow: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CAPTION_BAND_LAYOUT,
    motion: MotionPreset | None = ADVENTURE_CINEMATIC_MOTION,
) -> Page:
    """Create a full-bleed photo page.

    The image fills the entire page.  An optional caption and/or eyebrow
    label are overlaid using a ``'vertical'`` text layer.

    Args:
        page_id: Unique page id.
        image_src: URL of the full-bleed photo.
        overlay: When ``True``, adds a semi-transparent ``.ast-overlay`` layer
            between the image and text to improve text legibility.
        caption: Optional caption text displayed over the image.
        eyebrow: Optional small uppercase label above the caption.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    layers: list[Layer] = [
        Layer(
            "fill",
            children=[
                StoryPanningMedia(image_src)
                if motion is not None and motion.background_media == "panning"
                else AmpImg(image_src, alt="")
            ],
        ),
    ]
    if overlay:
        layers.append(Layer("fill", children=[DivElement(class_="ast-overlay")]))

    text_children: list[TextElement] = []
    if eyebrow is not None:
        text_children.append(
            _text("p", eyebrow, class_="ast-eyebrow", role="heading", theme=theme, motion=motion)
        )
    if caption is not None:
        text_children.append(
            _text(
                "p",
                caption,
                class_="ast-caption",
                role="body",
                theme=theme,
                motion=motion,
                delay=eyebrow is not None,
            )
        )

    if text_children:
        layers.append(_content_layer(text_children, layout=layout))

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def video_page(
    page_id: str,
    src: str,
    *,
    poster: str | None = None,
    caption: str | None = None,
    eyebrow: str | None = None,
    autoplay: bool = True,
    loop: bool = True,
    muted: bool = True,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CAPTION_BAND_LAYOUT,
    motion: MotionPreset | None = ADVENTURE_CINEMATIC_MOTION,
) -> Page:
    """Create a full-bleed video page.

    The video fills the entire page.  An optional *caption* and/or *eyebrow*
    label are overlaid in a ``'vertical'`` text layer.

    Args:
        page_id: Unique page id.
        src: URL of the video file.
        poster: Optional poster image URL shown before playback starts.
        caption: Optional caption text displayed over the video.
        eyebrow: Optional small uppercase label displayed above the caption.
        autoplay: Auto-play the video when the page becomes active.
        loop: Loop the video continuously.
        muted: Mute the video (required for autoplay in most browsers).
        auto_advance_after: CSS duration or media element id after which the
            page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    layers: list[Layer] = [
        Layer(
            "fill",
            children=[AmpVideo(src, poster=poster, autoplay=autoplay, loop=loop, muted=muted)],
        )
    ]

    text_children: list[TextElement] = []
    if eyebrow is not None:
        text_children.append(
            _text("p", eyebrow, class_="ast-eyebrow", role="heading", theme=theme, motion=motion)
        )
    if caption is not None:
        text_children.append(
            _text(
                "p",
                caption,
                class_="ast-caption",
                role="body",
                theme=theme,
                motion=motion,
                delay=eyebrow is not None,
            )
        )

    if text_children:
        layers.append(_content_layer(text_children, layout=layout))

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def text_page(
    page_id: str,
    heading: str,
    body: str,
    *,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a text-focused content page with a heading and body paragraph.

    Args:
        page_id: Unique page id.
        heading: Section heading text.
        body: Body paragraph text.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = [
        _text("h2", heading, class_="ast-subtitle", role="heading", theme=theme, motion=motion),
        _text("p", body, class_="ast-body", role="body", theme=theme, motion=motion, delay=True),
    ]

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def listicle_page(
    page_id: str,
    title: str,
    items: list[str],
    *,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a bullet-list page.

    Args:
        page_id: Unique page id.
        title: Heading for the list.
        items: Non-empty list of bullet-point strings.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.

    Raises:
        ValidationError: If *items* is empty.
    """
    if not items:
        raise ValidationError("listicle_page: items must not be empty.")

    text_children: list[TextElement] = [
        _text("h2", title, class_="ast-subtitle", role="heading", theme=theme, motion=motion),
    ]
    for item in items:
        text_children.append(
            _text(
                "p",
                f"\u2022 {item}",
                class_="ast-body",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def comparison_page(
    page_id: str,
    left_stat: str,
    left_label: str,
    right_stat: str,
    right_label: str,
    *,
    eyebrow: str | None = None,
    versus: str = "VS",
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = SPLIT_PANEL_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a two-column stat comparison page.

    Renders a side-by-side flex layout with an optional ``versus`` label in the
    centre.  Pairs well with :func:`stat_page` for building data stories.

    Args:
        page_id: Unique page id.
        left_stat: Large figure for the left column.
        left_label: Descriptor for the left stat.
        right_stat: Large figure for the right column.
        right_label: Descriptor for the right stat.
        eyebrow: Optional label shown at the top of the page.
        versus: Text shown between the two columns.  Defaults to ``'VS'``.
            Pass an empty string to suppress the centre label.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    layers = _background_layers(background_src, theme, motion=motion)

    # Build the two stat columns
    left_col = DivElement(
        class_="ast-comparison-col",
        children=[  # type: ignore[arg-type]
            TextElement(
                "p",
                left_stat,
                class_="ast-comparison-stat",
                animate_in=_motion_heading(theme, motion),
                animate_in_duration=_motion_duration(theme, motion),
            ),
            TextElement(
                "p",
                left_label,
                class_="ast-comparison-label",
                animate_in=_motion_body(theme, motion),
                animate_in_duration=_motion_duration(theme, motion),
                animate_in_delay=_motion_delay(theme, motion),
            ),
        ],
    )
    right_col = DivElement(
        class_="ast-comparison-col",
        children=[  # type: ignore[arg-type]
            TextElement(
                "p",
                right_stat,
                class_="ast-comparison-stat",
                animate_in=_motion_heading(theme, motion),
                animate_in_duration=_motion_duration(theme, motion),
            ),
            TextElement(
                "p",
                right_label,
                class_="ast-comparison-label",
                animate_in=_motion_body(theme, motion),
                animate_in_duration=_motion_duration(theme, motion),
                animate_in_delay=_motion_delay(theme, motion),
            ),
        ],
    )

    row_children: list[DivElement] = [left_col]
    if versus:
        row_children.append(
            DivElement(
                class_="ast-comparison-vs",
                children=[  # type: ignore[arg-type]
                    TextElement(
                        "p",
                        versus,
                        class_="ast-eyebrow",
                        animate_in=_motion_heading(theme, motion),
                        animate_in_duration=_motion_duration(theme, motion),
                    ),
                ],
            )
        )
    row_children.append(right_col)

    text_children: list[TextElement | DivElement] = []
    if eyebrow is not None:
        text_children.append(
            _text("p", eyebrow, class_="ast-eyebrow", role="heading", theme=theme, motion=motion)
        )
    text_children.append(
        DivElement(class_="ast-comparison-row", children=list(row_children))  # type: ignore[arg-type]
    )

    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def breaking_page(
    page_id: str,
    headline: str,
    *,
    badge: str = "BREAKING",
    body: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = TOP_STACK_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a breaking-news alert page.

    Displays a prominent badge (e.g. ``'BREAKING'``) above the headline.
    Pairs well with :data:`~amp_stories.themes.SIGNAL_THEME`.

    Args:
        page_id: Unique page id.
        headline: Main news headline.
        badge: Badge text shown above the headline.  Defaults to ``'BREAKING'``.
        body: Optional one-sentence summary below the headline.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = [
        _text("p", badge, class_="ast-badge", role="heading", theme=theme, motion=motion),
        _text(
            "h1",
            headline,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=True,
        ),
    ]

    if body is not None:
        text_children.append(
            _text("p", body, class_="ast-body", role="body", theme=theme, motion=motion, delay=True)
        )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def update_page(
    page_id: str,
    number: int,
    headline: str,
    body: str,
    *,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a numbered live-update card.

    Shows ``'UPDATE N'`` as an eyebrow above the headline and body.
    Useful for series of live news updates or episode recaps.

    Args:
        page_id: Unique page id.
        number: Update number (rendered as ``UPDATE 1``, ``UPDATE 2`` …).
        headline: Update headline.
        body: Body text for the update.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = [
        _text(
            "p",
            f"UPDATE {number}",
            class_="ast-eyebrow",
            role="heading",
            theme=theme,
            motion=motion,
        ),
        _text(
            "h1",
            headline,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=True,
        ),
        _text("p", body, class_="ast-body", role="body", theme=theme, motion=motion, delay=True),
    ]

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def itinerary_page(
    page_id: str,
    day: int | str,
    destination: str,
    *,
    details: list[str] | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = ADVENTURE_CINEMATIC_MOTION,
) -> Page:
    """Create a travel itinerary card.

    Shows a day label (``DAY N`` for integers, or the string verbatim) above
    the destination name and optional detail lines.
    Pairs well with :data:`~amp_stories.themes.SUMMIT_THEME`.

    Args:
        page_id: Unique page id.
        day: Day number (int → ``'DAY N'``) or a custom label string.
        destination: Destination or stop name.
        details: Optional list of detail strings (activities, highlights, etc.).
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    day_label = f"DAY {day}" if isinstance(day, int) else str(day)
    text_children: list[TextElement] = [
        _text(
            "p", day_label, class_="ast-chapter-number", role="heading", theme=theme, motion=motion
        ),
        _text(
            "h1",
            destination,
            class_="ast-chapter-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=True,
        ),
    ]

    if details:
        for detail in details:
            text_children.append(
                _text(
                    "p",
                    detail,
                    class_="ast-body",
                    role="body",
                    theme=theme,
                    motion=motion,
                    delay=True,
                )
            )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def data_chart_page(
    page_id: str,
    title: str,
    rows: list[ChartRow],
    *,
    max_value: float | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = SPLIT_PANEL_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a horizontal bar-chart data page.

    Each :class:`ChartRow` renders as a labelled bar scaled relative to the
    maximum value in the dataset (or a custom *max_value*).

    Args:
        page_id: Unique page id.
        title: Chart title shown above the bars.
        rows: Non-empty list of :class:`ChartRow` items.
        max_value: Optional explicit maximum value for bar scaling.  Defaults
            to the largest ``value`` in *rows*.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.

    Raises:
        ValidationError: If *rows* is empty.
    """
    if not rows:
        raise ValidationError("data_chart_page: rows must not be empty.")

    effective_max = max_value if max_value is not None else max(r.value for r in rows)

    title_el = _text(
        "h2", title, class_="ast-chart-title", role="heading", theme=theme, motion=motion
    )

    row_divs: list[DivElement] = []
    for row in rows:
        pct = min(row.value / effective_max * 100, 100) if effective_max else 0
        display = row.display if row.display is not None else f"{row.value:.4g}"
        row_divs.append(
            DivElement(
                class_="ast-chart-row",
                children=[
                    TextElement("span", row.label, class_="ast-chart-label"),
                    DivElement(
                        class_="ast-chart-track",
                        children=[
                            TextElement(
                                "span",
                                "",
                                class_="ast-chart-bar",
                                style=f"width:{pct:.4g}%",
                            )
                        ],
                    ),
                    TextElement("span", display, class_="ast-chart-value"),
                ],
            )
        )

    chart_children: list[TextElement | DivElement] = [title_el, *row_divs]
    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(chart_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def product_page(
    page_id: str,
    product_name: str,
    *,
    brand: str | None = None,
    price: str | None = None,
    was_price: str | None = None,
    image_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = COMMERCE_CRISP_MOTION,
) -> Page:
    """Create a product showcase page.

    Displays a brand eyebrow, product name, optional "was" price (struck
    through), and current price.  Pairs well with
    :data:`~amp_stories.themes.MARKET_THEME`.

    Args:
        page_id: Unique page id.
        product_name: Product title.
        brand: Optional brand / category eyebrow label.
        price: Optional current price string (e.g. ``'$49.99'``).
        was_price: Optional original price string shown with strikethrough.
        image_src: URL of a product / background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = []

    if brand is not None:
        text_children.append(
            _text("p", brand, class_="ast-eyebrow", role="heading", theme=theme, motion=motion)
        )

    text_children.append(
        _text(
            "h2",
            product_name,
            class_="ast-subtitle",
            role="heading",
            theme=theme,
            motion=motion,
            delay=brand is not None,
        )
    )

    if was_price is not None:
        text_children.append(
            _text(
                "p",
                was_price,
                class_="ast-price-was",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    if price is not None:
        text_children.append(
            _text(
                "p",
                price,
                class_="ast-stat-number",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    layers = _background_layers(image_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def deal_page(
    page_id: str,
    title: str,
    *,
    badge: str | None = None,
    description: str | None = None,
    price: str | None = None,
    was_price: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = COMMERCE_CRISP_MOTION,
) -> Page:
    """Create a deal / promotion highlight page.

    Designed for showcasing offers: an optional badge (``'SALE'``, ``'50% OFF'``),
    a deal title, optional description, and optional price information.
    Pairs well with :data:`~amp_stories.themes.MARKET_THEME`.

    Args:
        page_id: Unique page id.
        title: Deal headline.
        badge: Optional badge label (e.g. ``'SALE'`` or ``'LIMITED TIME'``).
        description: Optional one-sentence deal description.
        price: Optional current price string.
        was_price: Optional original price string shown with strikethrough.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SUMMIT_THEME`.
    """
    text_children: list[TextElement] = []

    if badge is not None:
        text_children.append(
            _text("p", badge, class_="ast-badge", role="heading", theme=theme, motion=motion)
        )

    text_children.append(
        _text(
            "h1",
            title,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=badge is not None,
        )
    )

    if description is not None:
        text_children.append(
            _text(
                "p",
                description,
                class_="ast-body",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    if was_price is not None:
        text_children.append(
            _text(
                "p",
                was_price,
                class_="ast-price-was",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    if price is not None:
        text_children.append(
            _text(
                "p",
                price,
                class_="ast-stat-number",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )

    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def timeline_step_page(
    page_id: str,
    label: str,
    headline: str,
    *,
    body: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a timeline or sequence step page."""
    text_children: list[TextElement] = [
        _text("p", label, class_="ast-eyebrow", role="heading", theme=theme, motion=motion),
        _text(
            "h1",
            headline,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=True,
        ),
    ]
    if body is not None:
        text_children.append(
            _text("p", body, class_="ast-body", role="body", theme=theme, motion=motion, delay=True)
        )
    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def fact_check_page(
    page_id: str,
    claim: str,
    verdict: str,
    *,
    explanation: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CARD_OVERLAY_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a fact-check style page with claim, verdict, and explanation."""
    text_children: list[TextElement] = [
        _text("p", "FACT CHECK", class_="ast-badge", role="heading", theme=theme, motion=motion),
        _text("p", claim, class_="ast-body", role="body", theme=theme, motion=motion, delay=True),
        _text(
            "h1",
            verdict,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=True,
        ),
    ]
    if explanation is not None:
        text_children.append(
            _text(
                "p",
                explanation,
                class_="ast-attribution",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )
    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def key_takeaways_page(
    page_id: str,
    title: str,
    takeaways: list[str],
    *,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CARD_OVERLAY_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a compact key takeaways page."""
    if not takeaways:
        raise ValidationError("key_takeaways_page: takeaways must not be empty.")
    text_children: list[TextElement] = [
        _text("h2", title, class_="ast-subtitle", role="heading", theme=theme, motion=motion),
    ]
    for takeaway in takeaways:
        text_children.append(
            _text(
                "p",
                f"\u2022 {takeaway}",
                class_="ast-body",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )
    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def process_step_page(
    page_id: str,
    step_label: str,
    title: str,
    body: str,
    *,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CARD_OVERLAY_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a process or explainer step page."""
    text_children: list[TextElement] = [
        _text(
            "p", step_label, class_="ast-chapter-number", role="heading", theme=theme, motion=motion
        ),
        _text(
            "h1",
            title,
            class_="ast-chapter-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=True,
        ),
        _text("p", body, class_="ast-body", role="body", theme=theme, motion=motion, delay=True),
    ]
    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def hero_video_page(
    page_id: str,
    src: str,
    headline: str,
    *,
    eyebrow: str | None = None,
    subtitle: str | None = None,
    poster: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = BOTTOM_STACK_LAYOUT,
    motion: MotionPreset | None = ADVENTURE_CINEMATIC_MOTION,
) -> Page:
    """Create a cinematic video-led hero page."""
    layers: list[Layer] = [
        Layer(
            "fill", children=[AmpVideo(src, poster=poster, autoplay=True, loop=True, muted=True)]
        ),
        Layer("fill", children=[DivElement(class_="ast-overlay")]),
    ]
    text_children: list[TextElement] = []
    if eyebrow is not None:
        text_children.append(
            _text("p", eyebrow, class_="ast-eyebrow", role="heading", theme=theme, motion=motion)
        )
    text_children.append(
        _text(
            "h1",
            headline,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=eyebrow is not None,
        )
    )
    if subtitle is not None:
        text_children.append(
            _text(
                "h2",
                subtitle,
                class_="ast-subtitle",
                role="body",
                theme=theme,
                motion=motion,
                delay=True,
            )
        )
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def card_overlay_page(
    page_id: str,
    heading: str,
    *,
    body: str | None = None,
    eyebrow: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SUMMIT_THEME,
    layout: LayoutPreset = CARD_OVERLAY_LAYOUT,
    motion: MotionPreset | None = EDITORIAL_SOFT_MOTION,
) -> Page:
    """Create a generic card-overlay page for busy imagery."""
    text_children: list[TextElement] = []
    if eyebrow is not None:
        text_children.append(
            _text("p", eyebrow, class_="ast-eyebrow", role="heading", theme=theme, motion=motion)
        )
    text_children.append(
        _text(
            "h1",
            heading,
            class_="ast-title",
            role="heading",
            theme=theme,
            motion=motion,
            delay=eyebrow is not None,
        )
    )
    if body is not None:
        text_children.append(
            _text("p", body, class_="ast-body", role="body", theme=theme, motion=motion, delay=True)
        )
    layers = _background_layers(background_src, theme, motion=motion)
    layers.append(_content_layer(text_children, layout=layout))
    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)

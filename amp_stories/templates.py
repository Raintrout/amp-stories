"""High-level page factory functions for common AMP Story page types.

Each function returns a ready-to-use :class:`~amp_stories.page.Page` styled
with the provided :class:`~amp_stories.themes.Theme`.  The pages use
``.ast-*`` CSS classes — you must apply the theme stylesheet to the story::

    from amp_stories import Story, title_page, quote_page, SLATE_THEME

    story = Story(
        title="My Story",
        publisher="Acme",
        publisher_logo_src="https://example.com/logo.png",
        poster_portrait_src="https://example.com/poster.jpg",
        canonical_url="https://example.com/story.html",
        custom_css=SLATE_THEME.generate_css(),
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

from amp_stories.elements import AmpImg, DivElement, TextElement
from amp_stories.layer import Layer
from amp_stories.outlink import PageOutlink
from amp_stories.page import Page
from amp_stories.themes import SLATE_THEME, Theme

# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _background_layers(
    background_src: str | None,
    theme: Theme,
) -> list[Layer]:
    """Return the background layers for a page.

    - No image: one fill layer with a solid-colour ``.ast-bg`` div.
    - Image provided: a fill layer with the image, *plus* a fill layer with
      a semi-transparent ``.ast-overlay`` div for text legibility.
    """
    if background_src is None:
        return [Layer("fill", children=[DivElement(class_="ast-bg")])]
    return [
        Layer("fill", children=[AmpImg(background_src, alt="")]),
        Layer("fill", children=[DivElement(class_="ast-overlay")]),
    ]


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
    theme: Theme = SLATE_THEME,
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
        theme: Visual theme to apply.  Defaults to :data:`SLATE_THEME`.
    """
    text_children: list[TextElement] = []

    if eyebrow is not None:
        text_children.append(
            TextElement(
                "p", eyebrow,
                class_="ast-eyebrow",
                animate_in=theme.heading_animate_in,
                animate_in_duration=theme.animate_in_duration,
            )
        )

    text_children.append(
        TextElement(
            "h1", title,
            class_="ast-title",
            animate_in=theme.heading_animate_in,
            animate_in_duration=theme.animate_in_duration,
            animate_in_delay=theme.animate_in_delay if eyebrow is not None else None,
        )
    )

    if subtitle is not None:
        text_children.append(
            TextElement(
                "h2", subtitle,
                class_="ast-subtitle",
                animate_in=theme.body_animate_in,
                animate_in_duration=theme.animate_in_duration,
                animate_in_delay=theme.animate_in_delay,
            )
        )

    layers = _background_layers(background_src, theme)
    layers.append(Layer("vertical", children=list(text_children)))  # type: ignore[arg-type]

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def quote_page(
    page_id: str,
    quote: str,
    *,
    attribution: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SLATE_THEME,
) -> Page:
    """Create a pull-quote page.

    Args:
        page_id: Unique page id.
        quote: The quotation text.
        attribution: Optional author / source line.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SLATE_THEME`.
    """
    text_children: list[TextElement] = [
        TextElement("p", "\u201c", class_="ast-quote-mark"),
        TextElement(
            "blockquote", quote,
            class_="ast-body",
            animate_in=theme.heading_animate_in,
            animate_in_duration=theme.animate_in_duration,
        ),
    ]

    if attribution is not None:
        text_children.append(
            TextElement(
                "p", attribution,
                class_="ast-attribution",
                animate_in=theme.body_animate_in,
                animate_in_duration=theme.animate_in_duration,
                animate_in_delay=theme.animate_in_delay,
            )
        )

    layers = _background_layers(background_src, theme)
    layers.append(Layer("vertical", children=list(text_children)))  # type: ignore[arg-type]

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def stat_page(
    page_id: str,
    stat: str,
    label: str,
    *,
    context: str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SLATE_THEME,
) -> Page:
    """Create a statistic / data-point page.

    Args:
        page_id: Unique page id.
        stat: The headline figure (e.g. ``'92%'`` or ``'1.4B'``).
        label: Short descriptor for the stat.
        context: Optional additional sentence of context.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SLATE_THEME`.
    """
    text_children: list[TextElement] = [
        TextElement(
            "p", stat,
            class_="ast-stat-number",
            animate_in=theme.heading_animate_in,
            animate_in_duration=theme.animate_in_duration,
        ),
        TextElement(
            "p", label,
            class_="ast-stat-label",
            animate_in=theme.body_animate_in,
            animate_in_duration=theme.animate_in_duration,
            animate_in_delay=theme.animate_in_delay,
        ),
    ]

    if context is not None:
        text_children.append(
            TextElement(
                "p", context,
                class_="ast-body",
                animate_in=theme.body_animate_in,
                animate_in_duration=theme.animate_in_duration,
                animate_in_delay=theme.animate_in_delay,
            )
        )

    layers = _background_layers(background_src, theme)
    layers.append(Layer("vertical", children=list(text_children)))  # type: ignore[arg-type]

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def chapter_page(
    page_id: str,
    chapter_title: str,
    *,
    chapter_number: int | str | None = None,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SLATE_THEME,
) -> Page:
    """Create a chapter / section divider page.

    Args:
        page_id: Unique page id.
        chapter_title: The chapter or section title.
        chapter_number: Optional chapter number or label (e.g. ``1``, ``'Part I'``).
            When an integer is given it is formatted as ``'Part N'``.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SLATE_THEME`.
    """
    text_children: list[TextElement] = []

    if chapter_number is not None:
        label = (
            f"Part {chapter_number}"
            if isinstance(chapter_number, int)
            else str(chapter_number)
        )
        text_children.append(
            TextElement(
                "p", label,
                class_="ast-chapter-number",
                animate_in=theme.heading_animate_in,
                animate_in_duration=theme.animate_in_duration,
            )
        )

    text_children.append(
        TextElement(
            "h1", chapter_title,
            class_="ast-chapter-title",
            animate_in=theme.heading_animate_in,
            animate_in_duration=theme.animate_in_duration,
            animate_in_delay=theme.animate_in_delay if chapter_number is not None else None,
        )
    )

    layers = _background_layers(background_src, theme)
    layers.append(Layer("vertical", children=list(text_children)))  # type: ignore[arg-type]

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
    theme: Theme = SLATE_THEME,
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
        theme: Visual theme.  Defaults to :data:`SLATE_THEME`.
    """
    text_children: list[TextElement] = [
        TextElement(
            "p", f"TRIP {number:02d}",
            class_="ast-eyebrow",
            animate_in=theme.heading_animate_in,
            animate_in_duration=theme.animate_in_duration,
        ),
        TextElement(
            "h1", location,
            class_="ast-title",
            animate_in=theme.heading_animate_in,
            animate_in_duration=theme.animate_in_duration,
            animate_in_delay=theme.animate_in_delay,
        ),
    ]

    if region is not None:
        text_children.append(
            TextElement(
                "h2", region,
                class_="ast-subtitle",
                animate_in=theme.body_animate_in,
                animate_in_duration=theme.animate_in_duration,
                animate_in_delay=theme.animate_in_delay,
            )
        )

    if highlight is not None:
        text_children.append(
            TextElement(
                "p", highlight,
                class_="ast-body",
                animate_in=theme.body_animate_in,
                animate_in_duration=theme.animate_in_duration,
                animate_in_delay=theme.animate_in_delay,
            )
        )

    layers = _background_layers(background_src, theme)
    layers.append(Layer("vertical", children=list(text_children)))  # type: ignore[arg-type]

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
    theme: Theme = SLATE_THEME,
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
        theme: Visual theme.  Defaults to :data:`SLATE_THEME`.
    """
    text_children: list[TextElement] = [
        TextElement(
            "h1", heading_text,
            class_="ast-title",
            animate_in=theme.heading_animate_in,
            animate_in_duration=theme.animate_in_duration,
        ),
    ]

    if body is not None:
        text_children.append(
            TextElement(
                "p", body,
                class_="ast-body",
                animate_in=theme.body_animate_in,
                animate_in_duration=theme.animate_in_duration,
                animate_in_delay=theme.animate_in_delay,
            )
        )

    layers = _background_layers(background_src, theme)
    layers.append(Layer("vertical", children=list(text_children)))  # type: ignore[arg-type]

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
    caption: str | None = None,
    eyebrow: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SLATE_THEME,
) -> Page:
    """Create a full-bleed photo page.

    The image fills the entire page.  An optional caption and/or eyebrow
    label are overlaid using a ``'vertical'`` text layer.

    Args:
        page_id: Unique page id.
        image_src: URL of the full-bleed photo.
        caption: Optional caption text displayed over the image.
        eyebrow: Optional small uppercase label above the caption.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SLATE_THEME`.
    """
    layers: list[Layer] = [
        Layer("fill", children=[AmpImg(image_src, alt="")]),
    ]

    text_children: list[TextElement] = []
    if eyebrow is not None:
        text_children.append(
            TextElement("p", eyebrow, class_="ast-eyebrow")
        )
    if caption is not None:
        text_children.append(
            TextElement(
                "p", caption,
                class_="ast-caption",
                animate_in=theme.body_animate_in,
                animate_in_duration=theme.animate_in_duration,
            )
        )

    if text_children:
        layers.append(Layer("vertical", children=list(text_children)))  # type: ignore[arg-type]

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)


def text_page(
    page_id: str,
    heading: str,
    body: str,
    *,
    background_src: str | None = None,
    auto_advance_after: str | None = None,
    theme: Theme = SLATE_THEME,
) -> Page:
    """Create a text-focused content page with a heading and body paragraph.

    Args:
        page_id: Unique page id.
        heading: Section heading text.
        body: Body paragraph text.
        background_src: URL of a background image.
        auto_advance_after: CSS duration after which the page auto-advances.
        theme: Visual theme.  Defaults to :data:`SLATE_THEME`.
    """
    text_children: list[TextElement] = [
        TextElement(
            "h2", heading,
            class_="ast-subtitle",
            animate_in=theme.heading_animate_in,
            animate_in_duration=theme.animate_in_duration,
        ),
        TextElement(
            "p", body,
            class_="ast-body",
            animate_in=theme.body_animate_in,
            animate_in_duration=theme.animate_in_duration,
            animate_in_delay=theme.animate_in_delay,
        ),
    ]

    layers = _background_layers(background_src, theme)
    layers.append(Layer("vertical", children=list(text_children)))  # type: ignore[arg-type]

    return Page(page_id, layers=layers, auto_advance_after=auto_advance_after)

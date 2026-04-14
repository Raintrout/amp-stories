"""amp_stories — Generate AMP Stories HTML with a clean Python API.

Public API has two layers:

**AMP standard** — classes that map directly to AMP HTML elements.
Import paths follow the component name: ``amp_stories.story``,
``amp_stories.page``, ``amp_stories.elements``, etc.

**Library helpers** — convenience utilities provided by this library on top
of the AMP primitives. Import from ``amp_stories.helpers`` (text constructors
and layer factories), ``amp_stories.themes`` (theming), or
``amp_stories.templates`` (page factory functions).

Everything is re-exported here for convenience::

    from amp_stories import (
        # AMP standard
        Story, Page, Layer, AmpImg, TextElement,
        # Library helpers
        heading, background_layer, title_page, SLATE_THEME,
    )
"""

from amp_stories._serde import from_dict
from amp_stories._validation import AmpStoriesWarning, ValidationError
from amp_stories.animation import Animation
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
from amp_stories.helpers import (
    background_layer,
    blockquote,
    heading,
    paragraph,
    positioned_layer,
    span,
    text_layer,
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
from amp_stories.page import Page, next_page_id
from amp_stories.shopping import ShoppingTag, StoryShopping
from amp_stories.story import Story
from amp_stories.templates import (
    ChartRow,
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
from amp_stories.themes import (
    EDITORIAL_THEME,
    LIGHT_THEME,
    NEWS_THEME,
    SHOPPING_THEME,
    SLATE_THEME,
    TRAVEL_THEME,
    WARM_THEME,
    Theme,
)

__all__ = [
    # ── AMP standard: document structure ──────────────────────────────────
    "Story",
    "Page",
    "next_page_id",
    "Layer",
    # ── AMP standard: content elements ────────────────────────────────────
    "AmpImg",
    "AmpVideo",
    "AmpAudio",
    "AmpList",
    "StoryPanningMedia",
    "Story360",
    "TextElement",
    "DivElement",
    "VideoSource",
    # ── AMP standard: animation ────────────────────────────────────────────
    "Animation",
    # ── AMP standard: interactive components ──────────────────────────────
    "InteractiveOption",
    "InteractiveBinaryPoll",
    "InteractivePoll",
    "InteractiveQuiz",
    "InteractiveSlider",
    "InteractiveResults",
    # ── AMP standard: page-level features ─────────────────────────────────
    "PageOutlink",
    "PageAttachment",
    "AttachmentLink",
    "Bookend",
    "BookendComponent",
    "BookendShareProvider",
    "AutoAds",
    "ShoppingTag",
    "StoryShopping",
    "AmpConsent",
    # ── Library helpers: text constructors ────────────────────────────────
    "heading",
    "paragraph",
    "span",
    "blockquote",
    # ── Library helpers: layer factories ──────────────────────────────────
    "background_layer",
    "text_layer",
    "positioned_layer",
    # ── Library helpers: page templates ───────────────────────────────────
    "ChartRow",
    "title_page",
    "quote_page",
    "stat_page",
    "chapter_page",
    "photo_page",
    "video_page",
    "text_page",
    "trip_page",
    "cta_page",
    "listicle_page",
    "comparison_page",
    "breaking_page",
    "update_page",
    "itinerary_page",
    "data_chart_page",
    "product_page",
    "deal_page",
    # ── Library helpers: theming ───────────────────────────────────────────
    "Theme",
    "SLATE_THEME",
    "LIGHT_THEME",
    "EDITORIAL_THEME",
    "WARM_THEME",
    "NEWS_THEME",
    "TRAVEL_THEME",
    "SHOPPING_THEME",
    # ── Serialization ──────────────────────────────────────────────────────
    "from_dict",
    # ── Errors / warnings ─────────────────────────────────────────────────
    "ValidationError",
    "AmpStoriesWarning",
]

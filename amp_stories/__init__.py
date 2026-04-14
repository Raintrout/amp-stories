"""amp_stories — Generate AMP Stories HTML with a clean Python API.

Quick start::

    from amp_stories import Story, Page, Layer, AmpImg, heading, paragraph

    story = Story(
        title="My Story",
        publisher="Example Publisher",
        publisher_logo_src="https://example.com/logo.png",
        poster_portrait_src="https://example.com/poster.jpg",
        canonical_url="https://example.com/my-story.html",
        pages=[
            Page(
                page_id="cover",
                layers=[
                    Layer("fill", children=[
                        AmpImg("https://example.com/hero.jpg", alt="Hero image"),
                    ]),
                    Layer("vertical", children=[
                        heading("My Story", animate_in="fly-in-bottom"),
                        paragraph("A great story.", animate_in="fade-in"),
                    ]),
                ],
            ),
        ],
    )

    story.save("output.html")
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
    blockquote,
    heading,
    paragraph,
    span,
)
from amp_stories.interactive import (
    InteractiveBinaryPoll,
    InteractiveOption,
    InteractivePoll,
    InteractiveQuiz,
    InteractiveResults,
    InteractiveSlider,
)
from amp_stories.layer import Layer, background_layer, text_layer
from amp_stories.outlink import PageOutlink
from amp_stories.page import Page
from amp_stories.shopping import ShoppingTag, StoryShopping
from amp_stories.story import Story

__all__ = [
    # Core
    "Story",
    "Page",
    "Layer",
    # Elements
    "AmpImg",
    "AmpVideo",
    "AmpAudio",
    "AmpList",
    "StoryPanningMedia",
    "Story360",
    "TextElement",
    "DivElement",
    "VideoSource",
    # Convenience element constructors
    "heading",
    "paragraph",
    "span",
    "blockquote",
    # Layer helpers
    "background_layer",
    "text_layer",
    # Animation
    "Animation",
    # Page attachments
    "PageOutlink",
    "PageAttachment",
    "AttachmentLink",
    # Bookend
    "Bookend",
    "BookendComponent",
    "BookendShareProvider",
    # Interactive components
    "InteractiveOption",
    "InteractiveBinaryPoll",
    "InteractivePoll",
    "InteractiveQuiz",
    "InteractiveSlider",
    "InteractiveResults",
    # Auto ads
    "AutoAds",
    # Shopping
    "ShoppingTag",
    "StoryShopping",
    # Consent
    "AmpConsent",
    # Serialization
    "from_dict",
    # Errors / warnings
    "ValidationError",
    "AmpStoriesWarning",
]

"""Basic AMP Story example demonstrating the major library features.

Run with:
    uv run python examples/basic_story.py

Then validate the output at https://validator.ampproject.org/
"""

from __future__ import annotations

import os
import pathlib

from amp_stories import (
    AmpImg,
    AmpVideo,
    AutoAds,
    Bookend,
    BookendComponent,
    BookendShareProvider,
    InteractiveOption,
    InteractivePoll,
    Layer,
    Page,
    PageOutlink,
    Story,
    VideoSource,
    background_layer,
    heading,
    paragraph,
    text_layer,
)

# ---------------------------------------------------------------------------
# Shared image/video URLs (placeholders — swap for real assets)
# ---------------------------------------------------------------------------

LOGO = "https://example.com/logo.png"
POSTER = "https://example.com/poster.jpg"
CANONICAL = "https://example.com/mountain-story.html"


def build_story() -> Story:
    # Page 1: cover with background image and animated text
    cover = Page(
        page_id="cover",
        auto_advance_after="8s",
        layers=[
            background_layer(
                AmpImg("https://example.com/hero.jpg", alt="Mountain at dusk")
            ),
            text_layer(
                heading(
                    "Mountains in Autumn",
                    animate_in="fly-in-bottom",
                    animate_in_duration="0.5s",
                ),
                paragraph(
                    "A visual journey through the peaks.",
                    animate_in="fade-in",
                    animate_in_delay="0.4s",
                ),
            ),
        ],
    )

    # Page 2: multi-format video background
    video_page = Page(
        page_id="video",
        layers=[
            Layer(
                "fill",
                children=[
                    AmpVideo(
                        sources=[
                            VideoSource("https://example.com/clip.mp4", "video/mp4"),
                            VideoSource("https://example.com/clip.webm", "video/webm"),
                        ],
                        poster="https://example.com/clip-poster.jpg",
                        loop=True,
                        muted=True,
                    )
                ],
            ),
            text_layer(heading("Hidden Valleys", level=2, animate_in="fade-in")),
        ],
    )

    # Page 3: interactive poll
    poll_page = Page(
        page_id="poll",
        layers=[
            background_layer(
                AmpImg("https://example.com/trail.jpg", alt="Hiking trail")
            ),
            Layer(
                "vertical",
                children=[
                    heading("Quick question", level=3),
                    InteractivePoll(
                        options=[
                            InteractiveOption("Spring"),
                            InteractiveOption("Summer"),
                            InteractiveOption("Autumn"),
                            InteractiveOption("Winter"),
                        ],
                        id="season-poll",
                    ),
                ],
            ),
        ],
    )

    # Page 4: CTA outlink
    cta_page = Page(
        page_id="cta",
        layers=[
            background_layer(
                AmpImg("https://example.com/valley.jpg", alt="Green valley")
            ),
            text_layer(
                heading("Plan your trip", level=2),
                paragraph("Discover routes less traveled."),
            ),
        ],
        outlink=PageOutlink(
            href="https://example.com/trails",
            cta_text="Explore Trails",
            theme="dark",
        ),
    )

    # Bookend: fluent helper API
    bookend = (
        Bookend(share_providers=[
            BookendShareProvider("twitter"),
            BookendShareProvider("facebook", param="my-app-id"),
        ])
        .add_heading("More Stories")
        .add_article(
            "Winter in the Alps",
            "https://example.com/winter",
            image="https://example.com/winter-thumb.jpg",
        )
        .add_cta("Subscribe to our newsletter", "https://example.com/subscribe")
    )
    # also add a component the constructor way (both approaches work)
    bookend.components.append(
        BookendComponent(
            type="small",
            title="Spring in the Alps",
            url="https://example.com/spring",
        )
    )

    return Story(
        title="Mountains in Autumn",
        publisher="Example Media",
        publisher_logo_src=LOGO,
        poster_portrait_src=POSTER,
        poster_square_src="https://example.com/poster-square.jpg",
        canonical_url=CANONICAL,
        lang="en",
        supports_landscape=True,
        pages=[cover, video_page, poll_page, cta_page],
        bookend=bookend,
        auto_ads=AutoAds(
            "https://ad-server.example.com/endpoint",
            ad_attributes={"type": "adsense"},
        ),
        structured_data={
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": "Mountains in Autumn",
            "publisher": {
                "@type": "Organization",
                "name": "Example Media",
                "logo": {"@type": "ImageObject", "url": LOGO},
            },
        },
        custom_css="""
            h1, h2, h3 { font-family: Georgia, serif; color: #fff; }
            p { color: rgba(255,255,255,0.9); }
        """,
    )


def main() -> None:
    story = build_story()
    output_dir = pathlib.Path(__file__).parent / "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = output_dir / "basic_story.html"
    story.save(output_path)
    print(f"Saved → {output_path}")
    print("Validate at: https://validator.ampproject.org/")


if __name__ == "__main__":
    main()

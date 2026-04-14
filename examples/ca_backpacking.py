"""AMP Story: California Backpacking — based on isik.dev/posts/CABackpacking.html

10 solo wilderness trips taken during the 2020-2021 pandemic lockdowns across
Big Sur, Yosemite, and the California backcountry.

Run with:
    uv run python examples/ca_backpacking.py

Output: examples/output/ca_backpacking.html
Validate at: https://validator.ampproject.org/
"""

from __future__ import annotations

import pathlib

from amp_stories import Story, cta_page, title_page, trip_page
from amp_stories.themes import Theme

# ---------------------------------------------------------------------------
# Theme — earthy wilderness palette
# ---------------------------------------------------------------------------

TRAIL_THEME = Theme(
    bg_color="#1c2a1e",
    text_color="#f0ede6",
    accent_color="#c9a84c",
    muted_color="#a89f8c",
    overlay_opacity=0.52,
    font_family="'Georgia', 'Times New Roman', serif",
    heading_font="'Georgia', 'Times New Roman', serif",
    h1_size="2.2rem",
    h2_size="1.6rem",
    body_size="1.2rem",
    small_size="0.8rem",
    heading_animate_in="fly-in-bottom",
    body_animate_in="fade-in",
    animate_in_duration="0.6s",
    animate_in_delay="0.35s",
)

# ---------------------------------------------------------------------------
# Unsplash image URLs (free to use, no auth required)
# ---------------------------------------------------------------------------

IMG_BIG_SUR  = "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=900"
IMG_TRAIL    = "https://images.unsplash.com/photo-1551632811-561732d1e306?w=900"
IMG_HETCH    = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=900"
IMG_TENT     = "https://images.unsplash.com/photo-1504851149312-7a075b496cc7?w=900"
IMG_RIDGE    = "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=900"
IMG_FIRE     = "https://images.unsplash.com/photo-1475113548492-f4e5f1f4a80f?w=900"
IMG_CLOUDS   = "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=900"
IMG_WILDLIFE = "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=900"
IMG_YOSEMITE = "https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=900"
IMG_SUMMIT   = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=900"

LOGO      = "https://isik.dev/favicon.ico"
POSTER    = IMG_BIG_SUR
CANONICAL = "https://isik.dev/posts/CABackpacking.html"

# ---------------------------------------------------------------------------
# Story
# ---------------------------------------------------------------------------

def build_story() -> Story:
    pages = [
        title_page(
            "cover",
            "California Backpacking",
            subtitle="10 solo trips into the wilderness, 2020–2021",
            eyebrow="Umut Isik",
            background_src=IMG_BIG_SUR,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-1",
            1,
            "Vicente Flats",
            region="Big Sur Coast",
            highlight="First trip. Wrong trail. Poison oak. Still worth every scratch.",
            background_src=IMG_BIG_SUR,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-2",
            2,
            "Silver Peak Wilderness",
            region="Santa Lucia Range",
            highlight="Estrella Camp. Remote enough that a wrong turn means a cold night.",
            background_src=IMG_TRAIL,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-3",
            3,
            "Hetch Hetchy",
            region="Yosemite",
            highlight="Below freezing. Emergency fire. Never forgot the lighter again.",
            background_src=IMG_TENT,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-4",
            4,
            "Cone Peak",
            region="Los Padres National Forest",
            highlight="Highest coastal peak in the contiguous US. Views to the Channel Islands.",
            background_src=IMG_RIDGE,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-5",
            5,
            "Sykes Hot Springs",
            region="Big Sur",
            highlight="10 miles in for a soak. Worth every step.",
            background_src=IMG_FIRE,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-6",
            6,
            "Ohlone Wilderness",
            region="East Bay Hills",
            highlight="Closest backcountry to the Bay Area. Surprisingly wild.",
            background_src=IMG_CLOUDS,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-7",
            7,
            "Emigrant Wilderness",
            region="Stanislaus National Forest",
            highlight="High granite country above 9,000 ft. First real Sierra night.",
            background_src=IMG_SUMMIT,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-8",
            8,
            "Ventana Double Cone",
            region="Big Sur",
            highlight="30 miles round trip. The hardest day of the year.",
            background_src=IMG_TRAIL,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-9",
            9,
            "Arroyo Seco",
            region="Los Padres",
            highlight="A mountain lion watched me set up my tent. Big Sur does not ease you in.",
            background_src=IMG_WILDLIFE,
            theme=TRAIL_THEME,
        ),
        trip_page(
            "trip-10",
            10,
            "Clouds Rest Loop",
            region="Yosemite",
            highlight="5 days. Vogelsang Lake. The first trip not taken alone.",
            background_src=IMG_YOSEMITE,
            theme=TRAIL_THEME,
        ),
        cta_page(
            "cta",
            "Want the full story?",
            body="Trip reports, gear lists, and lessons from 10 solo nights in the wild.",
            cta_text="Read on isik.dev",
            cta_url=CANONICAL,
            background_src=IMG_BIG_SUR,
            theme=TRAIL_THEME,
        ),
    ]

    return Story(
        title="California Backpacking — Umut Isik",
        publisher="isik.dev",
        publisher_logo_src=LOGO,
        poster_portrait_src=POSTER,
        poster_landscape_src=IMG_BIG_SUR,
        canonical_url=CANONICAL,
        supports_landscape=True,
        desktop_aspect_ratio="16:9",
        lang="en",
        custom_css=TRAIL_THEME.generate_css(),
        pages=pages,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "output" / "ca_backpacking.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    story = build_story()
    story.save(out)
    print(f"Saved → {out}")
    print(f"Pages: {len(story.pages)} (1 cover + 10 trips + 1 CTA)")
    print(f"File size: {out.stat().st_size / 1024:.1f} KB")
    print("Validate at: https://validator.ampproject.org/")

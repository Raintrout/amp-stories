"""Adventure/travel Web Story using the new style-system defaults.

This example focuses on the recommended cinematic travel stack:

- `SUMMIT_THEME`
- `BOTTOM_STACK_LAYOUT`, `CENTER_FOCUS_LAYOUT`, and `CAPTION_BAND_LAYOUT`
- newer page types like `hero_video_page`, `process_step_page`, and `card_overlay_page`

Run with:
    uv run python examples/ca_backpacking.py

Output: examples/output/ca_backpacking.html
"""

from __future__ import annotations

import pathlib

from amp_stories import (
    BOTTOM_STACK_LAYOUT,
    CAPTION_BAND_LAYOUT,
    CENTER_FOCUS_LAYOUT,
    SUMMIT_THEME,
    ChartRow,
    Story,
    card_overlay_page,
    chapter_page,
    cta_page,
    data_chart_page,
    hero_video_page,
    itinerary_page,
    photo_page,
    process_step_page,
    stat_page,
    title_page,
)

OUTPUT = pathlib.Path(__file__).parent / "output" / "ca_backpacking.html"

PUBLISHER = "Trail Atlas"
LOGO = "https://placehold.co/96x96/152226/d7a14d?text=TA"
CANONICAL = "https://example.com/stories/california-backpacking"


def unsplash(photo_id: str, *, w: int = 900, h: int = 1600) -> str:
    return (
        f"https://images.unsplash.com/{photo_id}"
        f"?w={w}&h={h}&fit=crop&crop=entropy&auto=format&q=80"
    )


POSTER = unsplash("photo-1500534314209-a25ddb2bd429")
POSTER_LANDSCAPE = unsplash("photo-1500534314209-a25ddb2bd429", w=1600, h=900)
IMG_COVER = unsplash("photo-1500534314209-a25ddb2bd429")
IMG_FOREST = unsplash("photo-1464822759023-fed622ff2c3b")
IMG_GRANITE = unsplash("photo-1519681393784-d120267933ba")
IMG_CAMP = unsplash("photo-1504851149312-7a075b496cc7")
IMG_PACK = unsplash("photo-1527631746610-bca00a040d60")
IMG_ROUTE = unsplash("photo-1501785888041-af3ef285b470")
IMG_SUMMIT = unsplash("photo-1464822759023-fed622ff2c3b")
VIDEO_POSTER = unsplash("photo-1500534314209-a25ddb2bd429")

story = Story(
    title="California Backpacking",
    publisher=PUBLISHER,
    publisher_logo_src=LOGO,
    poster_portrait_src=POSTER,
    poster_landscape_src=POSTER_LANDSCAPE,
    canonical_url=CANONICAL,
    supports_landscape=True,
    custom_css=SUMMIT_THEME.generate_css(),
    pages=[
        title_page(
            "cover",
            "California Backpacking",
            subtitle="3 wilderness routes worth the extra miles",
            eyebrow="SUMMER FIELD NOTES",
            background_src=IMG_COVER,
            theme=SUMMIT_THEME,
            layout=BOTTOM_STACK_LAYOUT,
        ),
        hero_video_page(
            "video-cover",
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "Granite mornings, cold lakes, long climbs",
            eyebrow="SIERRA LOOP",
            subtitle="A short series on how to plan a stronger first overnight route.",
            poster=VIDEO_POSTER,
            theme=SUMMIT_THEME,
        ),
        chapter_page(
            "chapter-1",
            "Choose a route with one strong payoff",
            chapter_number="PART I",
            background_src=IMG_FOREST,
            theme=SUMMIT_THEME,
            layout=CENTER_FOCUS_LAYOUT,
        ),
        itinerary_page(
            "route-1",
            1,
            "Hetch Hetchy to Rancheria Falls",
            details=[
                "Strong first-night destination with reliable water.",
                "Big valley views early, waterfalls late.",
                "Best for hikers testing longer mileage.",
            ],
            background_src=IMG_GRANITE,
            theme=SUMMIT_THEME,
        ),
        photo_page(
            "camp-photo",
            IMG_CAMP,
            overlay=True,
            eyebrow="AT CAMP",
            caption="Use a shallow caption band when the photo should stay dominant.",
            theme=SUMMIT_THEME,
            layout=CAPTION_BAND_LAYOUT,
        ),
        process_step_page(
            "step-1",
            "STEP 1",
            "Pack for the coldest hour, not the warmest one",
            "Sierra camps can swing fast after sunset, so insulation and dry layers matter more than noon comfort.",
            background_src=IMG_PACK,
            theme=SUMMIT_THEME,
        ),
        stat_page(
            "stat",
            "24 mi",
            "ideal weekend mileage",
            context="Enough distance to feel remote without turning the trip into a forced march.",
            background_src=IMG_ROUTE,
            theme=SUMMIT_THEME,
            layout=CENTER_FOCUS_LAYOUT,
        ),
        data_chart_page(
            "chart",
            "Where the effort goes",
            rows=[
                ChartRow("Climb", 6, "6h"),
                ChartRow("Camp", 14, "14h"),
                ChartRow("Water", 2, "2 stops"),
                ChartRow("Scenic", 5, "5 moments"),
            ],
            background_src=IMG_SUMMIT,
            theme=SUMMIT_THEME,
        ),
        card_overlay_page(
            "best-for",
            "Best for hikers moving beyond car camping",
            eyebrow="WHO THIS FITS",
            body=(
                "Pick routes with one iconic visual payoff, one dependable water source, and one early bailout "
                "option. That combination builds confidence without making the story feel tame."
            ),
            background_src=IMG_GRANITE,
            theme=SUMMIT_THEME,
        ),
        cta_page(
            "finale",
            "Read the full route guide",
            body="Trail notes, elevation profiles, and the exact packing list used for this series.",
            cta_text="Open guide",
            cta_url="https://example.com/guides/california-backpacking",
            background_src=IMG_COVER,
            theme=SUMMIT_THEME,
        ),
    ],
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
story.save(str(OUTPUT))
print(f"Saved -> {OUTPUT}")

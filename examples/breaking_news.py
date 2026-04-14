"""Editorial/news Web Story using the new style-system defaults.

This example focuses on the recommended editorial stack:

- `SIGNAL_THEME`
- `TOP_STACK_LAYOUT` and `CARD_OVERLAY_LAYOUT`
- news-specific pages like `timeline_step_page`, `fact_check_page`,
  and `key_takeaways_page`

Run with:
    uv run python examples/breaking_news.py

Output: examples/output/breaking_news.html
"""

from __future__ import annotations

import pathlib

from amp_stories import (
    CARD_OVERLAY_LAYOUT,
    SIGNAL_THEME,
    Story,
    TOP_STACK_LAYOUT,
    card_overlay_page,
    cta_page,
    fact_check_page,
    hero_video_page,
    key_takeaways_page,
    timeline_step_page,
    title_page,
)

OUTPUT = pathlib.Path(__file__).parent / "output" / "breaking_news.html"

PUBLISHER = "Signal Desk"
LOGO = "https://placehold.co/96x96/101820/ff5a5f?text=SD"
CANONICAL = "https://example.com/stories/city-shutdown"


def unsplash(photo_id: str, *, w: int = 900, h: int = 1600) -> str:
    return (
        f"https://images.unsplash.com/{photo_id}"
        f"?w={w}&h={h}&fit=crop&crop=entropy&auto=format&q=80"
    )


POSTER = unsplash("photo-1519501025264-65ba15a82390")
POSTER_LANDSCAPE = unsplash("photo-1519501025264-65ba15a82390", w=1600, h=900)
IMG_CITY = unsplash("photo-1519501025264-65ba15a82390")
IMG_CONTROL = unsplash("photo-1495020689067-958852a7765e")
IMG_GRID = unsplash("photo-1465447142348-e9952c393450")
IMG_PRESS = unsplash("photo-1504711434969-e33886168f5c")
IMG_REPAIR = unsplash("photo-1489515217757-5fd1be406fef")
VIDEO_POSTER = unsplash("photo-1504384308090-c894fdcc538d")

story = Story(
    title="City Shutdown: What Happened Overnight",
    publisher=PUBLISHER,
    publisher_logo_src=LOGO,
    poster_portrait_src=POSTER,
    poster_landscape_src=POSTER_LANDSCAPE,
    canonical_url=CANONICAL,
    supports_landscape=True,
    custom_css=SIGNAL_THEME.generate_css(),
    pages=[
        title_page(
            "cover",
            "City Shutdown",
            subtitle="What happened overnight",
            eyebrow="LIVE BRIEFING",
            background_src=IMG_CITY,
            theme=SIGNAL_THEME,
            layout=TOP_STACK_LAYOUT,
        ),
        hero_video_page(
            "hero-video",
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "Morning commuters face a second day of disruption",
            eyebrow="AT FIRST LIGHT",
            subtitle="Transit, schools, and city offices opened late.",
            poster=VIDEO_POSTER,
            theme=SIGNAL_THEME,
        ),
        timeline_step_page(
            "timeline-1",
            "5:42 AM",
            "A substation fire knocked out service downtown",
            body="Crews isolated the grid within 18 minutes to stop the outage from spreading.",
            background_src=IMG_GRID,
            theme=SIGNAL_THEME,
        ),
        fact_check_page(
            "fact-check",
            "Claim: the whole city lost power.",
            "False",
            explanation="Officials said the outage was concentrated in the central business district.",
            background_src=IMG_PRESS,
            theme=SIGNAL_THEME,
        ),
        key_takeaways_page(
            "takeaways",
            "What matters now",
            [
                "Subway service is partially restored.",
                "Schools in the affected zone start two hours late.",
                "Water and hospital backup systems stayed online.",
            ],
            background_src=IMG_CONTROL,
            theme=SIGNAL_THEME,
            layout=CARD_OVERLAY_LAYOUT,
        ),
        card_overlay_page(
            "context",
            "Why recovery is taking longer",
            eyebrow="INSIDE THE FIX",
            body=(
                "Engineers are replacing switching gear instead of resetting it, which reduces the risk "
                "of a second failure during the afternoon peak."
            ),
            background_src=IMG_REPAIR,
            theme=SIGNAL_THEME,
        ),
        cta_page(
            "finale",
            "Follow the live blog",
            body="We are updating routes, reopening times, and official advisories throughout the day.",
            cta_text="Open live updates",
            cta_url="https://example.com/live/city-shutdown",
            background_src=IMG_CITY,
            theme=SIGNAL_THEME,
        ),
    ],
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
story.save(str(OUTPUT))
print(f"Saved -> {OUTPUT}")

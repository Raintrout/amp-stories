"""AMP Story: Breaking News — demonstrates NEWS_THEME and news-specific templates.

A fictional multi-update story showing how to build a breaking-news experience
with live update cards, video, photo, and a CTA.

Run with:
    uv run python examples/breaking_news.py

Output: examples/output/breaking_news.html
Validate at: https://validator.ampproject.org/
"""

from __future__ import annotations

import pathlib

from amp_stories import (
    NEWS_THEME,
    Story,
    breaking_page,
    cta_page,
    photo_page,
    update_page,
    video_page,
)

OUTPUT = pathlib.Path(__file__).parent / "output" / "breaking_news.html"

PUBLISHER = "Global News Network"
LOGO = "https://placehold.co/60x60/0d0d0d/cc0000?text=GNN"
POSTER = "https://placehold.co/900x1600/0d0d0d/f2f2f2?text=Breaking+News"
CANONICAL = "https://example.com/stories/breaking-news"

pages = [
    # 1 — Breaking alert
    breaking_page(
        "cover",
        "Major Earthquake Strikes Pacific Coast",
        badge="BREAKING",
        body="A 7.2 magnitude quake has caused widespread disruption.",
        background_src="https://placehold.co/900x1600/1a0000/f2f2f2?text=Earthquake",
        theme=NEWS_THEME,
    ),

    # 2 — First video report
    video_page(
        "video-1",
        "https://www.w3schools.com/html/mov_bbb.mp4",
        poster="https://placehold.co/900x1600/0d0d0d/f2f2f2?text=Video+Report",
        eyebrow="LIVE REPORT",
        caption="Our correspondent reports from the scene.",
        theme=NEWS_THEME,
    ),

    # 3 — Update 1
    update_page(
        "update-1",
        1,
        "Emergency Services Deployed",
        "Hundreds of rescue workers are now on the ground across three provinces.",
        background_src="https://placehold.co/900x1600/111111/f2f2f2?text=Emergency",
        theme=NEWS_THEME,
    ),

    # 4 — Photo
    photo_page(
        "photo-1",
        "https://placehold.co/900x1600/222222/ffffff?text=Aerial+View",
        overlay=True,
        eyebrow="AERIAL VIEW",
        caption="Damage visible across the coastal district.",
        theme=NEWS_THEME,
    ),

    # 5 — Update 2
    update_page(
        "update-2",
        2,
        "Tsunami Warning Lifted",
        "Authorities have confirmed there is no longer a tsunami risk for the coast.",
        theme=NEWS_THEME,
    ),

    # 6 — Update 3
    update_page(
        "update-3",
        3,
        "Power Restored to 60% of Affected Homes",
        "Engineers worked through the night to repair critical infrastructure.",
        theme=NEWS_THEME,
    ),

    # 7 — CTA
    cta_page(
        "finale",
        "Read the full report",
        body="Follow our live blog for minute-by-minute updates.",
        cta_text="Open live blog",
        cta_url="https://example.com/live-blog",
        theme=NEWS_THEME,
    ),
]

story = Story(
    title="Earthquake: Latest Updates",
    publisher=PUBLISHER,
    publisher_logo_src=LOGO,
    poster_portrait_src=POSTER,
    canonical_url=CANONICAL,
    custom_css=NEWS_THEME.generate_css(),
    pages=pages,
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
story.save(str(OUTPUT))
print(f"Saved → {OUTPUT}")

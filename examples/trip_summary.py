"""AMP Story: Pacific Coast Road Trip — demonstrates TRAVEL_THEME and travel templates.

A fictional road trip story featuring itinerary cards, photo stops, stats,
a data chart, a quote, and a CTA — all styled with the TRAVEL_THEME.

Run with:
    uv run python examples/trip_summary.py

Output: examples/output/trip_summary.html
Validate at: https://validator.ampproject.org/
"""

from __future__ import annotations

import pathlib

from amp_stories import (
    TRAVEL_THEME,
    ChartRow,
    Story,
    chapter_page,
    cta_page,
    data_chart_page,
    itinerary_page,
    photo_page,
    quote_page,
    stat_page,
    title_page,
)

OUTPUT = pathlib.Path(__file__).parent / "output" / "trip_summary.html"

PUBLISHER = "Road & Wander"
LOGO = "https://placehold.co/60x60/1c2b2b/c9a84c?text=R%26W"
POSTER = "https://placehold.co/900x1600/1c2b2b/f0ece4?text=Road+Trip"
CANONICAL = "https://example.com/stories/pacific-coast-trip"

pages = [
    # 1 — Cover
    title_page(
        "cover",
        "Pacific Coast Road Trip",
        subtitle="San Francisco → Los Angeles",
        eyebrow="7 DAYS · 650 MILES",
        background_src="https://placehold.co/900x1600/1c2b2b/1c2b2b",
        theme=TRAVEL_THEME,
    ),

    # 2 — Chapter: The Route
    chapter_page(
        "chapter-route",
        "The Route",
        chapter_number="Part I",
        background_src="https://placehold.co/900x1600/1a2a2a/1a2a2a",
        theme=TRAVEL_THEME,
    ),

    # 3 — Day 1: San Francisco
    itinerary_page(
        "day-1",
        1,
        "San Francisco",
        details=["Golden Gate Bridge at sunrise", "Tartine Bakery for breakfast",
                 "Drive down Highway 1"],
        background_src="https://placehold.co/900x1600/152020/152020",
        theme=TRAVEL_THEME,
    ),

    # 4 — Day 2: Big Sur
    itinerary_page(
        "day-2",
        2,
        "Big Sur",
        details=["McWay Falls hike", "Camp at Pfeiffer Beach", "Stars over the Pacific"],
        background_src="https://placehold.co/900x1600/162222/162222",
        theme=TRAVEL_THEME,
    ),

    # 5 — Photo stop
    photo_page(
        "photo-bixby",
        "https://placehold.co/900x1600/1c2b2b/1c2b2b",
        overlay=True,
        eyebrow="DAY 2",
        caption="Bixby Creek Bridge — one of the most photographed spots on the coast.",
        theme=TRAVEL_THEME,
    ),

    # 6 — Day 3: San Luis Obispo
    itinerary_page(
        "day-3",
        3,
        "San Luis Obispo",
        details=["Farmers market on Higuera St", "Wine tasting in Edna Valley"],
        theme=TRAVEL_THEME,
    ),

    # 7 — Stats
    stat_page(
        "stat-miles",
        "650",
        "total miles driven",
        context="Across 7 days and 12 stops.",
        theme=TRAVEL_THEME,
    ),

    # 8 — Chapter: By the Numbers
    chapter_page(
        "chapter-data",
        "By the Numbers",
        chapter_number="Part II",
        theme=TRAVEL_THEME,
    ),

    # 9 — Bar chart: time spent per activity
    data_chart_page(
        "chart-activities",
        "Time Spent Per Activity",
        rows=[
            ChartRow("Driving", 18, display="18h"),
            ChartRow("Hiking", 12, display="12h"),
            ChartRow("Beaches", 9, display="9h"),
            ChartRow("Food & Wine", 8, display="8h"),
            ChartRow("Camping", 22, display="22h"),
        ],
        theme=TRAVEL_THEME,
    ),

    # 10 — Quote
    quote_page(
        "quote",
        "The road must eventually lead to the whole world.",
        attribution="— Jack Kerouac",
        theme=TRAVEL_THEME,
    ),

    # 11 — CTA
    cta_page(
        "finale",
        "Plan your own road trip",
        body="Full route guide, packing list, and campsite recommendations.",
        cta_text="Read the guide",
        cta_url="https://example.com/pacific-coast-guide",
        theme=TRAVEL_THEME,
    ),
]

story = Story(
    title="Pacific Coast Road Trip",
    publisher=PUBLISHER,
    publisher_logo_src=LOGO,
    poster_portrait_src=POSTER,
    canonical_url=CANONICAL,
    custom_css=TRAVEL_THEME.generate_css(),
    pages=pages,
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
story.save(str(OUTPUT))
print(f"Saved → {OUTPUT}")

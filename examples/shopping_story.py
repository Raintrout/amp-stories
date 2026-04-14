"""Commerce/recommendation Web Story using the new style-system defaults.

This example focuses on the recommended commerce stack:

- `MARKET_THEME`
- `CARD_OVERLAY_LAYOUT`
- newer page types like `card_overlay_page` plus polished product/deal flows

Run with:
    uv run python examples/shopping_story.py

Output: examples/output/shopping_story.html
"""

from __future__ import annotations

import pathlib

from amp_stories import (
    CARD_OVERLAY_LAYOUT,
    MARKET_THEME,
    Story,
    card_overlay_page,
    comparison_page,
    cta_page,
    deal_page,
    key_takeaways_page,
    product_page,
    title_page,
)

OUTPUT = pathlib.Path(__file__).parent / "output" / "shopping_story.html"

PUBLISHER = "Market Edit"
LOGO = "https://placehold.co/96x96/171717/d9a441?text=ME"
CANONICAL = "https://example.com/stories/desk-setup-picks"


def unsplash(photo_id: str, *, w: int = 900, h: int = 1600) -> str:
    return (
        f"https://images.unsplash.com/{photo_id}"
        f"?w={w}&h={h}&fit=crop&crop=entropy&auto=format&q=80"
    )


POSTER = unsplash("photo-1518455027359-f3f8164ba6bd")
POSTER_LANDSCAPE = unsplash("photo-1518455027359-f3f8164ba6bd", w=1600, h=900)
IMG_DESK = unsplash("photo-1518455027359-f3f8164ba6bd")
IMG_MONITOR = unsplash("photo-1496171367470-9ed9a91ea931")
IMG_KEYBOARD = unsplash("photo-1517336714739-489689fd1ca8")
IMG_SETUP = unsplash("photo-1498050108023-c5249f4df085")
IMG_NOTES = unsplash("photo-1516321318423-f06f85e504b3")

story = Story(
    title="Desk Setup Picks",
    publisher=PUBLISHER,
    publisher_logo_src=LOGO,
    poster_portrait_src=POSTER,
    poster_landscape_src=POSTER_LANDSCAPE,
    canonical_url=CANONICAL,
    supports_landscape=True,
    custom_css=MARKET_THEME.generate_css(),
    pages=[
        title_page(
            "cover",
            "Desk Setup Picks",
            subtitle="Five upgrades that actually change the workday",
            eyebrow="EDITOR'S SHORTLIST",
            background_src=IMG_DESK,
            theme=MARKET_THEME,
        ),
        card_overlay_page(
            "framework",
            "Build around one hero object, not five small ones",
            eyebrow="BUYING RULE",
            body=(
                "The strongest commerce pages make one product feel inevitable. Supporting accessories should "
                "clarify the setup, not compete with it."
            ),
            background_src=IMG_SETUP,
            theme=MARKET_THEME,
            layout=CARD_OVERLAY_LAYOUT,
        ),
        product_page(
            "product-1",
            "27-inch 4K Monitor",
            brand="North Studio",
            price="$449",
            was_price="$599",
            image_src=IMG_MONITOR,
            theme=MARKET_THEME,
        ),
        comparison_page(
            "compare",
            "$449",
            "Color-accurate panel",
            "$329",
            "Budget 1440p option",
            eyebrow="WHICH MONITOR?",
            versus="VS",
            background_src=IMG_DESK,
            theme=MARKET_THEME,
        ),
        deal_page(
            "deal-1",
            "Mechanical Keyboard Bundle",
            badge="LIMITED DROP",
            description="Aluminum board, tactile switches, and matching desk mat in one kit.",
            was_price="$249",
            price="$179",
            background_src=IMG_KEYBOARD,
            theme=MARKET_THEME,
        ),
        key_takeaways_page(
            "takeaways",
            "What to prioritize",
            [
                "Buy the monitor first.",
                "Keep input devices consistent across laptop and desktop.",
                "Use warm task lighting to reduce contrast fatigue at night.",
            ],
            background_src=IMG_NOTES,
            theme=MARKET_THEME,
            layout=CARD_OVERLAY_LAYOUT,
        ),
        cta_page(
            "finale",
            "See the full shopping guide",
            body="Detailed picks, alternate budgets, and the exact accessories shown in this story.",
            cta_text="Open buying guide",
            cta_url="https://example.com/guides/desk-setup",
            background_src=IMG_DESK,
            theme=MARKET_THEME,
        ),
    ],
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
story.save(str(OUTPUT))
print(f"Saved -> {OUTPUT}")

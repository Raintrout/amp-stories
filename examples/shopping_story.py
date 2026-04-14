"""AMP Story: Tech Deals — demonstrates SHOPPING_THEME and commerce templates.

A fictional shopping story featuring product cards, deal highlights,
a comparison page, and a listicle, all styled with the SHOPPING_THEME.

Run with:
    uv run python examples/shopping_story.py

Output: examples/output/shopping_story.html
Validate at: https://validator.ampproject.org/
"""

from __future__ import annotations

import pathlib

from amp_stories import (
    SHOPPING_THEME,
    Story,
    comparison_page,
    cta_page,
    deal_page,
    listicle_page,
    product_page,
    title_page,
)

OUTPUT = pathlib.Path(__file__).parent / "output" / "shopping_story.html"

PUBLISHER = "Deal Finder"
LOGO = "https://placehold.co/60x60/ffffff/e63946?text=DF"
POSTER = "https://placehold.co/900x1600/ffffff/1a1a1a?text=Tech+Deals"
CANONICAL = "https://example.com/stories/tech-deals"

pages = [
    # 1 — Cover
    title_page(
        "cover",
        "Best Tech Deals",
        subtitle="This week's top picks",
        eyebrow="EDITOR'S CHOICE",
        theme=SHOPPING_THEME,
    ),

    # 2 — Featured product (solid background so SHOPPING_THEME's dark text is legible)
    product_page(
        "product-1",
        "ANC Headphones",
        brand="SoundCore Pro",
        price="$89.99",
        was_price="$149.99",
        theme=SHOPPING_THEME,
    ),

    # 3 — Deal highlight
    deal_page(
        "deal-1",
        "Laptop Bundle",
        badge="48H ONLY",
        description="15-inch laptop + wireless mouse + carrying case.",
        was_price="$1,299",
        price="$799",
        theme=SHOPPING_THEME,
    ),

    # 4 — Product 2
    product_page(
        "product-2",
        "4K Smart TV 55\"",
        brand="VisionTech",
        price="$399",
        was_price="$599",
        theme=SHOPPING_THEME,
    ),

    # 5 — Comparison
    comparison_page(
        "compare",
        "$89",
        "Standard model",
        "$129",
        "Pro model",
        eyebrow="WHICH ONE TO BUY?",
        versus="VS",
        theme=SHOPPING_THEME,
    ),

    # 6 — Listicle: top features
    listicle_page(
        "features",
        "What to look for",
        items=[
            "Active Noise Cancellation",
            "24h+ total battery life",
            "Multipoint Bluetooth pairing",
            "IPX4 water resistance",
        ],
        theme=SHOPPING_THEME,
    ),

    # 7 — Flash deal
    deal_page(
        "deal-2",
        "Smart Home Starter Kit",
        badge="FLASH SALE",
        description="Hub + 4 smart bulbs + 2 smart plugs.",
        price="$59.99",
        was_price="$119.99",
        theme=SHOPPING_THEME,
    ),

    # 8 — CTA
    cta_page(
        "finale",
        "See all deals",
        body="New offers added every day. Don't miss out.",
        cta_text="Shop now",
        cta_url="https://example.com/deals",
        theme=SHOPPING_THEME,
    ),
]

story = Story(
    title="Best Tech Deals This Week",
    publisher=PUBLISHER,
    publisher_logo_src=LOGO,
    poster_portrait_src=POSTER,
    canonical_url=CANONICAL,
    custom_css=SHOPPING_THEME.generate_css(),
    pages=pages,
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
story.save(str(OUTPUT))
print(f"Saved → {OUTPUT}")

# amp-stories-python

A lightweight, zero-dependency Python library for generating [AMP Stories](https://amp.dev/about/stories/) (Web Stories) HTML.

## Features

- **Constructor-based API** — compose stories with nested Python dataclasses
- **High-level page templates** — cover, timeline, fact-check, itinerary, commerce, data, CTA, and more
- **Layout and motion presets** — reusable `LayoutPreset` and `MotionPreset` objects for consistent composition
- **Theme system** — CSS generated from typed `Theme` objects; cohesive built-in families for editorial, travel, and commerce
- **Strict validation** — `ValidationError` raised at construction time with clear messages
- **Auto script injection** — required AMP extension scripts detected and injected automatically
- **Full AMP Stories spec coverage** — pages, layers, animations, bookend, outlinks, attachments, interactive polls, live stories, `amp-list`
- **Zero runtime dependencies** — stdlib only (`html`, `json`, `warnings`)
- **100% test coverage**

## Installation

```bash
uv add amp-stories
# or
pip install amp-stories
```

## Quick start — template API

The fastest path is:

1. Pick a site-level theme family.
2. Use the page factories with the built-in layout defaults.
3. Override layout or motion only when a page truly needs a different composition.

```python
from amp_stories import (
    BOTTOM_STACK_LAYOUT,
    CARD_OVERLAY_LAYOUT,
    SUMMIT_THEME,
    Story,
    card_overlay_page,
    cta_page,
    hero_video_page,
    key_takeaways_page,
    title_page,
)

theme = SUMMIT_THEME

story = Story(
    title="Mountain Biking in Moab",
    publisher="Trail Times",
    publisher_logo_src="https://example.com/logo.png",
    poster_portrait_src="https://example.com/poster.jpg",
    canonical_url="https://example.com/moab-story.html",
    poster_landscape_src="https://example.com/poster-landscape.jpg",
    supports_landscape=True,
    custom_css=theme.generate_css(),
    pages=[
        title_page(
            "cover",
            "Moab in May",
            subtitle="Red rock riding at its finest",
            eyebrow="TRAIL REPORT",
            background_src="https://example.com/hero.jpg",
            theme=theme,
            layout=BOTTOM_STACK_LAYOUT,
        ),
        hero_video_page(
            "hero-video",
            "https://example.com/clip.mp4",
            "Ride early for colder rock and emptier lines",
            eyebrow="FIELD NOTE",
            subtitle="The first hour changes the whole day.",
            poster="https://example.com/clip-poster.jpg",
            theme=theme,
        ),
        card_overlay_page(
            "context",
            "Why this route works for a weekend story",
            eyebrow="ROUTE FIT",
            body="One iconic section, one scenic payoff, and one clean bailout option.",
            background_src="https://example.com/map.jpg",
            theme=theme,
            layout=CARD_OVERLAY_LAYOUT,
        ),
        key_takeaways_page(
            "takeaways",
            "What to remember",
            [
                "Start before sunrise.",
                "Carry more water than you think you need.",
                "Build around one hero trail, not three rushed ones.",
            ],
            background_src="https://example.com/notes.jpg",
            theme=theme,
            layout=CARD_OVERLAY_LAYOUT,
        ),
        cta_page(
            "finale",
            "Plan your trip",
            body="Gear lists, trail maps, and campsite picks.",
            cta_text="Read the guide",
            cta_url="https://example.com/moab-guide",
            background_src="https://example.com/finale.jpg",
            theme=theme,
        ),
    ],
)
story.save("moab.html")
```

## Themes

A `Theme` controls colours, typography, animation defaults, content-card styling, and optional landscape scaling.
Pass `theme.generate_css()` to `Story.custom_css` so the `.ast-*` class styles load.

### Recommended theme families

| Constant | Description |
|---|---|
| `SIGNAL_THEME` | Editorial/news default — deep charcoal, warm white, coral alert accent |
| `SUMMIT_THEME` | Travel/adventure default — forest/slate tones, warm text, cinematic feel |
| `MARKET_THEME` | Commerce/recommendation default — dark neutral base, gold accent, product-forward |
| `FEATURE_THEME` | Premium feature/lifestyle default — richer editorial palette and display typography |

### Legacy built-in themes

These remain available for backwards compatibility and simpler use cases.

| Constant | Description |
|---|---|
| `SLATE_THEME` | Default — dark navy/slate, near-white text, teal accent |
| `LIGHT_THEME` | White background, near-black text, blue accent |
| `EDITORIAL_THEME` | Near-black background, white text, red accent |
| `WARM_THEME` | Off-white background, rich brown text, amber accent |
| `NEWS_THEME` | Breaking-news style — dark bg, white text, red accent, mixed serif/sans fonts |
| `TRAVEL_THEME` | Deep forest green, warm off-white, gold accent; landscape-scaled at 0.75× |
| `SHOPPING_THEME` | Clean white bg, near-black text, vivid red accent, sans-serif |

### Theme guidance

- Use `SIGNAL_THEME` for live coverage, explainers, and accountability reporting.
- Use `SUMMIT_THEME` for destination, outdoors, and image-led editorial stories.
- Use `MARKET_THEME` for shopping, product recommendations, and deal-driven stories.
- Use `FEATURE_THEME` when the story should feel more magazine-like than urgent or utilitarian.

### Custom themes

```python
from amp_stories import Theme, Story

theme = Theme(
    bg_color="#1a1a2e",
    text_color="#eaeaea",
    accent_color="#e94560",
    muted_color="#888888",
    panel_color="#101522",
    panel_opacity=0.84,
    caption_opacity=0.7,
    font_family="'Inter', sans-serif",
    heading_font="'Playfair Display', serif",
    h1_size="3.2rem",
    overlay_opacity=0.55,
    panel_radius="1rem",
    content_max_width="34rem",
    heading_animate_in="fly-in-bottom",
    body_animate_in="fade-in",
    landscape_font_scale=0.8,      # scale all font sizes in landscape orientation
    google_font="Playfair+Display:400,700",  # auto-builds Google Fonts URL
)

story = Story(..., custom_css=theme.generate_css(),
              font_links=[url for url in [theme.get_google_fonts_url()] if url])
```

## Page templates

All factory functions accept a `theme` keyword argument (default: `SLATE_THEME`) and an optional `auto_advance_after` CSS duration.
Many also accept `layout` and `motion` overrides so you can keep a consistent site-wide system while still changing page composition intentionally.

### Layout and motion presets

| Constant | Description |
|---|---|
| `BOTTOM_STACK_LAYOUT` | Default lower-third stack; best general-purpose layout |
| `TOP_STACK_LAYOUT` | Better for alerts, skyline shots, and scenes where the lower frame matters |
| `CENTER_FOCUS_LAYOUT` | Best for dividers, quotes, and stat hero pages |
| `CAPTION_BAND_LAYOUT` | Shallow media caption treatment |
| `CARD_OVERLAY_LAYOUT` | Semi-opaque text card for busy imagery and commerce pages |
| `SPLIT_PANEL_LAYOUT` | Comparison and compact data framing |
| `EDITORIAL_SOFT_MOTION` | Conservative headline/body reveal for news and explainers |
| `ADVENTURE_CINEMATIC_MOTION` | Media-first cinematic motion profile for travel/outdoors |
| `COMMERCE_CRISP_MOTION` | Tighter conversion-oriented motion profile for shopping |

### Content pages

| Function | Description |
|---|---|
| `title_page(id, title, *, subtitle, eyebrow, background_src)` | Cover / title card |
| `text_page(id, heading, body, *, background_src)` | Heading + body paragraph |
| `quote_page(id, quote, *, attribution, background_src)` | Pull-quote with decorative mark |
| `stat_page(id, stat, label, *, context, background_src)` | Large stat number + descriptor |
| `chapter_page(id, title, *, chapter_number, background_src)` | Section divider |
| `card_overlay_page(id, heading, *, body, eyebrow, background_src)` | Generic text-card page for busy imagery |
| `photo_page(id, image_src, *, overlay, caption, eyebrow)` | Full-bleed photo |
| `video_page(id, src, *, poster, caption, eyebrow, autoplay, loop, muted)` | Full-bleed video |
| `hero_video_page(id, src, headline, *, eyebrow, subtitle, poster)` | Cinematic video-led hero page |
| `listicle_page(id, title, items, *, background_src)` | Bulleted list; raises if `items` empty |
| `key_takeaways_page(id, title, takeaways, *, background_src)` | Condensed three-to-five point summary card |
| `cta_page(id, heading, *, body, cta_text, cta_url, background_src)` | CTA finale with outlink button |

### News / live updates

| Function | Description |
|---|---|
| `breaking_page(id, headline, *, badge, body, background_src)` | Alert page with `.ast-badge`; default badge `"BREAKING"` |
| `update_page(id, number, headline, body, *, background_src)` | Numbered live-update card (`UPDATE 1`, `UPDATE 2` …) |
| `timeline_step_page(id, label, headline, *, body, background_src)` | Timestamped or staged development card |
| `fact_check_page(id, claim, verdict, *, explanation, background_src)` | Claim/verdict/explanation structure |

### Travel / itinerary

| Function | Description |
|---|---|
| `trip_page(id, number, location, *, region, highlight, background_src)` | Numbered trip card (`TRIP 01` …) |
| `itinerary_page(id, day, destination, *, details, background_src)` | Day card (`DAY N` or custom string) with optional detail list |
| `process_step_page(id, step_label, title, body, *, background_src)` | Travel or explainer step-by-step card |

### Data visualisation

| Function | Description |
|---|---|
| `stat_page(id, stat, label, *, context, background_src)` | Single large figure |
| `comparison_page(id, left_stat, left_label, right_stat, right_label, *, eyebrow, versus, background_src)` | Side-by-side stat comparison using thirds layout |
| `data_chart_page(id, title, rows, *, max_value, background_src)` | Horizontal bar chart; `rows` is a list of `ChartRow(label, value, display?)` |

### Shopping / e-commerce

| Function | Description |
|---|---|
| `product_page(id, product_name, *, brand, price, was_price, image_src)` | Product card with optional strikethrough "was" price |
| `deal_page(id, title, *, badge, description, price, was_price, background_src)` | Promotion highlight with optional badge and pricing |

### `ChartRow`

```python
from amp_stories import ChartRow, data_chart_page

page = data_chart_page(
    "chart",
    "Most-used languages",
    rows=[
        ChartRow("Python",     45, display="45%"),
        ChartRow("JavaScript", 35, display="35%"),
        ChartRow("Rust",       10, display="10%"),
        ChartRow("Go",         10, display="10%"),
    ],
    theme=theme,
)
```

Bar widths are computed as `value / max_value * 100%` (max inferred from data or set explicitly).

## Low-level API

For full control, construct `Page` and `Layer` objects directly:

```python
from amp_stories import (
    Story, Page, Layer,
    AmpImg, heading, paragraph,
    PageOutlink, Bookend, BookendComponent, BookendShareProvider,
)

story = Story(
    title="The Alps in Autumn",
    publisher="Example Media",
    publisher_logo_src="https://example.com/logo.png",
    poster_portrait_src="https://example.com/poster.jpg",
    canonical_url="https://example.com/alps-story.html",
    supports_landscape=True,
    pages=[
        Page(
            page_id="cover",
            auto_advance_after="8s",
            layers=[
                Layer("fill", children=[
                    AmpImg("https://example.com/hero.jpg", alt="Mountain at dusk"),
                ]),
                Layer("vertical", children=[
                    heading("The Alps in Autumn", animate_in="fly-in-bottom"),
                    paragraph(
                        "A visual journey through the peaks.",
                        animate_in="fade-in",
                        animate_in_delay="0.4s",
                    ),
                ]),
            ],
        ),
        Page(
            page_id="details",
            layers=[
                Layer("fill", children=[
                    AmpImg("https://example.com/valley.jpg", alt="Green valley"),
                ]),
                Layer("vertical", children=[
                    heading("Hidden Valleys", level=2),
                    paragraph("Discover routes less traveled."),
                ]),
            ],
            outlink=PageOutlink(
                href="https://example.com/trails",
                cta_text="Read More",
            ),
        ),
    ],
    bookend=Bookend(
        share_providers=[BookendShareProvider("twitter")],
        components=[
            BookendComponent(type="heading", text="More Stories"),
            BookendComponent(type="small", title="Winter in the Alps",
                             url="https://example.com/winter",
                             image="https://example.com/winter-thumb.jpg"),
        ],
    ),
)

story.save("alps.html")
```

### Layer templates

`"fill"` — single full-bleed element · `"vertical"` — stacked children · `"horizontal"` — side-by-side · `"thirds"` — three equal columns (use `grid_area="left-third"` / `"middle-third"` / `"right-third"`)

### Animation effects

`animate_in` values: `fly-in-bottom`, `fly-in-top`, `fly-in-left`, `fly-in-right`, `fade-in`, `rotate-in-left`, `rotate-in-right`, `drop`, `pan-left`, `pan-right`, `pan-up`, `pan-down`, `zoom-in`, `zoom-out`, `pulse`, `twirl-in`, `whoosh-in-left`, `whoosh-in-right`

### `PageOutlink`

```python
PageOutlink(
    href="https://example.com",
    cta_text="Swipe up",
    theme="light",                # "light" | "dark" | "custom"
    cta_accent_color=None,        # required if theme="custom"
    cta_accent_element=None,      # "text" | "background"
    cta_image=None,               # URL to 32×32 icon, or "none"
)
```

### Live stories

```python
Story(
    ...,
    live_story=True,
    data_poll_interval=15000,    # minimum 15000 ms
    pages=[
        Page("p1", layers=[...], data_sort_time=1700000000000),
        Page("p2", layers=[...], data_sort_time=1700000001000),
    ],
)
```

## Examples

The `examples/` directory contains runnable stories:

| File | Demonstrates |
|---|---|
| `breaking_news.py` | `SIGNAL_THEME`, `TOP_STACK_LAYOUT`, `timeline_step_page`, `fact_check_page`, `hero_video_page` |
| `ca_backpacking.py` | `SUMMIT_THEME`, cinematic travel layouts, `process_step_page`, `hero_video_page`, `data_chart_page` |
| `shopping_story.py` | `MARKET_THEME`, `CARD_OVERLAY_LAYOUT`, `product_page`, `deal_page`, `comparison_page`, `key_takeaways_page` |

```bash
uv run python examples/breaking_news.py   # → examples/output/breaking_news.html
uv run python examples/ca_backpacking.py  # → examples/output/ca_backpacking.html
uv run python examples/shopping_story.py  # → examples/output/shopping_story.html
```

## Development

```bash
uv sync                                               # install dev dependencies
uv run pytest                                         # run tests
uv run pytest --cov=amp_stories --cov-fail-under=100  # with coverage
uv run ruff check amp_stories/ tests/                 # lint
uv run ruff check --fix amp_stories/ tests/           # lint + auto-fix
uv run ty check amp_stories/                          # type check
```

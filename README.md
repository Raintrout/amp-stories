# amp-stories-python

A lightweight, zero-dependency Python library for generating [AMP Stories](https://amp.dev/about/stories/) (Web Stories) HTML.

## Features

- **Constructor-based API** — compose stories with nested Python dataclasses
- **Strict validation** — `ValidationError` raised at construction time with clear messages
- **Auto script injection** — required AMP extension scripts detected and injected automatically
- **Full AMP Stories spec coverage** — pages, layers, animations, bookend, outlinks, attachments, live stories, amp-list
- **Zero runtime dependencies** — stdlib only (`html`, `json`, `warnings`)
- **100% test coverage**

## Installation

```bash
uv add amp-stories
# or
pip install amp-stories
```

## Quick start

```python
from amp_stories import (
    Story, Page, Layer,
    AmpImg, heading, paragraph,
    Bookend, BookendComponent, BookendShareProvider,
    PageOutlink,
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
            BookendComponent(
                type="small",
                title="Winter in the Alps",
                url="https://example.com/winter",
                image="https://example.com/winter-thumb.jpg",
            ),
        ],
    ),
)

story.save("output/alps.html")
# or: html_string = story.render()
```

## API reference

### `Story`

Root document. Required fields: `title`, `publisher`, `publisher_logo_src`, `poster_portrait_src`, `canonical_url`, `pages`.

```python
Story(
    title="...",
    publisher="...",
    publisher_logo_src="https://...",
    poster_portrait_src="https://...",
    canonical_url="https://...",
    pages=[...],
    # Optional:
    poster_square_src=None,
    poster_landscape_src=None,
    supports_landscape=False,
    background_audio=None,
    live_story=False,
    live_story_disabled=False,
    data_poll_interval=None,      # ms, min 15000
    desktop_aspect_ratio=None,    # e.g. "16:9"
    lang="en",
    custom_css=None,              # injected as <style amp-custom>
    bookend=None,
    entity=None,
    entity_logo_src=None,
    entity_url=None,
)
```

### `Page`

One screen of the story. Required: `page_id` (valid HTML id), `layers` (non-empty list).

```python
Page(
    page_id="cover",
    layers=[...],
    auto_advance_after="5s",      # CSS duration or media element id
    background_audio=None,
    outlink=None,                 # PageOutlink — mutually exclusive with attachment
    attachment=None,              # PageAttachment
    data_sort_time=None,          # Unix ms timestamp for live stories
)
```

### `Layer`

A `<amp-story-grid-layer>`. Templates: `"fill"`, `"vertical"`, `"horizontal"`, `"thirds"`.

```python
Layer(
    template="fill",
    children=[AmpImg("bg.jpg")],
    grid_area=None,               # for "thirds" positioning
    aspect_ratio=None,            # e.g. "4:3"
    preset=None,                  # "2021-background" | "2021-foreground"
    anchor=None,                  # "top" | "bottom" | "top-left" | ...
)
```

### Elements

```python
AmpImg("img.jpg", width=900, height=1600, alt="", layout="fill")
AmpVideo("video.mp4", loop=False, autoplay=True, muted=True, poster=None)
AmpAudio("audio.mp3", autoplay=True, loop=False)
AmpList("https://example.com/data.json", template="<p>{{item}}</p>")

# Convenience text constructors:
heading("Title", level=1)        # <h1>–<h6>
paragraph("Body text")           # <p>
span("Inline")                   # <span>
blockquote("Quote")              # <blockquote>

# Container:
DivElement(children=[...], style=None, class_=None)
```

All media and text elements support flat animation kwargs:

```python
heading(
    "Title",
    animate_in="fly-in-bottom",         # see all effects below
    animate_in_duration="0.5s",
    animate_in_delay="0.3s",
    animate_in_after="other-element-id",
    id="my-heading",
)
```

**`animate_in` effects:** `fly-in-bottom`, `fly-in-top`, `fly-in-left`, `fly-in-right`, `fade-in`, `rotate-in-left`, `rotate-in-right`, `drop`, `pan-left`, `pan-right`, `pan-up`, `pan-down`, `zoom-in`, `zoom-out`, `pulse`, `twirl-in`, `whoosh-in-left`, `whoosh-in-right`

### `PageOutlink` (recommended)

Swipe-up / tap CTA that links out to a URL.

```python
PageOutlink(
    href="https://example.com",
    cta_text="Swipe up",
    theme="light",                # "light" | "dark" | "custom"
    cta_accent_color=None,        # required if theme="custom", e.g. "#FF0000"
    cta_accent_element=None,      # "text" | "background"
    cta_image=None,               # URL to 32×32 icon, or "none"
)
```

### `PageAttachment` (deprecated)

Swipe-up drawer. Supports link-list mode or HTML mode (not both).

```python
# Link-list mode:
PageAttachment(
    cta_text="Swipe up",
    theme="light",
    links=[
        AttachmentLink("Article", "https://example.com", image="thumb.jpg"),
    ],
)

# HTML mode:
PageAttachment(
    html_content=[heading("More details"), paragraph("...")],
)
```

### `Bookend`

End-card with sharing and related links.

```python
Bookend(
    share_providers=[
        BookendShareProvider("twitter"),
        BookendShareProvider("facebook", param="app_id_here"),
    ],
    components=[
        BookendComponent(type="heading", text="More Stories"),
        BookendComponent(type="small", title="Article", url="https://...", image="https://..."),
        BookendComponent(type="cta-link", title="Subscribe", url="https://..."),
    ],
)
```

**Share providers:** `email`, `twitter`, `tumblr`, `facebook`, `gplus`, `linkedin`, `whatsapp`, `sms`, `system`

**Component types:** `heading`, `small`, `portrait`, `landscape`, `cta-link`, `textbox`

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

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=amp_stories --cov-fail-under=100

# Lint
uv run ruff check src/ tests/

# Type check
uv run ty check src/
```

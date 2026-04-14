# Web Story Style Guide

## Purpose

This guide defines a cohesive visual and structural system for revamping the template layer in this repository so it can support a wide range of Web Story page types while still feeling like one product across a website.

It is based on:

- Existing template/theme patterns in this repo
- Google for Creators editorial guidance for Web Stories
- Current publisher and brand usage patterns surfaced in the Google for Creators showcase
- Representative publisher examples from travel and editorial sites

## Research Summary

### What current Web Stories tend to look like

Across the official showcase and publisher examples, a few patterns repeat:

- News publishers use short, high-contrast headlines, badge-driven urgency, and stepwise update cards.
- Travel and adventure publishers lean on full-bleed destination imagery, restrained copy, route/itinerary structures, and chapter dividers.
- Lifestyle and commerce-oriented stories use strong visual hierarchy, product closeups, quick list formats, and CTA endings.
- Most strong stories keep one dominant idea per page instead of mixing multiple competing text blocks.
- Motion is usually subtle: background pan/zoom plus a staggered text reveal, not many competing element animations.

### Representative examples

- Google for Creators showcase highlights publishers such as USA Today, Bustle, Vice, Refinery29, Forbes, Lonely Planet, and Input using distinct but structured Web Story formats.
- Lonely Planet travel stories emphasize destination-led photography and modular recommendation pages.
- Refinery29 and related showcase examples lean into bold editorial headlines, food/beauty/product framing, and swipe-through list structures.

### Key official guidance to carry into the system

- Video-first and full-bleed media should be the default where possible.
- Keep text concise. Google recommends less than 280 characters and roughly 40 to 70 words per page.
- Preserve legibility with contrast, overlays, or text boxes; do not rely on busy photography carrying text.
- Keep important content inside the safe zone.
- Simple animations should complete quickly, generally under 500ms, while background panning can run longer.
- Stories should generally be 4 to 30 pages, with 11 to 15 pages being a common engagement range.

## Design Principles

### 1. One system, many page types

The template layer should stop being a flat collection of unrelated page factories and instead become a system with:

- `page category`
- `layout variant`
- `content schema`
- `motion preset`
- `theme token set`

The goal is variety through composition, not by inventing one-off templates for every niche.

### 2. One idea per page

Every page should answer one question only:

- What is the viewer meant to notice first?
- What is the supporting context?
- What action, if any, should happen next?

### 3. Media first, text second

Text should explain or focus the media, not compete with it. Full-screen imagery, portrait video, and strong focal crops should do most of the work.

### 4. Consistency at the site level

Different stories can have different moods, but the website should still feel coherent through:

- Shared spacing rules
- Shared text placements
- Shared motion language
- Shared theme families
- Shared CTA treatment

## Proposed Template Taxonomy

These are the recommended page families for the revamp.

### Core narrative pages

- `cover`: Hero entry page with title, eyebrow, optional subtitle, strong media.
- `chapter-divider`: Section break with large title and minimal supporting text.
- `statement`: Big idea, quote, fact, or pull-line.
- `body`: Short heading plus short supporting paragraph.
- `media-caption`: Full-bleed photo or video with compact caption.
- `ending-cta`: Final page with one clear action.

### News pages

- `breaking-alert`: Badge plus headline plus one-line summary.
- `live-update`: Sequential numbered updates.
- `timeline-step`: Event marker with timestamp or stage label.
- `fact-check`: Claim, verdict, supporting line.
- `key-takeaways`: Three to five concise bullets.

### Adventure and travel pages

- `destination-hero`: Place name, region, seasonal mood.
- `itinerary-stop`: Day/stop label plus destination plus two to four details.
- `map-route`: Route headline with visual path or region emphasis.
- `packing-tip`: Single practical recommendation with icon or object image.
- `best-for`: Audience-fit page such as hikers, families, budget travelers.

### Commerce and product pages

- `product-hero`: Brand, product, price, image.
- `deal-card`: Badge, offer, supporting description, current/was price.
- `comparison`: Two options or features side-by-side.
- `list-ranked`: Ordered product or recommendation list.
- `swipe-shop-cta`: Final conversion page.

### Data and explainer pages

- `stat-hero`: One big number and short label.
- `chart-bars`: Horizontal bars or progress rows.
- `before-after`: Side-by-side comparison frame.
- `process-step`: Step title plus one supporting sentence.
- `myth-vs-fact`: Two-column correction pattern.

## Recommended Layout System

Each page type should choose from a small set of reusable layout anchors.

### Layout anchors

- `bottom-stack`: Best default. Text sits in the lower third over media.
- `top-stack`: Good for travel/trail/skyline images where lower image detail matters.
- `center-focus`: Use sparingly for chapter dividers, quotes, and stats.
- `split-panel`: For comparisons, timelines, and data.
- `caption-band`: Thin text band at bottom for photo/video pages.
- `card-overlay`: Semi-opaque text box floating over busy imagery.

### Recommended default by content type

- News: `top-stack` for alerts, `bottom-stack` for updates, `split-panel` for facts/data.
- Adventure: `bottom-stack` for hero and itinerary pages, `caption-band` for scenic media, `center-focus` for chapter breaks.
- Commerce: `card-overlay` or `bottom-stack` to preserve product visibility.
- Explainers: `center-focus` for stats, `split-panel` for comparisons and charts.

## Text Placement Rules

### Safe-zone policy

Critical text should stay in a conservative central vertical band and avoid the extreme top and bottom edges where UI chrome and device cropping are most likely to interfere.

### Placement rules

- Default important text block: lower-middle to lower-third.
- Put urgency badges and eyebrows above the main headline, not detached in a corner.
- Keep captions shallow and wide; they should not become mini-articles.
- Avoid placing long copy directly over faces or visual focal points.
- If the media is busy, switch from transparent overlay text to a solid or blurred text card.

### Copy limits

- Headline: 3 to 8 words preferred.
- Supporting deck/body: 12 to 28 words preferred.
- Maximum body copy on any single page: about 40 to 70 words.
- Bullets/details: 2 to 5 lines only.

## Motion System

The current repo already uses a stagger pattern. Keep that idea, but formalize it into motion presets.

### Motion principles

- Motion should guide reading order, not call attention to itself.
- One page should usually have one background motion plus one staggered text sequence.
- Avoid rotation-heavy or novelty motion unless the story is intentionally playful.

### Recommended motion presets

#### `editorial-soft`

- Background: subtle pan or slow zoom
- Eyebrow/badge: `fade-in`
- Headline: `fly-in-bottom`
- Supporting text: `fade-in`
- Use for: news, features, explainers

#### `adventure-cinematic`

- Background: Ken Burns style pan/zoom
- Eyebrow: `fade-in`
- Title: `whoosh-in-left` or `fly-in-bottom`
- Body/caption: `fade-in`
- Use for: destination, itinerary, photo-led pages

#### `commerce-crisp`

- Background/product image: static or very slight zoom
- Badge: `pulse-in` only if truly promotional
- Product name/price: `fly-in-bottom`
- Secondary text: `fade-in`
- Use for: shopping and deal pages

### Timing rules

- Text entrance: 250ms to 500ms
- Stagger delay: 120ms to 240ms
- Background motion: 3s to 8s depending on page dwell
- Avoid more than three independently animated text elements on one page

## Theme Family

The site should ship with a small, opinionated theme family rather than unlimited ad hoc colors.

### 1. `Signal`

Best for news and explainers.

- Background: deep charcoal or midnight navy
- Text: warm white
- Accent: alert red or electric coral
- Mood: urgent, trustworthy, clean

### 2. `Summit`

Best for travel, adventure, outdoors.

- Background: forest, slate, or deep earth
- Text: off-white
- Accent: alpine teal or sunrise amber
- Mood: expansive, cinematic, grounded

### 3. `Market`

Best for commerce, shopping, recommendations.

- Background: soft black, cream-black contrast, or muted stone
- Text: near-white or deep graphite depending on media
- Accent: saffron, lime-gold, or sharp cyan
- Mood: modern, product-forward, conversion-aware

### 4. `Feature`

Best for magazine/editorial/lifestyle content.

- Background: rich neutral with stronger typography contrast
- Text: warm white
- Accent: rose, cobalt, or citrus depending on brand
- Mood: premium, expressive, stylish

## Recommended Default Website Look

If the goal is one cohesive website-level story experience, use this as the primary default:

### Primary theme

- Theme: `Summit` as the base system theme
- Why: it works for adventure/travel, still feels premium for editorial, and can flex into data or news with accent swaps

### Accent variants

- News variant: `Summit` base with `Signal` accent rules
- Commerce variant: `Summit` base with `Market` accent and card treatment

### Typography direction

- Headings: a high-contrast serif or serif-adjacent display face
- Body: a clean sans or readable serif companion
- Rule: expressive headings, highly legible body, never more than two families in one story

For this repo, the visual direction should move away from generic newspaper styling and toward:

- cinematic headline typography
- restrained but premium body typography
- fewer colors
- stronger image-led composition

## Page-by-Page Design Defaults

### Cover

- Layout: `bottom-stack`
- Media: full-bleed photo or video
- Text: eyebrow, title, optional subtitle
- Motion: `adventure-cinematic`
- Overlay: medium dark scrim

### News alert

- Layout: `top-stack`
- Text: badge, headline, one-line summary
- Motion: `editorial-soft`
- Theme: `Signal`

### Update/timeline

- Layout: `bottom-stack`
- Text: label plus headline plus short body
- Motion: `editorial-soft`
- Theme: `Signal`

### Destination/itinerary

- Layout: `bottom-stack`
- Text: day/stop label, location, two to three detail lines
- Motion: `adventure-cinematic`
- Theme: `Summit`

### Photo/video caption

- Layout: `caption-band`
- Text: one caption line, optional eyebrow
- Motion: background only or caption fade
- Theme: inherit story theme

### Stat/data

- Layout: `center-focus` or `split-panel`
- Text: one big number or one compact chart
- Motion: headline reveal only
- Theme: `Signal` or `Feature`

### Product/deal

- Layout: `card-overlay`
- Text: brand or badge, product/deal title, price
- Motion: `commerce-crisp`
- Theme: `Market`

### Final CTA

- Layout: `bottom-stack`
- Text: one headline, one support line
- CTA: single outlink only
- Motion: `fade-in` plus button reveal

## Template API Direction

This is the recommended structural direction for the code revamp.

### Move from page-specific factories to composed templates

Instead of only functions like `title_page()` and `quote_page()`, the system should support:

- `PageSpec`
- `LayoutPreset`
- `MotionPreset`
- `ThemeVariant`
- `ContentBlock`

### Suggested model

- `page_type`: semantic purpose such as `cover`, `update`, `itinerary-stop`
- `layout`: placement strategy such as `bottom-stack`, `split-panel`
- `variant`: visual style such as `immersive`, `card`, `minimal`
- `theme`: token set
- `content`: structured fields validated per page type

This makes it easier to add new use cases without adding a new CSS universe each time.

## Immediate Implementation Recommendations For This Repo

### Keep

- Theme-driven CSS generation
- High-level factory APIs
- Existing travel/news/shopping coverage as a semantic starting point

### Change

- Split visual layout concerns from content semantics
- Add explicit layout presets
- Add motion presets instead of raw repeated animation assignments
- Add theme families with variants rather than one theme per use case
- Add text container styles for busy-image pages
- Standardize caption, badge, price, and metadata treatments

### Add next

- `timeline_step_page`
- `map_route_page`
- `fact_check_page`
- `key_takeaways_page`
- `process_step_page`
- `before_after_page`
- `hero_video_page`
- `card_overlay_page`

## Recommended Baseline Defaults

If only one default system is implemented first, use:

- Layout default: `bottom-stack`
- Motion default: `editorial-soft`
- Theme default: `Summit`
- Overlay default: medium scrim around `0.48` to `0.62`
- Heading animation: `fly-in-bottom`
- Body animation: `fade-in`
- Stagger delay: `0.18s` to `0.24s`
- Text card fallback: enabled when media contrast is weak

This will produce a cohesive, premium, image-led experience suitable for a website that needs to publish travel, editorial, news, and occasional commerce stories without feeling fragmented.

## Sources

- Google for Creators, Web Stories showcase: https://creators.google/en-us/content-creation-products/own-your-content/web-stories/
- Google for Creators, Modern Storytelling with Web Stories hub: https://creators.google/en-us/content-creation-guides/modern-storytelling-with-web-stories/
- Google for Creators, Web Story taxonomy: https://creators.google/pt-br/content-creation-guides/modern-storytelling-with-web-stories/web-story-taxonomy/
- Google for Creators, Introduction to editorial guidelines: https://creators.google/hi-in/content-creation-guides/modern-storytelling-with-web-stories/introduction-to-editorial-guidelines/
- Google for Creators, Text and font editorial guidelines: https://creators.google/en-us/content-creation-guides/modern-storytelling-with-web-stories/web-story-text-and-font-editorial-guidelines/
- Google for Creators, Video and images editorial guidelines: https://creators.google/en-us/content-creation-guides/modern-storytelling-with-web-stories/video-and-images-editorial-guidelines/
- Google for Creators, Animations editorial guidelines: https://creators.google/en-us/content-creation-guides/modern-storytelling-with-web-stories/animations-editorial-guidelines/
- Google for Creators, Embeds, links and interactive content editorial guidelines: https://creators.google/en-us/content-creation-guides/modern-storytelling-with-web-stories/embeds-links-and-interactive-content-editorial-guidelines/
- Google for Creators, Web Story publishing checklist: https://creators.google/en-us/content-creation-guides/modern-storytelling-with-web-stories/web-story-publishing-checklist/
- Google for Creators, Web Story discovery and promotion: https://creators.google/en-us/content-creation-guides/modern-storytelling-with-web-stories/web-story-discovery-and-promotion/
- Lonely Planet, example destination story: https://www.lonelyplanet.com/articles/best-state-parks-in-the-usa
- Lonely Planet, example family adventure story: https://www.lonelyplanet.com/articles/where-to-travel-with-elementary-school-kids
- Refinery29, example explainer/story format surfaced via search: https://www.refinery29.com/stories/how-stuff-is-made-money/

## Notes

- Observations about publisher patterns are partly inferred from the Google for Creators showcase examples and representative publisher pages, not from a formal dataset.
- Discover availability can change over time; the cited guidance page currently says Web Stories surface in Google Discover in the United States, India, and Brazil.

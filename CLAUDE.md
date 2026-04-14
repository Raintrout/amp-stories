# amp-stories-python

## Project overview

Python library for generating AMP Stories (Web Stories) HTML. Lives at `src/amp_stories/`. Zero runtime dependencies — stdlib only.

## Commands

```bash
uv run pytest                                       # run tests
uv run pytest --cov=amp_stories --cov-fail-under=100  # with coverage
uv run ruff check src/ tests/                       # lint
uv run ruff check --fix src/ tests/                 # lint + auto-fix
uv run ty check src/                                # type check
```

## Architecture

```
src/amp_stories/
├── _html.py        # HtmlNode / RawHtmlNode — sole rendering primitives
├── _types.py       # Shared Literal type aliases
├── _validation.py  # ValidationError, AmpStoriesWarning, validators
├── animation.py    # Animation dataclass (animate-in attrs)
├── elements.py     # AmpImg, AmpVideo, AmpAudio, AmpList, TextElement, DivElement
├── layer.py        # Layer → <amp-story-grid-layer>
├── page.py         # Page → <amp-story-page>
├── outlink.py      # PageOutlink → <amp-story-page-outlink>
├── attachment.py   # PageAttachment → <amp-story-page-attachment> (deprecated)
├── bookend.py      # Bookend, BookendComponent, BookendShareProvider
└── story.py        # Story — root document, render(), save()
```

### Key design decisions

- **Constructor-based API** — no fluent chaining; children are passed into constructors.
- **Strict validation** — `ValidationError` raised in `__post_init__`, not deferred to `render()`.
- **`HtmlNode` as the single rendering primitive** — all `to_node()` methods return `HtmlNode | RawHtmlNode`. No string concatenation.
- **Auto AMP script detection** — `Story.render()` walks the page tree to determine which AMP extension `<script>` tags are needed. Do not inject scripts manually.
- **`from __future__ import annotations`** everywhere — enables forward references and TYPE_CHECKING blocks for circular-import-safe type hints.

### Validation conventions

- `ValidationError(ValueError)` — structural problems (missing required fields, invalid enum values, incompatible combinations).
- `AmpStoriesWarning(UserWarning)` — likely mistakes that produce valid but suboptimal HTML (e.g. no fill layer on a page). Issued via `warn()` in `_validation.py`.

### Adding new AMP components

1. Add a new element class in `elements.py` (or a new module for complex components).
2. Add the component's AMP extension to `_EXTENSION_SCRIPTS` in `story.py`.
3. Add detection logic in `Story._collect_required_scripts()`.
4. Export from `__init__.py`.
5. Add tests in `tests/`.

## Deferred features

- **Themes** — CSS theme system planned but not yet implemented.
- **amp-twitter, amp-consent** — out of scope for initial implementation.

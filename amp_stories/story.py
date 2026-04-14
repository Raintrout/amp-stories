"""AMP Story root document — assembles the full HTML page."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from amp_stories._html import HtmlNode, NodeChild, RawHtmlNode
from amp_stories._validation import (
    ValidationError,
    validate_nonempty,
    validate_poll_interval,
    warn_css_too_large,
    warn_landscape_no_poster,
    warn_outlink_not_last_page,
    warn_page_count_high,
    warn_page_count_low,
)

if TYPE_CHECKING:
    import os
    from typing import Any

    from amp_stories.page import Page

# ---------------------------------------------------------------------------
# AMP boilerplate CSS (required verbatim by the AMP spec)
# ---------------------------------------------------------------------------

_AMP_BOILERPLATE_CSS = (
    "body{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;"
    "-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;"
    "-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;"
    "animation:-amp-start 8s steps(1,end) 0s 1 normal both}"
    "@-webkit-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}"
    "@-moz-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}"
    "@-ms-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}"
    "@keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}"
)

_AMP_BOILERPLATE_NOSCRIPT_CSS = (
    "body{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}"
)

# ---------------------------------------------------------------------------
# AMP CDN base URL
# ---------------------------------------------------------------------------

_AMP_CDN = "https://cdn.ampproject.org"

# Extension script registry: component name → (version, custom-element|custom-template)
_EXTENSION_SCRIPTS: dict[str, tuple[str, str]] = {
    "amp-story": ("1.0", "custom-element"),
    "amp-story-bookend": ("0.1", "custom-element"),
    "amp-story-page-outlink": ("0.1", "custom-element"),
    "amp-story-page-attachment": ("0.1", "custom-element"),
    "amp-story-auto-ads": ("0.1", "custom-element"),
    "amp-story-interactive": ("0.1", "custom-element"),
    "amp-video": ("0.1", "custom-element"),
    "amp-audio": ("0.1", "custom-element"),
    "amp-list": ("0.1", "custom-element"),
    "amp-mustache": ("0.2", "custom-template"),
    "amp-story-panning-media": ("0.1", "custom-element"),
    "amp-story-360": ("0.1", "custom-element"),
    "amp-story-shopping": ("0.1", "custom-element"),
    "amp-consent": ("0.1", "custom-element"),
}


def _script_node(component: str) -> HtmlNode:
    version, attr_name = _EXTENSION_SCRIPTS[component]
    return HtmlNode(
        "script",
        {
            "async": True,
            attr_name: component,
            "src": f"{_AMP_CDN}/v0/{component}-{version}.js",
        },
        void=False,
    )


# ---------------------------------------------------------------------------
# Story
# ---------------------------------------------------------------------------

@dataclass
class Story:
    """The root AMP Story document.

    Calling :meth:`render` validates the complete story tree and returns
    a fully-formed HTML string ready to be served or written to disk.

    Required args:
        title: Story headline (shown in SERP previews).
        publisher: Publisher name (shown in the story UI).
        publisher_logo_src: URL to a square publisher logo (min 96×96 px).
        poster_portrait_src: URL to a 3:4 portrait poster image.
        canonical_url: The canonical URL of this story document.
        pages: At least one :class:`~amp_stories.page.Page`.

    Optional args:
        poster_square_src: 1:1 square poster image URL.
        poster_landscape_src: 4:3 landscape poster image URL.
        supports_landscape: Enable landscape viewing mode.
        background_audio: URL to audio that plays throughout the story.
        live_story: Enable live-story polling mode.
        live_story_disabled: Pause live-story polling (keeps the badge).
        data_poll_interval: Polling interval in ms (min 15 000).
        desktop_aspect_ratio: Aspect ratio for desktop layout (e.g. ``'16:9'``).
        lang: BCP-47 language tag for the HTML document. Defaults to ``'en'``.
        custom_css: CSS injected as ``<style amp-custom>`` (max 75 KB).
        bookend: A :class:`~amp_stories.bookend.Bookend` end-card.
        entity: Creator/platform name.
        entity_logo_src: Creator/platform logo URL.
        entity_url: Creator/platform URL.
    """

    title: str
    publisher: str
    publisher_logo_src: str
    poster_portrait_src: str
    canonical_url: str
    pages: list[Page]
    poster_square_src: str | None = None
    poster_landscape_src: str | None = None
    supports_landscape: bool = True
    background_audio: str | None = None
    live_story: bool = False
    live_story_disabled: bool = False
    data_poll_interval: int | None = None
    desktop_aspect_ratio: str | None = None
    lang: str = "en"
    custom_css: str | None = None
    font_links: list[str] = field(default_factory=list)
    bookend: object | None = None       # Bookend | None
    auto_ads: object | None = None      # AutoAds | None
    shopping: object | None = None      # StoryShopping | None
    consent: object | None = None       # AmpConsent | None
    structured_data: dict | None = None  # type: ignore[type-arg]
    entity: str | None = None
    entity_logo_src: str | None = None
    entity_url: str | None = None

    def __post_init__(self) -> None:
        validate_nonempty(self.title, "Story.title")
        validate_nonempty(self.publisher, "Story.publisher")
        validate_nonempty(self.publisher_logo_src, "Story.publisher_logo_src")
        validate_nonempty(self.poster_portrait_src, "Story.poster_portrait_src")
        validate_nonempty(self.canonical_url, "Story.canonical_url")
        if not self.pages:
            raise ValidationError("Story must have at least one Page.")
        if self.data_poll_interval is not None:
            validate_poll_interval(self.data_poll_interval, "Story.data_poll_interval")
        if self.live_story and self.data_poll_interval is None:
            raise ValidationError(
                "Story.data_poll_interval is required when live_story=True."
            )

    def __repr__(self) -> str:
        return f"Story(title={self.title!r}, pages={len(self.pages)})"

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """Run all cross-object validation checks without rendering.

        Raises :class:`~amp_stories._validation.ValidationError` if the story
        tree is invalid.  Issues :class:`~amp_stories._validation.AmpStoriesWarning`
        for best-practice violations.
        """
        self._validate_unique_page_ids()
        self._validate_page_count()
        if self.supports_landscape and self.poster_landscape_src is None:
            warn_landscape_no_poster()
        if self.custom_css is not None:
            size_bytes = len(self.custom_css.encode("utf-8"))
            if size_bytes > 75_000:
                warn_css_too_large(size_bytes / 1000)
        self._validate_outlink_positions()

    def add_page(self, *pages: Page) -> Story:
        """Append one or more pages and return *self* for chaining."""
        self.pages.extend(pages)
        return self

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _repr_html_(self) -> str:
        """Return a sandboxed iframe preview for Jupyter notebook display."""
        import html as _html  # noqa: PLC0415

        content = self.render()
        escaped = _html.escape(content, quote=True)
        return (
            f'<iframe srcdoc="{escaped}" '
            'width="360" height="640" '
            'style="border:none;display:block;" '
            'title="AMP Story preview">'
            "</iframe>"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize this story to a plain Python dict.

        The returned dict can be stored as JSON and later reconstructed
        with :meth:`from_dict`::

            import json
            data = story.to_dict()
            story2 = Story.from_dict(json.loads(json.dumps(data)))
        """
        from amp_stories._serde import _serialize  # noqa: PLC0415

        result = _serialize(self)
        return result  # type: ignore[return-value]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Story:
        """Reconstruct a :class:`Story` from a dict produced by :meth:`to_dict`.

        Args:
            data: A plain dict previously returned by :meth:`to_dict`.

        Raises:
            ValueError: If *data* does not represent a :class:`Story`.
        """
        type_tag = data.get("__type__")
        if type_tag != "Story":
            raise ValueError(
                f"Expected a Story dict (__type__='Story'), "
                f"got __type__={type_tag!r}"
            )
        from amp_stories._serde import _deserialize  # noqa: PLC0415

        return _deserialize(data)  # type: ignore[return-value]

    def generate_structured_data(self) -> dict[str, Any]:
        """Return a JSON-LD dict for a Web Story (schema.org/WebStory).

        Assign the result to :attr:`structured_data` to embed it in the
        rendered HTML ``<head>``::

            story.structured_data = story.generate_structured_data()
        """
        return {
            "@context": "https://schema.org",
            "@type": "WebStory",
            "headline": self.title,
            "url": self.canonical_url,
            "publisher": {
                "@type": "Organization",
                "name": self.publisher,
                "logo": {
                    "@type": "ImageObject",
                    "url": self.publisher_logo_src,
                },
            },
            "image": {
                "@type": "ImageObject",
                "url": self.poster_portrait_src,
            },
        }

    def render(self) -> str:
        """Validate, assemble, and return the full AMP HTML document string."""
        self.validate()

        required_scripts = self._collect_required_scripts()

        head = self._build_head(required_scripts)
        body = self._build_body()
        html_node = HtmlNode(
            "html",
            {"⚡": True, "lang": self.lang},
            children=[head, body],  # type: ignore[list-item]
        )
        return f"<!doctype html>\n{html_node.render()}"

    def save(self, path: str | os.PathLike[str]) -> None:
        """Render the story and write it to *path*."""
        content = self.render()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_outlink_positions(self) -> None:
        from amp_stories.outlink import PageOutlink  # noqa: PLC0415

        last_idx = len(self.pages) - 1
        for i, page in enumerate(self.pages):
            if isinstance(page.outlink, PageOutlink) and i < last_idx:
                warn_outlink_not_last_page(page.page_id)

    def _validate_unique_page_ids(self) -> None:
        seen: set[str] = set()
        for page in self.pages:
            if page.page_id in seen:
                raise ValidationError(
                    f"Duplicate page id: '{page.page_id}'. Each page must have a unique id."
                )
            seen.add(page.page_id)

    def _validate_page_count(self) -> None:
        count = len(self.pages)
        if count < 4:
            warn_page_count_low(count)
        elif count > 30:
            warn_page_count_high(count)

    def _collect_required_scripts(self) -> list[str]:
        """Walk the page tree and return the list of AMP extension names needed."""
        scripts: list[str] = ["amp-story"]

        from amp_stories.attachment import PageAttachment  # noqa: PLC0415
        from amp_stories.auto_ads import AutoAds  # noqa: PLC0415
        from amp_stories.bookend import Bookend  # noqa: PLC0415
        from amp_stories.consent import AmpConsent  # noqa: PLC0415
        from amp_stories.elements import (  # noqa: PLC0415
            AmpAudio,
            AmpList,
            AmpVideo,
            Story360,
            StoryPanningMedia,
        )
        from amp_stories.interactive import (  # noqa: PLC0415
            InteractiveBinaryPoll,
            InteractivePoll,
            InteractiveQuiz,
            InteractiveResults,
            InteractiveSlider,
        )
        from amp_stories.outlink import PageOutlink  # noqa: PLC0415
        from amp_stories.shopping import ShoppingAttachment, StoryShopping  # noqa: PLC0415

        _interactive_types = (
            InteractiveBinaryPoll,
            InteractivePoll,
            InteractiveQuiz,
            InteractiveSlider,
            InteractiveResults,
        )

        if self.bookend is not None and isinstance(self.bookend, Bookend):
            scripts.append("amp-story-bookend")

        if self.auto_ads is not None and isinstance(self.auto_ads, AutoAds):
            scripts.append("amp-story-auto-ads")

        if self.shopping is not None and isinstance(self.shopping, StoryShopping):
            scripts.append("amp-story-shopping")

        if self.consent is not None and isinstance(self.consent, AmpConsent):
            scripts.append("amp-consent")

        for page in self.pages:
            if isinstance(page.outlink, PageOutlink) and "amp-story-page-outlink" not in scripts:
                scripts.append("amp-story-page-outlink")
            if (
                isinstance(page.attachment, PageAttachment)
                and "amp-story-page-attachment" not in scripts
            ):
                scripts.append("amp-story-page-attachment")
            if (
                isinstance(page.shopping_attachment, ShoppingAttachment)
                and "amp-story-shopping" not in scripts
            ):
                scripts.append("amp-story-shopping")
            for layer in page.layers:
                for child in layer.children:
                    if isinstance(child, AmpVideo) and "amp-video" not in scripts:
                        scripts.append("amp-video")
                    if isinstance(child, AmpAudio) and "amp-audio" not in scripts:
                        scripts.append("amp-audio")
                    if isinstance(child, StoryPanningMedia) and (
                        "amp-story-panning-media" not in scripts
                    ):
                        scripts.append("amp-story-panning-media")
                    if isinstance(child, Story360) and "amp-story-360" not in scripts:
                        scripts.append("amp-story-360")
                    if isinstance(child, AmpList):
                        if "amp-list" not in scripts:
                            scripts.append("amp-list")
                        if "amp-mustache" not in scripts:
                            scripts.append("amp-mustache")
                    if (
                        isinstance(child, _interactive_types)
                        and "amp-story-interactive" not in scripts
                    ):
                        scripts.append("amp-story-interactive")

        return scripts

    def _build_head(self, required_scripts: list[str]) -> HtmlNode:
        children: list[NodeChild] = [
            HtmlNode("meta", {"charset": "utf-8"}, void=True),
            HtmlNode(
                "script",
                {"async": True, "src": f"{_AMP_CDN}/v0.js"},
            ),
            *[_script_node(s) for s in required_scripts],
            HtmlNode(
                "link",
                {"rel": "canonical", "href": self.canonical_url},
                void=True,
            ),
            *[
                HtmlNode("link", {"rel": "stylesheet", "href": url}, void=True)
                for url in self.font_links
            ],
            HtmlNode(
                "meta",
                {"name": "viewport", "content": "width=device-width"},
                void=True,
            ),
            HtmlNode(
                "style",
                {"amp-boilerplate": True},
                children=[RawHtmlNode(_AMP_BOILERPLATE_CSS)],
            ),
            HtmlNode(
                "noscript",
                {},
                children=[
                    HtmlNode(
                        "style",
                        {"amp-boilerplate": True},
                        children=[RawHtmlNode(_AMP_BOILERPLATE_NOSCRIPT_CSS)],
                    )
                ],
            ),
            HtmlNode("title", {}, children=[self.title]),
        ]

        if self.custom_css:
            children.append(
                HtmlNode(
                    "style",
                    {"amp-custom": True},
                    children=[RawHtmlNode(self.custom_css)],
                )
            )

        if self.structured_data is not None:
            import json as _json  # noqa: PLC0415
            children.append(
                HtmlNode(
                    "script",
                    {"type": "application/ld+json"},
                    children=[RawHtmlNode(_json.dumps(self.structured_data))],
                )
            )

        return HtmlNode("head", {}, children=children)

    def _build_body(self) -> HtmlNode:
        story_attrs: dict[str, str | bool | None] = {
            "standalone": True,
            "title": self.title,
            "publisher": self.publisher,
            "publisher-logo-src": self.publisher_logo_src,
            "poster-portrait-src": self.poster_portrait_src,
            "poster-square-src": self.poster_square_src,
            "poster-landscape-src": self.poster_landscape_src,
            "supports-landscape": True if self.supports_landscape else None,
            "background-audio": self.background_audio,
            "live-story": True if self.live_story else None,
            "live-story-disabled": True if self.live_story_disabled else None,
            "desktop-aspect-ratio": self.desktop_aspect_ratio,
            "entity": self.entity,
            "entity-logo-src": self.entity_logo_src,
            "entity-url": self.entity_url,
        }
        if self.data_poll_interval is not None:
            story_attrs["data-poll-interval"] = str(self.data_poll_interval)

        story_children: list[NodeChild] = []

        if self.consent is not None:
            from amp_stories.consent import AmpConsent  # noqa: PLC0415

            assert isinstance(self.consent, AmpConsent)
            story_children.append(self.consent.to_node())

        if self.auto_ads is not None:
            from amp_stories.auto_ads import AutoAds  # noqa: PLC0415

            assert isinstance(self.auto_ads, AutoAds)
            story_children.append(self.auto_ads.to_node())

        if self.shopping is not None:
            from amp_stories.shopping import StoryShopping  # noqa: PLC0415

            assert isinstance(self.shopping, StoryShopping)
            story_children.append(self.shopping.to_node())

        story_children.extend(page.to_node() for page in self.pages)

        if self.bookend is not None:
            from amp_stories.bookend import Bookend  # noqa: PLC0415

            assert isinstance(self.bookend, Bookend)
            story_children.append(self.bookend.to_node())

        story_node = HtmlNode("amp-story", story_attrs, children=story_children)
        return HtmlNode("body", {}, children=[story_node])

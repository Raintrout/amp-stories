"""AMP Story root document — assembles the full HTML page."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from amp_stories._html import HtmlNode, RawHtmlNode
from amp_stories._validation import ValidationError, validate_nonempty, validate_poll_interval

if TYPE_CHECKING:
    import os

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
    "amp-video": ("0.1", "custom-element"),
    "amp-audio": ("0.1", "custom-element"),
    "amp-list": ("0.1", "custom-element"),
    "amp-mustache": ("0.2", "custom-template"),
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
    supports_landscape: bool = False
    background_audio: str | None = None
    live_story: bool = False
    live_story_disabled: bool = False
    data_poll_interval: int | None = None
    desktop_aspect_ratio: str | None = None
    lang: str = "en"
    custom_css: str | None = None
    bookend: object | None = None   # Bookend | None
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

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> str:
        """Validate, assemble, and return the full AMP HTML document string."""
        self._validate_unique_page_ids()

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

    def _validate_unique_page_ids(self) -> None:
        seen: set[str] = set()
        for page in self.pages:
            if page.page_id in seen:
                raise ValidationError(
                    f"Duplicate page id: '{page.page_id}'. Each page must have a unique id."
                )
            seen.add(page.page_id)

    def _collect_required_scripts(self) -> list[str]:
        """Walk the page tree and return the list of AMP extension names needed."""
        scripts: list[str] = ["amp-story"]

        from amp_stories.attachment import PageAttachment  # noqa: PLC0415
        from amp_stories.bookend import Bookend  # noqa: PLC0415
        from amp_stories.elements import AmpAudio, AmpList, AmpVideo  # noqa: PLC0415
        from amp_stories.outlink import PageOutlink  # noqa: PLC0415

        if self.bookend is not None and isinstance(self.bookend, Bookend):
            scripts.append("amp-story-bookend")

        for page in self.pages:
            if isinstance(page.outlink, PageOutlink) and "amp-story-page-outlink" not in scripts:
                scripts.append("amp-story-page-outlink")
            if (
                isinstance(page.attachment, PageAttachment)
                and "amp-story-page-attachment" not in scripts
            ):
                scripts.append("amp-story-page-attachment")
            for layer in page.layers:
                for child in layer.children:
                    if isinstance(child, AmpVideo) and "amp-video" not in scripts:
                        scripts.append("amp-video")
                    if isinstance(child, AmpAudio) and "amp-audio" not in scripts:
                        scripts.append("amp-audio")
                    if isinstance(child, AmpList):
                        if "amp-list" not in scripts:
                            scripts.append("amp-list")
                        if "amp-mustache" not in scripts:
                            scripts.append("amp-mustache")

        return scripts

    def _build_head(self, required_scripts: list[str]) -> HtmlNode:
        children: list[HtmlNode | RawHtmlNode] = [
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

        return HtmlNode("head", {}, children=children)  # type: ignore[arg-type]

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

        story_children: list[HtmlNode] = [page.to_node() for page in self.pages]

        if self.bookend is not None:
            from amp_stories.bookend import Bookend  # noqa: PLC0415

            assert isinstance(self.bookend, Bookend)
            story_children.append(self.bookend.to_node())

        story_node = HtmlNode("amp-story", story_attrs, children=story_children)  # type: ignore[arg-type]
        return HtmlNode("body", {}, children=[story_node])  # type: ignore[arg-type]

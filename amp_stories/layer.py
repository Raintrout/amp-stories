"""amp-story-grid-layer wrapper."""

from __future__ import annotations

from dataclasses import dataclass, field

from amp_stories._html import HtmlNode, NodeChild
from amp_stories._types import Anchor, LayerPreset, LayerTemplate
from amp_stories._validation import validate_aspect_ratio, validate_literal
from amp_stories.elements import AmpAudio, AmpImg, AmpList, AmpVideo, DivElement, TextElement
from amp_stories.interactive import (
    InteractiveBinaryPoll,
    InteractivePoll,
    InteractiveQuiz,
    InteractiveResults,
    InteractiveSlider,
)

# Union of all valid layer child element types
LayerChild = (
    AmpImg
    | AmpVideo
    | AmpAudio
    | TextElement
    | DivElement
    | AmpList
    | InteractiveBinaryPoll
    | InteractivePoll
    | InteractiveQuiz
    | InteractiveSlider
    | InteractiveResults
    | str
)


@dataclass
class Layer:
    """An ``<amp-story-grid-layer>`` element.

    Args:
        template: Grid layout type — one of ``'fill'``, ``'vertical'``,
            ``'horizontal'``, or ``'thirds'``.
        children: Content elements rendered inside the layer.
        grid_area: Named grid area for positioning (used with ``'thirds'``).
        aspect_ratio: Layer aspect ratio in ``'W:H'`` format (e.g. ``'4:3'``).
        preset: Responsive layout preset — ``'2021-background'`` or
            ``'2021-foreground'``.
        anchor: Anchor point for aspect-ratio layers.
    """

    template: LayerTemplate
    children: list[LayerChild] = field(default_factory=list)
    grid_area: str | None = None
    aspect_ratio: str | None = None
    preset: LayerPreset | None = None
    anchor: Anchor | None = None

    def __post_init__(self) -> None:
        validate_literal(self.template, "Layer.template", LayerTemplate)
        if self.aspect_ratio is not None:
            validate_aspect_ratio(self.aspect_ratio, "Layer.aspect_ratio")
        if self.preset is not None:
            validate_literal(self.preset, "Layer.preset", LayerPreset)
        if self.anchor is not None:
            validate_literal(self.anchor, "Layer.anchor", Anchor)

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "template": self.template,
            "grid-area": self.grid_area,
            "aspect-ratio": self.aspect_ratio,
            "preset": self.preset,
            "anchor": self.anchor,
        }
        child_nodes: list[NodeChild] = []
        for child in self.children:
            if isinstance(child, str):
                child_nodes.append(child)
            else:
                child_nodes.append(child.to_node())
        return HtmlNode("amp-story-grid-layer", attrs, children=child_nodes)


# ---------------------------------------------------------------------------
# Convenience layer factories
# ---------------------------------------------------------------------------

def background_layer(media: AmpImg | AmpVideo) -> Layer:
    """Shorthand for ``Layer('fill', children=[media])``."""
    return Layer("fill", children=[media])


def text_layer(*elements: LayerChild) -> Layer:
    """Shorthand for ``Layer('vertical', children=list(elements))``."""
    return Layer("vertical", children=list(elements))

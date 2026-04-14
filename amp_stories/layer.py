"""amp-story-grid-layer wrapper."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from amp_stories._html import HtmlNode, NodeChild
from amp_stories._types import Anchor, LayerPreset, LayerTemplate
from amp_stories._validation import (
    validate_aspect_ratio,
    validate_literal,
    warn_fill_layer_multiple_children,
)
from amp_stories.elements import (
    AmpAudio,
    AmpImg,
    AmpList,
    AmpVideo,
    DivElement,
    Story360,
    StoryPanningMedia,
    TextElement,
)
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
    | StoryPanningMedia
    | Story360
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
    position: Literal["absolute"] | None = None

    def __post_init__(self) -> None:
        validate_literal(self.template, "Layer.template", LayerTemplate)
        if self.aspect_ratio is not None:
            validate_aspect_ratio(self.aspect_ratio, "Layer.aspect_ratio")
        if self.preset is not None:
            validate_literal(self.preset, "Layer.preset", LayerPreset)
        if self.anchor is not None:
            validate_literal(self.anchor, "Layer.anchor", Anchor)
        if self.position is not None:
            validate_literal(self.position, "Layer.position", Literal["absolute"])
        if self.template == "fill" and len(self.children) > 1:
            warn_fill_layer_multiple_children(len(self.children))

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "template": self.template,
            "grid-area": self.grid_area,
            "aspect-ratio": self.aspect_ratio,
            "preset": self.preset,
            "anchor": self.anchor,
            "position": self.position,
        }
        child_nodes: list[NodeChild] = []
        for child in self.children:
            if isinstance(child, str):
                child_nodes.append(child)
            else:
                child_nodes.append(child.to_node())
        return HtmlNode("amp-story-grid-layer", attrs, children=child_nodes)

    def add_child(self, *children: LayerChild) -> Layer:
        """Append one or more children and return *self* for chaining."""
        self.children.extend(children)
        return self

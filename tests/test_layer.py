"""Tests for layer.py."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.elements import AmpImg, AmpVideo, heading, paragraph
from amp_stories.layer import Layer, background_layer, text_layer


class TestLayer:
    def test_valid_fill_template(self) -> None:
        layer = Layer("fill")
        assert layer.to_node().attrs["template"] == "fill"

    def test_valid_vertical_template(self) -> None:
        assert Layer("vertical").to_node().attrs["template"] == "vertical"

    def test_valid_horizontal_template(self) -> None:
        assert Layer("horizontal").to_node().attrs["template"] == "horizontal"

    def test_valid_thirds_template(self) -> None:
        assert Layer("thirds").to_node().attrs["template"] == "thirds"

    def test_invalid_template_raises(self) -> None:
        with pytest.raises(ValidationError, match="template"):
            Layer("full-screen")  # type: ignore[arg-type]

    def test_renders_amp_story_grid_layer_tag(self) -> None:
        layer = Layer("fill")
        assert layer.to_node().tag == "amp-story-grid-layer"

    def test_children_rendered(self) -> None:
        img = AmpImg("img.jpg", alt="")
        layer = Layer("fill", children=[img])
        node = layer.to_node()
        assert len(node.children) == 1
        assert node.children[0].tag == "amp-img"  # type: ignore[union-attr]

    def test_multiple_children(self) -> None:
        layer = Layer("vertical", children=[
            heading("Title"),
            paragraph("Body"),
        ])
        node = layer.to_node()
        assert len(node.children) == 2

    def test_grid_area_attr(self) -> None:
        layer = Layer("thirds", grid_area="upper-third")
        assert layer.to_node().attrs["grid-area"] == "upper-third"

    def test_aspect_ratio_attr(self) -> None:
        layer = Layer("fill", aspect_ratio="4:3")
        assert layer.to_node().attrs["aspect-ratio"] == "4:3"

    def test_invalid_aspect_ratio_raises(self) -> None:
        with pytest.raises(ValidationError, match="aspect_ratio"):
            Layer("fill", aspect_ratio="widescreen")

    def test_preset_attr(self) -> None:
        layer = Layer("fill", preset="2021-background")
        assert layer.to_node().attrs["preset"] == "2021-background"

    def test_invalid_preset_raises(self) -> None:
        with pytest.raises(ValidationError, match="preset"):
            Layer("fill", preset="old-style")  # type: ignore[arg-type]

    def test_anchor_attr(self) -> None:
        layer = Layer("fill", anchor="top-left")
        assert layer.to_node().attrs["anchor"] == "top-left"

    def test_invalid_anchor_raises(self) -> None:
        with pytest.raises(ValidationError, match="anchor"):
            Layer("fill", anchor="center")  # type: ignore[arg-type]

    def test_optional_attrs_none_when_not_set(self) -> None:
        layer = Layer("vertical")
        node = layer.to_node()
        assert node.attrs.get("grid-area") is None
        assert node.attrs.get("aspect-ratio") is None
        assert node.attrs.get("preset") is None
        assert node.attrs.get("anchor") is None

    def test_string_child_passthrough(self) -> None:
        layer = Layer("vertical", children=["raw text"])
        node = layer.to_node()
        assert node.children[0] == "raw text"


class TestLayerHelpers:
    def test_background_layer_is_fill(self) -> None:
        img = AmpImg("bg.jpg", alt="background")
        layer = background_layer(img)
        assert layer.template == "fill"
        assert layer.children == [img]

    def test_background_layer_with_video(self) -> None:
        video = AmpVideo("bg.mp4")
        layer = background_layer(video)
        assert layer.template == "fill"
        assert layer.children == [video]

    def test_text_layer_is_vertical(self) -> None:
        h = heading("Title")
        p = paragraph("Body")
        layer = text_layer(h, p)
        assert layer.template == "vertical"
        assert layer.children == [h, p]

    def test_text_layer_no_args(self) -> None:
        layer = text_layer()
        assert layer.template == "vertical"
        assert layer.children == []

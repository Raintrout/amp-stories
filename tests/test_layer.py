"""Tests for layer.py."""

from __future__ import annotations

import pytest

from amp_stories._validation import AmpStoriesWarning, ValidationError
from amp_stories.elements import AmpImg
from amp_stories.helpers import heading, paragraph
from amp_stories.layer import Layer


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

    def test_fill_layer_multiple_children_warns(self) -> None:
        img1 = AmpImg("img1.jpg", alt="")
        img2 = AmpImg("img2.jpg", alt="")
        with pytest.warns(AmpStoriesWarning, match="fill"):
            Layer("fill", children=[img1, img2])

    def test_fill_layer_single_child_no_warning(self) -> None:
        import warnings
        img = AmpImg("img.jpg", alt="")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            Layer("fill", children=[img])  # must not raise


class TestLayerStyle:
    def test_style_attr_set(self) -> None:
        layer = Layer("fill", style="top:10%;left:5%")
        assert layer.to_node().attrs["style"] == "top:10%;left:5%"

    def test_style_absent_when_none(self) -> None:
        layer = Layer("fill")
        assert layer.to_node().attrs.get("style") is None


class TestLayerPosition:
    def test_default_position_is_none(self) -> None:
        layer = Layer("fill")
        assert layer.position is None

    def test_absolute_position_accepted(self) -> None:
        layer = Layer("fill", position="absolute")
        assert layer.position == "absolute"

    def test_invalid_position_raises(self) -> None:
        with pytest.raises(ValidationError, match="position"):
            Layer("fill", position="relative")  # type: ignore[arg-type]

    def test_position_in_node_attrs_when_set(self) -> None:
        layer = Layer("fill", position="absolute")
        assert layer.to_node().attrs["position"] == "absolute"

    def test_position_absent_from_node_when_none(self) -> None:
        layer = Layer("fill")
        assert layer.to_node().attrs.get("position") is None


class TestLayerAddChild:
    def test_add_child_returns_self(self) -> None:
        layer = Layer("vertical")
        img = AmpImg("img.jpg", alt="")
        result = layer.add_child(img)
        assert result is layer
        assert img in layer.children

    def test_add_child_appends(self) -> None:
        img = AmpImg("img.jpg", alt="")
        layer = Layer("vertical", children=[img])
        h = heading("Title")
        layer.add_child(h)
        assert layer.children == [img, h]

    def test_add_child_multiple_at_once(self) -> None:
        layer = Layer("vertical")
        h = heading("Title")
        p = paragraph("Body")
        layer.add_child(h, p)
        assert len(layer.children) == 2
        assert layer.children[0] is h
        assert layer.children[1] is p



"""Tests for outlink.py."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.outlink import PageOutlink


class TestPageOutlink:
    def test_basic_outlink(self) -> None:
        ol = PageOutlink(href="https://example.com")
        node = ol.to_node()
        assert node.tag == "amp-story-page-outlink"

    def test_nodisplay_layout(self) -> None:
        ol = PageOutlink(href="https://example.com")
        assert ol.to_node().attrs["layout"] == "nodisplay"

    def test_href_in_anchor_child(self) -> None:
        ol = PageOutlink(href="https://example.com/article")
        node = ol.to_node()
        anchor = node.children[0]
        assert anchor.tag == "a"  # type: ignore[union-attr]
        assert anchor.attrs["href"] == "https://example.com/article"  # type: ignore[union-attr]

    def test_default_cta_text(self) -> None:
        ol = PageOutlink(href="https://example.com")
        anchor = ol.to_node().children[0]
        assert anchor.children[0] == "Swipe up"  # type: ignore[index]

    def test_custom_cta_text(self) -> None:
        ol = PageOutlink(href="https://example.com", cta_text="Learn More")
        anchor = ol.to_node().children[0]
        assert anchor.children[0] == "Learn More"  # type: ignore[index]

    def test_light_theme_default(self) -> None:
        ol = PageOutlink(href="https://example.com")
        assert ol.to_node().attrs["theme"] == "light"

    def test_dark_theme(self) -> None:
        ol = PageOutlink(href="https://example.com", theme="dark")
        assert ol.to_node().attrs["theme"] == "dark"

    def test_custom_theme_with_accent_color(self) -> None:
        ol = PageOutlink(
            href="https://example.com",
            theme="custom",
            cta_accent_color="#FF0000",
            cta_accent_element="text",
        )
        node = ol.to_node()
        assert node.attrs["cta-accent-color"] == "#FF0000"

    def test_custom_theme_without_accent_color_raises(self) -> None:
        with pytest.raises(ValidationError, match="cta_accent_color"):
            PageOutlink(href="https://example.com", theme="custom")

    def test_custom_theme_without_accent_element_raises(self) -> None:
        with pytest.raises(ValidationError, match="cta_accent_element"):
            PageOutlink(
                href="https://example.com",
                theme="custom",
                cta_accent_color="#FF0000",
            )

    def test_invalid_theme_raises(self) -> None:
        with pytest.raises(ValidationError, match="theme"):
            PageOutlink(href="https://example.com", theme="neon")  # type: ignore[arg-type]

    def test_cta_accent_element_attr(self) -> None:
        ol = PageOutlink(
            href="https://example.com",
            theme="custom",
            cta_accent_color="#00FF00",
            cta_accent_element="background",
        )
        assert ol.to_node().attrs["cta-accent-element"] == "background"

    def test_invalid_cta_accent_element_raises(self) -> None:
        with pytest.raises(ValidationError, match="cta_accent_element"):
            PageOutlink(
                href="https://example.com",
                theme="custom",
                cta_accent_color="#FF0000",
                cta_accent_element="border",  # type: ignore[arg-type]
            )

    def test_cta_image_attr(self) -> None:
        ol = PageOutlink(href="https://example.com", cta_image="icon.png")
        assert ol.to_node().attrs["cta-image"] == "icon.png"

    def test_cta_image_none_value(self) -> None:
        ol = PageOutlink(href="https://example.com", cta_image="none")
        assert ol.to_node().attrs["cta-image"] == "none"

    def test_empty_href_raises(self) -> None:
        with pytest.raises(ValidationError, match="href"):
            PageOutlink(href="")

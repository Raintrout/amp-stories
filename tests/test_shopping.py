"""Tests for shopping.py."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.shopping import ShoppingTag, StoryShopping


def _tag(**kwargs: object) -> ShoppingTag:
    defaults: dict[str, object] = {
        "product_id": "p1",
        "product_title": "Widget",
        "product_brand": "Acme",
        "product_price": 9.99,
        "product_price_currency": "USD",
        "product_images": ["https://example.com/img.jpg"],
    }
    defaults.update(kwargs)
    return ShoppingTag(**defaults)  # type: ignore[arg-type]


class TestShoppingTag:
    def test_renders_shopping_tag(self) -> None:
        tag = _tag()
        assert tag.to_node().tag == "amp-story-shopping-tag"

    def test_product_attrs(self) -> None:
        tag = _tag(
            product_id="abc",
            product_title="Cool Widget",
            product_brand="Acme Corp",
            product_price=19.99,
            product_price_currency="EUR",
            product_images=["https://example.com/img.jpg"],
        )
        node = tag.to_node()
        assert node.attrs["data-product-id"] == "abc"
        assert node.attrs["data-product-title"] == "Cool Widget"
        assert node.attrs["data-product-brand"] == "Acme Corp"
        assert node.attrs["data-product-price"] == "19.99"
        assert node.attrs["data-product-price-currency"] == "EUR"
        assert node.attrs["data-product-images"] == "https://example.com/img.jpg"

    def test_multiple_product_images_joined(self) -> None:
        tag = _tag(product_images=["img1.jpg", "img2.jpg", "img3.jpg"])
        node = tag.to_node()
        assert node.attrs["data-product-images"] == "img1.jpg,img2.jpg,img3.jpg"

    def test_empty_product_id_raises(self) -> None:
        with pytest.raises(ValidationError, match="product_id"):
            _tag(product_id="")

    def test_empty_product_title_raises(self) -> None:
        with pytest.raises(ValidationError, match="product_title"):
            _tag(product_title="")

    def test_empty_product_brand_raises(self) -> None:
        with pytest.raises(ValidationError, match="product_brand"):
            _tag(product_brand="")

    def test_empty_currency_raises(self) -> None:
        with pytest.raises(ValidationError, match="product_price_currency"):
            _tag(product_price_currency="")

    def test_empty_product_images_raises(self) -> None:
        with pytest.raises(ValidationError, match="product_images"):
            _tag(product_images=[])

    def test_integer_price_rendered_as_string(self) -> None:
        tag = _tag(product_price=10)
        assert tag.to_node().attrs["data-product-price"] == "10"


class TestStoryShopping:
    def test_renders_amp_story_shopping(self) -> None:
        shopping = StoryShopping(tags=[_tag()])
        assert shopping.to_node().tag == "amp-story-shopping"

    def test_tags_rendered_as_children(self) -> None:
        shopping = StoryShopping(tags=[_tag(product_id="p1"), _tag(product_id="p2")])
        node = shopping.to_node()
        assert len(node.children) == 2
        assert node.children[0].tag == "amp-story-shopping-tag"  # type: ignore[union-attr]
        assert node.children[1].tag == "amp-story-shopping-tag"  # type: ignore[union-attr]

    def test_empty_tags_raises(self) -> None:
        with pytest.raises(ValidationError, match="tags"):
            StoryShopping(tags=[])

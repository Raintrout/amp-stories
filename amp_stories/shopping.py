"""AMP Story Shopping components."""

from __future__ import annotations

from dataclasses import dataclass, field

from amp_stories._html import HtmlNode, NodeChild
from amp_stories._validation import ValidationError, validate_nonempty


@dataclass
class ShoppingTag:
    """An ``<amp-story-shopping-tag>`` element for product tagging.

    Args:
        product_id: Unique identifier for the product.
        product_title: Display name of the product.
        product_brand: Brand name.
        product_price: Price as a float.
        product_price_currency: ISO 4217 currency code (e.g. ``'USD'``).
        product_images: List of product image URLs (at least one required).
    """

    product_id: str
    product_title: str
    product_brand: str
    product_price: float
    product_price_currency: str
    product_images: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        validate_nonempty(self.product_id, "ShoppingTag.product_id")
        validate_nonempty(self.product_title, "ShoppingTag.product_title")
        validate_nonempty(self.product_brand, "ShoppingTag.product_brand")
        validate_nonempty(self.product_price_currency, "ShoppingTag.product_price_currency")
        if not self.product_images:
            raise ValidationError("ShoppingTag.product_images must not be empty.")

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "data-product-id": self.product_id,
            "data-product-title": self.product_title,
            "data-product-brand": self.product_brand,
            "data-product-price": str(self.product_price),
            "data-product-price-currency": self.product_price_currency,
            "data-product-images": ",".join(self.product_images),
        }
        return HtmlNode("amp-story-shopping-tag", attrs)


@dataclass
class StoryShopping:
    """An ``<amp-story-shopping>`` element wrapping one or more product tags.

    Args:
        tags: One or more :class:`ShoppingTag` objects (required).
    """

    tags: list[ShoppingTag] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.tags:
            raise ValidationError("StoryShopping.tags must not be empty.")

    def to_node(self) -> HtmlNode:
        children: list[NodeChild] = [tag.to_node() for tag in self.tags]
        return HtmlNode("amp-story-shopping", {}, children=children)

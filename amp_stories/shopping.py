"""AMP Story Shopping components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

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
        product_url: URL of the product page (shown in the shopping panel).
        product_rating: Aggregate star rating (0–5).
        product_rating_count: Number of reviews behind the rating.
        product_details: Short description shown in the shopping panel.
        product_icon: URL to a small product icon shown on the tag.
        product_tag_text: Custom label for the shopping tag button.
    """

    product_id: str
    product_title: str
    product_brand: str
    product_price: float
    product_price_currency: str
    product_images: list[str] = field(default_factory=list)
    product_url: str | None = None
    product_rating: float | None = None
    product_rating_count: int | None = None
    product_details: str | None = None
    product_icon: str | None = None
    product_tag_text: str | None = None

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
            "data-product-url": self.product_url,
            "data-product-rating": (
                str(self.product_rating) if self.product_rating is not None else None
            ),
            "data-product-rating-count": (
                str(self.product_rating_count) if self.product_rating_count is not None else None
            ),
            "data-product-details": self.product_details,
            "data-product-icon": self.product_icon,
            "data-product-tag-text": self.product_tag_text,
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


@dataclass
class ShoppingAttachment:
    """An ``<amp-story-shopping-attachment>`` element that opens the shopping panel.

    Place on a :class:`~amp_stories.page.Page` via ``shopping_attachment=`` to
    enable the product drawer on that page.  The panel is populated from the
    :class:`ShoppingTag` elements on the same page (placed inside a layer).

    Args:
        theme: Visual theme for the shopping panel — ``'dark'`` or ``'light'``.
        cta_text: Custom call-to-action label on the drawer handle.
    """

    theme: Literal["dark", "light"] | None = None
    cta_text: str | None = None

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "theme": self.theme,
            "cta-text": self.cta_text,
        }
        return HtmlNode("amp-story-shopping-attachment", attrs)

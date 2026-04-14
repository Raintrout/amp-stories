"""HTML rendering primitives.

HtmlNode and RawHtmlNode are the only rendering abstractions in the library.
All component .to_node() methods return one of these two types.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import Union

# Forward-reference-safe type alias for node children
NodeChild = Union["HtmlNode", "RawHtmlNode", str]


@dataclass
class HtmlNode:
    """An HTML element that renders itself to a string.

    Attribute rules:
    - str value  → rendered as key="escaped-value"
    - True       → rendered as bare attribute name (e.g. standalone, async)
    - None       → attribute is omitted entirely (useful for conditionals)
    """

    tag: str
    attrs: dict[str, str | bool | None] = field(default_factory=dict)
    children: list[NodeChild] = field(default_factory=list)
    void: bool = False  # True for <meta>, <link>, <br>, etc.

    def render(self, indent: int = 0) -> str:
        pad = " " * indent
        attr_str = _render_attrs(self.attrs)
        open_tag = f"<{self.tag}{attr_str}>"

        if self.void:
            return f"{pad}{open_tag}"

        if not self.children:
            return f"{pad}{open_tag}</{self.tag}>"

        # Single text child with no nested nodes → inline
        if len(self.children) == 1 and isinstance(self.children[0], str):
            text = html.escape(self.children[0])
            return f"{pad}{open_tag}{text}</{self.tag}>"

        inner_lines: list[str] = []
        for child in self.children:
            if isinstance(child, str):
                inner_lines.append(" " * (indent + 2) + html.escape(child))
            else:
                inner_lines.append(child.render(indent + 2))

        inner = "\n".join(inner_lines)
        return f"{pad}{open_tag}\n{inner}\n{pad}</{self.tag}>"

    def __str__(self) -> str:
        return self.render()


@dataclass
class RawHtmlNode:
    """Renders content verbatim — no escaping.

    Use for AMP boilerplate CSS blocks, JSON script contents, and
    any other pre-formatted content that must not be escaped.
    """

    content: str

    def render(self, indent: int = 0) -> str:
        return self.content

    def __str__(self) -> str:
        return self.render()


def _render_attrs(attrs: dict[str, str | bool | None]) -> str:
    """Render an attribute dict to a string suitable for inclusion in a tag."""
    parts: list[str] = []
    for key, value in attrs.items():
        if value is None:
            continue
        if value is True:
            parts.append(f" {key}")
        else:
            escaped = html.escape(str(value), quote=True)
            parts.append(f' {key}="{escaped}"')
    return "".join(parts)

"""Tests for _html.py — the core rendering primitive."""

from __future__ import annotations

from amp_stories._html import HtmlNode, RawHtmlNode, _render_attrs


class TestRenderAttrs:
    def test_string_attr(self) -> None:
        assert _render_attrs({"class": "foo"}) == ' class="foo"'

    def test_bool_true_attr(self) -> None:
        assert _render_attrs({"standalone": True}) == " standalone"

    def test_none_attr_omitted(self) -> None:
        assert _render_attrs({"src": None}) == ""

    def test_attr_value_escaped(self) -> None:
        result = _render_attrs({"title": '<script>alert("xss")</script>'})
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_quote_in_value_escaped(self) -> None:
        result = _render_attrs({"data": 'say "hello"'})
        assert '"hello"' not in result
        assert "&quot;hello&quot;" in result

    def test_multiple_attrs_order_preserved(self) -> None:
        attrs = {"a": "1", "b": True, "c": None, "d": "4"}
        result = _render_attrs(attrs)
        assert result == ' a="1" b d="4"'


class TestHtmlNode:
    def test_simple_element(self) -> None:
        node = HtmlNode("p", {}, children=["Hello"])
        assert node.render() == "<p>Hello</p>"

    def test_text_child_escaped(self) -> None:
        node = HtmlNode("p", {}, children=["<b>bold</b>"])
        assert "&lt;b&gt;" in node.render()
        assert "<b>" not in node.render()

    def test_void_element_no_closing_tag(self) -> None:
        node = HtmlNode("meta", {"charset": "utf-8"}, void=True)
        rendered = node.render()
        assert rendered == '<meta charset="utf-8">'
        assert "</meta>" not in rendered

    def test_empty_element_inline(self) -> None:
        node = HtmlNode("div", {})
        assert node.render() == "<div></div>"

    def test_boolean_attribute(self) -> None:
        node = HtmlNode("amp-story", {"standalone": True})
        assert "standalone" in node.render()
        assert 'standalone="' not in node.render()

    def test_none_attribute_omitted(self) -> None:
        node = HtmlNode("amp-img", {"src": "img.jpg", "poster": None})
        rendered = node.render()
        assert "poster" not in rendered
        assert "src" in rendered

    def test_nested_children_indented(self) -> None:
        inner = HtmlNode("span", {}, children=["text"])
        outer = HtmlNode("div", {}, children=[inner])
        rendered = outer.render()
        assert "<div>" in rendered
        assert "  <span>text</span>" in rendered
        assert "</div>" in rendered

    def test_deeply_nested_indentation(self) -> None:
        deep = HtmlNode("b", {}, children=["deep"])
        mid = HtmlNode("p", {}, children=[deep])
        outer = HtmlNode("div", {}, children=[mid])
        rendered = outer.render(indent=0)
        lines = rendered.splitlines()
        assert lines[0] == "<div>"
        assert lines[1].startswith("  <p>")
        assert lines[2].startswith("    <b>deep</b>")
        assert lines[3].startswith("  </p>")
        assert lines[4] == "</div>"

    def test_str_dunder(self) -> None:
        node = HtmlNode("p", {}, children=["hi"])
        assert str(node) == node.render()

    def test_unicode_attribute_key(self) -> None:
        # ⚡ is used on <html ⚡>
        node = HtmlNode("html", {"⚡": True})
        assert "⚡" in node.render()

    def test_mixed_string_and_node_children(self) -> None:
        # Exercises line 51: str child in a multi-child context with node siblings
        inner = HtmlNode("b", {}, children=["bold"])
        outer = HtmlNode("p", {}, children=["prefix ", inner])
        rendered = outer.render()
        assert "prefix " in rendered
        assert "<b>bold</b>" in rendered

    def test_amp_story_structure(self) -> None:
        node = HtmlNode(
            "amp-story",
            {"standalone": True, "title": "Test"},
            children=[HtmlNode("amp-story-page", {"id": "p1"})],
        )
        rendered = node.render()
        assert "amp-story" in rendered
        assert "standalone" in rendered
        assert 'title="Test"' in rendered
        assert "amp-story-page" in rendered


class TestRawHtmlNode:
    def test_raw_content_not_escaped(self) -> None:
        raw = RawHtmlNode("<b>not escaped</b>")
        assert raw.render() == "<b>not escaped</b>"

    def test_raw_in_style_tag(self) -> None:
        css = "body{color:red}"
        style = HtmlNode("style", {"amp-boilerplate": True}, children=[RawHtmlNode(css)])
        rendered = style.render()
        assert css in rendered
        assert "&lt;" not in rendered

    def test_str_dunder(self) -> None:
        raw = RawHtmlNode("content")
        assert str(raw) == "content"

    def test_raw_in_script_tag(self) -> None:
        json_str = '{"bookendVersion": "v1.0"}'
        script = HtmlNode(
            "script",
            {"type": "application/json"},
            children=[RawHtmlNode(json_str)],
        )
        rendered = script.render()
        assert json_str in rendered
        assert "&quot;" not in rendered

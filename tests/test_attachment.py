"""Tests for attachment.py."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.attachment import AttachmentLink, PageAttachment
from amp_stories.helpers import heading, paragraph


class TestAttachmentLink:
    def test_valid_link(self) -> None:
        link = AttachmentLink("Read More", "https://example.com")
        assert link.title == "Read More"
        assert link.url == "https://example.com"

    def test_optional_image(self) -> None:
        link = AttachmentLink("Read", "https://example.com", image="thumb.jpg")
        assert link.image == "thumb.jpg"

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValidationError, match="title"):
            AttachmentLink("", "https://example.com")

    def test_empty_url_raises(self) -> None:
        with pytest.raises(ValidationError, match="url"):
            AttachmentLink("Read", "")


class TestPageAttachment:
    def test_default_attrs(self) -> None:
        att = PageAttachment()
        node = att.to_node()
        assert node.tag == "amp-story-page-attachment"
        assert node.attrs["layout"] == "nodisplay"
        assert node.attrs["theme"] == "light"
        assert node.attrs["cta-text"] == "Swipe up"

    def test_dark_theme(self) -> None:
        att = PageAttachment(theme="dark")
        assert att.to_node().attrs["theme"] == "dark"

    def test_invalid_theme_raises(self) -> None:
        with pytest.raises(ValidationError, match="theme"):
            PageAttachment(theme="custom")  # type: ignore[arg-type]

    def test_link_list_mode(self) -> None:
        att = PageAttachment(links=[
            AttachmentLink("Article 1", "https://example.com/1"),
            AttachmentLink("Article 2", "https://example.com/2"),
        ])
        node = att.to_node()
        anchors = [c for c in node.children if c.tag == "a"]  # type: ignore[union-attr]
        assert len(anchors) == 2
        assert anchors[0].attrs["href"] == "https://example.com/1"  # type: ignore[union-attr]
        assert anchors[1].attrs["href"] == "https://example.com/2"  # type: ignore[union-attr]

    def test_link_with_image_gets_data_img(self) -> None:
        att = PageAttachment(links=[
            AttachmentLink("Art", "https://example.com", image="thumb.jpg")
        ])
        node = att.to_node()
        anchor = node.children[0]
        assert anchor.attrs.get("data-img") == "thumb.jpg"  # type: ignore[union-attr]

    def test_html_mode(self) -> None:
        att = PageAttachment(html_content=[
            heading("More Details"),
            paragraph("Extended description here."),
        ])
        node = att.to_node()
        tags = [c.tag for c in node.children]  # type: ignore[union-attr]
        assert "h1" in tags
        assert "p" in tags

    def test_mixing_links_and_html_raises(self) -> None:
        with pytest.raises(ValidationError, match="cannot mix"):
            PageAttachment(
                links=[AttachmentLink("x", "https://example.com")],
                html_content=[paragraph("text")],
            )

    def test_empty_attachment_no_children(self) -> None:
        att = PageAttachment()
        node = att.to_node()
        assert node.children == []

    def test_custom_cta_text(self) -> None:
        att = PageAttachment(cta_text="Explore")
        assert att.to_node().attrs["cta-text"] == "Explore"

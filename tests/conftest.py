"""Shared fixtures and helpers for the amp_stories test suite."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from amp_stories import AmpImg, Layer, Page, Story

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def minimal_page() -> Page:
    """A minimal valid Page with one fill layer and one vertical layer."""
    return Page(
        page_id="test-page",
        layers=[
            Layer("fill", children=[AmpImg("https://example.com/img.jpg", alt="test")]),
            Layer("vertical", children=[]),
        ],
    )


@pytest.fixture()
def minimal_story(minimal_page: Page) -> Story:
    """A minimal valid Story wrapping one page."""
    return Story(
        title="Test Story",
        publisher="Test Publisher",
        publisher_logo_src="https://example.com/logo.png",
        poster_portrait_src="https://example.com/poster.jpg",
        canonical_url="https://example.com/story.html",
        pages=[minimal_page],
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_html(html: str) -> ET.Element:
    """Parse the rendered story HTML and return the root element.

    Strips the ``<!doctype html>`` declaration, which xml.etree cannot parse,
    before parsing.
    """
    # Remove the doctype declaration
    cleaned = html.replace("<!doctype html>\n", "").replace("<!DOCTYPE html>\n", "")
    # The ⚡ attribute on <html> confuses the XML parser — replace with amp
    cleaned = cleaned.replace("<html ⚡", "<html amp", 1)
    return ET.fromstring(cleaned)


def find_tag(root: ET.Element, tag: str) -> ET.Element | None:
    """Find the first element with *tag* anywhere in *root*'s subtree."""
    if root.tag == tag:
        return root
    return root.find(f".//{tag}")


def find_all_tags(root: ET.Element, tag: str) -> list[ET.Element]:
    """Find all elements with *tag* in *root*'s subtree."""
    results = []
    if root.tag == tag:
        results.append(root)
    results.extend(root.findall(f".//{tag}"))
    return results

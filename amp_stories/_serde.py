"""Serialization and deserialization for amp_stories dataclasses.

All library components can be round-tripped through plain Python dicts::

    data = story.to_dict()          # dict with "type" discriminators
    story2 = Story.from_dict(data)  # reconstructed from the dict
    assert story2.render() == story.render()

The public entry points are :func:`from_dict` (module-level) and the
:meth:`~amp_stories.story.Story.to_dict` / :meth:`~amp_stories.story.Story.from_dict`
methods on :class:`~amp_stories.story.Story`.
"""

from __future__ import annotations

import dataclasses
from typing import Any

# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def _serialize(obj: Any) -> Any:
    """Recursively convert a dataclass instance to a plain dict.

    Rules:
    - ``None`` values are omitted to keep output compact.
    - Scalars (str, int, float, bool) pass through unchanged.
    - Lists and dicts are traversed recursively.
    - Dataclass instances gain a ``"type"`` key with the class name.
    - Any other type is returned as-is.
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        result: dict[str, Any] = {"__type__": type(obj).__name__}
        for f in dataclasses.fields(obj):
            if not f.init:
                continue
            val = getattr(obj, f.name)
            serialized = _serialize(val)
            if serialized is not None:
                result[f.name] = serialized
        return result
    # Non-dataclass, non-primitive: return as-is (e.g. custom user objects)
    return obj  # pragma: no cover


# ---------------------------------------------------------------------------
# Deserialization
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, type] | None = None


def _get_registry() -> dict[str, type]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


def _build_registry() -> dict[str, type]:
    """Build the type-name → class mapping for all serializable components."""
    from amp_stories.animation import Animation  # noqa: PLC0415
    from amp_stories.attachment import AttachmentLink, PageAttachment  # noqa: PLC0415
    from amp_stories.auto_ads import AutoAds  # noqa: PLC0415
    from amp_stories.bookend import (  # noqa: PLC0415
        Bookend,
        BookendComponent,
        BookendShareProvider,
    )
    from amp_stories.consent import AmpConsent  # noqa: PLC0415
    from amp_stories.elements import (  # noqa: PLC0415
        AmpAudio,
        AmpImg,
        AmpList,
        AmpVideo,
        DivElement,
        Story360,
        StoryPanningMedia,
        TextElement,
        VideoSource,
    )
    from amp_stories.interactive import (  # noqa: PLC0415
        InteractiveBinaryPoll,
        InteractiveOption,
        InteractivePoll,
        InteractiveQuiz,
        InteractiveResults,
        InteractiveSlider,
    )
    from amp_stories.layer import Layer  # noqa: PLC0415
    from amp_stories.outlink import PageOutlink  # noqa: PLC0415
    from amp_stories.page import Page  # noqa: PLC0415
    from amp_stories.shopping import ShoppingTag, StoryShopping  # noqa: PLC0415
    from amp_stories.story import Story  # noqa: PLC0415
    from amp_stories.themes import Theme  # noqa: PLC0415

    return {
        "Animation": Animation,
        "AmpImg": AmpImg,
        "VideoSource": VideoSource,
        "AmpVideo": AmpVideo,
        "StoryPanningMedia": StoryPanningMedia,
        "Story360": Story360,
        "AmpAudio": AmpAudio,
        "TextElement": TextElement,
        "DivElement": DivElement,
        "AmpList": AmpList,
        "Layer": Layer,
        "Page": Page,
        "Story": Story,
        "PageOutlink": PageOutlink,
        "AttachmentLink": AttachmentLink,
        "PageAttachment": PageAttachment,
        "Bookend": Bookend,
        "BookendComponent": BookendComponent,
        "BookendShareProvider": BookendShareProvider,
        "AutoAds": AutoAds,
        "StoryShopping": StoryShopping,
        "ShoppingTag": ShoppingTag,
        "AmpConsent": AmpConsent,
        "InteractiveOption": InteractiveOption,
        "InteractiveBinaryPoll": InteractiveBinaryPoll,
        "InteractivePoll": InteractivePoll,
        "InteractiveQuiz": InteractiveQuiz,
        "InteractiveSlider": InteractiveSlider,
        "InteractiveResults": InteractiveResults,
        "Theme": Theme,
    }


def _deserialize(data: Any) -> Any:
    """Reconstruct a dataclass (or nested structure) from a plain dict.

    Dicts with a ``"type"`` key that matches a registered class are
    reconstructed as that class.  Unknown type tags and plain dicts (no
    ``"type"`` key) are returned as plain dicts with their values
    recursively deserialized.
    """
    if data is None or isinstance(data, (str, int, float, bool)):
        return data
    if isinstance(data, list):
        return [_deserialize(item) for item in data]
    if isinstance(data, dict):
        type_name = data.get("__type__")
        if type_name is not None:
            cls = _get_registry().get(type_name)
            if cls is not None:
                valid_fields = {f.name for f in dataclasses.fields(cls) if f.init}
                kwargs = {
                    k: _deserialize(v)
                    for k, v in data.items()
                    if k != "__type__" and k in valid_fields
                }
                return cls(**kwargs)
        # Plain dict or unknown __type__: recurse into values but preserve all keys
        return {k: _deserialize(v) for k, v in data.items()}
    return data  # pragma: no cover


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def from_dict(data: dict[str, Any]) -> Any:
    """Reconstruct any amp_stories component from a dict produced by ``to_dict()``.

    The dict must contain a ``"type"`` key whose value matches a registered
    class name.  Returns the reconstructed dataclass instance.

    Example::

        import json
        from amp_stories import from_dict

        story = from_dict(json.loads(saved_json))
    """
    return _deserialize(data)

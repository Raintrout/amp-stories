"""Tests for animation.py."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.animation import Animation


class TestAnimation:
    def test_valid_effect(self) -> None:
        anim = Animation(effect="fade-in")
        assert anim.effect == "fade-in"

    def test_invalid_effect_raises(self) -> None:
        with pytest.raises(ValidationError, match="animate_in"):
            Animation(effect="spin-around")  # type: ignore[arg-type]

    def test_valid_duration(self) -> None:
        anim = Animation(effect="fade-in", duration="0.5s")
        assert anim.duration == "0.5s"

    def test_valid_duration_ms(self) -> None:
        anim = Animation(effect="fade-in", duration="300ms")
        assert anim.duration == "300ms"

    def test_invalid_duration_raises(self) -> None:
        with pytest.raises(ValidationError, match="animate_in_duration"):
            Animation(effect="fade-in", duration="fast")

    def test_valid_delay(self) -> None:
        anim = Animation(effect="fly-in-bottom", delay="1s")
        assert anim.delay == "1s"

    def test_invalid_delay_raises(self) -> None:
        with pytest.raises(ValidationError, match="animate_in_delay"):
            Animation(effect="fade-in", delay="1second")

    def test_after_field(self) -> None:
        anim = Animation(effect="fade-in", after="hero-img")
        assert anim.after == "hero-img"

    def test_to_attrs_all_fields(self) -> None:
        anim = Animation(effect="drop", duration="1.6s", delay="0.2s", after="prev")
        attrs = anim.to_attrs()
        assert attrs["animate-in"] == "drop"
        assert attrs["animate-in-duration"] == "1.6s"
        assert attrs["animate-in-delay"] == "0.2s"
        assert attrs["animate-in-after"] == "prev"

    def test_to_attrs_none_fields(self) -> None:
        anim = Animation(effect="fade-in")
        attrs = anim.to_attrs()
        assert attrs["animate-in"] == "fade-in"
        assert attrs["animate-in-duration"] is None
        assert attrs["animate-in-delay"] is None
        assert attrs["animate-in-after"] is None

    def test_all_valid_effects(self) -> None:
        valid_effects = [
            "fly-in-bottom", "fly-in-top", "fly-in-left", "fly-in-right",
            "fade-in", "rotate-in-left", "rotate-in-right", "drop",
            "pan-left", "pan-right", "pan-up", "pan-down",
            "zoom-in", "zoom-out", "pulse", "twirl-in",
            "whoosh-in-left", "whoosh-in-right",
        ]
        for effect in valid_effects:
            anim = Animation(effect=effect)  # type: ignore[arg-type]
            assert anim.effect == effect

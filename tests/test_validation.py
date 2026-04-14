"""Exhaustive tests for _validation.py helpers."""

from __future__ import annotations

import warnings

import pytest

from amp_stories._types import LayerTemplate
from amp_stories._validation import (
    AmpStoriesWarning,
    ValidationError,
    validate_aspect_ratio,
    validate_duration,
    validate_html_id,
    validate_literal,
    validate_nonempty,
    validate_poll_interval,
    warn,
)


class TestValidateNonempty:
    def test_valid_string(self) -> None:
        validate_nonempty("hello", "field")  # no error

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValidationError, match="field"):
            validate_nonempty("", "field")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationError, match="myfield"):
            validate_nonempty("   ", "myfield")


class TestValidateHtmlId:
    def test_valid_simple_id(self) -> None:
        validate_html_id("cover", "id")

    def test_valid_with_hyphen(self) -> None:
        validate_html_id("page-1", "id")

    def test_valid_with_dot(self) -> None:
        validate_html_id("page.1", "id")

    def test_valid_with_colon(self) -> None:
        validate_html_id("page:sec", "id")

    def test_valid_with_underscore(self) -> None:
        validate_html_id("my_page", "id")

    def test_starts_with_digit_raises(self) -> None:
        with pytest.raises(ValidationError, match="valid HTML id"):
            validate_html_id("1cover", "id")

    def test_starts_with_hyphen_raises(self) -> None:
        with pytest.raises(ValidationError, match="valid HTML id"):
            validate_html_id("-cover", "id")

    def test_space_raises(self) -> None:
        with pytest.raises(ValidationError, match="valid HTML id"):
            validate_html_id("my page", "id")

    def test_empty_raises(self) -> None:
        with pytest.raises(ValidationError):
            validate_html_id("", "id")


class TestValidateDuration:
    def test_seconds(self) -> None:
        validate_duration("1s", "dur")
        validate_duration("0.5s", "dur")
        validate_duration("10s", "dur")

    def test_milliseconds(self) -> None:
        validate_duration("300ms", "dur")
        validate_duration("1000ms", "dur")

    def test_decimal_ms(self) -> None:
        validate_duration("0.5ms", "dur")

    def test_no_unit_raises(self) -> None:
        with pytest.raises(ValidationError, match="duration"):
            validate_duration("500", "dur")

    def test_wrong_unit_raises(self) -> None:
        with pytest.raises(ValidationError, match="duration"):
            validate_duration("1sec", "dur")

    def test_text_raises(self) -> None:
        with pytest.raises(ValidationError, match="duration"):
            validate_duration("fast", "dur")

    def test_empty_raises(self) -> None:
        with pytest.raises(ValidationError, match="duration"):
            validate_duration("", "dur")


class TestValidateAspectRatio:
    def test_valid_ratio(self) -> None:
        validate_aspect_ratio("4:3", "ar")
        validate_aspect_ratio("16:9", "ar")
        validate_aspect_ratio("1:1", "ar")

    def test_decimal_raises(self) -> None:
        with pytest.raises(ValidationError, match="W:H"):
            validate_aspect_ratio("4.5:3", "ar")

    def test_missing_colon_raises(self) -> None:
        with pytest.raises(ValidationError, match="W:H"):
            validate_aspect_ratio("169", "ar")

    def test_text_raises(self) -> None:
        with pytest.raises(ValidationError, match="W:H"):
            validate_aspect_ratio("widescreen", "ar")


class TestValidateLiteral:
    def test_valid_value(self) -> None:
        validate_literal("fill", "template", LayerTemplate)

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValidationError, match="template"):
            validate_literal("full", "template", LayerTemplate)


class TestValidatePollInterval:
    def test_exactly_15000_allowed(self) -> None:
        validate_poll_interval(15000, "poll")

    def test_above_minimum_allowed(self) -> None:
        validate_poll_interval(30000, "poll")

    def test_below_minimum_raises(self) -> None:
        with pytest.raises(ValidationError, match="15000"):
            validate_poll_interval(14999, "poll")

    def test_zero_raises(self) -> None:
        with pytest.raises(ValidationError, match="15000"):
            validate_poll_interval(0, "poll")


class TestWarn:
    def test_emits_amp_stories_warning(self) -> None:
        with pytest.warns(AmpStoriesWarning, match="test warning"):
            warn("test warning")

    def test_warning_category(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            warn("check category")
        assert len(caught) == 1
        assert issubclass(caught[0].category, AmpStoriesWarning)

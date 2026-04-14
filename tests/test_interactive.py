"""Tests for interactive.py — amp-story-interactive components."""

from __future__ import annotations

import pytest

from amp_stories._validation import ValidationError
from amp_stories.interactive import (
    InteractiveBinaryPoll,
    InteractiveOption,
    InteractivePoll,
    InteractiveQuiz,
    InteractiveResults,
    InteractiveSlider,
)


class TestInteractiveOption:
    def test_defaults(self) -> None:
        opt = InteractiveOption("Option A")
        assert opt.text == "Option A"
        assert opt.correct is False
        assert opt.confetti is None

    def test_correct_flag(self) -> None:
        opt = InteractiveOption("Yes", correct=True)
        assert opt.correct is True

    def test_confetti(self) -> None:
        opt = InteractiveOption("Fun", confetti="🎉")
        assert opt.confetti == "🎉"


class TestInteractiveBinaryPoll:
    def test_renders_binary_poll_tag(self) -> None:
        poll = InteractiveBinaryPoll("Yes", "No")
        assert poll.to_node().tag == "amp-story-interactive-binary-poll"

    def test_option_attrs(self) -> None:
        poll = InteractiveBinaryPoll("Agree", "Disagree")
        node = poll.to_node()
        assert node.attrs["option-1-text"] == "Agree"
        assert node.attrs["option-2-text"] == "Disagree"

    def test_optional_id(self) -> None:
        poll = InteractiveBinaryPoll("A", "B", id="my-poll")
        assert poll.to_node().attrs["id"] == "my-poll"

    def test_empty_option_1_raises(self) -> None:
        with pytest.raises(ValidationError, match="option_1_text"):
            InteractiveBinaryPoll("", "B")

    def test_empty_option_2_raises(self) -> None:
        with pytest.raises(ValidationError, match="option_2_text"):
            InteractiveBinaryPoll("A", "")

    def test_whitespace_option_raises(self) -> None:
        with pytest.raises(ValidationError, match="option_1_text"):
            InteractiveBinaryPoll("   ", "B")


class TestInteractivePoll:
    def test_renders_poll_tag(self) -> None:
        poll = InteractivePoll([InteractiveOption("A"), InteractiveOption("B")])
        assert poll.to_node().tag == "amp-story-interactive-poll"

    def test_two_options_renders_attrs(self) -> None:
        poll = InteractivePoll([InteractiveOption("A"), InteractiveOption("B")])
        node = poll.to_node()
        assert node.attrs["option-1-text"] == "A"
        assert node.attrs["option-2-text"] == "B"
        assert node.attrs.get("option-3-text") is None

    def test_four_options_allowed(self) -> None:
        opts = [InteractiveOption(c) for c in "ABCD"]
        poll = InteractivePoll(opts)
        node = poll.to_node()
        assert node.attrs["option-4-text"] == "D"

    def test_confetti_attr_included(self) -> None:
        opts = [InteractiveOption("A", confetti="🎉"), InteractiveOption("B")]
        poll = InteractivePoll(opts)
        assert poll.to_node().attrs["option-1-confetti"] == "🎉"

    def test_one_option_raises(self) -> None:
        with pytest.raises(ValidationError, match="2 and 4"):
            InteractivePoll([InteractiveOption("A")])

    def test_five_options_raises(self) -> None:
        opts = [InteractiveOption(c) for c in "ABCDE"]
        with pytest.raises(ValidationError, match="2 and 4"):
            InteractivePoll(opts)

    def test_optional_id(self) -> None:
        opts = [InteractiveOption("A"), InteractiveOption("B")]
        poll = InteractivePoll(opts, id="my-poll")
        assert poll.to_node().attrs["id"] == "my-poll"


class TestInteractiveQuiz:
    def test_renders_quiz_tag(self) -> None:
        opts = [InteractiveOption("A", correct=True), InteractiveOption("B")]
        quiz = InteractiveQuiz(opts)
        assert quiz.to_node().tag == "amp-story-interactive-quiz"

    def test_correct_option_attr(self) -> None:
        opts = [InteractiveOption("A", correct=True), InteractiveOption("B")]
        quiz = InteractiveQuiz(opts)
        node = quiz.to_node()
        assert node.attrs["option-1-correct"] is True
        assert node.attrs.get("option-2-correct") is None

    def test_no_correct_raises(self) -> None:
        opts = [InteractiveOption("A"), InteractiveOption("B")]
        with pytest.raises(ValidationError, match="exactly one correct"):
            InteractiveQuiz(opts)

    def test_two_correct_raises(self) -> None:
        opts = [InteractiveOption("A", correct=True), InteractiveOption("B", correct=True)]
        with pytest.raises(ValidationError, match="exactly one correct"):
            InteractiveQuiz(opts)

    def test_too_few_options_raises(self) -> None:
        with pytest.raises(ValidationError, match="2 and 4"):
            InteractiveQuiz([InteractiveOption("A", correct=True)])

    def test_optional_id(self) -> None:
        opts = [InteractiveOption("A", correct=True), InteractiveOption("B")]
        quiz = InteractiveQuiz(opts, id="q1")
        assert quiz.to_node().attrs["id"] == "q1"

    def test_confetti_attr_included(self) -> None:
        opts = [InteractiveOption("A", correct=True, confetti="🎉"), InteractiveOption("B")]
        quiz = InteractiveQuiz(opts)
        assert quiz.to_node().attrs["option-1-confetti"] == "🎉"


class TestInteractiveSlider:
    def test_renders_slider_tag(self) -> None:
        slider = InteractiveSlider()
        assert slider.to_node().tag == "amp-story-interactive-slider"

    def test_default_emojis(self) -> None:
        slider = InteractiveSlider()
        node = slider.to_node()
        assert node.attrs["emoji-start"] == "😐"
        assert node.attrs["emoji-end"] == "😍"

    def test_custom_emojis(self) -> None:
        slider = InteractiveSlider(emoji_start="😢", emoji_end="😊")
        node = slider.to_node()
        assert node.attrs["emoji-start"] == "😢"
        assert node.attrs["emoji-end"] == "😊"

    def test_optional_id(self) -> None:
        slider = InteractiveSlider(id="slider-1")
        assert slider.to_node().attrs["id"] == "slider-1"


class TestInteractiveResults:
    def test_renders_results_tag(self) -> None:
        opts = [InteractiveOption("Good"), InteractiveOption("Great")]
        results = InteractiveResults(opts)
        assert results.to_node().tag == "amp-story-interactive-results"

    def test_results_category_attrs(self) -> None:
        opts = [InteractiveOption("Good"), InteractiveOption("Great")]
        results = InteractiveResults(opts)
        node = results.to_node()
        assert node.attrs["option-1-results-category"] == "Good"
        assert node.attrs["option-2-results-category"] == "Great"

    def test_confetti_attr_included(self) -> None:
        opts = [InteractiveOption("A", confetti="🎊"), InteractiveOption("B")]
        results = InteractiveResults(opts)
        assert results.to_node().attrs["option-1-confetti"] == "🎊"

    def test_too_few_options_raises(self) -> None:
        with pytest.raises(ValidationError, match="2 and 4"):
            InteractiveResults([InteractiveOption("A")])

    def test_optional_id(self) -> None:
        opts = [InteractiveOption("A"), InteractiveOption("B")]
        results = InteractiveResults(opts, id="res-1")
        assert results.to_node().attrs["id"] == "res-1"

"""amp-story-interactive element wrappers.

Provides five interactive component types that can be embedded in story pages
inside an ``amp-story-grid-layer``. All require the ``amp-story-interactive``
extension script, which is injected automatically by
:class:`~amp_stories.story.Story`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from amp_stories._html import HtmlNode
from amp_stories._validation import ValidationError


@dataclass
class InteractiveOption:
    """A single option entry for polls, quizzes, and results components.

    Args:
        text: Display text for this option.
        correct: Whether this is the correct answer (used by :class:`InteractiveQuiz`).
        confetti: Confetti emoji displayed when this option is selected.
    """

    text: str
    correct: bool = False
    confetti: str | None = None


@dataclass
class InteractiveBinaryPoll:
    """An ``<amp-story-interactive-binary-poll>`` element with exactly two options.

    Args:
        option_1_text: Text for the first option.
        option_2_text: Text for the second option.
        id: Optional HTML id for the element.
    """

    option_1_text: str
    option_2_text: str
    id: str | None = None

    def __post_init__(self) -> None:
        if not self.option_1_text.strip():
            raise ValidationError("InteractiveBinaryPoll.option_1_text must not be empty.")
        if not self.option_2_text.strip():
            raise ValidationError("InteractiveBinaryPoll.option_2_text must not be empty.")

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "option-1-text": self.option_1_text,
            "option-2-text": self.option_2_text,
            "id": self.id,
        }
        return HtmlNode("amp-story-interactive-binary-poll", attrs)


def _validate_poll_options(options: list[InteractiveOption], cls_name: str) -> None:
    if not 2 <= len(options) <= 4:
        raise ValidationError(
            f"{cls_name} requires between 2 and 4 options. Got: {len(options)}"
        )


@dataclass
class InteractivePoll:
    """An ``<amp-story-interactive-poll>`` element with 2–4 options.

    Args:
        options: List of 2–4 :class:`InteractiveOption` items.
        id: Optional HTML id for the element.
    """

    options: list[InteractiveOption] = field(default_factory=list)
    id: str | None = None

    def __post_init__(self) -> None:
        _validate_poll_options(self.options, "InteractivePoll")

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {"id": self.id}
        for i, opt in enumerate(self.options, start=1):
            attrs[f"option-{i}-text"] = opt.text
            if opt.confetti is not None:
                attrs[f"option-{i}-confetti"] = opt.confetti
        return HtmlNode("amp-story-interactive-poll", attrs)


@dataclass
class InteractiveQuiz:
    """An ``<amp-story-interactive-quiz>`` element with 2–4 options, exactly one correct.

    Args:
        options: List of 2–4 :class:`InteractiveOption` items; exactly one must
            have ``correct=True``.
        id: Optional HTML id for the element.
    """

    options: list[InteractiveOption] = field(default_factory=list)
    id: str | None = None

    def __post_init__(self) -> None:
        _validate_poll_options(self.options, "InteractiveQuiz")
        correct_count = sum(1 for o in self.options if o.correct)
        if correct_count != 1:
            raise ValidationError(
                f"InteractiveQuiz requires exactly one correct option. "
                f"Got: {correct_count}"
            )

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {"id": self.id}
        for i, opt in enumerate(self.options, start=1):
            attrs[f"option-{i}-text"] = opt.text
            if opt.correct:
                attrs[f"option-{i}-correct"] = True
            if opt.confetti is not None:
                attrs[f"option-{i}-confetti"] = opt.confetti
        return HtmlNode("amp-story-interactive-quiz", attrs)


@dataclass
class InteractiveSlider:
    """An ``<amp-story-interactive-slider>`` element.

    Args:
        emoji_start: Emoji displayed at the start of the slider.
        emoji_end: Emoji displayed at the end of the slider.
        id: Optional HTML id for the element.
    """

    emoji_start: str = "\U0001f610"  # 😐
    emoji_end: str = "\U0001f60d"    # 😍
    id: str | None = None

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {
            "emoji-start": self.emoji_start,
            "emoji-end": self.emoji_end,
            "id": self.id,
        }
        return HtmlNode("amp-story-interactive-slider", attrs)


@dataclass
class InteractiveResults:
    """An ``<amp-story-interactive-results>`` display-only results card.

    Args:
        options: Outcome text entries for the different result buckets.
        id: Optional HTML id for the element.
    """

    options: list[InteractiveOption] = field(default_factory=list)
    id: str | None = None

    def __post_init__(self) -> None:
        _validate_poll_options(self.options, "InteractiveResults")

    def to_node(self) -> HtmlNode:
        attrs: dict[str, str | bool | None] = {"id": self.id}
        for i, opt in enumerate(self.options, start=1):
            attrs[f"option-{i}-results-category"] = opt.text
            if opt.confetti is not None:
                attrs[f"option-{i}-confetti"] = opt.confetti
        return HtmlNode("amp-story-interactive-results", attrs)

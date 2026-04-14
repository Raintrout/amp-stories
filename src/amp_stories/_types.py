"""Shared type aliases and Literal definitions for amp_stories."""

from typing import Literal

AnimateIn = Literal[
    "fly-in-bottom",
    "fly-in-top",
    "fly-in-left",
    "fly-in-right",
    "fade-in",
    "rotate-in-left",
    "rotate-in-right",
    "drop",
    "pan-left",
    "pan-right",
    "pan-up",
    "pan-down",
    "zoom-in",
    "zoom-out",
    "pulse",
    "twirl-in",
    "whoosh-in-left",
    "whoosh-in-right",
]

LayerTemplate = Literal["fill", "vertical", "horizontal", "thirds"]

LayerPreset = Literal["2021-background", "2021-foreground"]

Anchor = Literal[
    "top",
    "bottom",
    "left",
    "right",
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
]

ShareProvider = Literal[
    "email",
    "twitter",
    "tumblr",
    "facebook",
    "gplus",
    "linkedin",
    "whatsapp",
    "sms",
    "system",
]

BookendComponentType = Literal[
    "heading",
    "small",
    "portrait",
    "landscape",
    "cta-link",
    "textbox",
]

ImageLayout = Literal["fill", "fixed", "responsive", "intrinsic"]

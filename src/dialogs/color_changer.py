"""
This class lets the user configure a color.
"""

from tkinter import colorchooser


class ColorChanger:
    """Lets the user configure a color via a color chooser dialog."""

    def __init__(self, default_color: str) -> None:
        self.default_color = default_color

    def ask_color(self) -> str | None:
        """Show color chooser; return selected hex color or None if cancelled."""
        return colorchooser.askcolor(self.default_color)[1]

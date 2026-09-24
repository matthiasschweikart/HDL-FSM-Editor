"""
This class lets the user configure regex patterns for log parsing.
"""

import re
import tkinter as tk
from dataclasses import dataclass
from tkinter import simpledialog, ttk


@dataclass
class RegexConfig:
    """Configuration for regex pattern matching in log files."""

    pattern: str
    filename_group: str
    line_number_group: str
    debug_active: bool


class RegexDialog(simpledialog.Dialog):
    """Dialog for configuring regex patterns for log parsing."""

    def __init__(
        self,
        parent: tk.Tk | tk.Toplevel,
        language: str,
        current_pattern: str,
        current_filename_group: str,
        current_line_number_group: str,
        current_debug_active: bool,
    ) -> None:
        self.language = language
        self.current_pattern = current_pattern
        self.current_filename_group = current_filename_group
        self.current_line_number_group = current_line_number_group
        self.current_debug_active = current_debug_active
        super().__init__(parent, "Enter Regex for Python:")

    def validate_regex(self, pattern: str) -> bool:
        """Validate if the given pattern is a valid regex."""
        if not pattern.strip():
            return True  # Empty pattern is considered valid
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False

    def on_pattern_change(self, _event: tk.Event) -> None:
        """Handle pattern entry changes and update background color based on validity."""
        pattern = self.pattern_entry.get()
        is_valid = self.validate_regex(pattern)

        if is_valid:
            self.pattern_entry.configure(style="My.TEntry")
        else:
            self.pattern_entry.configure(style="InvalidRegex.TEntry")

    def body(self, master: tk.Frame) -> tk.Widget | None:
        """
        Overrides body() of simpledialog.Dialog.
        Create the dialog body. Return the widget that should have initial focus.
        """
        # Header
        ttk.Label(
            master,
            text="Regex to extract file name and line number from simulator messages:",
            justify="left",
            style="My.TLabel",
        ).grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # Pattern entry
        self.pattern_entry = ttk.Entry(master, style="My.TEntry")
        self.pattern_entry.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.pattern_entry.insert(0, self.current_pattern)
        # Bind the validation function to key release events
        self.pattern_entry.bind("<KeyRelease>", self.on_pattern_change)
        # Initial validation
        self.on_pattern_change(None)

        # Group identifiers frame
        id_frame = ttk.Frame(master, style="My.TFrame")
        id_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)

        # Filename group
        ttk.Label(id_frame, text="Group identifier for file-name:", justify="left", style="My.TLabel").grid(
            row=0, column=0, sticky="w", padx=0, pady=0
        )
        self.filename_entry = ttk.Entry(id_frame, width=40, style="My.TEntry")
        self.filename_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.filename_entry.insert(0, self.current_filename_group)

        # Line number group
        ttk.Label(id_frame, text="Group identifier for line-number:", justify="left", style="My.TLabel").grid(
            row=1, column=0, sticky="w", padx=0, pady=0
        )
        self.line_number_entry = ttk.Entry(id_frame, width=40, style="My.TEntry")
        self.line_number_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.line_number_entry.insert(0, self.current_line_number_group)

        # Debug options frame
        debug_frame = ttk.Frame(master, style="My.TFrame")
        debug_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=2)
        ttk.Label(debug_frame, text="Debug Regex at STDOUT:", padding=0, style="My.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.debug_var = tk.IntVar(value=2 if self.current_debug_active else 1)
        ttk.Radiobutton(
            debug_frame, takefocus=False, variable=self.debug_var, text="Inactive", value=1, style="My.TRadiobutton"
        ).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(
            debug_frame, takefocus=False, variable=self.debug_var, text="Active", value=2, style="My.TRadiobutton"
        ).grid(row=0, column=2, sticky="w")

        # Configure grid weights
        master.columnconfigure(0, weight=1)
        id_frame.columnconfigure(1, weight=1)

        return self.pattern_entry  # Return widget that should have initial focus

    def apply(self) -> None:
        """
        Overrides apply() of simpledialog.Dialog.
        Process the dialog data and set the result.
        """
        self.result = RegexConfig(
            pattern=self.pattern_entry.get(),
            filename_group=self.filename_entry.get(),
            line_number_group=self.line_number_entry.get(),
            debug_active=self.debug_var.get() == 2,
        )

    @classmethod
    def ask_regex(
        cls,
        parent: tk.Tk | tk.Toplevel,
        language: str,
        current_pattern: str,
        current_filename_group: str,
        current_line_number_group: str,
        current_debug_active: bool,
    ) -> RegexConfig | None:
        """Show the regex configuration dialog and return the result."""
        dialog = cls(
            parent, language, current_pattern, current_filename_group, current_line_number_group, current_debug_active
        )
        return dialog.result

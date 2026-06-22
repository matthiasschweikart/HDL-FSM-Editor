"""
Extensions to the standard tkinter.Text widget for code editing.

- Word-wise cursor movement (Ctrl+Left/Right) and selection (Ctrl+Shift+Left/Right)
- Correct Shift+Arrow selection and anchor handling
- Whole-word deletion (Ctrl+BackSpace, Ctrl+Delete)
- Indent/unindent (Ctrl+], Ctrl+[ and Shift+Tab)
"""

import platform
import re
import tkinter as tk
from collections.abc import Callable
from typing import Any


class CodeEditor(tk.Text):
    """
    A code editor widget extending tkinter.Text with word movement,
    selection, word deletion, and indent/unindent.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Ctrl-c/x without selection should copy/cut the whole line:
        self.bind("<Control-c>", lambda event: self._copy())
        self.bind("<Control-x>", lambda event: self._cut())
        # Ctrl-v after Ctrl-c/x without selection should paste at the beginning of the line:
        self.bind("<Control-v>", lambda event: self._paste())
        self.paste_always_at_line_begin = False
        # Word-wise cursor movement
        self.bind("<Control-Left>", lambda event: self.move_word_left())
        self.bind("<Control-Right>", lambda event: self.move_word_right())
        # Word selection
        self.bind("<Shift-Control-Left>", lambda event: self.select_word_left())
        self.bind("<Shift-Control-Right>", lambda event: self.select_word_right())
        # Shift+arrow: normal selection with correct anchor when switching from word selection
        self.bind("<Shift-Left>", lambda event: self._handle_normal_selection_left())
        self.bind("<Shift-Right>", lambda event: self._handle_normal_selection_right())
        # Reset anchor when moving with arrow keys (no shift)
        self.bind("<Left>", lambda event: self._reset_anchor_if_no_selection())
        self.bind("<Right>", lambda event: self._reset_anchor_if_no_selection())
        self.bind("<Up>", lambda event: self._reset_anchor_if_no_selection())
        self.bind("<Down>", lambda event: self._reset_anchor_if_no_selection())
        # Whole word deletion
        self.bind("<Control-BackSpace>", lambda event: self.delete_word_backward())
        self.bind("<Control-Delete>", lambda event: self.delete_word_forward())
        # Indent/unindent (works only under Linux)
        self.bind("<Control-bracketleft>", lambda event: self.unindent_selection())
        self.bind("<Control-bracketright>", lambda event: self.indent_selection())
        # Indent/unindent
        self.bind("<Tab>", lambda event: self.indent_selection())
        if platform.system() == "Windows":
            self.bind("<Shift-Tab>", lambda event: self.unindent_selection())
        else:
            self.bind("<ISO_Left_Tab>", lambda event: self.unindent_selection())
        # Pos1/Home
        self.bind("<Home>", lambda event: self._move_to_line_start())

    def _move_to_line_start(self) -> str:
        """Move cursor to the first non-blank character of the line, or to the absolute line start if already there."""
        line_start_index = self.index("insert linestart")
        line_text = self.get(line_start_index, f"{line_start_index} lineend")
        first_non_blank_index = re.search(r"\S", line_text)
        if first_non_blank_index:
            target_index = f"{line_start_index} + {first_non_blank_index.start()} chars"
            if self.index(tk.INSERT) == self.index(target_index):  # Cursor is already at the first non-blank character
                target_index = line_start_index  # Move to line start
        else:  # The line is empty or consists of blanks only
            target_index = line_start_index
        self.mark_set(tk.INSERT, target_index)  # set the insertion marker to the target index.
        self.tag_remove(tk.SEL, "1.0", tk.END)  # Remove any existing selection.
        self.mark_set(tk.ANCHOR, target_index)  # Set the selection anchor (for shift-click extension) to the target.
        return "break"

    def _copy(self) -> str | None:
        self.paste_always_at_line_begin = False
        sel_ranges: tuple[str, ...] = self.tag_ranges(tk.SEL)
        if not sel_ranges:
            self._copy_complete_line()
            return "break"
        return  # pass ctrl-c to default handler for copying the selection

    def _cut(self) -> str | None:
        # Called by CTRL-x with or without selection.
        sel_ranges: tuple[str, ...] = self.tag_ranges(tk.SEL)
        if not sel_ranges:
            self._cut_complete_line()
            self.format_after_idle(None)
            return "break"  # Nothing else todo
        self.format_after_idle(None)
        # format_after_idle() is needed here also, because custom_text cuts the selected part
        # with Ctrl-x as expected, but custom_text is only triggered by "Ctrl" (and ignores
        # the following "x") and misses the text change.
        return  # pass ctrl-x to default handler for cutting the selection

    def _paste(self) -> str | None:
        sel_ranges: tuple[str, ...] = self.tag_ranges(tk.SEL)
        if not sel_ranges and self.paste_always_at_line_begin:
            self._paste_complete_line()
            self.format_after_idle(None)
            return "break"
        self.format_after_idle(None)  # Trigger formatting after default paste action (which may be line-wise or not)
        return  # pass ctrl-v to default handler for pasting the selection

    def _copy_complete_line(self) -> None:
        self.paste_always_at_line_begin = True
        line_start = self.index("insert linestart")
        line_end = self.index("insert lineend")
        self.clipboard_clear()
        # Put a return character at the end, regardless of whether the line already ends with one.
        self.clipboard_append(self.get(line_start, line_end) + "\n")
        return line_start, line_end

    def _cut_complete_line(self) -> None:
        line_start, line_end = self._copy_complete_line()
        # Delete also the possible newline character at the end of the line, regardless of whether it exists.
        self.delete(line_start, line_end + "+1c")

    def _paste_complete_line(self) -> None:
        line_start = self.index("insert linestart")
        self.insert(line_start, self.clipboard_get())

    def format_after_idle(self, event) -> None:
        """Override in subclass to trigger formatting after indent/unindent. No-op by default."""

    def _handle_normal_selection(self, direction: str) -> str:
        """
        Handle Shift+Left or Shift+Right for character selection.
        direction: "left" or "right".
        """
        sel_ranges: tuple[str, ...] = self.tag_ranges(tk.SEL)  # type: ignore[assignment]
        try:
            anchor_pos = self.index(tk.ANCHOR)
        except tk.TclError:
            self.mark_set(tk.ANCHOR, tk.INSERT)
        cursor_pos = self.index(tk.INSERT)
        if not sel_ranges:
            self.mark_set(tk.ANCHOR, cursor_pos)
            anchor_pos = cursor_pos
        try:
            delta = "- 1 char" if direction == "left" else "+ 1 char"
            new_cursor_pos = self.index(f"{cursor_pos} {delta}")
        except tk.TclError:
            return "break"
        self.mark_set(tk.INSERT, new_cursor_pos)
        if self.compare(anchor_pos, ">", new_cursor_pos):
            sel_start, sel_end = new_cursor_pos, anchor_pos
        else:
            sel_start, sel_end = anchor_pos, new_cursor_pos
        self.tag_remove(tk.SEL, "1.0", tk.END)
        if self.compare(sel_start, "!=", sel_end):
            self.tag_add(tk.SEL, sel_start, sel_end)
        return "break"

    def _handle_normal_selection_left(self) -> str:
        return self._handle_normal_selection("left")

    def _handle_normal_selection_right(self) -> str:
        return self._handle_normal_selection("right")

    def _reset_anchor_if_no_selection(self) -> None:
        """Reset anchor to cursor when there is no selection (after default movement)."""
        sel_ranges: tuple[str, ...] = self.tag_ranges(tk.SEL)  # type: ignore[assignment]
        if not sel_ranges:

            def reset_anchor() -> None:
                self.mark_set(tk.ANCHOR, self.index(tk.INSERT))

            self.after_idle(reset_anchor)

    def _move_cursor(self, find_boundary_func: Callable[[str], str]) -> str:
        """Move cursor to token boundary; clear selection and set anchor."""
        current_pos = self.index(tk.INSERT)
        target_pos = find_boundary_func(current_pos)
        if not target_pos:
            return "break"
        self.tag_remove(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.ANCHOR, target_pos)
        self.mark_set(tk.INSERT, target_pos)
        return "break"

    def _select_token(self, find_boundary_func: Callable[[str], str]) -> str:
        """Extend selection by one token in the given direction."""
        cursor_pos = self.index(tk.INSERT)
        target_pos = find_boundary_func(cursor_pos)
        if not target_pos:
            return "break"
        sel_ranges: tuple[str, ...] = self.tag_ranges(tk.SEL)  # type: ignore[assignment]
        self.tag_remove(tk.SEL, "1.0", tk.END)
        if sel_ranges:
            sel_start, sel_end = sel_ranges[0], sel_ranges[1]
        else:
            sel_start = sel_end = cursor_pos
        sel_anchor = sel_start if self.compare(sel_end, "==", cursor_pos) else sel_end
        self.mark_set(tk.ANCHOR, sel_anchor)
        self.mark_set(tk.INSERT, target_pos)
        if self.compare(target_pos, "<", sel_anchor):
            sel_start, sel_end = target_pos, sel_anchor
        else:
            sel_start, sel_end = sel_anchor, target_pos
        if self.compare(sel_start, "!=", sel_end):
            self.tag_add(tk.SEL, sel_start, sel_end)
            self.focus_set()
        return "break"

    def _find_token_start_backward(self, idx: str) -> str:
        token_rx = re.compile(r"\n|(?:[\w_]+|[^\w\s]+)[ \t]*")
        txt = self.get("1.0", idx)
        m = None
        for match in re.finditer(token_rx, txt):
            m = match
        if not m:
            return ""
        return f"1.0 + {m.start()} chars"

    def _find_token_end_forward(self, idx: str) -> str:
        token_rx = re.compile(r"\n|[ \t]*(?:[\w_]+|[^\w\s]+)")
        txt = self.get(idx, "end-1c")
        m = re.search(token_rx, txt)
        if m:
            return f"{idx} + {m.end()} chars"
        return ""

    def move_word_left(self) -> str:
        """Move insertion cursor one word left"""
        return self._move_cursor(self._find_token_start_backward)

    def move_word_right(self) -> str:
        """Move insertion cursor one word right"""
        return self._move_cursor(self._find_token_end_forward)

    def select_word_left(self) -> str:
        """Extend selection by one word to the left"""
        return self._select_token(self._find_token_start_backward)

    def select_word_right(self) -> str:
        """Extend selection by one word to the right"""
        return self._select_token(self._find_token_end_forward)

    def _delete_token(
        self,
        find_boundary_func: Callable[[str], str],
        backward: bool,
    ) -> str:
        """Delete one token backward or forward. Override to call format_after_idle."""
        current_pos = self.index(tk.INSERT)
        target_pos = find_boundary_func(current_pos)
        if not target_pos:
            return "break"
        if backward:
            self.delete(target_pos, current_pos)
        else:
            self.delete(current_pos, target_pos)
        self.format_after_idle(None)
        return "break"

    def delete_word_backward(self) -> str:
        """Delete one word left"""
        return self._delete_token(self._find_token_start_backward, backward=True)

    def delete_word_forward(self) -> str:
        """Delete one word right"""
        return self._delete_token(self._find_token_end_forward, backward=False)

    def _apply_indent_action(self, line_action: Callable[[int], None]) -> None:
        """Apply indent/unindent to selection or current line."""
        sel = self.tag_ranges(tk.SEL)
        if sel:
            start_line, end_line = self._get_start_and_end_line_of_selection(sel)
        else:
            start_line = int(self.index(tk.INSERT).split(".", maxsplit=1)[0])
            end_line = start_line
        for line_num in range(start_line, end_line + 1):
            line_action(line_num)

    def indent_selection(self) -> str:
        """Indents the line or all lines in the selection by inserting 4 blanks at the beginning of each line."""

        def _indent_line(line_num: int) -> None:
            line_start_index, number_of_leading_blanks = self._get_number_of_leading_blanks(line_num)
            spaces_to_add = 4 - number_of_leading_blanks if (number_of_leading_blanks % 4 != 0) else 4
            # The new characters shall be selected if the line is already selected:
            tags = (tk.SEL) if tk.SEL in self.tag_names(line_start_index) else ()
            self.insert(line_start_index, " " * spaces_to_add, tags)

        sel = self.tag_ranges(tk.SEL)
        insert_column = self.index(tk.INSERT).split(".", maxsplit=1)[1]
        if sel:
            sel_start_line, sel_start_column, sel_end_line, sel_end_column = self._get_position_of_the_selection(sel)
            if self._part_of_line_is_selected(sel_start_line, sel_start_column, sel_end_line, sel_end_column):
                self.delete(sel_start_line + "." + sel_start_column, sel_start_line + "." + sel_end_column)
                self._insert_blanks_until_next_indent_level(sel_start_column)
                self.format_after_idle(None)
                return "break"
        elif insert_column != "0":
            self._insert_blanks_until_next_indent_level(insert_column)
            self.format_after_idle(None)
            return "break"
        # One or several lines are selected, or the cursor is at the beginning of a line:
        self._apply_indent_action(_indent_line)
        self.format_after_idle(None)
        return "break"

    def _insert_blanks_until_next_indent_level(self, column):
        number_of_blanks = 4 - int(column) % 4
        self.insert(self.index(tk.INSERT), " " * number_of_blanks)

    def _get_position_of_the_selection(self, sel):
        sel_start_line = str(sel[0]).split(".", maxsplit=1)[0]
        sel_start_column = str(sel[0]).split(".", maxsplit=1)[1]
        sel_end_line = str(sel[1]).split(".", maxsplit=1)[0]
        sel_end_column = str(sel[1]).split(".", maxsplit=1)[1]  # zeigt auf das Zeichen nach der Selektion
        if sel_start_line != sel_end_line and sel_end_column == "0":
            # If the selection ends at the start of a line, don't include that line:
            sel_end_line = str(int(sel_end_line) - 1)
            sel_end_column = self.index(sel_end_line + ".end").split(".", maxsplit=1)[1]
        return sel_start_line, sel_start_column, sel_end_line, sel_end_column

    def _part_of_line_is_selected(self, sel_start_line, sel_start_column, sel_end_line, sel_end_column) -> bool:
        if sel_start_line == sel_end_line:
            line_end_column = self.index(sel_end_line + ".end").split(".", maxsplit=1)[1]
            if sel_start_column != "0" or sel_end_column != line_end_column:
                return True
        return False

    def unindent_selection(self) -> str:
        """Unindents the line or all lines in the selection by removing 4 blanks at the beginning of each line."""

        def _unindent_line(line_num: int) -> None:
            line_start_index, number_of_leading_blanks = self._get_number_of_leading_blanks(line_num)
            spaces_to_remove = 4 if number_of_leading_blanks % 4 == 0 else number_of_leading_blanks % 4
            self.delete(line_start_index, f"{line_num}.{spaces_to_remove}")

        if self._unindent_selection_is_allowed():
            self._apply_indent_action(_unindent_line)
            self.format_after_idle(None)
        return "break"

    def _unindent_selection_is_allowed(self) -> bool:
        sel = self.tag_ranges(tk.SEL)
        if sel:
            # Don't unindent if any of the lines in the selection does not start with blank:
            start_line, end_line = self._get_start_and_end_line_of_selection(sel)
        else:
            # Don't unindent if the current line does not start with blank:
            start_line = int(self.index(tk.INSERT).split(".", maxsplit=1)[0])
            end_line = start_line
        return all(self.get(f"{line_num}.0") == " " for line_num in range(start_line, end_line + 1))

    def _get_start_and_end_line_of_selection(self, sel) -> tuple[int, int]:
        sel_start, sel_end = sel[0], sel[1]
        if str(sel_end).endswith(
            ".0"
        ):  # If selection ends at the start of a line, don't include that line in the action.
            sel_end = self.index(f"{sel_end} - 1 char")
        start_line = int(str(sel_start).split(".", maxsplit=1)[0])
        end_line = int(str(sel_end).split(".", maxsplit=1)[0])
        return start_line, end_line

    def _get_number_of_leading_blanks(self, line_num: int) -> tuple[str, int]:
        line_start_index = f"{line_num}.0"
        line_text = self.get(line_start_index, f"{line_num}.end")
        number_of_leading_blanks = len(line_text) - len(line_text.lstrip())
        return line_start_index, number_of_leading_blanks

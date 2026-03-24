"""
This module contains a class which implements a dialog to
show the user how to work with keyboard shortcuts in the code editor.
"""

from dialogs import text_dialog


class ShortCutsDialog:
    """
    This class implements a dialog to show the user how to work with keyboard shortcuts in the code editor.
    """

    def __init__(self):
        content = """1. Ctrl-e loads the text into an external editor.
2. Ctrl-a selects all text.
3. Ctrl-c copies the selection into the clipboard.
4. Ctrl-x cuts the selection into the clipboard.
5. Ctrl-v pastes the content of the clipboard at the position of the insertion cursor, replacing any selection.
6. Ctrl-z undoes the last action.
7. Ctrl-Z or Ctrl-y redoes the last action.
8. Ctrl-G opens a dialog to jump to a specific line number (only in "Generated HDL" tab).
9. Ctrl-Left moves insertion-cursor 1 word left.
10. Ctrl-Right moves insertion-cursor 1 word right.
11. Ctrl-Up moves the insertion cursor to the beginning of the text.
12. Ctrl-Down moves the insertion cursor to the end of the text.
13. Ctrl-Home moves the insertion cursor to the beginning of the text.
14. Ctrl-End moves the insertion cursor to the end of the text.
15. Ctrl-] indents the selection or the current line (works only under Linux).
16. Ctrl-[ unindents the selection or the current line (works only under Linux).
17. Ctrl-Backspace deletes the word before the insertion cursor.
18. Ctrl-Delete deletes the word after the insertion cursor.
19. Tab without selection adds blanks at the cursor position to the next multiple of four characters.
20. Tab with selection inside a line deletes the selection and adds blanks at the cursor position to the next multiple\
 of four characters.
21. Tab with selection spanning multiple lines indents all selected lines (independent from start and end selection).
22. Shift-Tab unindents the selection or the current line.
23. The Home-Button zooms the diagram to show the entire design (same as "view all").
"""
        text_dialog.TextDialog("Keyboard Shortcuts for text editing", content, "1000x400")

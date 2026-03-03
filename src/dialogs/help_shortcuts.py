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
8. Ctrl-Left moves insertion-cursor 1 word left.
9. Ctrl-Right moves insertion-cursor 1 word right.
10. Ctrl-] indents the selection or the current line (works only under Linux).
11. Ctrl-[ unindents the selection or the current line (works only under Linux).
12. Ctrl-Backspace deletes the word before the insertion cursor.
13. Ctrl-Delete deletes the word after the insertion cursor.
14. Tab without selection adds blanks at the cursor position to the next multiple of four characters.
15. Tab with selection inside a line deletes the selection and adds blanks at the cursor position to the next multiple\
of four characters.
16. Tab with selection spanning multiple lines indents all selected lines (independent from start and end selection).
17. Shift-Tab unindents the selection or the current line.
18. The Home-Button zooms the diagram to show the entire design (same as "view all").
"""
        text_dialog.TextDialog("Keyboard Shortcuts for text editing", content, "1000x320")

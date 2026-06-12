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
3. Ctrl-c copies the selection into the clipboard. Ctrl-c without selection copies the whole line into the clipboard.
4. Ctrl-x cuts the selection into the clipboard. Ctrl-x without selection cuts the whole line into the clipboard.
5. Ctrl-v pastes the content of the clipboard at the position of the insertion cursor, replacing any selection.
6. Ctrl-v without selection after Ctrl-c/x without selection pastes before the actual line.
7. Ctrl-z undoes the last action.
8. Ctrl-Z or Ctrl-y redoes the last action.
9. Ctrl-G opens a dialog to jump to a specific line number (only in "Generated HDL" tab).
10. Ctrl-Left moves insertion-cursor 1 word left.
11. Ctrl-Right moves insertion-cursor 1 word right.
12. Ctrl-Up moves the insertion cursor to the beginning of the text.
13. Ctrl-Down moves the insertion cursor to the end of the text.
14. Ctrl-Home moves the insertion cursor to the beginning of the text.
15. Ctrl-End moves the insertion cursor to the end of the text.
16. Ctrl-] indents the selection or the current line (works only under Linux).
17. Ctrl-[ unindents the selection or the current line (works only under Linux).
18. Ctrl-Backspace deletes the word before the insertion cursor.
19. Ctrl-Delete deletes the word after the insertion cursor.
20. Tab without selection adds blanks at the cursor position to the next multiple of four characters.
21. Tab with selection inside a line deletes the selection and adds blanks at the cursor position to the next multiple\
 of four characters.
22. Tab with selection spanning multiple lines indents all selected lines (independent from start and end selection).
23. Shift-Tab unindents the selection or the current line.
24. The Home-Button zooms the diagram to show the entire design (same as "view all").
25. The Home-Button inside a text editor moves the insertion cursor to the first non-blank character of the line,\
 or to the beginning of the line if already there.
"""
        text_dialog.TextDialog("Keyboard Shortcuts for text editing", content, "1000x420")

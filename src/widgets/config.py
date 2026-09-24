"""
Configuration constants for HDL-FSM-Editor.
This file contains constants that don't change during runtime.
"""

# Syntax Highlighting Colors
HIGHLIGHT_COLORS = {
    "not_read": "orange",
    "not_written": "red",
    "control": "green4",
    "datatype": "brown",
    "function": "violet",
    "line_number": "red",
    "comment": "blue",
}
HIGHLIGHT_COLORS_DARK_MODE = {
    "not_read": "orange",
    "not_written": "red",
    "control": "green3",
    "datatype": "burlywood1",
    "function": "violet",
    "line_number": "red",
    "comment": "#5BCBFE",
}
BRACKET_HIGHLIGHTING_COLOR_NORMAL_LIST = ["green", "blue", "cyan", "brown"]
BRACKET_HIGHLIGHTING_NAME_NORMAL_LIST = [
    f"bracket_color_{position}{index}"
    for index in range(len(BRACKET_HIGHLIGHTING_COLOR_NORMAL_LIST))
    for position in ("start", "end")
]
BRACKET_HIGHLIGHTING_COLOR_NORMAL_LIST_DARK_MODE = ["green2", "#5BCBFE", "cyan", "orange"]
BRACKET_HIGHLIGHTING_NAME_NORMAL_LIST_DARK_MODE = [
    f"bracket_color_{position}{index}"
    for index in range(len(BRACKET_HIGHLIGHTING_COLOR_NORMAL_LIST_DARK_MODE))
    for position in ("start", "end")
]
BRACKET_HIGHLIGHTING_NAME_BOLD_LIST = [
    "bracket_color_wrong",
]

ELEMENT_NAMES_IN_DESIGN_DICTIONARY = (
    "state",
    "text",
    "line",
    "polygon",
    "rectangle",
    "window_state_action_block",
    "window_state_comment",
    "window_condition_action_block",
    "window_global_actions",
    "window_global_actions_combinatorial",
    "window_state_actions_default",
)

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
    "comment": "blue",
}
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

"""
Handles the global actions window in the diagram.
"""

import tkinter as tk

from actions import canvas_editing, canvas_modify_bindings
from project_manager import project_manager

from .canvas_window import CanvasWindow


class GlobalActionsClocked(CanvasWindow):
    """
    Handles the global actions clocked window in the diagram.
    """

    ref_dict = {}

    def __init__(self, menu_x, menu_y, padding, tags, before, after) -> None:
        entry_dicts = [
            {
                "label_text": "Global actions clocked (executed before running the state machine):",
                "text_type": "action",
                "text": before,
            },
            {
                "label_text": "Global actions clocked (executed after running the state machine):",
                "text_type": "action",
                "text": after,
            },
        ]
        super().__init__(menu_x, menu_y, tags, padding, entry_dicts, additional_move_func=None)

        # Create dictionary for translating the canvas-id of the canvas-window into a reference to this object:
        GlobalActionsClocked.ref_dict[self.window_id] = self

    def delete(self):
        """Remove window, ref_dict entry, and re-enable global_action_clocked button."""
        self._delete_read_and_written_variables()
        project_manager.canvas.delete(self.window_id)
        del GlobalActionsClocked.ref_dict[self.window_id]
        project_manager.global_action_clocked_button.config(state=tk.NORMAL)

    @classmethod
    def create(cls, event) -> None:
        """Create clocked global-actions window at event position."""
        project_manager.global_action_clocked_button.config(state=tk.DISABLED)
        canvas_grid_coordinates_of_the_event = (
            canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        )
        GlobalActionsClocked(
            canvas_grid_coordinates_of_the_event[0],
            canvas_grid_coordinates_of_the_event[1],
            padding=1,
            tags=("global_actions1",),
            before="",
            after="",
        )
        project_manager.undo_handling_ref.design_has_changed()
        canvas_modify_bindings.switch_to_move_mode()

    @classmethod
    def apply_new_font_size(cls) -> None:
        """Apply new font size to all clocked global-actions windows."""
        for global_action_clocked in GlobalActionsClocked.ref_dict.values():
            global_action_clocked.apply_new_font_size_to_canvas_window()

"""
Handles the combinatorial default actions for all states.
"""

import tkinter as tk

from actions import canvas_delete, canvas_editing, canvas_modify_bindings, move_handling_canvas_window
from project_manager import project_manager

from .canvas_window import CanvasWindow


class StateActionsDefault(CanvasWindow):
    """
    Handles the combinatorial default actions for all states.
    """

    ref_dict = {}

    def __init__(
        self,
        coord_x,
        coord_y,
        padding,
        tags,
        action,
        move_handling_class,
        canvas_delete_class,
        zoom_wheel_function,
    ) -> None:
        entry_dicts = [
            {
                "label_text": "Default state actions (combinatorial): ",
                "text_type": "action",
                "text": action,
            }
        ]
        super().__init__(
            coord_x,
            coord_y,
            tags,
            padding,
            move_handling_class,
            canvas_delete_class,
            zoom_wheel_function,
            entry_dicts,
            additional_move_func=None,
        )
        StateActionsDefault.ref_dict[self.window_id] = self

    def delete(self):
        """Remove window, ref_dict entry, and re-enable state_action_default button."""
        self._delete_read_and_written_variables()
        project_manager.canvas.delete(self.window_id)  # delete window
        del StateActionsDefault.ref_dict[self.window_id]
        project_manager.state_action_default_button.config(state=tk.NORMAL)

    @classmethod
    def create(cls, event) -> None:
        """Create state-actions-default window at event position and disable insert button."""
        project_manager.state_action_default_button.config(state=tk.DISABLED)
        canvas_grid_coordinates_of_the_event = (
            canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        )
        StateActionsDefault(
            canvas_grid_coordinates_of_the_event[0],
            canvas_grid_coordinates_of_the_event[1],
            padding=1,
            tags=("state_actions_default",),
            action="",
            move_handling_class=move_handling_canvas_window.MoveHandlingCanvasWindow,
            canvas_delete_class=canvas_delete.CanvasDelete,
            zoom_wheel_function=canvas_editing.zoom_wheel,
        )
        project_manager.undo_handling_ref.design_has_changed()
        canvas_modify_bindings.switch_to_move_mode()

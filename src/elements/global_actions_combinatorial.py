"""
Class for combinatorial actions independent from the state machine
"""

import tkinter as tk

from actions import canvas_delete, canvas_editing, canvas_modify_bindings, move_handling_canvas_window
from project_manager import project_manager

from .canvas_window import CanvasWindow


class GlobalActionsCombinatorial(CanvasWindow):
    """
    Class for combinatorial actions independent from the state machine
    """

    ref_dict = {}

    def __init__(
        self,
        menu_x,
        menu_y,
        padding,
        tags,
        actions,
        move_handling_class,
        canvas_delete_class,
        zoom_wheel_function,
    ) -> None:
        entry_dicts = [
            {
                "label_text": "Global actions combinatorial: ",
                "text_type": "action",
                "text": actions,
            }
        ]
        super().__init__(
            menu_x,
            menu_y,
            tags,
            padding,
            move_handling_class,
            canvas_delete_class,
            zoom_wheel_function,
            entry_dicts,
            additional_move_func=None,
        )
        GlobalActionsCombinatorial.ref_dict[self.window_id] = self

    def delete(self):
        """Remove window, ref_dict entry, and re-enable global_action_combinatorial button."""
        self._delete_read_and_written_variables()
        project_manager.canvas.delete(self.window_id)  # delete window
        del GlobalActionsCombinatorial.ref_dict[self.window_id]
        project_manager.global_action_combinatorial_button.config(state=tk.NORMAL)

    @classmethod
    def create(cls, event) -> None:
        """Create combinatorial global-actions window at event position."""
        project_manager.global_action_combinatorial_button.config(state=tk.DISABLED)
        canvas_grid_coordinates_of_the_event = (
            canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        )
        GlobalActionsCombinatorial(
            canvas_grid_coordinates_of_the_event[0],
            canvas_grid_coordinates_of_the_event[1],
            padding=1,
            tags=("global_actions_combinatorial1",),
            move_handling_class=move_handling_canvas_window.MoveHandlingCanvasWindow,
            canvas_delete_class=canvas_delete.CanvasDelete,
            zoom_wheel_function=canvas_editing.zoom_wheel,
            actions="",
        )
        project_manager.undo_handling_ref.design_has_changed()
        canvas_modify_bindings.switch_to_move_mode()

    @classmethod
    def apply_new_font_size(cls) -> None:
        """Apply new font size to all combinatorial global-actions windows."""
        for global_action_combinatorial in GlobalActionsCombinatorial.ref_dict.values():
            global_action_combinatorial.apply_new_font_size_to_canvas_window()

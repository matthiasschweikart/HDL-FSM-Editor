"""
This class handles the condition&action box which can be activated for each transition.

"""

import tkinter as tk

from actions import canvas_delete, canvas_editing, move_handling_canvas_window
from project_manager import project_manager

from .canvas_window import CanvasWindow


class ConditionAction(CanvasWindow):
    """This class handles the condition&action box which can be activated for each transition."""

    ref_dict = {}
    conditionaction_id = 0

    def __init__(
        self,
        menu_x,
        menu_y,
        connected_to_reset_entry,
        padding,
        tags,
        condition,
        action,
        line_coords,
        line_tags,
        move_handling_class,
        canvas_delete_class,
        zoom_wheel_function,
    ) -> None:
        label_text_for_action = (
            "Transition actions (asynchronous):" if connected_to_reset_entry else "Transition actions (clocked):"
        )
        entry_dicts = [
            {"label_text": "Transition condition: ", "text_type": "condition", "text": condition},
            {"label_text": label_text_for_action, "text_type": "action", "text": action},
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
            additional_move_func=self.move_line,
        )
        self.line_id = project_manager.canvas.create_line(
            menu_x,
            menu_y,
            line_coords[2],
            line_coords[3],
            dash=(2, 2),
            state=tk.HIDDEN,
            tag=line_tags,
        )
        project_manager.canvas.tag_lower(self.line_id)
        # Create dictionary for translating the canvas-id of the canvas-window into a reference to this object:
        ConditionAction.ref_dict[self.window_id] = self
        ConditionAction.conditionaction_id += 1

    def move_line(self, event_x, event_y) -> None:
        """Move the canvas line connecting this condition-action window to the transition."""
        # Move the line which connects the window to the transition:
        line_coords = project_manager.canvas.coords(self.line_id)
        line_coords[0] = event_x
        line_coords[1] = event_y
        project_manager.canvas.coords(self.line_id, line_coords)
        project_manager.canvas.itemconfig(self.line_id, state=tk.NORMAL)

    def hide_line(self) -> None:
        """Hide the canvas line connecting this condition-action window to the transition."""
        project_manager.canvas.itemconfig(self.line_id, state=tk.HIDDEN)

    def delete(self):
        """Remove condition-action window, line, and ref_dict entries; delete linked transition if connector-based."""
        self._delete_read_and_written_variables()
        number = project_manager.canvas.gettags(self.window_id)[0][16:]  # extract <n> from "condition_action<n>"
        project_manager.canvas.delete(self.window_id)
        project_manager.canvas.delete(self.line_id)
        project_manager.canvas.dtag("all", "ca_connection" + number + "_end")
        del ConditionAction.ref_dict[self.window_id]

    def change_descriptor_to(self, text) -> None:
        """Set the action label text (e.g. 'asynchronous' or 'synchronous')."""
        # Used for switching between "asynchronous" and "synchronous" (clocked) transition:
        self.label_ids[1].config(text=text)

    @classmethod
    def create(cls, transition_id, menu_x, menu_y, connected_to_reset_entry):
        """Create a new condition-action window at menu position with connection to the transition."""
        transition_coords = project_manager.canvas.coords(transition_id)
        line_coords = [menu_x, menu_y, transition_coords[0], transition_coords[1]]
        while project_manager.canvas.find_withtag("condition_action" + str(ConditionAction.conditionaction_id)):
            # Increase until an unused number is found.
            # This avoids a number conflict that may happen if the design was created with an old version of HFE.
            ConditionAction.conditionaction_id += 1
        project_manager.canvas.addtag_withtag(
            "ca_connection" + str(ConditionAction.conditionaction_id) + "_end", transition_id
        )
        tags = [
            "condition_action" + str(ConditionAction.conditionaction_id),
            "ca_connection" + str(ConditionAction.conditionaction_id) + "_anchor",
        ]
        if connected_to_reset_entry:
            tags.append("connected_to_reset_transition")
        transition_tags = project_manager.canvas.gettags(transition_id)
        line_tags = [
            "ca_connection" + str(ConditionAction.conditionaction_id),
            "connected_to_" + transition_tags[0],
        ]
        condition_action_ref = ConditionAction(
            menu_x,
            menu_y,
            connected_to_reset_entry,
            padding=1,
            tags=tags,
            condition="",
            action="",
            line_coords=line_coords,
            line_tags=line_tags,
            move_handling_class=move_handling_canvas_window.MoveHandlingCanvasWindow,
            canvas_delete_class=canvas_delete.CanvasDelete,
            zoom_wheel_function=canvas_editing.zoom_wheel,
        )
        condition_action_ref.text_ids[0].focus_set()  # Puts the text input cursor into the text box.

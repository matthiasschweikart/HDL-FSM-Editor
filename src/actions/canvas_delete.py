"""
This class provides all methods needed to delete a Canvas item and
all its connected parts.
Because all connected items must also be deleted, the deletion is not done by
a binding at each canvas item, but by a binding of the key delete at the canvas.
"""

from tkinter import messagebox

from elements import (
    condition_action,
    connector,
    global_actions_clocked,
    global_actions_combinatorial,
    reset_entry,
    state,
    state_action,
    state_actions_default,
    state_comment,
    transition,
)
from project_manager import project_manager


class CanvasDelete:
    """This class provides all methods needed to delete a Canvas item and all its connected parts."""

    canvas_x_coordinate = 0
    canvas_y_coordinate = 0

    def __init__(self):
        self.item_was_deleted = False
        canvas_ids = self._find_canvas_ids_under_cursor()
        # As condition&action windows are placed over transition lines, it is possible
        # that canvas_ids contains both a transition line and a condition&action window.
        # In this case, only the condition&action window must be deleted.
        # Therefore the following loop over canvas_ids is not stopped, when a transition is found:
        canvas_id_to_delete, type_of_item_to_delete, tags_of_item_to_delete = (
            self._determine_id_and_type_and_tags_of_item_to_delete(canvas_ids)
        )
        if canvas_id_to_delete is not None:
            self._dispatch_delete_by_type(canvas_id_to_delete, type_of_item_to_delete, tags_of_item_to_delete)
            # Must be called only once after all involved items have been deleted:
            project_manager.undo_handling_ref.design_has_changed()

    def _find_canvas_ids_under_cursor(self):
        ids = project_manager.canvas.find_overlapping(
            CanvasDelete.canvas_x_coordinate - 2,
            CanvasDelete.canvas_y_coordinate - 2,
            CanvasDelete.canvas_x_coordinate + 2,
            CanvasDelete.canvas_y_coordinate + 2,
        )
        return ids

    def _determine_id_and_type_and_tags_of_item_to_delete(self, canvas_ids):
        canvas_id_to_delete = None
        type_of_item_to_delete = None
        tags_of_item_to_delete = None
        for canvas_id in canvas_ids:
            type_of_item = project_manager.canvas.type(canvas_id)
            tags_of_item = project_manager.canvas.gettags(canvas_id)
            if type_of_item == "line":
                for tag in tags_of_item:
                    if tag.startswith("transition"):  # a line can also be a grid-line or a anchor-line.
                        canvas_id_to_delete = canvas_id
                        type_of_item_to_delete = type_of_item
                        tags_of_item_to_delete = tags_of_item
                        # No return here, as a condition&action window can be on top of the transition line.
            elif type_of_item == "rectangle":
                for tag in tags_of_item:
                    if tag.startswith("connector"):  # a rectangle can also be a not removable priority rectangle.
                        return canvas_id, type_of_item, tags_of_item
            elif type_of_item in ["oval", "polygon", "window"]:
                return canvas_id, type_of_item, tags_of_item
        return canvas_id_to_delete, type_of_item_to_delete, tags_of_item_to_delete

    def _dispatch_delete_by_type(self, canvas_id, item_type, tags):
        if item_type == "polygon":
            reset_entry.ResetEntry.delete()
        elif item_type == "window":
            self._delete_window_item(canvas_id, tags)
        elif item_type == "oval":
            state.States.ref_dict[canvas_id].delete()
        elif item_type == "rectangle":
            connector.ConnectorInstance.ref_dict[canvas_id].delete()
        elif item_type == "line":
            transition.TransitionLine.ref_dict[canvas_id].delete()
        elif item_type == "text":  # Text of reset entry
            pass
        else:
            messagebox.showerror(
                "Delete",
                "Fatal, cannot delete canvas_type "
                + str(project_manager.canvas.type(canvas_id))
                + " with tags "
                + str(project_manager.canvas.gettags(canvas_id)),
            )

    def _delete_window_item(self, canvas_id, tags):
        for tag in tags:
            if tag.startswith("state_actions_default"):
                state_actions_default.StateActionsDefault.ref_dict[canvas_id].delete()
                return
            if tag == "global_actions1":
                global_actions_clocked.GlobalActionsClocked.ref_dict[canvas_id].delete()
                return
            if tag == "global_actions_combinatorial1":
                global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict[canvas_id].delete()
                return
            if tag.startswith("state_action"):
                state_action.StateAction.ref_dict[canvas_id].delete()
                return
            if tag.endswith("_comment"):
                state_comment.StateComment.ref_dict[canvas_id].delete()
                return
            if tag.startswith("condition_action"):
                condition_action.ConditionAction.ref_dict[canvas_id].delete()
                return

    @classmethod
    def store_mouse_position(cls, event) -> None:
        """Store canvas coordinates of the mouse from the given event."""
        cls.canvas_x_coordinate = project_manager.canvas.canvasx(event.x)
        cls.canvas_y_coordinate = project_manager.canvas.canvasy(event.y)

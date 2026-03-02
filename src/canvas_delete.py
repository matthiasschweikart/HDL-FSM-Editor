"""
This class provides all methods needed to delete a Canvas item and
all its connected parts.
"""

from tkinter import messagebox

import undo_handling
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
        ids = self._find_items_to_delete()
        for canvas_id in ids:
            self._delete_item(canvas_id)
        if self.item_was_deleted:
            # Must be called only after all involved items have been completely deleted:
            undo_handling.design_has_changed()

    def _find_items_to_delete(self):
        ids = project_manager.canvas.find_overlapping(
            CanvasDelete.canvas_x_coordinate - 2,
            CanvasDelete.canvas_y_coordinate - 2,
            CanvasDelete.canvas_x_coordinate + 2,
            CanvasDelete.canvas_y_coordinate + 2,
        )
        return ids

    def _delete_item(self, canvas_id):
        item_type = project_manager.canvas.type(canvas_id)
        if item_type is None:
            # This item i is a member of the list stored in ids but was already deleted,
            # when one of the items earlier in the list was deleted.
            return
        tags_of_item_i = project_manager.canvas.gettags(canvas_id)
        if self._item_is_a_not_deletable_object(tags_of_item_i):
            return
        self.item_was_deleted = True
        self._dispatch_delete_by_type(item_type, canvas_id, tags_of_item_i)

    def _dispatch_delete_by_type(self, item_type, canvas_id, tags):
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

    def _item_is_a_not_deletable_object(self, tags_of_item_i) -> bool:
        for single_tag in tags_of_item_i:
            if (
                single_tag == "grid_line"
                or single_tag.endswith("_comment_line")  # line to state-comment
                or single_tag.endswith("rectangle")  # transition priority rectangle
                or single_tag.endswith("priority")  # transition priority value
                or single_tag.startswith("connected_to_state")  # line to state-comment
            ):
                return True
        return False

    @classmethod
    def store_mouse_position(cls, event) -> None:
        """Store canvas coordinates of the mouse from the given event."""
        cls.canvas_x_coordinate = project_manager.canvas.canvasx(event.x)
        cls.canvas_y_coordinate = project_manager.canvas.canvasy(event.y)

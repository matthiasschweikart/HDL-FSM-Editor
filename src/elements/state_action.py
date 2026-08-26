"""
Handles the state action of all states.
"""

from actions import canvas_delete, canvas_editing, move_handling_canvas_window
from project_manager import project_manager

from .canvas_window import CanvasWindow


class StateAction(CanvasWindow):
    """Implements the state action of a single state."""

    state_action_id = 0
    ref_dict = {}

    def __init__(
        self,
        coord_x,
        coord_y,
        padding,
        tags,
        line_coords,
        line_tags,
        action,
        move_handling_class,
        canvas_delete_class,
        zoom_wheel_function,
    ) -> None:
        entry_dicts = [
            {
                "label_text": "State actions (combinatorial): ",
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
        StateAction.state_action_id += 1
        StateAction.ref_dict[self.window_id] = self
        self.line_id = project_manager.canvas.create_line(line_coords, dash=(2, 2), tags=line_tags)
        project_manager.canvas.tag_lower(self.line_id)

    def delete(self):
        """Remove state-action window, connection line, tags, and ref_dict entry."""
        self._delete_read_and_written_variables()
        state_number = project_manager.canvas.gettags(self.window_id)[0][12:]  # remove "state_action"
        project_manager.canvas.delete(self.line_id)  # delete connection line
        project_manager.canvas.delete(self.window_id)  # delete state action window
        project_manager.canvas.dtag("all", "connection" + state_number + "_end")  # delete tag "connection<n>_end".
        del StateAction.ref_dict[self.window_id]

    @classmethod
    def create(cls, menu_x, menu_y, state_id) -> None:
        """Create a new state-action window at menu position with connection to the state."""
        project_manager.canvas.addtag_withtag("connection" + str(cls.state_action_id) + "_end", state_id)
        while project_manager.canvas.find_withtag("state_action" + str(cls.state_action_id)):
            # Increase until an unused number is found.
            # This number conflict may happen, if the design was created with an old version of HFE.
            cls.state_action_id += 1
        line_tags = (
            "connection" + str(cls.state_action_id),
            "connected_to_" + project_manager.canvas.gettags(state_id)[0],
        )
        state_action_tags = (
            "state_action" + str(cls.state_action_id),
            "connection" + str(cls.state_action_id) + "_start",
        )
        coords = project_manager.canvas.coords(state_id)
        middle_x = (coords[0] + coords[2]) / 2
        middle_y = (coords[1] + coords[3]) / 2
        line_coords = [menu_x + 100, menu_y, middle_x, middle_y]
        StateAction(
            menu_x + 100,
            menu_y,
            padding=1,
            tags=state_action_tags,
            line_coords=line_coords,
            line_tags=line_tags,
            action="",
            move_handling_class=move_handling_canvas_window.MoveHandlingCanvasWindow,
            canvas_delete_class=canvas_delete.CanvasDelete,
            zoom_wheel_function=canvas_editing.zoom_wheel,
        )

    @classmethod
    def apply_new_font_size(cls) -> None:
        """Apply new font size to all state-action windows."""
        for state_action in StateAction.ref_dict.values():
            state_action.apply_new_font_size_to_canvas_window()

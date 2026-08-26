"""
This class handles "state-comments".
"""

from actions import canvas_delete, canvas_editing, move_handling_canvas_window
from elements.canvas_window import CanvasWindow
from project_manager import project_manager


class StateComment(CanvasWindow):
    """
    This class handles "state-comments".
    """

    ref_dict = {}

    def __init__(
        self,
        coord_x,
        coord_y,
        padding,
        tags,
        line_coords,
        comment,
        move_handling_class,
        canvas_delete_class,
        zoom_wheel_function,
    ) -> None:
        entry_dicts = [
            {
                "label_text": "State-Comment: ",
                "text_type": "comment",
                "text": comment,
            }
        ]
        super().__init__(
            coord_x + 100,
            coord_y,
            tags,
            padding,
            move_handling_class,
            canvas_delete_class,
            zoom_wheel_function,
            entry_dicts,
            additional_move_func=None,
        )
        StateComment.ref_dict[self.window_id] = self  # Store the object-reference with the Canvas-id as key.
        self.text_ids[0].config(fg="blue")
        # Line starts at comment, ends at state:
        self.line_id = project_manager.canvas.create_line(line_coords, tags=tags[0] + "_line", dash=(2, 2))
        project_manager.canvas.tag_lower(self.line_id)  # Lines are always "under" anything else.

    def delete(self):
        """Remove state-comment window, line, dtag, and ref_dict entry."""
        comment_number = project_manager.canvas.gettags(self.window_id)[0][5:-8]  # remove "state" and "_comment"
        project_manager.canvas.delete(self.window_id)
        project_manager.canvas.delete(self.line_id)
        project_manager.canvas.dtag("all", "state" + comment_number + "_comment_line_end")
        del StateComment.ref_dict[self.window_id]

    @classmethod
    def create(cls, menu_x, menu_y, tags) -> None:
        """Create a new state-comment window at menu position with connection to the state."""
        for tag in tags:
            if tag.startswith("state"):
                state_coords = project_manager.canvas.coords(tag)
                project_manager.canvas.addtag_withtag(tag + "_comment_line_end", tag)
                StateComment(
                    menu_x,
                    menu_y,
                    padding=1,
                    tags=[tag + "_comment", tag + "_comment_line_start"],
                    line_coords=[
                        menu_x + 100,
                        menu_y,
                        (state_coords[2] + state_coords[0]) / 2,
                        (state_coords[3] + state_coords[1]) / 2,
                    ],
                    comment="",
                    move_handling_class=move_handling_canvas_window.MoveHandlingCanvasWindow,
                    canvas_delete_class=canvas_delete.CanvasDelete,
                    zoom_wheel_function=canvas_editing.zoom_wheel,
                )

    @classmethod
    def apply_new_font_size(cls) -> None:
        """Apply new font size to all state-comment windows."""
        for state_comment in StateComment.ref_dict.values():
            state_comment.apply_new_font_size_to_canvas_window()

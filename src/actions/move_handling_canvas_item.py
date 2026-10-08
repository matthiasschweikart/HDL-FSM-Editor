"""
This module handles the movement of states, connectors at the Canvas.
"""

from actions import move_handling, move_handling_finish, move_handling_initialization
from project_manager import project_manager


class MoveHandlingCanvasItem:
    """
    When a state is moved at the Canvas, a MoveHandlingCanvasItem object is created and handles the movement.
    """

    transition_insertion_runs = False
    move_handling_canvas_item_is_active = False

    def __init__(self, event, canvas_id):
        if (
            MoveHandlingCanvasItem.move_handling_canvas_item_is_active
            or MoveHandlingCanvasItem.transition_insertion_runs
        ):
            return  # Button-1 shall now not move any canvas item

        MoveHandlingCanvasItem.move_handling_canvas_item_is_active = True
        self.canvas_id = canvas_id
        self.move_list, self.coords_before_move = move_handling_initialization.create_move_list_and_extend_transitions(
            self.canvas_id
        )

        # This first move does not move the object.
        # It is needed to define difference_x, difference_y of the used move_to method.
        # The values are set to 0 when the state is picked up in the middle:
        move_handling.move_to_coordinates(event.x, event.y, self.move_list, first=True, move_to_grid=False)

        # Create a binding for the now following movements of the mouse and for finishing the moving:
        self.funcid_motion = project_manager.canvas.tag_bind(self.canvas_id, "<Motion>", self._motion)
        self.funcid_release = project_manager.canvas.tag_bind(self.canvas_id, "<ButtonRelease-1>", self._release)

    def _motion(self, motion_event):
        move_handling.move_to_coordinates(
            motion_event.x,
            motion_event.y,
            self.move_list,
            first=False,
            move_to_grid=False,
        )

    def _release(self, release_event):
        project_manager.canvas.tag_unbind(self.canvas_id, "<Motion>", self.funcid_motion)
        project_manager.canvas.tag_unbind(self.canvas_id, "<ButtonRelease-1>", self.funcid_release)
        move_handling.move_to_coordinates(
            release_event.x,
            release_event.y,
            self.move_list,
            first=False,
            move_to_grid=True,
        )
        move_handling_finish.move_finish_for_transitions(self.move_list)
        MoveHandlingCanvasItem.move_handling_canvas_item_is_active = False
        coords_after_move = project_manager.canvas.coords(self.canvas_id)
        for index, coord_after_move in enumerate(coords_after_move):
            if abs(coord_after_move - self.coords_before_move[index]) > project_manager.state_radius / 2:
                project_manager.undo_handling_ref.design_has_changed()
                return

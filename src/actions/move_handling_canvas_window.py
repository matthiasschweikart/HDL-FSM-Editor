"""
A MoveCanvasWindow object is created, when the user moves a Canvas window object.
"""

from actions import move_handling, move_handling_finish, move_handling_initialization
from project_manager import project_manager


class MoveHandlingCanvasWindow:
    """Handles dragging of a canvas window when the user moves it."""

    def __init__(self, event, widget, window_id):
        self.move_active = True
        self.widget = widget
        self.window_id = window_id
        window_coords = project_manager.canvas.coords(self.window_id)
        self.move_list = move_handling_initialization.create_move_list(
            [self.window_id], window_coords[0], window_coords[1]
        )
        self.touching_point_x = event.x
        self.touching_point_y = event.y

        # This first move does not move the object.
        # It is needed to set self.difference_x, self.difference_y of the moved window to 0.
        # Both values are used, when the window is picked up at its border.
        # The values are set to 0 by using window_coords[0] and window_coords[1] as event coords:
        move_handling.move_to_coordinates(
            window_coords[0],
            window_coords[1],
            self.move_list,
            first=True,
            move_to_grid=False,
        )

        # Create a binding for the now following movements of the mouse and for finishing the moving:
        self.funcid_motion = self.widget.bind("<Motion>", self._motion)
        self.funcid_release = self.widget.bind("<ButtonRelease-1>", self._release)

    def _motion(self, motion_event):
        # At slow systems, tkinter needs some time to rearrange the canvas items before
        # it is able to give correct coords at events inside the Canvas window item.
        # So first do not listen to events anymore:
        self.widget.unbind("<Motion>", self.funcid_motion)
        self.funcid_motion = None
        if not self.move_active:
            # The release event did already happen:
            return
        delta_x = motion_event.x - self.touching_point_x
        delta_y = motion_event.y - self.touching_point_y
        window_coords = project_manager.canvas.coords(self.window_id)
        move_handling.move_to_coordinates(
            window_coords[0] + delta_x,
            window_coords[1] + delta_y,
            self.move_list,
            first=False,
            move_to_grid=False,
        )
        # Later on, listen to events again:
        project_manager.root.after(50, self._bind_motion_again)
        # project_manager.root.after_idle(self._bind_motion_again)

    def _bind_motion_again(self):
        self.funcid_motion = self.widget.bind("<Motion>", self._motion)

    def _release(self, _):
        self.move_active = False
        if self.funcid_motion is not None:
            self.widget.unbind("<Motion>", self.funcid_motion)
            self.funcid_motion = None
        if self.funcid_release is not None:
            self.widget.unbind("<ButtonRelease-1>", self.funcid_release)
            self.funcid_release = None
        window_coords = project_manager.canvas.coords(self.window_id)
        move_handling.move_to_coordinates(
            window_coords[0],
            window_coords[1],
            self.move_list,
            first=False,
            move_to_grid=False,  # Only used by the line to a window.
        )
        move_handling_finish.move_finish_for_transitions(self.move_list)
        project_manager.undo_handling_ref.design_has_changed()

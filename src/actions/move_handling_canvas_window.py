"""
A MoveCanvasWindow object is created, when the user moves a Canvas window object.
"""

from actions import move_handling, move_handling_canvas_item, move_handling_finish, move_handling_initialization
from project_manager import project_manager


class MoveHandlingCanvasWindow:
    """Handles dragging of a canvas window when the user moves it."""

    def __init__(self, event, widget, window_id):
        if move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs:
            return  # Button-1 shall now not move any canvas item
        self.move_active = True
        self.widget = widget  # This is a reference to the Frame or to a Label of the canvas_window object.
        self.window_id = window_id
        self.move_list, self.window_coords_before_move = (
            move_handling_initialization.create_move_list_and_extend_transitions(self.window_id)
        )
        self.touching_point_x = event.x
        self.touching_point_y = event.y

        # The first move does not move the object.
        # It is needed to define difference_x, difference_y of the used move_to method.
        # The coordinates are converted from canvas to screen coordinates in order to avoid any confusion,
        # as move_to_coordinates works with screen coordinates.
        # But using canvas coordinates would not make any difference, as difference_x/y are based on deltas.
        # The values of difference_x/y should calculate to 0, as the differences are build between the
        # position determined here and the position calculated in the used move_to method.
        # But they are not exactly 0, because of the conversion between the coordinate systems.
        window_coords_screen_before_move = self._canvas_to_screen(self.window_coords_before_move)
        move_handling.move_to_coordinates(
            window_coords_screen_before_move[0],
            window_coords_screen_before_move[1],
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
        # Determine the change in mouse position compared to the initial touching point.
        delta_x = motion_event.x - self.touching_point_x
        delta_y = motion_event.y - self.touching_point_y
        # Move the window by the delta values, which moves the touching point under the actual mouse pointer again:
        window_coords = self._canvas_to_screen(project_manager.canvas.coords(self.window_id))
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
        window_coords = self._canvas_to_screen(project_manager.canvas.coords(self.window_id))
        move_handling.move_to_coordinates(
            window_coords[0],
            window_coords[1],
            self.move_list,
            first=False,
            move_to_grid=False,  # Only used by the line to a window.
        )
        move_handling_finish.move_finish_for_transitions(self.move_list)
        project_manager.undo_handling_ref.design_has_changed()

    def _canvas_to_screen(self, coords):
        canvas_lu_x = project_manager.canvas.canvasx(0)
        canvas_lu_y = project_manager.canvas.canvasy(0)
        x_screen = coords[0] - canvas_lu_x
        y_screen = coords[1] - canvas_lu_y
        return x_screen, y_screen

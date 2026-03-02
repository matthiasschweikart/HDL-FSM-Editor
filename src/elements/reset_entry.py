"""Creates the Reset-Entry element in the canvas."""

import tkinter as tk

import canvas_editing
import canvas_modify_bindings
import undo_handling
from elements import transition
from project_manager import project_manager


class ResetEntry:
    """
    Creates the Reset-Entry element in the canvas.

    As only 1 Reset-Entry is allowed in a diagram, no element dictionary (as used for all other elements) is necessary.
    For the same reason only a class method is used for moving the Reset-Entry polygon.

    Class variables:
        difference_x: Difference in x direction between mouse pointer and Reset-Entry polygon at move start.
        difference_y: Difference in y direction between mouse pointer and Reset-Entry polygon at move start.
    """

    difference_x = 0
    difference_y = 0

    def __init__(self, reset_entry_polygon_coords, tags) -> None:
        polygon_id = project_manager.canvas.create_polygon(
            *reset_entry_polygon_coords, fill="red", outline="orange", tags=tags
        )
        project_manager.canvas.tag_bind(
            polygon_id, "<Enter>", lambda event, id=polygon_id: project_manager.canvas.itemconfig(id, width=2)
        )
        project_manager.canvas.tag_bind(
            polygon_id, "<Leave>", lambda event, id=polygon_id: project_manager.canvas.itemconfig(id, width=1)
        )
        project_manager.canvas.create_text(
            reset_entry_polygon_coords[4] - 4 * project_manager.reset_entry_size / 5,
            reset_entry_polygon_coords[5],
            text="Reset",
            tag="reset_text",
            font=project_manager.state_name_font,
        )

    @classmethod
    def delete(cls):
        """Delete reset entry polygon/text and any transition starting from it; clear ref_dict."""
        reset_entry_tags = project_manager.canvas.gettags("reset_entry")
        for reset_entry_tag in reset_entry_tags:
            if reset_entry_tag.startswith("transition") and reset_entry_tag.endswith("_start"):
                canvas_id = project_manager.canvas.find_withtag(reset_entry_tag[:-6])[0]
                transition.TransitionLine.ref_dict[canvas_id].delete()
        project_manager.canvas.delete("reset_entry")
        project_manager.canvas.delete("reset_text")

    @classmethod
    def move_to(cls, event_x, event_y, polygon_id, first, last) -> None:
        """Reposition reset-entry polygon and text; snap to grid when last is True."""
        if first is True:
            # Calculate the difference between the "anchor" point and the event:
            coords = project_manager.canvas.coords(polygon_id)
            middle_point = [coords[4], coords[5]]
            cls.difference_x, cls.difference_y = -event_x + middle_point[0], -event_y + middle_point[1]
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + cls.difference_x, event_y + cls.difference_y
        if last is True:
            event_x = project_manager.state_radius * round(event_x / project_manager.state_radius)
            event_y = project_manager.state_radius * round(event_y / project_manager.state_radius)
        width = cls._determine_width_of_the_polygon(polygon_id)
        height = cls._determine_height_of_the_polygon(polygon_id)
        new_upper_left_corner = cls._calculate_new_upper_left_corner_of_the_polygon(event_x, event_y, width, height)
        new_upper_right_corner = cls._calculate_new_upper_right_corner_of_the_polygon(event_x, event_y, width, height)
        new_point_right_corner = [event_x, event_y]
        new_lower_right_corner = cls._calculate_new_lower_right_corner_of_the_polygon(event_x, event_y, width, height)
        new_lower_left_corner = cls._calculate_new_lower_left_corner_of_the_polygon(event_x, event_y, width, height)
        new_coords = [
            *new_upper_left_corner,
            *new_upper_right_corner,
            *new_point_right_corner,
            *new_lower_right_corner,
            *new_lower_left_corner,
        ]
        new_center = cls._calculate_new_center_of_the_polygon(event_x, event_y, width)
        cls._move_polygon_in_canvas(polygon_id, new_coords, new_center)

    @classmethod
    def _determine_width_of_the_polygon(cls, polygon_id):
        polygon_coords = project_manager.canvas.coords(polygon_id)
        return polygon_coords[2] - polygon_coords[0]

    @classmethod
    def _determine_height_of_the_polygon(cls, polygon_id):
        polygon_coords = project_manager.canvas.coords(polygon_id)
        return polygon_coords[9] - polygon_coords[1]

    @classmethod
    def _calculate_new_upper_left_corner_of_the_polygon(cls, event_x, event_y, width, height) -> list:
        return [event_x - 13 * width / 10, event_y - height / 2]

    @classmethod
    def _calculate_new_upper_right_corner_of_the_polygon(cls, event_x, event_y, width, height) -> list:
        return [event_x - 3 * width / 10, event_y - height / 2]

    @classmethod
    def _calculate_new_lower_right_corner_of_the_polygon(cls, event_x, event_y, width, height) -> list:
        return [event_x - 3 * width / 10, event_y + height / 2]

    @classmethod
    def _calculate_new_lower_left_corner_of_the_polygon(cls, event_x, event_y, width, height) -> list:
        return [event_x - 13 * width / 10, event_y + height / 2]

    @classmethod
    def _calculate_new_center_of_the_polygon(cls, event_x, event_y, width) -> list:
        return [event_x - 4 * width / 5, event_y]

    @classmethod
    def _move_polygon_in_canvas(cls, polygon_id, new_coords, new_center) -> None:
        project_manager.canvas.coords(polygon_id, *new_coords)
        project_manager.canvas.coords("reset_text", *new_center)

    @classmethod
    def insert_reset_entry(cls, event) -> None:
        """Create reset entry at event position."""
        project_manager.reset_entry_button.config(state=tk.DISABLED)
        canvas_grid_coordinates_of_the_event = (
            canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
        )
        reset_entry_polygon_coords = cls._create_polygon_shape_for_reset_entry()
        reset_entry_polygon_coords = cls._move_reset_entry_polygon_to_event(
            canvas_grid_coordinates_of_the_event, reset_entry_polygon_coords
        )
        cls(reset_entry_polygon_coords, tags=("reset_entry",))
        undo_handling.design_has_changed()
        canvas_modify_bindings.switch_to_move_mode()

    @classmethod
    def _create_polygon_shape_for_reset_entry(cls) -> list:
        # upper_left_corner  = [-20,-12]
        # upper_right_corner = [+20,-12]
        # point_corner       = [+32, 0]   connect-point for transition
        # lower_right_corner = [+20,+12]
        # lower_left_corner  = [-20,+12]
        size = project_manager.reset_entry_size
        # Coordinates when the mouse-pointer is at point_corner of the polygon:
        upper_left_corner = [-size / 2 - 4 * size / 5, -3 * size / 10]
        upper_right_corner = [+size / 2 - 4 * size / 5, -3 * size / 10]
        point_corner = [0, 0]
        lower_right_corner = [+size / 2 - 4 * size / 5, +3 * size / 10]
        lower_left_corner = [-size / 2 - 4 * size / 5, +3 * size / 10]
        coords = []
        coords.extend(upper_left_corner)
        coords.extend(upper_right_corner)
        coords.extend(point_corner)
        coords.extend(lower_right_corner)
        coords.extend(lower_left_corner)
        return coords

    @classmethod
    def _move_reset_entry_polygon_to_event(cls, canvas_grid_coordinates_of_the_event, reset_entry_polygon):
        reset_entry_polygon = [
            p + canvas_grid_coordinates_of_the_event[0] if i % 2 == 0 else p + canvas_grid_coordinates_of_the_event[1]
            for i, p in enumerate(reset_entry_polygon)
        ]
        return reset_entry_polygon

"""
Module handling connectors on the canvas.
"""

import canvas_editing
import constants
import undo_handling
from elements import transition
from project_manager import project_manager


class ConnectorInstance:
    """
    For each connector on the canvas a ConnectorInstance object is created.
    """

    connector_number = 0
    difference_x = 0
    difference_y = 0
    ref_dict = {}

    def __init__(self, coords, tags):
        self.connector_id = project_manager.canvas.create_rectangle(coords, fill=constants.CONNECTOR_COLOR, tags=tags)
        project_manager.canvas.tag_bind(
            self.connector_id,
            "<Enter>",
            lambda event: project_manager.canvas.itemconfig(self.connector_id, width=2),
        )
        project_manager.canvas.tag_bind(
            self.connector_id,
            "<Leave>",
            lambda event: project_manager.canvas.itemconfig(self.connector_id, width=1),
        )
        ConnectorInstance.ref_dict[self.connector_id] = self

    def delete(self):
        """Remove connector from canvas and delete any transition it started or ended; update ref_dict."""
        connector_tags = project_manager.canvas.gettags(self.connector_id)
        project_manager.canvas.delete(self.connector_id)
        for connector_tag in connector_tags:
            if connector_tag.startswith("transition") and connector_tag.endswith("_start"):
                canvas_ids = project_manager.canvas.find_withtag(connector_tag[:-6])
                if canvas_ids:
                    transition.TransitionLine.ref_dict[canvas_ids[0]].delete()
            elif connector_tag.startswith("transition") and connector_tag.endswith("_end"):
                canvas_ids = project_manager.canvas.find_withtag(connector_tag[:-4])
                if canvas_ids:
                    transition.TransitionLine.ref_dict[canvas_ids[0]].delete()
        del ConnectorInstance.ref_dict[self.connector_id]

    @classmethod
    def create_connector(cls, event) -> None:
        """Create a new connector at event position if no other item overlaps; mark design changed."""
        # Translate the window coordinate into the canvas coordinate (the Canvas is bigger than the window):
        event_x, event_y = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
        overlapping_items = project_manager.canvas.find_overlapping(
            event_x - project_manager.state_radius / 2,
            event_y - project_manager.state_radius / 2,
            event_x + project_manager.state_radius / 2,
            event_y + project_manager.state_radius / 2,
        )
        for overlapping_item in overlapping_items:
            if "grid_line" not in project_manager.canvas.gettags(overlapping_item):
                # Another item (different from a grid-line) is already at this position.
                return
        ConnectorInstance.connector_number += 1
        tag = "connector" + str(ConnectorInstance.connector_number)
        coords = (
            event_x - project_manager.state_radius / 4,
            event_y - project_manager.state_radius / 4,
            event_x + project_manager.state_radius / 4,
            event_y + project_manager.state_radius / 4,
        )
        ConnectorInstance(coords, tag)
        undo_handling.design_has_changed()

    @classmethod
    def move_to(cls, event_x, event_y, rectangle_id, first, last) -> None:
        """Move connector rectangle to (event_x, event_y);
        Updates the move offset when first is True."""
        # global difference_x, difference_y
        if first is True:
            # Calculate the difference between the "anchor" point and the event:
            coords = project_manager.canvas.coords(rectangle_id)
            middle_point = ConnectorInstance._calculate_middle_point(coords)
            cls.difference_x, cls.difference_y = -event_x + middle_point[0], -event_y + middle_point[1]
        # Keep the distance between event and anchor point constant (important for moving with connected transitions):
        event_x, event_y = event_x + cls.difference_x, event_y + cls.difference_y
        if last is True:
            event_x = project_manager.state_radius * round(event_x / project_manager.state_radius)
            event_y = project_manager.state_radius * round(event_y / project_manager.state_radius)
        edge_length = ConnectorInstance._determine_edge_length_of_the_rectangle(rectangle_id)
        new_upper_left_corner = ConnectorInstance._calculate_new_upper_left_corner_of_the_rectangle(
            event_x, event_y, edge_length
        )
        new_lower_right_corner = ConnectorInstance._calculate_new_lower_right_corner_of_the_rectangle(
            event_x, event_y, edge_length
        )
        project_manager.canvas.coords(rectangle_id, *new_upper_left_corner, *new_lower_right_corner)

    @classmethod
    def _calculate_middle_point(cls, coords) -> list:
        middle_x = (coords[0] + coords[2]) / 2
        middle_y = (coords[1] + coords[3]) / 2
        return [middle_x, middle_y]

    @classmethod
    def _determine_edge_length_of_the_rectangle(cls, rectangle_id):
        rectangle_coords = project_manager.canvas.coords(rectangle_id)
        edge_length = rectangle_coords[2] - rectangle_coords[0]
        return edge_length

    @classmethod
    def _calculate_new_upper_left_corner_of_the_rectangle(cls, event_x, event_y, edge_length) -> list:
        return [event_x - edge_length / 2, event_y - edge_length / 2]

    @classmethod
    def _calculate_new_lower_right_corner_of_the_rectangle(cls, event_x, event_y, edge_length) -> list:
        return [event_x + edge_length / 2, event_y + edge_length / 2]

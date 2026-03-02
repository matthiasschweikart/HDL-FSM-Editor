"""
This module contains a method to decide which graphical object must be moved.
"""

import canvas_editing
import constants
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


def move_do(event, move_list, first, move_to_grid=False) -> None:
    """Move all items in move_list to the event's canvas coordinates."""
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    move_to_coordinates(event_x, event_y, move_list, first, move_to_grid)


def move_to_coordinates(event_x, event_y, move_list, first, move_to_grid):
    """Apply move to (event_x, event_y) for each item in move_list; respect grid and proximity checks."""
    if _connector_moved_too_close_to_other_object(move_list, event_x, event_y):
        return
    for entry in move_list:
        item_id = entry[0]
        item_point_to_move = entry[1]
        item_type = project_manager.canvas.type(item_id)
        if item_type == "oval":
            state.States.move_to(event_x, event_y, item_id, first, move_to_grid)
        elif item_type == "polygon":
            reset_entry.ResetEntry.move_to(event_x, event_y, item_id, first, move_to_grid)
        elif item_type == "line":
            tags = project_manager.canvas.gettags(item_id)
            if tags[0].startswith("transition"):
                transition.TransitionLine.move_to(
                    event_x, event_y, item_id, item_point_to_move, first, move_list, move_to_grid
                )
            elif (
                tags[0].endswith("comment_line") and item_point_to_move == "end"
            ):  # state is moved and state_comment line must follow
                tag_of_comment_window = tags[0][:-5]  # tag[0] = state<number>_comment_line
                canvas_id_of_comment_window = project_manager.canvas.find_withtag(tag_of_comment_window)[0]
                ref = state_comment.StateComment.ref_dict[canvas_id_of_comment_window]
                ref.move_line_point_to(event_x, event_y, first)
            elif (
                tags[0].startswith("connection") and item_point_to_move == "end"
            ):  # state is moved and state action line must follow
                tag_of_connected_state_action = "state_action" + tags[0][10:]  # connection<n>
                canvas_id_of_connected_state_action = project_manager.canvas.find_withtag(
                    tag_of_connected_state_action
                )[0]
                ref = state_action.StateAction.ref_dict[canvas_id_of_connected_state_action]
                ref.move_line_point_to(event_x, event_y, first)
        elif item_type == "rectangle":
            connector.ConnectorInstance.move_to(event_x, event_y, item_id, first, move_to_grid)
        elif item_type == "window":
            if item_id in state_action.StateAction.ref_dict:
                ref = state_action.StateAction.ref_dict[item_id]
            elif item_id in state_comment.StateComment.ref_dict:
                ref = state_comment.StateComment.ref_dict[item_id]
            elif item_id in state_actions_default.StateActionsDefault.ref_dict:
                ref = state_actions_default.StateActionsDefault.ref_dict[item_id]
            elif item_id in global_actions_clocked.GlobalActionsClocked.ref_dict:
                ref = global_actions_clocked.GlobalActionsClocked.ref_dict[item_id]
            elif item_id in global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict:
                ref = global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict[item_id]
            else:
                ref = condition_action.ConditionAction.ref_dict[item_id]
            ref.move_to(event_x, event_y, first)
        else:
            print("move: Fatal, unknown canvas type", "|" + item_type + "|")


def _connector_moved_too_close_to_other_object(move_list, event_x, event_y) -> bool:
    for entry in move_list:
        moved_item_id = entry[0]
        if (
            project_manager.canvas.type(moved_item_id) == "rectangle"
            and project_manager.canvas.itemcget(moved_item_id, "fill") == constants.CONNECTOR_COLOR
        ):
            # Keep the distance between event and anchor point constant:
            event_x_mod, event_y_mod = (
                event_x + connector.ConnectorInstance.difference_x,
                event_y + connector.ConnectorInstance.difference_y,
            )
            event_x_mod = project_manager.state_radius * round(
                event_x_mod / project_manager.state_radius
            )  # move event_x to grid.
            event_y_mod = project_manager.state_radius * round(
                event_y_mod / project_manager.state_radius
            )  # move event_y to grid.
            connector_coords = project_manager.canvas.coords(moved_item_id)
            edge_length = connector_coords[2] - connector_coords[0]
            new_upper_left_corner = [event_x_mod - edge_length / 2, event_y_mod - edge_length / 2]
            new_lower_right_corner = [event_x_mod + edge_length / 2, event_y_mod + edge_length / 2]
            moved_connector_coords = [*new_upper_left_corner, *new_lower_right_corner]
            overlapping_list = project_manager.canvas.find_overlapping(
                moved_connector_coords[0] - project_manager.state_radius / 2,
                moved_connector_coords[1] - project_manager.state_radius / 2,
                moved_connector_coords[2] + project_manager.state_radius / 2,
                moved_connector_coords[3] + project_manager.state_radius / 2,
            )
            for overlapping_item in overlapping_list:
                if overlapping_item != moved_item_id and (
                    project_manager.canvas.type(overlapping_item) == "oval"
                    or (
                        project_manager.canvas.type(overlapping_item) == "rectangle"
                        and project_manager.canvas.itemcget(overlapping_item, "fill") == constants.CONNECTOR_COLOR
                    )
                ):
                    return True
    return False

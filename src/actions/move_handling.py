"""
This module contains a method to decide which graphical object must be moved.
"""

import constants
from actions import canvas_editing
from project_manager import project_manager


def move_do(event, move_list, first, move_to_grid=False) -> None:
    """Move all items in move_list to the event's canvas coordinates."""
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    move_to_coordinates(event_x, event_y, move_list, first, move_to_grid)


def move_to_coordinates(event_x, event_y, move_list, first, move_to_grid):
    """Apply move to (event_x, event_y) for each item in move_list; respect grid and proximity checks."""
    from elements import connector, reset_entry, state, transition

    if _object_is_moved_too_close_to_state_or_connector(move_list, event_x, event_y):
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
            elif tags[0].endswith("comment_line"):
                transition.TransitionLine.move_to(
                    event_x, event_y, item_id, item_point_to_move + "_comment_line", first, move_list, move_to_grid
                )
            elif tags[0].startswith("connection"):
                transition.TransitionLine.move_to(
                    event_x, event_y, item_id, item_point_to_move + "_connection", first, move_list, move_to_grid
                )
            else:
                print("move: Fatal, unknown line type with tags", tags)
        elif item_type == "rectangle":
            connector.ConnectorInstance.move_to(event_x, event_y, item_id, first, move_to_grid)
        elif item_type == "window":
            # breaks circular import, so import here instead of at the top of the file:
            from elements import (
                condition_action,
                global_actions_clocked,
                global_actions_combinatorial,
                state_action,
                state_actions_default,
                state_comment,
            )

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


def _object_is_moved_too_close_to_state_or_connector(move_list, event_x, event_y) -> bool:
    from elements import connector, state

    for entry in move_list:
        moved_object_item_id = entry[0]
        moved_object_must_be_checked = False
        event_x_mod, event_y_mod = 0, 0
        if (
            project_manager.canvas.type(moved_object_item_id) == "rectangle"
            and project_manager.canvas.itemcget(moved_object_item_id, "fill") == constants.CONNECTOR_COLOR
        ):
            moved_object_must_be_checked = True
            event_x_mod = event_x + connector.ConnectorInstance.difference_x
            event_y_mod = event_y + connector.ConnectorInstance.difference_y
        elif project_manager.canvas.type(moved_object_item_id) == "oval":
            moved_object_must_be_checked = True
            event_x_mod = event_x + state.States.difference_x
            event_y_mod = event_y + state.States.difference_y
        if moved_object_must_be_checked and _too_close(moved_object_item_id, event_x_mod, event_y_mod):
            return True
    return False


def _too_close(moved_object_item_id, event_x_mod, event_y_mod) -> bool:
    event_x_mod = project_manager.state_radius * round(event_x_mod / project_manager.state_radius)
    event_y_mod = project_manager.state_radius * round(event_y_mod / project_manager.state_radius)
    item_coords = project_manager.canvas.coords(moved_object_item_id)
    item_length = item_coords[2] - item_coords[0]
    new_upper_left__corner = [event_x_mod - item_length / 2, event_y_mod - item_length / 2]
    new_lower_right_corner = [event_x_mod + item_length / 2, event_y_mod + item_length / 2]
    moved_coords = [*new_upper_left__corner, *new_lower_right_corner]
    overlapping_list = project_manager.canvas.find_overlapping(
        moved_coords[0] - project_manager.state_radius / 2,
        moved_coords[1] - project_manager.state_radius / 2,
        moved_coords[2] + project_manager.state_radius / 2,
        moved_coords[3] + project_manager.state_radius / 2,
    )
    for overlapping_item in overlapping_list:
        if overlapping_item != moved_object_item_id:
            if project_manager.canvas.type(overlapping_item) == "oval":
                return True
            tags = project_manager.canvas.gettags(overlapping_item)
            for tag in tags:
                if tag.startswith("connector"):
                    return True
    return False

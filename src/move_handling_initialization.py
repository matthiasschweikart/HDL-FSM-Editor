"""
The method move_initialization is bound to to "Button-1" (click at left mouse button).
When the mouse hovers over one of the text boxes, this binding is not active,
as the text boxes are Canvas-Windows, for which the Canvas binding is not valid.
"""

import math
import tkinter as tk

import canvas_editing
import move_handling
import move_handling_canvas_item
import move_handling_finish
from elements import transition
from project_manager import project_manager


def move_initialization(event) -> None:
    """Start move on Button-1: find items under cursor, build move list, bind Motion and ButtonRelease-1."""
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    items_near_mouse_click_location = _create_a_list_of_overlapping_items_near_the_mouse_click_location(
        event_x, event_y
    )
    if _any_item_is_not_allowed_to_be_moved(items_near_mouse_click_location):
        return
    move_list = create_move_list(items_near_mouse_click_location, event_x, event_y)
    # The move_list has an entry for each item, which must be moved.
    # The first entry belongs always to the object, the user wants to move.
    # All following entries are objects, which are "connected" to the object of the first entry and must also be moved.
    # These items can be moved:
    # reset_entry, state, transition, connector, state_action_window, condition_action_window, global_action windows.
    # When a transitions is moved, then its connection-line to a condition_action_window is adapted after the
    # moving (as the line is not visible during moving).
    # For each item a "move_to" function exists, which moves all elements of the item (for example at a
    # transition: line, priority-rectangle, priority-text, but not the connection-line to a condition_action_window).
    # Each entry consists out of 2 or 3 values (stored in a list):
    # The first value is always the canvas-item-id.
    # The second value is only different from "" at transitions:
    # There the point of the line which has to bemoved is stored as a string:
    # 'start', 'next_to_start', 'next_to_end', 'end'.
    # The third value is the tag of the transition to which the moved condition_action belongs.

    if move_list:
        # The check for an empty movelist is needed, because move_finish accesses always move_list[0].

        # When the user ends moving at an illegal place, the moving continues until he clicks Button-1 again.
        # This second Button-1 click shall not start a new moving, so the binding for Button-1 is removed here:
        project_manager.canvas.unbind("<Button-1>")
        # The second Button-1 shall also not start a moving of canvas-items:
        move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = True

        # With first=True the position of the cursor relativly to the anchor point of the object to move is
        # determined and stored. This distance is afterwards at each cursor movement added to the event coordinates
        # in order to get the new coordinates of the anchor point.
        # This prevents the object from jumping to the cursor at the first movement.
        move_handling.move_do(event, move_list, first=True)

        # Create a binding for the now following movements of the mouse and for finishing the moving:
        move_do_funcid = project_manager.canvas.bind(
            "<Motion>",
            lambda motion_event, move_list=move_list: move_handling.move_do(motion_event, move_list, first=False),
            add="+",
        )  # Must be "added", as store_mouse_position is already bound to "Motion".
        project_manager.canvas.bind(
            "<ButtonRelease-1>",
            lambda release_event, move_list=move_list, move_do_funcid=move_do_funcid: move_handling_finish.move_finish(
                release_event, move_list, move_do_funcid
            ),
        )  # move_finish must unbind move_do from "Motion", so it needs the function id.


def _any_item_is_not_allowed_to_be_moved(items_near_mouse_click_location):
    if not items_near_mouse_click_location:
        return True
    if _mouse_click_happened_in_state_name(items_near_mouse_click_location):
        return True  # The state name shall be changed and no moving is required.
    if _mouse_click_happened_in_priority_number(items_near_mouse_click_location):
        return True  # The priority shall be changed and no moving is required.
    if _mouse_click_happened_in_connection_line(items_near_mouse_click_location):
        return True  # No connection-line can be moved.
    if _mouse_click_happened_in_state_comment_line(items_near_mouse_click_location):
        return True  # No state-comment-line can be moved.
    return _mouse_click_happened_in_grid_line(items_near_mouse_click_location)


def _create_a_list_of_overlapping_items_near_the_mouse_click_location(event_x, event_y) -> list:
    # As soon as a mouse click happens inside a canvas-window item, this click does not call move_initialization,
    # as there is no binding inside the canvas-window for this event. If there would be a binding,
    # it would return event coordinates from inside the window, which cannot be easily converted into canvas
    # coordinates, as the window does not know its own location. So here a bigger overlapping area must be used,
    # so that the user can click beneath the window and catch it.
    list_of_overlapping_items = []
    overlapping_items = project_manager.canvas.find_overlapping(event_x, event_y, event_x, event_y)
    for overlapping_item in overlapping_items:
        if project_manager.canvas.type(overlapping_item) == "oval":
            # The cursor is inside a state, in this case moving shall use MoveHandlingCanvasItem.
            return []
        overlap_tag = project_manager.canvas.gettags(overlapping_item)[0]
        if overlap_tag.startswith("transition") and overlap_tag.endswith("priority"):
            # The cursor is inside a priority-rectangle, no moving in this case
            return []
        if overlap_tag.startswith("transition") and overlap_tag.endswith("rectangle"):
            # The cursor is inside a priority-rectangle, no moving in this case
            return []
    overlapping_items = project_manager.canvas.find_overlapping(
        event_x - project_manager.state_radius / 4,
        event_y - project_manager.state_radius / 4,
        event_x + project_manager.state_radius / 4,
        event_y + project_manager.state_radius / 4,
    )
    for overlapping_item in overlapping_items:
        overlap_tag = project_manager.canvas.gettags(overlapping_item)[0]
        if "grid_line" not in project_manager.canvas.gettags(
            overlapping_item
        ) and "polygon_for_move" not in project_manager.canvas.gettags(overlapping_item):
            list_of_overlapping_items.append(overlapping_item)
    return list_of_overlapping_items


def _mouse_click_happened_in_state_name(items_near_mouse_click_location) -> bool:
    list_item_types = []
    for item_id in items_near_mouse_click_location:
        list_item_types.append(project_manager.canvas.type(item_id))
    return "oval" in list_item_types and "text" in list_item_types


def _mouse_click_happened_in_priority_number(items_near_mouse_click_location) -> bool:
    list_item_types = []
    for item_id in items_near_mouse_click_location:
        list_item_types.append(project_manager.canvas.type(item_id))
    return "rectangle" in list_item_types and "text" in list_item_types


def _mouse_click_happened_in_connection_line(items_near_mouse_click_location) -> bool:
    for item_id in items_near_mouse_click_location:
        if project_manager.canvas.type(item_id) == "line":
            tags = project_manager.canvas.gettags(item_id)
            for t in tags:
                if t.startswith("connected_to"):
                    return True
    return False


def _mouse_click_happened_in_state_comment_line(items_near_mouse_click_location) -> bool:
    for item_id in items_near_mouse_click_location:
        if project_manager.canvas.type(item_id) == "line":
            tags = project_manager.canvas.gettags(item_id)
            for t in tags:
                if t.startswith("state") and t.endswith("_comment_line"):
                    return True
    return False


def _mouse_click_happened_in_grid_line(items_near_mouse_click_location) -> bool:
    return all("grid_line" in project_manager.canvas.gettags(item_id) for item_id in items_near_mouse_click_location)


def create_move_list(items_near_mouse_click_location, event_x, event_y) -> list:
    """Build list of [[item_id, point_index], ...] to move.
    Includes connected diagram objects or a single line point."""
    move_list = []
    move_list_entry_for_diagram_object = _create_move_list_entry_if_a_diagram_object_is_moved(
        items_near_mouse_click_location
    )
    if move_list_entry_for_diagram_object is not None:
        move_list.append(move_list_entry_for_diagram_object)
        _add_lines_connected_to_the_diagram_object_to_the_list(move_list)
    else:  # A Canvas line point is moved.
        _add_items_for_moving_a_single_line_point_to_the_list(
            move_list, items_near_mouse_click_location, event_x, event_y
        )
    return move_list


def _create_move_list_entry_if_a_diagram_object_is_moved(items_near_mouse_click_location) -> list | None:
    move_list_entry = None
    for item_id in items_near_mouse_click_location:
        tags_of_item_id = project_manager.canvas.gettags(item_id)
        if (
            tags_of_item_id != ()
        ):  # If left mouse button is pressed during view-area with the right mouse-button, the list is empty.
            for tag in tags_of_item_id:
                if tag.startswith("state") and tag.endswith("_name"):
                    # This can happen only if the moving is started by MoveHandlingCanvasItem.
                    # Then only the canvas-id of the state-name is in the list items_near_mouse_click_location.
                    # To be able to create a complete move_list, the canvas-id of the state
                    # must be added to the move_list:
                    state_tag = tag[:-5]
                    canvas_id_of_state = project_manager.canvas.find_withtag(state_tag)[0]
                    move_list_entry = [
                        canvas_id_of_state,
                        "",
                    ]
                elif (
                    (  # state<nr>, state<nr>_comment, state<nr>_name:
                        tag.startswith("state") and not tag.endswith("_comment_line_end")
                    )
                    or tag.startswith("state_action")  # state_action<nr>, state_actions_default
                    or tag.startswith("condition_action")
                    or tag.startswith("reset_entry")
                    or tag.startswith("global_actions")
                    or tag.startswith("global_actions_combinatorial")
                    or tag.startswith("connector")
                ):
                    # The move_list_entry must contain item_ids (and not tags), as only the item_id can
                    # later be used as a key for a dictionary.
                    # The empty second entry is needed, as later on it will be accessed in
                    # move_handling.move_do without checking if its exists:
                    move_list_entry = [
                        item_id,
                        "",
                    ]
                    return move_list_entry
    return move_list_entry


def _add_lines_connected_to_the_diagram_object_to_the_list(move_list) -> None:
    tag_list_of_object_to_move = project_manager.canvas.gettags(move_list[0][0])
    # tag_list_of_object_to_move may have different entries (additional to "current"):
    # When moving a state:
    # ('state1',
    # 'connection0_end',       -> for state_action
    # 'transition0_start', 'transition2_end',
    # 'state1_comment_line_end')
    # When moving a state action:
    # ('state_action0', 'connection0_start')
    # When moving a state comment:
    # ('state1_comment', 'state1_comment_line_start')
    tag_of_connected_line = None
    for tag in (
        tag_list_of_object_to_move
    ):  # Check which Canvas lines are "connected" and must be moved together with the diagram object.
        to_be_moved_point_of_connected_line = ""
        if tag.startswith("connection") and tag.endswith("_start"):
            tag_of_connected_line = tag[:-6]  # transition<n>, state<n>_comment_line, connection<n>
            to_be_moved_point_of_connected_line = "start"
            # transition.TransitionLine.extend_transition_to_state_middle_points(tag_of_connected_line)
        elif tag.startswith("transition") and tag.endswith("_start"):
            tag_of_connected_line = tag[:-6]  # transition<n>, state<n>_comment_line, connection<n>
            to_be_moved_point_of_connected_line = "start"
            transition.TransitionLine.extend_transition_to_state_middle_points(tag_of_connected_line)
        elif tag.endswith("_comment_line_end"):
            tag_of_connected_line = tag[:-4]
            to_be_moved_point_of_connected_line = "end"
        elif tag.endswith("_end"):
            tag_of_connected_line = tag[:-4]  # transition<n>, state<n>_comment_line, connection<n>, ca_connection<n>
            to_be_moved_point_of_connected_line = "end"
            transition.TransitionLine.extend_transition_to_state_middle_points(tag_of_connected_line)
        if to_be_moved_point_of_connected_line != "":
            # tag_of_connected_line identifies a single object.
            # So the method find_withtag() returns always a list of length 1:
            id_of_connected_line = project_manager.canvas.find_withtag(tag_of_connected_line)[0]
            move_list.append([id_of_connected_line, to_be_moved_point_of_connected_line])
            transition.TransitionLine.extend_transition_to_state_middle_points(tag_of_connected_line)


def _add_items_for_moving_a_single_line_point_to_the_list(
    move_list, items_near_mouse_click_location, event_x, event_y
) -> None:
    line_id = _find_the_item_id_of_the_line(items_near_mouse_click_location)
    if line_id is None:
        return  # move_list is emtpy in this case.
    transition_tags = _search_for_the_tags_of_a_transition(
        line_id
    )  # A line can represent a "transition" or a "connection" (connections are ignored here).
    if transition_tags != ():
        moving_point = get_point_to_move(line_id, event_x, event_y)
        for tag in transition_tags:
            if tag.startswith("transition"):
                id_of_transition = project_manager.canvas.find_withtag(tag)[0]
                # moving point is one of: "start", "next_to_start", "next_to_end", "end" as
                # at maximum 4 points are supported:
                move_list.append([id_of_transition, moving_point])
                transition.TransitionLine.extend_transition_to_state_middle_points(tag)
                _remove_tags_and_hide_priority(line_id, tag, transition_tags, moving_point)


def _find_the_item_id_of_the_line(items_near_mouse_click_location) -> None:
    for item_id in items_near_mouse_click_location:
        if project_manager.canvas.type(item_id) == "line" and "grid_line" not in project_manager.canvas.gettags(
            item_id
        ):
            return item_id
    return None


def _search_for_the_tags_of_a_transition(line_id) -> tuple | None:
    line_tags = project_manager.canvas.gettags(line_id)
    for tag in line_tags:
        if tag.startswith("transition"):
            return line_tags
        return ()


def _remove_tags_and_hide_priority(line_id, transition_tag, transition_tags, moving_point) -> None:
    for tag in transition_tags:
        if moving_point == "start" and tag.startswith("coming_from_"):
            project_manager.canvas.dtag(line_id, tag)  # delete the "coming_from_" tag from the line
            start_state_tag = tag[12:]
            project_manager.canvas.dtag(
                start_state_tag, transition_tag + "_start"
            )  # delete the transition<n>_start-tag from the connected state.
            if tag == "coming_from_reset_entry":
                for t in transition_tags:
                    if t.startswith("ca_connection"):
                        project_manager.canvas.dtag("connected_to_reset_transition", "connected_to_reset_transition")
            priority_dict = transition.TransitionLine.determine_priorities_of_outgoing_transitions(start_state_tag)
            if len(priority_dict) == 1:
                for outgoing_transition in priority_dict:
                    project_manager.canvas.itemconfigure(outgoing_transition + "priority", state=tk.HIDDEN)
                    project_manager.canvas.itemconfigure(outgoing_transition + "rectangle", state=tk.HIDDEN)
        elif moving_point == "end" and tag.startswith("going_to_"):
            end_state_tag = tag[9:]
            project_manager.canvas.dtag(
                end_state_tag, transition_tag + "_end"
            )  # delete the transition<n>_end-tag from the connected state.
            project_manager.canvas.dtag(line_id, tag)  # delete the "going_to_" tag from the line


def get_point_to_move(item_id, event_x, event_y) -> str:
    """Return index of the transition point nearest to (event_x, event_y); insert extra point if needed."""
    # Determine which point of the transition is nearest to the event and insert an additional if necessary:
    transition_coords = project_manager.canvas.coords(item_id)
    number_of_points = len(transition_coords) // 2
    distance_event_to_point = []
    distance_to_neighbour = []
    for i in range(number_of_points):
        distance_event_to_point.append(
            math.sqrt((event_x - transition_coords[2 * i]) ** 2 + (event_y - transition_coords[2 * i + 1]) ** 2)
        )
        if i < number_of_points - 1:
            distance_to_neighbour.append(
                math.sqrt(
                    (transition_coords[2 * i] - transition_coords[2 * i + 2]) ** 2
                    + (transition_coords[2 * i + 1] - transition_coords[2 * i + 3]) ** 2
                )
            )
    if number_of_points == 4:
        return_value = ""
        if distance_event_to_point[0] < 2 * project_manager.state_radius:
            return_value = "start"
        if (
            distance_event_to_point[3] < 2 * project_manager.state_radius
            and distance_event_to_point[3] < distance_event_to_point[0]
        ):
            return_value = "end"
        if return_value == "":
            return_value = "next_to_start" if distance_event_to_point[1] < distance_event_to_point[2] else "next_to_end"
        return return_value
    if number_of_points == 3:
        return_value = ""
        if distance_event_to_point[0] < 2 * project_manager.state_radius:
            return_value = "start"
        if (
            distance_event_to_point[2] < 2 * project_manager.state_radius
            and distance_event_to_point[2] < distance_event_to_point[0]
        ):
            return_value = "end"
        if return_value != "":
            return return_value
        ratio = distance_event_to_point[0] / distance_event_to_point[2]
        if 0.8 < ratio < 1.2:
            return "next_to_start"  # equal to "next_to_end" because no new point is inserted.
        _change_the_number_of_points_from_3_to_4(item_id, transition_coords)
        if distance_event_to_point[2] < distance_event_to_point[0]:
            return "next_to_end"
        return "next_to_start"
    # number_of_points == 2
    if distance_event_to_point[0] < distance_to_neighbour[0] / 3:
        return "start"
    if distance_event_to_point[0] < distance_to_neighbour[0] * 2 / 3:
        _change_the_number_of_points_from_2_to_3(item_id, transition_coords, event_x, event_y)
        return "next_to_start"
    return "end"


def _change_the_number_of_points_from_3_to_4(item_id, transition_coords):
    transition_coords = _calculate_4_points_from_3_points(transition_coords)
    project_manager.canvas.coords(item_id, *transition_coords)  # insert new point into transition


def _calculate_4_points_from_3_points(transition_coords):
    vector_to_point0 = transition_coords[0], transition_coords[1]
    vector_to_point1 = transition_coords[2], transition_coords[3]
    vector_to_point2 = transition_coords[4], transition_coords[5]
    vector_point0_to_point2 = [vector_to_point2[i] - vector_to_point0[i] for i in range(2)]
    vector_to_half_02 = [vector_to_point0[i] + 0.50 * vector_point0_to_point2[i] for i in range(2)]
    vector_to_shor_02 = [vector_to_point0[i] + 0.25 * vector_point0_to_point2[i] for i in range(2)]
    vector_to_long_02 = [vector_to_point0[i] + 0.75 * vector_point0_to_point2[i] for i in range(2)]
    vector_half_02_to_point1 = [vector_to_point1[i] - vector_to_half_02[i] for i in range(2)]
    new_point2 = [vector_to_shor_02[i] + 0.5 * vector_half_02_to_point1[i] for i in range(2)]
    new_point3 = [vector_to_long_02[i] + 0.5 * vector_half_02_to_point1[i] for i in range(2)]
    return (
        transition_coords[0],
        transition_coords[1],
        new_point2,
        new_point3,
        transition_coords[4],
        transition_coords[5],
    )


def _change_the_number_of_points_from_2_to_3(item_id, transition_coords, event_x, event_y):
    project_manager.canvas.coords(item_id, *transition_coords[0:2], event_x, event_y, *transition_coords[2:4])

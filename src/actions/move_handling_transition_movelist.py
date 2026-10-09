"""
This module handles the creation of the move_list for transitions.

A move_list has an entry for each item, which must be moved.
In case of a transition the move_list has only 1 entry.
Each entry is a list containing the canvas-item-id of the object to be moved,
the point to move (or an empty string for non-transition items),
and optionally a third entry which is not needed for moving transitions.
The point to move is always one of: 'start', 'next_to_start', 'next_to_end', 'end'.

If the transition has a priority rectangle, the priority rectangle is moved
together with the transition and needs no entry in the move_list.

If the transition has a condition_action_window, its connection-line is
adapted after the moving (as the line is not visible during moving).
"""

import math

from project_manager import project_manager


def create_move_list_for_transition(line_id, event_x, event_y) -> list:
    # A Canvas line point from a transition is moved:
    coords_before_move = project_manager.canvas.coords(line_id)
    point_to_move = _get_point_to_move_and_insert_point_if_needed(line_id, event_x, event_y)
    # moving point is one of: "start", "next_to_start", "next_to_end", "end"
    move_list = [[line_id, point_to_move]]
    return move_list, coords_before_move


def _get_point_to_move_and_insert_point_if_needed(item_id, event_x, event_y) -> str:
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
        minimum = None
        index_of_minimum = 0
        for index, distance in enumerate(distance_event_to_point):
            if minimum is None or distance < minimum:
                minimum = distance
                index_of_minimum = index
        possible_return_values = ["start", "next_to_start", "next_to_end", "end"]
        return possible_return_values[index_of_minimum]
    if number_of_points == 3:
        return_value = ""
        if distance_event_to_point[0] < 2 * project_manager.state_radius:
            return_value = "start"
        if (
            distance_event_to_point[2] < 2 * project_manager.state_radius
            # Additional condition for loopback transition (return_value may have value "start" already):
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

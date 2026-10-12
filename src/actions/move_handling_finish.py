"""
Includes all methods needed, when moving objects ends.
"""

import math

from elements import transition
from project_manager import project_manager


def move_finish_for_transitions(move_list):
    """Shorten transitions to state borders, move condition-action endpoints, hide connection lines, lower grid."""
    _shorten_all_moved_transitions_to_the_state_borders(move_list)
    _move_all_ca_connection_end_points_to_the_new_transition_start_points(move_list)
    _hide_the_connection_line_of_moved_condition_action_window(move_list)  # Gets visible when the window is moved alone
    project_manager.canvas.tag_lower("grid_line")


def _shorten_all_moved_transitions_to_the_state_borders(move_list) -> None:
    # Prevent transitions to be shortened twice (would happen at transitions that point from
    # a state to the same state back) by writing a done-list:
    done = []
    for move_list_entry in move_list:
        # print("move_list_entry =", move_list_entry)
        if move_list_entry[1] in ["start", "next_to_start", "next_to_end", "end"] and move_list_entry[0] not in done:
            tags_of_moved_object = project_manager.canvas.gettags(move_list_entry[0])
            transition_tag = None
            for tag in tags_of_moved_object:
                if tag.startswith("transition"):
                    transition_tag = tag
            if transition_tag is not None:  # A "connection" or a "ca_connection"must not be shortened.
                transition_coords = _try_to_convert_into_straight_line(project_manager.canvas.coords(transition_tag))
                project_manager.canvas.coords(transition_tag, transition_coords)
                transition.TransitionLine.shorten_to_state_border(transition_tag)
                done.append(move_list_entry[0])


def _move_all_ca_connection_end_points_to_the_new_transition_start_points(move_list) -> None:
    for move_list_entry in move_list:
        if project_manager.canvas.type(move_list_entry[0]) == "line":  # transition or connection/ca_connection
            ca_connection_tag = None
            transition_tag = None
            tags_of_moved_object = project_manager.canvas.gettags(move_list_entry[0])
            for tag in tags_of_moved_object:
                if tag.startswith("ca_connection") and tag.endswith("_end"):
                    # The moved transition has a connection line to a condition&action box.
                    # The end point of this connection line must be moved to the new start point of the transition.
                    ca_connection_tag = tag[:-4]
                    ca_connection_coords = project_manager.canvas.coords(ca_connection_tag)
                    transition_coords = project_manager.canvas.coords(move_list_entry[0])
                    project_manager.canvas.coords(
                        ca_connection_tag,
                        ca_connection_coords[0],
                        ca_connection_coords[1],
                        transition_coords[0],  # move end-point of the ca_connection to the transition start point
                        transition_coords[1],  # move end-point of the ca_connection to the transition start point
                    )
                elif tag.startswith("ca_connection"):
                    # The moved line is a ca_connection (happens at moved loopback transition with condition&action box)
                    # Wait until the transition_tag is found in the subsequent tags.
                    ca_connection_tag = tag
                elif tag.startswith("connected_to_transition"):
                    # The moved line is a ca_connection (happens at moved loopback transition with condition&action box)
                    # Wait until the ca_connection_tag is found in the subsequent tags.
                    transition_tag = tag[13:]
            if ca_connection_tag is not None and transition_tag is not None:
                # Move the end point of the ca_connection line to the start point of the transition.
                # The start point of the ca_connection line is moved together with the condition&action box.
                transition_coords = project_manager.canvas.coords(transition_tag)
                ca_connection_coords = project_manager.canvas.coords(ca_connection_tag)
                project_manager.canvas.coords(
                    ca_connection_tag,
                    ca_connection_coords[0],
                    ca_connection_coords[1],
                    transition_coords[0],
                    transition_coords[1],
                )
                ca_connection_tag = None
                transition_tag = None


def _hide_the_connection_line_of_moved_condition_action_window(move_list) -> None:
    for move_list_entry in move_list:
        if project_manager.canvas.type(move_list_entry[0]) == "window":
            tags = project_manager.canvas.gettags(move_list_entry[0])
            for t in tags:
                if t.startswith("condition_action"):
                    ref = project_manager.canvas_windows_ref_dict[move_list_entry[0]]
                    ref.hide_line()


def _try_to_convert_into_straight_line(coords) -> list:
    """If coords form a near-straight line, return [x0,y0, x_end,y_end]; otherwise return coords unchanged."""
    number_of_points = len(coords) / 2
    if number_of_points == 2:
        return coords
    vector_list = _calculate_vectors_from_line_point_to_next_line_point(coords)
    cos_phi_list = _calculate_cos_phi_values_between_vectors(vector_list)
    eliminate_points = True
    for cos_phi in cos_phi_list:
        if cos_phi < 0.97:
            eliminate_points = False
    if eliminate_points:
        return [coords[0], coords[1], coords[-2], coords[-1]]
    return coords


def _calculate_vectors_from_line_point_to_next_line_point(coords) -> list:
    vector_list = []
    for i in range(len(coords) // 2 - 1):
        vector_from_point_to_point = _sub_vectors(
            coords[i * 2 + 2], coords[i * 2 + 3], coords[i * 2 + 0], coords[i * 2 + 1]
        )
        if vector_from_point_to_point != [0, 0]:
            vector_list.append(vector_from_point_to_point)
    return vector_list


def _calculate_cos_phi_values_between_vectors(vector_list) -> list:
    cos_phi_list = []
    for i in range(len(vector_list) - 1):
        product_vector1_vector2 = _calculate_scalar_product(
            vector_list[i][0], vector_list[i][1], vector_list[i + 1][0], vector_list[i + 1][1]
        )
        amount_vector1 = math.sqrt(
            _calculate_scalar_product(vector_list[i][0], vector_list[i][1], vector_list[i][0], vector_list[i][1])
        )
        amount_vector2 = math.sqrt(
            _calculate_scalar_product(
                vector_list[i + 1][0], vector_list[i + 1][1], vector_list[i + 1][0], vector_list[i + 1][1]
            )
        )
        cos_phi = product_vector1_vector2 / (amount_vector1 * amount_vector2)
        cos_phi_list.append(cos_phi)
    return cos_phi_list


def _sub_vectors(x1, y1, x2, y2) -> list:
    return [x1 - x2, y1 - y2]


def _calculate_scalar_product(x1, y1, x2, y2):
    return x1 * x2 + y1 * y2

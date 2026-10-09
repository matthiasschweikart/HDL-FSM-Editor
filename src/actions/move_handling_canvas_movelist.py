"""
This module handles the creation of the move_list for all canvas items but transitions.

A move_list has an entry for each item, which must be moved.
The first entry of the move_list is always for the item to be moved.
All following entries are needed for items that are connected to the item to be moved
and must be moved as well. This can be connected transitions, attached state-actions,
or other related canvas items.

Each entry in the move_list is a list and has 2 values.
The first value is always the canvas-item-id of the item to be moved.
The second value is the point to move (or an empty string for non-transition items).
"""

import tkinter as tk

from elements import transition
from project_manager import project_manager


def create_move_list(canvas_id) -> list | None:
    # The move_list_entry must contain item_ids (and not tags), as only the item_id can
    # later be used as a key for a dictionary.
    # The empty second entry is needed, as later on it will be accessed in
    # move_handling.move_to_coordinates without checking if its exists:
    tags_of_canvas_id = project_manager.canvas.gettags(canvas_id)
    for tag in tags_of_canvas_id:
        if tag == "reset_text":
            canvas_id_of_polygon = project_manager.canvas.find_withtag("reset_entry")[0]
            return [[canvas_id_of_polygon, ""]], project_manager.canvas.coords(canvas_id_of_polygon)
        if (
            tag.startswith("reset_entry")
            or tag.startswith("state_action")  # state_action<nr>, state_actions_default
            or tag.endswith("_comment")  # state<nr>_comment
            or tag.startswith("condition_action")
            or tag.startswith("global_actions")
            or tag.startswith("global_actions_combinatorial")
            or tag.startswith("connector")
        ):
            return [[canvas_id, ""]], project_manager.canvas.coords(canvas_id)
        if tag.startswith("state"):
            state_tag = None
            if tag.endswith("_name"):
                # A state is moved by moving its state-name.
                state_tag = tag[:-5]  # remove "_name"
                canvas_id_of_state = project_manager.canvas.find_withtag(state_tag)[0]
            elif not tag.endswith("_comment_line_end"):
                # A state is moved by moving its circle.
                state_tag = tag
                canvas_id_of_state = canvas_id
            if state_tag is not None:
                move_list = [[canvas_id_of_state, ""]]
                move_list = _add_connected_elements(state_tag, move_list)
                return move_list, project_manager.canvas.coords(canvas_id)


def _add_connected_elements(state_tag, move_list) -> list:
    # A comment window is always moved together with its state:
    tag_list = project_manager.canvas.find_withtag(state_tag + "_comment")
    if tag_list:
        move_list.append([tag_list[0], ""])  # canvas-id of state comment
    # A state action window is always moved together with its state and
    # a loopback-transition (and its condition&action window) is always moved together with its state:
    tag_list = project_manager.canvas.gettags(state_tag)
    for tag_list_entry in tag_list:
        if tag_list_entry.startswith("connection") and tag_list_entry.endswith("_end"):  # line to state action
            connection_tag = tag_list_entry[:-4]
            canvas_id_of_state_action = project_manager.canvas.find_withtag(connection_tag + "_start")
            move_list.append([canvas_id_of_state_action[0], ""])  # canvas-id state action
        elif tag_list_entry.startswith("transition") and tag_list_entry.endswith("_start"):
            transition_tag = tag_list_entry[:-6]  # transition<n>_start
            if transition_tag + "_end" in tag_list:  # Then this is a loopback transition.
                transition_tags = project_manager.canvas.gettags(transition_tag)
                for tag in transition_tags:
                    if tag.startswith("ca_connection"):  # Then the transition has a condition&action box.
                        ca_connection_tag = tag[:-4]  # tag = "ca_connection<p>_end"
                        move_list.append(  # Add the canvas-id of the condition&action window.
                            [project_manager.canvas.find_withtag(ca_connection_tag + "_anchor")[0], ""]
                        )
                        move_list.append(  # Add the canvas-id of the line between condition&action and transition.
                            [project_manager.canvas.find_withtag(ca_connection_tag)[0], "start"]
                        )
                        move_list.append(  # Add the canvas_id of the line between condition&action and transition..
                            [project_manager.canvas.find_withtag(ca_connection_tag)[0], "end"]
                        )
    return move_list


def add_connected_lines_and_add_transitions_extended(move_list) -> None:
    tag_list_of_object_to_move = project_manager.canvas.gettags(move_list[0][0])  # State/Connector/Reset-Entry/Window
    tag_of_connected_line = None
    # Check which Canvas lines are "connected" and must be moved together with the diagram object:
    for tag in tag_list_of_object_to_move:
        to_be_moved_point_of_connected_line = None
        loop_back_transition = False
        add_line_start_point = False
        if tag.startswith("transition") and tag.endswith("_start"):
            # A state or connector is moved, so the start-point of a connected transition line must be moved as well:
            tag_of_connected_line = tag[:-6]  # transition<n>
            to_be_moved_point_of_connected_line = "start"
            transition.TransitionLine.extend_transition_to_state_middle_points(tag_of_connected_line)
            loop_back_transition = tag_of_connected_line + "_end" in tag_list_of_object_to_move
        elif tag.startswith("transition") and tag.endswith("_end"):
            # A state or connector is moved, so the end-point of a connected transition line must be moved as well:
            tag_of_connected_line = tag[:-4]  # transition<n>
            to_be_moved_point_of_connected_line = "end"
            transition.TransitionLine.extend_transition_to_state_middle_points(tag_of_connected_line)
        elif tag.startswith("connection") and tag.endswith("_end"):
            # A state is moved and has a state_action, so move both points of the action line as well:
            to_be_moved_point_of_connected_line = "end"
            add_line_start_point = True
            tag_of_connected_line = tag[:-4]  # connection<n>_end
        elif tag.endswith("_comment_line_end"):
            # A state is moved and has a state_comment, so move both points of the comment line as well:
            to_be_moved_point_of_connected_line = "end"
            add_line_start_point = True
            tag_of_connected_line = tag[:-4]  # state<n>_comment_line_end
        elif tag.startswith("connection") and tag.endswith("_start"):
            # A state action window is moved and moves the start point of the action line as well:
            tag_of_connected_line = tag[:-6]  # = connection<n>; line from a state action to a state
            to_be_moved_point_of_connected_line = "start"
        elif tag.endswith("_comment_line_start"):
            # A comment_window is moved and moves the the startpoint of the comment line as well:
            tag_of_connected_line = tag[:-6]  # state<n>_comment_line_start
            to_be_moved_point_of_connected_line = "start"
        elif tag.startswith("ca_connection") and tag.endswith("_anchor"):
            # A condition-action window is moved and moves the start point of a ca_connection line as well:
            tag_of_connected_line = tag[:-7]  # = ca_connection<n>; line from a condition-action to a transition
            project_manager.canvas.itemconfigure(tag_of_connected_line, state=tk.NORMAL)
            to_be_moved_point_of_connected_line = "start"
        if to_be_moved_point_of_connected_line is not None:
            # tag_of_connected_line identifies a single object.
            # So the method find_withtag() returns always a list of length 1:
            id_of_connected_line = project_manager.canvas.find_withtag(tag_of_connected_line)[0]
            move_list.append([id_of_connected_line, to_be_moved_point_of_connected_line])
            if loop_back_transition:
                move_list.append([id_of_connected_line, "next_to_start"])
                move_list.append([id_of_connected_line, "next_to_end"])
                loop_back_transition = False
            if add_line_start_point:
                move_list.append([id_of_connected_line, "start"])

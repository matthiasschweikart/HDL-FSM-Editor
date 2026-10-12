"""
This module handles the movement of transitions at the Canvas.
"""

import tkinter as tk
from tkinter import messagebox

from actions import (
    canvas_editing,
    move_handling_canvas_item,
    move_handling_canvas_movelist,
    move_handling_finish,
    move_handling_transition_movelist,
    move_handling_work_on_movelist,
)
from elements import transition
from project_manager import project_manager


class MoveHandlingTransition:
    """
    When a transition is moved at the Canvas,
    a MoveHandlingTransition object is created and handles the movement.
    """

    def __init__(self, event, canvas_id):
        if (
            move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs
            or move_handling_work_on_movelist.move_is_active
        ):
            return  # Button-1 shall now not move any canvas item
        move_handling_work_on_movelist.move_is_active = True
        canvas_id = canvas_id
        event_x, event_y = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        self.move_list, self.coords_before_move = move_handling_transition_movelist.create_move_list_for_transition(
            canvas_id, event_x, event_y
        )
        transition_tags = project_manager.canvas.gettags(canvas_id)
        for tag in transition_tags:
            if tag.startswith("transition"):
                transition_tag = tag
        transition.TransitionLine.extend_transition_to_state_middle_points(transition_tag)
        point_to_move = self.move_list[0][1]
        self._prepare_for_disconnecting_the_transition(transition_tag, point_to_move)
        move_handling_canvas_movelist.add_connected_lines_and_add_transitions_extended(self.move_list)

        # With first=True the position of the cursor relativly to the anchor point of the object to move is
        # determined and stored. This distance is afterwards at each cursor movement added to the event coordinates
        # in order to get the new coordinates of the object to move.
        # This prevents the object from jumping to the cursor at the first movement.
        move_handling_work_on_movelist.move_to_coordinates(
            event.x, event.y, self.move_list, first=True, move_to_grid=False
        )

        # Create a binding for the now following movements of the mouse and for finishing the moving.
        # Bind to canvas, because the cursor might leave the small line during moving.
        # Must be "added", as store_mouse_position is already bound to "Motion":
        self.funcid_motion = project_manager.canvas.bind("<Motion>", self._motion, add="+")
        self.funcid_release = project_manager.canvas.bind("<ButtonRelease-1>", self._release)

    def _motion(self, motion_event):
        move_handling_work_on_movelist.move_to_coordinates(
            motion_event.x,
            motion_event.y,
            self.move_list,
            first=False,
            move_to_grid=False,
        )

    def _release(self, event):
        moved_point = self.move_list[0][1]
        canvas_ids_at_target = self._get_canvas_ids_at_target(event, self.move_list)
        if moved_point in ("start", "end") and not canvas_ids_at_target:
            return  # no state/connector or illegal element under cursor
        move_handling_work_on_movelist.move_is_active = False
        project_manager.canvas.unbind("<Motion>", self.funcid_motion)
        project_manager.canvas.unbind("<ButtonRelease-1>")
        if moved_point in ("start", "end"):
            self._move_the_line_to_the_center_of_the_target(canvas_ids_at_target)
            self._update_the_tags_of_the_transition(canvas_ids_at_target)
        move_handling_finish.move_finish_for_transitions(self.move_list)
        for index, coord_after_move in enumerate(project_manager.canvas.coords(self.move_list[0][0])):
            if abs(coord_after_move - self.coords_before_move[index]) > project_manager.state_radius / 2:
                project_manager.undo_handling_ref.design_has_changed()
                return

    def _prepare_for_disconnecting_the_transition(self, transition_tag, point_to_move) -> None:
        transition_tags = project_manager.canvas.gettags(transition_tag)
        for tag in transition_tags:
            if point_to_move == "start" and tag.startswith("coming_from_"):
                project_manager.canvas.dtag(transition_tag, tag)  # delete the "coming_from_" tag from the line
                start_state_tag = tag[12:]
                # delete the transition<n>_start-tag from the connected state:
                project_manager.canvas.dtag(start_state_tag, transition_tag + "_start")
                if tag == "coming_from_reset_entry":
                    for t in transition_tags:
                        if t.startswith("ca_connection"):
                            project_manager.canvas.dtag(
                                "connected_to_reset_transition", "connected_to_reset_transition"
                            )
                priority_dict = transition.TransitionLine.determine_priorities_of_outgoing_transitions(start_state_tag)
                if len(priority_dict) == 1:
                    for outgoing_transition in priority_dict:
                        project_manager.canvas.itemconfigure(outgoing_transition + "priority", state=tk.HIDDEN)
                        project_manager.canvas.itemconfigure(outgoing_transition + "rectangle", state=tk.HIDDEN)
            elif point_to_move == "end" and tag.startswith("going_to_"):
                end_state_tag = tag[9:]
                # delete the transition<n>_end-tag from the connected state:
                project_manager.canvas.dtag(end_state_tag, transition_tag + "_end")
                project_manager.canvas.dtag(transition_tag, tag)  # delete the "going_to_" tag from the line

    def _get_canvas_ids_at_target(self, event, move_list) -> list:
        event_x, event_y = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        transition_point = move_list[0][1]
        canvas_ids_at_target = self._get_all_canvas_ids_at_target(event_x, event_y, move_list)
        if transition_point in ("start", "end") and self._illegal_target(canvas_ids_at_target, move_list):
            return []
        return canvas_ids_at_target

    def _get_all_canvas_ids_at_target(self, event_x, event_y, move_list) -> list:
        move_items = []
        for move_entry in move_list:
            move_items.append(move_entry[0])
            if project_manager.canvas.type(move_entry[0]) == "oval":
                move_items.append(self._get_canvas_id_of_state_name(move_entry[0]))
        overlapping_items = project_manager.canvas.find_overlapping(event_x, event_y, event_x, event_y)
        item_ids_at_moving_end_location = []
        for item in overlapping_items:
            if item not in move_items:
                item_ids_at_moving_end_location.append(item)
        return item_ids_at_moving_end_location

    def _move_the_line_to_the_center_of_the_target(self, item_ids_at_moving_end_location) -> None:
        transition_id = self.move_list[0][0]
        transition_point = self.move_list[0][1]
        for target in item_ids_at_moving_end_location:
            target_coords = project_manager.canvas.coords(target)
            target_type = project_manager.canvas.type(target)
            if target_type == "polygon":
                polygon_coords = project_manager.canvas.coords(target)
                transition.TransitionLine.move_to(
                    polygon_coords[4], polygon_coords[5], transition_id, transition_point, False, self.move_list
                )
            elif target_type in ["oval", "rectangle"]:
                state_middle_x = (target_coords[2] + target_coords[0]) / 2
                state_middle_y = (target_coords[3] + target_coords[1]) / 2
                transition.TransitionLine.move_to(
                    state_middle_x, state_middle_y, transition_id, transition_point, False, self.move_list
                )

    def _update_the_tags_of_the_transition(self, item_ids_at_moving_end_location) -> None:
        transition_id = self.move_list[0][0]
        transition_point = self.move_list[0][1]
        transition_tags = project_manager.canvas.gettags(transition_id)
        transition_tag = ""
        condition_action_line_tag = ""
        ref = None
        for tag in transition_tags:
            if tag.startswith("transition"):
                transition_tag = tag
            elif tag.startswith("ca_connection"):
                condition_action_line_tag = tag[:-4]
                condition_action_window_id = project_manager.canvas.find_withtag(condition_action_line_tag + "_anchor")[
                    0
                ]
                ref = project_manager.canvas_windows_ref_dict[condition_action_window_id]
        for target_id in item_ids_at_moving_end_location:
            if project_manager.canvas.type(target_id) not in ["oval", "rectangle", "polygon"]:
                continue
            target_tag = project_manager.canvas.gettags(target_id)[0]
            # target_tag is equal to "state<n>" or "connector<n>" or "reset_entry"
            if transition_point == "start":
                # update tags of transition:
                project_manager.canvas.addtag_withtag("coming_from_" + target_tag, transition_id)
                # update tags of the start object of the transition:
                project_manager.canvas.addtag_withtag(transition_tag + "_start", target_id)
                # update condition-action block descriptor and tags:
                if condition_action_line_tag != "":
                    if target_tag == "reset_entry":
                        project_manager.canvas.addtag_withtag(
                            "connected_to_reset_transition", condition_action_window_id
                        )
                        ref.change_descriptor_to("Transition actions (asynchronous):")
                    else:
                        ref.change_descriptor_to("Transition actions (clocked):")
                priority_dict = transition.TransitionLine.determine_priorities_of_outgoing_transitions(target_id)
                transition_priority_visibility = tk.HIDDEN if len(priority_dict) == 1 else tk.NORMAL
                for outgoing_transition in priority_dict:
                    project_manager.canvas.itemconfigure(
                        outgoing_transition + "priority", state=transition_priority_visibility
                    )
                    project_manager.canvas.itemconfigure(
                        outgoing_transition + "rectangle", state=transition_priority_visibility
                    )
            elif transition_point == "end":
                # update tags of transition:
                project_manager.canvas.addtag_withtag("going_to_" + target_tag, transition_id)
                # update tags of the end object of the transition:
                project_manager.canvas.addtag_withtag(transition_tag + "_end", target_id)

    def _get_canvas_id_of_state_name(self, state_id):
        tags = project_manager.canvas.gettags(state_id)
        return project_manager.canvas.find_withtag(tags[0] + "_name")[0]

    def _illegal_target(self, item_ids_at_moving_end_location, move_list) -> bool:
        debug_illegal_move = False
        if self._a_line_is_moved_to_a_window(item_ids_at_moving_end_location):
            if debug_illegal_move:
                print("Illegal: A transition start- or end-point was moved to a window.")
            return True
        if self._a_line_is_moved_to_a_priority_rectangle(item_ids_at_moving_end_location):
            if debug_illegal_move:
                print("Illegal: A transition start- or end-point was moved to a priority rectangle.")
            return True
        if self._a_line_start_or_end_point_is_moved_to_a_line(item_ids_at_moving_end_location):
            if debug_illegal_move:
                print("Illegal: A transition start- or end-point was moved to a transition.")
            return True
        if self._a_point_of_a_line_is_moved_illegally_to_a_reset_entry(item_ids_at_moving_end_location, move_list):
            if debug_illegal_move:
                print("Illegal: A transition start- or end-point was moved to a reset entry.")
            return True
        if self._start_or_end_of_a_line_was_moved_to_free_space(item_ids_at_moving_end_location):
            if debug_illegal_move:
                print("Illegal: A transition start- or end-point was moved to free space.")
            return True
        if self._transition_connects_reset_entry_and_connector(item_ids_at_moving_end_location, move_list):
            if debug_illegal_move:
                print("Illegal: A transition connects reset entry and connector.")
            return True
        if self._a_line_is_changed_into_a_loopback_transition_with_less_than_4_points(
            item_ids_at_moving_end_location, move_list
        ):
            messagebox.showerror(
                "Error", "A transition with less than 4 points cannot\nbe turned into a loopback transition."
            )
            return True
        if self._a_line_is_changed_into_a_loopback_transition_from_connector_to_connector(
            item_ids_at_moving_end_location, move_list
        ):
            messagebox.showerror("Error", "No loopback transition from connector to connector is allowed.")
            return True
        return False

    def _a_line_is_moved_to_a_window(self, item_ids_at_moving_end_location) -> bool:
        return any(project_manager.canvas.type(target) == "window" for target in item_ids_at_moving_end_location)

    def _a_line_is_moved_to_a_priority_rectangle(self, item_ids_at_moving_end_location) -> bool:
        for target in item_ids_at_moving_end_location:
            if project_manager.canvas.type(target) == "rectangle" and project_manager.canvas.gettags(target)[
                0
            ].startswith("transition"):
                return True
        return False

    def _a_line_start_or_end_point_is_moved_to_a_line(self, item_ids_at_moving_end_location) -> bool:
        target_is_a_line = True
        for target in item_ids_at_moving_end_location:
            if project_manager.canvas.type(target) in ["oval", "rectangle", "polygon"]:
                target_is_a_line = False
        if target_is_a_line is True:
            for target in item_ids_at_moving_end_location:
                if project_manager.canvas.type(target) == "line":
                    return True
        return False

    def _a_point_of_a_line_is_moved_illegally_to_a_reset_entry(
        self, item_ids_at_moving_end_location, move_list
    ) -> bool:
        for target in item_ids_at_moving_end_location:
            if project_manager.canvas.type(target) == "polygon":
                for move_list_entry in move_list:
                    if move_list_entry[1] == "end" and project_manager.canvas.gettags(move_list_entry[0])[0].startswith(
                        "transition"
                    ):
                        return True
                    if move_list_entry[1] == "start":
                        reset_entry_tags = project_manager.canvas.gettags(target)
                        for reset_entry_tag in reset_entry_tags:
                            if reset_entry_tag.startswith("transition"):
                                connected_transition_tag = reset_entry_tag[0:-6]
                                moved_transition_tags = project_manager.canvas.gettags(move_list_entry[0])
                                for tag in moved_transition_tags:
                                    if tag.startswith("transition") and connected_transition_tag != tag:
                                        return True
        return False

    def _start_or_end_of_a_line_was_moved_to_free_space(self, item_ids_at_moving_end_location) -> bool:
        return item_ids_at_moving_end_location == []

    def _a_line_is_changed_into_a_loopback_transition_with_less_than_4_points(
        self, item_ids_at_moving_end_location, move_list
    ) -> bool:
        target_state_tag = ""
        for item in item_ids_at_moving_end_location:
            if project_manager.canvas.type(item) == "oval":
                for tag in project_manager.canvas.gettags(item):
                    if tag.startswith("state"):
                        target_state_tag = tag
                        break
        if target_state_tag == "":
            return False  # Transition shall not end at a state, no loopback transition is possible.
        start_state_tag = ""
        for tag in project_manager.canvas.gettags(move_list[0][0]):
            if tag.startswith("coming_from_state"):
                start_state_tag = tag[12:]
                break
        if start_state_tag == "":
            return False  # Transition does not start at a state, no loopback transition is possible.
        return start_state_tag == target_state_tag and len(project_manager.canvas.coords(move_list[0][0])) < 8

    def _a_line_is_changed_into_a_loopback_transition_from_connector_to_connector(
        self, item_ids_at_moving_end_location, move_list
    ) -> bool:
        target_connector_tag = ""
        for item in item_ids_at_moving_end_location:
            if project_manager.canvas.type(item) == "rectangle":
                for tag in project_manager.canvas.gettags(item):
                    if tag.startswith("connector"):
                        target_connector_tag = tag
                        break
        if target_connector_tag == "":
            return False  # Transition does not end at a connector, no connector loopback transition is possible.
        connector_start_tag = ""
        for tag in project_manager.canvas.gettags(move_list[0][0]):
            if tag.startswith("coming_from_connector"):
                connector_start_tag = tag[12:]
                break
            if tag.startswith("going_to_connector"):
                connector_start_tag = tag[9:]
                break
        if connector_start_tag == "":
            return False  # Transition does not start/end at a connector, no connector loopback transition is possible.
        return connector_start_tag == target_connector_tag

    def _transition_connects_reset_entry_and_connector(self, item_ids_at_moving_end_location, move_list) -> bool:
        for target in item_ids_at_moving_end_location:
            if project_manager.canvas.type(target) == "rectangle":
                for move_list_entry in move_list:
                    moved_object_tags = project_manager.canvas.gettags(move_list_entry[0])
                    if "coming_from_reset_entry" in moved_object_tags:
                        return True
        return False

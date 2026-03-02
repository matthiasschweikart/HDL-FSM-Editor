"""
Module handling transitions on the canvas.
"""

import math
import tkinter as tk

import canvas_delete
import canvas_editing
import canvas_modify_bindings
import constants
import move_handling_initialization
import undo_handling
from elements import condition_action
from project_manager import project_manager
from widgets.option_menu import OptionMenu


class TransitionLine:
    """
    For each transition at the Canvas a TransitionLine object is created.
    """

    transition_number = 0
    ref_dict = {}

    def __init__(self, transition_coords, tags, priority, new_transition=False) -> None:
        if new_transition:
            TransitionLine.transition_number += 1
        self.difference_x = 0
        self.difference_y = 0
        transition_tag = tags[0]  # "transition<n>"
        rectangle_coords = self._determine_position_of_priority_rectangle(transition_coords)
        self.transition_id = project_manager.canvas.create_line(
            transition_coords, arrow="last", fill="blue", smooth=True, tags=tags
        )
        self.priority_text = project_manager.canvas.create_text(
            rectangle_coords,
            text=priority,
            tag=transition_tag + "priority",
            font=project_manager.state_name_font,
        )
        self.priority_rectangle = project_manager.canvas.create_rectangle(
            project_manager.canvas.bbox(self.priority_text),
            tag=transition_tag + "rectangle",
            fill=constants.STATE_COLOR,
        )
        project_manager.canvas.tag_bind(
            self.transition_id,
            "<Enter>",
            lambda event: project_manager.canvas.itemconfig(self.transition_id, width=3),
        )
        project_manager.canvas.tag_bind(
            self.transition_id,
            "<Leave>",
            lambda event: project_manager.canvas.itemconfig(self.transition_id, width=1),
        )
        project_manager.canvas.tag_bind(self.transition_id, "<Button-3>", self._show_menu)
        project_manager.canvas.tag_bind(
            self.priority_text,
            "<Double-Button-1>",
            lambda event: self._edit_priority(event, transition_tag),
        )
        project_manager.canvas.tag_lower(self.transition_id)
        if project_manager.canvas.find_withtag("grid_line"):
            project_manager.canvas.tag_raise(self.transition_id, "grid_line")
        project_manager.canvas.tag_raise(self.priority_text)
        TransitionLine.ref_dict[self.transition_id] = self

    def _determine_position_of_priority_rectangle(self, transition_coords):
        # Determine middle of the priority rectangle position by calculating a shortened transition:
        priority_middle_x, priority_middle_y, _, _ = TransitionLine.shorten_vector(
            project_manager.priority_distance,
            transition_coords[0],
            transition_coords[1],
            0,
            transition_coords[2],
            transition_coords[3],
            1,
            0,
        )
        return priority_middle_x, priority_middle_y

    def _show_menu(self, event) -> None:
        listbox = OptionMenu(
            project_manager.canvas,
            ["add condition&action", "straighten shape"],
            height=2,
            bg="lightgrey",
            width=21,
            activestyle="dotbox",
            relief=tk.RAISED,
        )
        [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        window = project_manager.canvas.create_window(event_x + 40, event_y, window=listbox)
        listbox.bind(
            "<Button-1>",
            lambda event, window=window, listbox=listbox, menu_x=event_x, menu_y=event_y: self._evaluate_menu(
                event, window, listbox, menu_x, menu_y
            ),
        )
        listbox.bind("<Leave>", lambda event, window=window, listbox=listbox: self._close_menu(event, window, listbox))

    def _evaluate_menu(
        self,
        _event,
        window,
        listbox,
        menu_x,
        menu_y,
    ) -> None:
        design_was_changed = False
        selected_entry = listbox.get(listbox.curselection())
        if selected_entry == "add condition&action":
            transition_tags = project_manager.canvas.gettags(self.transition_id)
            has_condition_action = False
            connected_to_reset_entry = False
            for tag in transition_tags:
                if tag.startswith("ca_connection"):
                    has_condition_action = True
                elif tag == "coming_from_reset_entry":
                    connected_to_reset_entry = True
            if has_condition_action is False:
                transition_coords = project_manager.canvas.coords(self.transition_id)
                line_coords = [menu_x, menu_y, transition_coords[0], transition_coords[1]]
                # Incrementing of conditionaction_id is needed, as in old versions of HFE first conditionaction_id was
                # incremented and afterwards the tags were created by reading this new value:
                project_manager.canvas.addtag_withtag(
                    "ca_connection" + str(condition_action.ConditionAction.conditionaction_id + 1) + "_end",
                    self.transition_id,
                )
                tags = [
                    "condition_action" + str(condition_action.ConditionAction.conditionaction_id + 1),
                    "ca_connection" + str(condition_action.ConditionAction.conditionaction_id + 1) + "_anchor",
                ]
                if connected_to_reset_entry:
                    tags.append("connected_to_reset_transition")
                transition_tags = project_manager.canvas.gettags(self.transition_id)
                line_tags = [
                    "ca_connection" + str(condition_action.ConditionAction.conditionaction_id + 1),
                    "connected_to_" + transition_tags[0],
                ]
                condition_action_ref = condition_action.ConditionAction(
                    menu_x,
                    menu_y,
                    connected_to_reset_entry,
                    height=1,
                    width=8,
                    padding=1,
                    tags=tags,
                    condition="",
                    action="",
                    line_coords=line_coords,
                    line_tags=line_tags,
                    increment=True,
                )
                condition_action_ref.condition_id.focus()  # Puts the text input cursor into the text box.
                design_was_changed = True
        elif selected_entry == "straighten shape":
            transition_tags = project_manager.canvas.gettags(self.transition_id)
            start_state_radius = 0
            end_state_radius = 0
            for tag in transition_tags:
                if tag.startswith("transition"):
                    transition_tag = tag
                    TransitionLine.extend_transition_to_state_middle_points(transition_tag)
                elif tag.startswith("coming_from_"):
                    start_state = tag.replace("coming_from_", "")
                    if start_state == "reset_entry":
                        start_state_radius = 0
                    else:
                        start_state_coords = project_manager.canvas.coords(start_state)
                        start_state_radius = abs(start_state_coords[2] - start_state_coords[0]) / 2
                elif tag.startswith("going_to_"):
                    end_state = tag.replace("going_to_", "")
                    end_state_coords = project_manager.canvas.coords(end_state)
                    end_state_radius = abs(end_state_coords[2] - end_state_coords[0]) / 2
            old_coords = project_manager.canvas.coords(self.transition_id)
            new_coords = []
            new_coords.append(old_coords[0])
            new_coords.append(old_coords[1])
            new_coords.append(old_coords[-2])
            new_coords.append(old_coords[-1])
            new_coords = TransitionLine.shorten_vector(
                start_state_radius, new_coords[0], new_coords[1], end_state_radius, new_coords[2], new_coords[3], 1, 1
            )
            project_manager.canvas.coords(self.transition_id, new_coords)
            # Calculates the position of the priority rectangle by shortening the distance between the first point of
            # the transition and the second point of the transition.
            [priority_middle_x, priority_middle_y, _, _] = TransitionLine.shorten_vector(
                project_manager.priority_distance, new_coords[0], new_coords[1], 0, new_coords[2], new_coords[3], 1, 0
            )
            [rectangle_width_half, rectangle_height_half] = TransitionLine.get_rectangle_dimensions(
                transition_tag + "rectangle"
            )
            project_manager.canvas.coords(
                transition_tag + "rectangle",
                priority_middle_x - rectangle_width_half,
                priority_middle_y - rectangle_height_half,
                priority_middle_x + rectangle_width_half,
                priority_middle_y + rectangle_height_half,
            )
            project_manager.canvas.coords(transition_tag + "priority", priority_middle_x, priority_middle_y)
            project_manager.canvas.tag_raise(transition_tag + "rectangle", transition_tag)
            project_manager.canvas.tag_raise(transition_tag + "priority", transition_tag + "rectangle")
            design_was_changed = True
        listbox.destroy()
        project_manager.canvas.delete(window)
        if design_was_changed:
            undo_handling.design_has_changed()  # It must be waited until the window for the menu is deleted.

    def _close_menu(self, _event, window, listbox) -> None:
        listbox.destroy()
        project_manager.canvas.delete(window)

    def _edit_priority(self, event, transition_tag) -> None:
        project_manager.canvas.unbind("<Button-1>")
        project_manager.canvas.unbind_all("<Delete>")
        priority_tag = transition_tag + "priority"
        old_text = project_manager.canvas.itemcget(priority_tag, "text")
        text_box = tk.Entry(project_manager.canvas, width=10, justify=tk.CENTER)
        text_box.insert(tk.END, old_text)
        text_box.select_range(0, tk.END)
        text_box.bind(
            "<Return>",
            lambda event, transition_tag=transition_tag, text_box=text_box: self._update_priority(
                transition_tag, text_box
            ),
        )
        text_box.bind(
            "<Escape>",
            lambda event, transition_tag=transition_tag, text_box=text_box, old_text=old_text: self._abort_edit_text(
                transition_tag, text_box, old_text
            ),
        )
        [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        project_manager.canvas.create_window(event_x, event_y, window=text_box, tag="entry-window")
        text_box.focus_set()

    def _update_priority(self, transition_tag, text_box) -> None:
        project_manager.canvas.delete("entry-window")
        project_manager.canvas.itemconfig(transition_tag + "priority", text=text_box.get())
        text_rectangle = project_manager.canvas.bbox(transition_tag + "priority")
        project_manager.canvas.coords(transition_tag + "rectangle", text_rectangle)
        text_box.destroy()
        project_manager.canvas.tag_raise(transition_tag + "rectangle", transition_tag)
        project_manager.canvas.tag_raise(transition_tag + "priority", transition_tag + "rectangle")
        undo_handling.design_has_changed()
        project_manager.canvas.bind("<Button-1>", move_handling_initialization.move_initialization)
        project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete())

    def _abort_edit_text(self, transition_tag, text_box, old_text) -> None:
        project_manager.canvas.delete("entry-window")
        project_manager.canvas.itemconfig(transition_tag + "priority", text=old_text)
        text_box.destroy()
        project_manager.canvas.tag_raise(transition_tag + "rectangle", transition_tag)
        project_manager.canvas.tag_raise(transition_tag + "priority", transition_tag + "rectangle")
        project_manager.canvas.bind("<Button-1>", move_handling_initialization.move_initialization)
        project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete())

    def delete(self) -> None:
        """Remove transition line, priority rect/text, tags, linked condition-action; update ref_dict and visibility."""
        transition_tags = project_manager.canvas.gettags(self.transition_id)
        project_manager.canvas.delete(self.transition_id)
        project_manager.canvas.delete(self.priority_text)
        project_manager.canvas.delete(self.priority_rectangle)
        project_manager.canvas.dtag("all", transition_tags[0] + "_start")  # delete: "transition"<integer>"_start"
        project_manager.canvas.dtag("all", transition_tags[0] + "_end")  # delete: "transition"<integer>"_end"
        for transition_tag in transition_tags:
            if transition_tag.startswith("ca_connection"):
                ca_window_anchor_tag = transition_tag[:-4] + "_anchor"
                ca_window_canvas_id = project_manager.canvas.find_withtag(ca_window_anchor_tag)[0]
                ref = condition_action.ConditionAction.ref_dict[ca_window_canvas_id]
                ref.delete()
            if transition_tag.startswith("coming_from_"):
                start_state = transition_tag[12:]
                TransitionLine.adapt_visibility_of_priority_rectangles_at_state(start_state)
        del TransitionLine.ref_dict[self.transition_id]

    @classmethod
    def adapt_visibility_of_priority_rectangles_at_state(cls, start_state) -> None:
        """Hide priority rect/text for the single outgoing transition from start_state; show if multiple."""
        tags_of_start_state = project_manager.canvas.gettags(start_state)
        number_of_outgoing_transitions = 0
        tag_of_outgoing_transition = ""
        for start_state_tag in tags_of_start_state:
            if start_state_tag.startswith("transition") and start_state_tag.endswith("_start"):
                number_of_outgoing_transitions += 1
                tag_of_outgoing_transition = start_state_tag.replace("_start", "")
        if number_of_outgoing_transitions == 1:
            project_manager.canvas.itemconfigure(tag_of_outgoing_transition + "rectangle", state=tk.HIDDEN)
            project_manager.canvas.itemconfigure(tag_of_outgoing_transition + "priority", state=tk.HIDDEN)

    @classmethod
    def move_to(cls, event_x, event_y, transition_id, point, first, move_list, last=False) -> None:
        """Move transition point (start/next_to_start/next_to_end/end) to (event_x, event_y);
        Records the move offset when first is True, else maintains the offset.
        Snaps to grid when last is True."""
        if project_manager.canvas.type(move_list[0][0]) == "line" and (move_list[0][1] in ("start", "end")):
            middle_of_line_is_moved = False
        else:
            middle_of_line_is_moved = True
        if middle_of_line_is_moved is True:
            if first is True:
                # Calculate the difference between the "anchor" point and the event:
                coords = project_manager.canvas.coords(transition_id)
                if point == "start":
                    point_to_move = [coords[0], coords[1]]
                elif point == "next_to_start":
                    point_to_move = [coords[2], coords[3]]
                elif point == "next_to_end":
                    point_to_move = [coords[-4], coords[-3]]
                elif point == "end":
                    point_to_move = [coords[-2], coords[-1]]
                else:
                    print("transition_handling: Fatal, unknown point =", point)
                    return
                cls.difference_x, cls.difference_y = -event_x + point_to_move[0], -event_y + point_to_move[1]
        else:
            cls.difference_x = 0
            cls.difference_y = 0
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + cls.difference_x, event_y + cls.difference_y
        if last is True:
            event_x = project_manager.state_radius * round(event_x / project_manager.state_radius)
            event_y = project_manager.state_radius * round(event_y / project_manager.state_radius)
        all_transition_tags = project_manager.canvas.gettags(transition_id)
        for single_transition_tag in all_transition_tags:
            if (
                single_transition_tag.startswith("transition")
                or single_transition_tag.startswith("connection")
                or single_transition_tag.endswith("comment_line")
            ):
                transition_tag = single_transition_tag
                project_manager.canvas.tag_lower(transition_tag)
        # Move transition:
        transition_coords = project_manager.canvas.coords(transition_tag)
        if point == "start":
            project_manager.canvas.coords(transition_tag, event_x, event_y, *transition_coords[2:])
        elif point == "next_to_start":
            project_manager.canvas.coords(
                transition_tag, *transition_coords[0:2], event_x, event_y, *transition_coords[4:]
            )
        elif point == "next_to_end":
            project_manager.canvas.coords(
                transition_tag, *transition_coords[-8:-4], event_x, event_y, *transition_coords[-2:]
            )
        elif point == "end":
            project_manager.canvas.coords(transition_tag, *transition_coords[-8:-2], event_x, event_y)
        else:
            print("transition_handling: Fatal, unknown point =", point)
        if project_manager.grid_drawer.show_grid:
            list_of_grid_line_canvas_ids = project_manager.canvas.find_withtag("grid_line")
            if list_of_grid_line_canvas_ids:
                project_manager.canvas.tag_raise(transition_tag, "grid_line")
        # Move priority rectangle:
        if transition_tag.startswith("transition"):  # There is no priority rectangle at a "connection".
            # The tag "transition_tag + '_start'" is already removed from the old start state when
            #  the transition start-point is moved. In all other cases the tag exists.
            # So try to get the coordinates of the start state (there the priority rectangle is positioned):
            start_state_coords = project_manager.canvas.coords(transition_tag + "_start")
            if point == "start":
                if (
                    start_state_coords == [] or project_manager.canvas.type(transition_tag + "_start") == "polygon"
                ):  # Transition start point is disconnected from its start state and moved alone.
                    start_state_radius = 0
                else:  #  State with connected transition is moved.
                    start_state_radius = abs(start_state_coords[2] - start_state_coords[0]) / 2
                # Calculates the position of the priority rectangle by shortening the vector from the
                # event (= first point of transition) to the second point of the transition.
                [priority_middle_x, priority_middle_y, _, _] = TransitionLine.shorten_vector(
                    start_state_radius + project_manager.priority_distance,
                    event_x,
                    event_y,
                    0,
                    transition_coords[2],
                    transition_coords[3],
                    1,
                    0,
                )
            else:
                # Calculates the position of the priority rectangle by shortening the first point of the
                # transition to the second point of the transition.
                start_state_radius = abs(start_state_coords[2] - start_state_coords[0]) / 2
                # Because the transition is already extended to the start-state middle, the length of the
                # vector must be shortened additionally by the start state radius,
                # to keep the priority outside of the start-state.
                [priority_middle_x, priority_middle_y, _, _] = TransitionLine.shorten_vector(
                    start_state_radius + project_manager.priority_distance,
                    transition_coords[0],
                    transition_coords[1],
                    0,
                    transition_coords[2],
                    transition_coords[3],
                    1,
                    0,
                )
            [rectangle_width_half, rectangle_height_half] = TransitionLine.get_rectangle_dimensions(
                transition_tag + "rectangle"
            )
            project_manager.canvas.coords(
                transition_tag + "rectangle",
                priority_middle_x - rectangle_width_half,
                priority_middle_y - rectangle_height_half,
                priority_middle_x + rectangle_width_half,
                priority_middle_y + rectangle_height_half,
            )
            project_manager.canvas.coords(transition_tag + "priority", priority_middle_x, priority_middle_y)
            project_manager.canvas.tag_raise(transition_tag + "rectangle", transition_tag)
            project_manager.canvas.tag_raise(transition_tag + "priority", transition_tag + "rectangle")

    @classmethod
    def extend_transition_to_state_middle_points(cls, transition_tag) -> None:
        """Set transition start/end to center of connected state/connector; lower line under states."""
        transition_coords = project_manager.canvas.coords(transition_tag)
        end_state_coords = project_manager.canvas.coords(transition_tag + "_end")
        if transition_tag.startswith(
            "transition"
        ):  # When transition_tag starts with "connection" no start point is needed.
            start_coords = project_manager.canvas.coords(
                transition_tag + "_start"
            )  # Coords are from a circle (state) or from a connector (rectangle) or from the reset entry (polygon).
            if (
                project_manager.canvas.type(transition_tag + "_start") != "polygon"
            ):  # At the reset entry the transition start point is not modified for moving.
                transition_coords[0] = (start_coords[0] + start_coords[2]) // 2
                transition_coords[1] = (start_coords[1] + start_coords[3]) // 2
        transition_coords[-2] = (end_state_coords[0] + end_state_coords[2]) // 2
        transition_coords[-1] = (end_state_coords[1] + end_state_coords[3]) // 2
        project_manager.canvas.coords(transition_tag, *transition_coords)
        # Hide the line "under" the states:
        project_manager.canvas.tag_lower(transition_tag, transition_tag + "_start")
        project_manager.canvas.tag_lower(transition_tag, transition_tag + "_end")

    @classmethod
    def determine_priorities_of_outgoing_transitions(cls, start_state_canvas_id) -> dict:
        """Return dict mapping transition_tag -> priority text for all transitions starting at start_state_canvas_id."""
        priority_dict = {}
        all_tags = project_manager.canvas.gettags(start_state_canvas_id)
        for tag in all_tags:
            if tag.startswith("transition") and tag.endswith("_start"):
                transition_tag = tag[:-6]
                priority_dict[transition_tag] = project_manager.canvas.itemcget(transition_tag + "priority", "text")
        return priority_dict

    @classmethod
    def shorten_to_state_border(cls, transition_tag) -> None:
        """Shorten transition line to state borders, remove duplicate points, reposition priority rect."""
        transition_coords = project_manager.canvas.coords(transition_tag)
        tag_list = project_manager.canvas.gettags(transition_tag)
        connection = False
        start_state_tag = None
        end_state_tag = None
        for tag in tag_list:
            if tag.startswith("coming_from_"):
                start_state_tag = tag[12:]
            elif tag.startswith("going_to_"):
                end_state_tag = tag[9:]
            elif tag.startswith("connected_to_"):
                connection = True
                end_state_tag = tag[13:]
        if connection is False:
            start_state_coords = project_manager.canvas.coords(start_state_tag)
            end_state_coords = project_manager.canvas.coords(end_state_tag)
            if start_state_tag == "reset_entry":
                start_state_radius = 0
            else:
                start_state_radius = (start_state_coords[2] - start_state_coords[0]) / 2
            end_state_radius = (end_state_coords[2] - end_state_coords[0]) / 2
            transition_start_coords = TransitionLine.shorten_vector(
                start_state_radius,
                transition_coords[0],
                transition_coords[1],
                0,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
            transition_end_coords = TransitionLine.shorten_vector(
                0,
                transition_coords[-4],
                transition_coords[-3],
                end_state_radius,
                transition_coords[-2],
                transition_coords[-1],
                0,
                1,
            )
            transition_coords[0] = transition_start_coords[0]
            transition_coords[1] = transition_start_coords[1]
            transition_coords[-2] = transition_end_coords[-2]
            transition_coords[-1] = transition_end_coords[-1]
            transition_coords = TransitionLine.remove_duplicate_points(transition_coords)
            project_manager.canvas.coords(transition_tag, transition_coords)
            project_manager.canvas.tag_lower(transition_tag)
            # Move priority rectangle:
            start_state_radius = abs(start_state_coords[2] - start_state_coords[0]) / 2
            [priority_middle_x, priority_middle_y, _, _] = TransitionLine.shorten_vector(
                0 + project_manager.priority_distance,
                transition_coords[0],
                transition_coords[1],
                0,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
            [rectangle_width_half, rectangle_height_half] = TransitionLine.get_rectangle_dimensions(
                transition_tag + "rectangle"
            )
            project_manager.canvas.coords(
                transition_tag + "rectangle",
                priority_middle_x - rectangle_width_half,
                priority_middle_y - rectangle_height_half,
                priority_middle_x + rectangle_width_half,
                priority_middle_y + rectangle_height_half,
            )
            project_manager.canvas.coords(transition_tag + "priority", priority_middle_x, priority_middle_y)
            list_of_grid_line_canvas_ids = project_manager.canvas.find_withtag("grid_line")
            if list_of_grid_line_canvas_ids:
                project_manager.canvas.tag_raise(transition_tag, "grid_line")
        else:
            end_state_coords = project_manager.canvas.coords(end_state_tag)
            end_state_radius = (end_state_coords[2] - end_state_coords[0]) / 2

            transition_end_coords = TransitionLine.shorten_vector(
                0,
                transition_coords[-4],
                transition_coords[-3],
                end_state_radius,
                transition_coords[-2],
                transition_coords[-1],
                0,
                1,
            )
            transition_coords[-2] = transition_end_coords[-2]
            transition_coords[-1] = transition_end_coords[-1]
            project_manager.canvas.coords(transition_tag, transition_coords)
            project_manager.canvas.tag_lower(transition_tag)

    @classmethod
    def remove_duplicate_points(cls, transition_coords) -> list:
        """Return coords list with consecutive duplicate points removed."""
        new_transition_coords = []
        new_transition_coords.append(transition_coords[0])
        new_transition_coords.append(transition_coords[1])
        for i in range(int(len(transition_coords) / 2) - 1):
            if (
                transition_coords[2 * i] != transition_coords[2 * i + 2]
                or transition_coords[2 * i + 1] != transition_coords[2 * i + 3]
            ):
                new_transition_coords.append(transition_coords[2 * i + 2])
                new_transition_coords.append(transition_coords[2 * i + 3])
        return new_transition_coords

    @classmethod
    def get_rectangle_dimensions(cls, canvas_id) -> list:
        """Return [width_half, height_half] for the rectangle canvas item."""
        rectangle_coords = project_manager.canvas.coords(canvas_id)
        rectangle_width_half = (rectangle_coords[2] - rectangle_coords[0]) / 2
        rectangle_height_half = (rectangle_coords[3] - rectangle_coords[1]) / 2
        return [rectangle_width_half, rectangle_height_half]

    @classmethod
    def hide_priority_of_single_outgoing_transitions(cls) -> None:
        """Hide priority rect/text where a state has only one outgoing transition; show where multiple."""
        canvas_ids = project_manager.canvas.find_all()
        for canvas_id in canvas_ids:
            if project_manager.canvas.type(canvas_id) in [
                "oval",
                "polygon",
                "rectangle",
            ]:  # state, reset_entry, connector
                tags = project_manager.canvas.gettags(canvas_id)
                outgoing_transition_tags = []
                for tag in tags:
                    if tag.startswith("transition") and tag.endswith("_start"):
                        outgoing_transition_tags.append(tag[:-6])
                if len(outgoing_transition_tags) == 1:
                    project_manager.canvas.itemconfigure(outgoing_transition_tags[0] + "priority", state=tk.HIDDEN)
                    project_manager.canvas.itemconfigure(outgoing_transition_tags[0] + "rectangle", state=tk.HIDDEN)
                else:
                    for outgoing_transition_tag in outgoing_transition_tags:
                        project_manager.canvas.itemconfigure(outgoing_transition_tag + "priority", state=tk.NORMAL)
                        project_manager.canvas.itemconfigure(outgoing_transition_tag + "rectangle", state=tk.NORMAL)

    @classmethod
    def shorten_vector(cls, delta0, x0, y0, delta1, x1, y1, modify0, modify1) -> list:
        """Return [x0', y0', x1', y1'] shortening (x0,y0)->(x1,y1) by delta0 at start and delta1 at end (modify flags)."""
        phi = math.pi / 2 if x1 - x0 == 0 else math.atan((y1 - y0) / (x1 - x0))
        phi = abs(phi)
        delta0_x = delta0 * math.cos(phi)
        delta0_y = delta0 * math.sin(phi)
        delta1_x = delta1 * math.cos(phi)
        delta1_y = delta1 * math.sin(phi)
        if y1 >= y0 and x1 >= x0:
            return [x0 + delta0_x * modify0, y0 + delta0_y * modify0, x1 - delta1_x * modify1, y1 - delta1_y * modify1]
        if y1 >= y0 and x1 < x0:
            return [x0 - delta0_x * modify0, y0 + delta0_y * modify0, x1 + delta1_x * modify1, y1 - delta1_y * modify1]
        if y1 < y0 and x1 >= x0:
            return [x0 + delta0_x * modify0, y0 - delta0_y * modify0, x1 - delta1_x * modify1, y1 + delta1_y * modify1]
        return [x0 - delta0_x * modify0, y0 - delta0_y * modify0, x1 + delta1_x * modify1, y1 + delta1_y * modify1]

    @classmethod
    def transition_start(cls, event) -> None:
        """Begin new transition from item under cursor (state/reset/connector); bind Motion and ButtonRelease."""
        [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        ids = project_manager.canvas.find_overlapping(event_x, event_y, event_x, event_y)
        if ids != ():
            for canvas_id in ids:
                element_type = project_manager.canvas.type(canvas_id)
                if cls._is_legal_start_point(canvas_id, element_type):
                    line_start_x, line_start_y = cls._determine_transition_start_point(canvas_id, element_type)
                    transition_id = project_manager.canvas.create_line(
                        [line_start_x, line_start_y, line_start_x, line_start_y],
                        arrow="last",
                        fill="blue",
                        smooth=True,
                    )
                    project_manager.canvas.tag_lower(transition_id)  # Line should be under states/connectors
                    transition_draw_funcid = project_manager.canvas.bind(
                        "<Motion>",
                        lambda event, transition_id=transition_id: cls._transition_continue(event, transition_id),
                        add="+",
                    )
                    transition_start_object_tag = cls._get_tag_of_start_object(canvas_id)
                    project_manager.canvas.bind(
                        "<Button-1>",
                        lambda event,
                        transition_id=transition_id,
                        canvas_id_of_start_item=canvas_id,
                        transition_draw_funcid=transition_draw_funcid,
                        transition_start_object_tag=transition_start_object_tag: (
                            cls._handle_next_added_transition_point(
                                event,
                                transition_id,
                                canvas_id_of_start_item,
                                transition_draw_funcid,
                                transition_start_object_tag,
                            )
                        ),
                    )
                    project_manager.root.bind_all(
                        "<Escape>",
                        lambda event,
                        transition_id=transition_id,
                        transition_draw_funcid=transition_draw_funcid: cls._end_inserting_transition(
                            transition_id, transition_draw_funcid
                        ),
                    )

    @classmethod
    def _is_legal_start_point(cls, canvas_id, element_type) -> bool:
        return (
            element_type == "oval"
            or (element_type == "polygon" and cls._reset_entry_has_no_transition(canvas_id))
            or (element_type == "rectangle" and project_manager.canvas.gettags(canvas_id)[0].startswith("connector"))
        )

    @classmethod
    def _determine_transition_start_point(cls, canvas_id, element_type) -> tuple[float, float]:
        start_object_coords = project_manager.canvas.coords(canvas_id)
        if element_type in ["oval", "rectangle"]:
            line_start_x = start_object_coords[0] / 2 + start_object_coords[2] / 2
            line_start_y = start_object_coords[1] / 2 + start_object_coords[3] / 2
        else:  # polygon, this means reset-entry
            line_start_x = start_object_coords[4]
            line_start_y = start_object_coords[5]
        return line_start_x, line_start_y

    @classmethod
    def _get_tag_of_start_object(cls, canvas_id):
        for tag in project_manager.canvas.gettags(canvas_id):
            if (
                (tag.startswith("state") and not tag.endswith("_comment_line_end"))
                or tag.startswith("connector")
                or tag.startswith("reset_entry")
            ):
                transition_start_object_tag = tag
                break
        return transition_start_object_tag

    @classmethod
    def _reset_entry_has_no_transition(cls, canvas_id) -> bool:
        tags_of_reset_entry = project_manager.canvas.gettags(canvas_id)
        return all(not tag.startswith("transition") for tag in tags_of_reset_entry)

    @classmethod
    def _transition_continue(cls, event, canvas_id) -> None:
        [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        coords_new = project_manager.canvas.coords(canvas_id)
        coords_new[-2] = event_x
        coords_new[-1] = event_y
        project_manager.canvas.coords(canvas_id, coords_new)

    @classmethod
    def _handle_next_added_transition_point(
        cls, event, transition_id, start_state_canvas_id, transition_draw_funcid, transition_start_object_tag
    ) -> None:
        [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        transition_coords = project_manager.canvas.coords(transition_id)
        end_state_canvas_id = cls._get_canvas_id_of_state_or_connector_under_new_transition_point(event_x, event_y)
        transition_ends_at_connector = cls._check_if_transition_ends_at_connector(end_state_canvas_id)
        if end_state_canvas_id is None:
            if len(transition_coords) < 8:  # An additional intermediate point is added to the transition.
                cls._add_next_transition_point_(transition_id, transition_coords, event_x, event_y)
        elif transition_start_object_tag == "reset_entry" and transition_ends_at_connector is True:
            return
        elif end_state_canvas_id == start_state_canvas_id and len(transition_coords) == 4:
            # Going back to the start state with only 2 points cannot be drawn. The transition point is not accepted.
            return
        else:
            project_manager.canvas.addtag_withtag(  # Add tag to start object
                "transition" + str(TransitionLine.transition_number) + "_start",
                start_state_canvas_id,
            )
            project_manager.canvas.addtag_withtag(  # Add tag to end object
                "transition" + str(TransitionLine.transition_number) + "_end", end_state_canvas_id
            )
            # Create tags for line:
            end_state_tags = project_manager.canvas.gettags(end_state_canvas_id)
            for tag in end_state_tags:
                if (tag.startswith("state") and not tag.endswith("_comment_line_end")) or tag.startswith("connector"):
                    end_state_tag = tag
                    break
            tags = [
                "transition" + str(TransitionLine.transition_number),
                "coming_from_" + transition_start_object_tag,
                "going_to_" + end_state_tag,
            ]
            transition_coords = cls._move_transition_end_point_to_the_middle_of_the_end_state(
                end_state_canvas_id, transition_id
            )
            transition_coords = cls._move_transition_start_and_end_point_to_the_edge_of_the_state_circle(
                start_state_canvas_id, end_state_canvas_id, transition_id
            )
            priority_dict = TransitionLine.determine_priorities_of_outgoing_transitions(start_state_canvas_id)
            unused_priority = cls._get_unused_priority(priority_dict)
            cls._end_inserting_transition(transition_id, transition_draw_funcid)
            TransitionLine(transition_coords, tags, unused_priority, new_transition=True)
            TransitionLine.hide_priority_of_single_outgoing_transitions()
            undo_handling.design_has_changed()

    @classmethod
    def _end_inserting_transition(cls, transition_id, transition_draw_funcid) -> None:
        project_manager.canvas.delete(transition_id)
        # Restore bindings:
        project_manager.canvas.unbind("<Motion>", transition_draw_funcid)
        project_manager.canvas.bind("<Button-1>", cls.transition_start)
        project_manager.root.bind_all("<Escape>", lambda event: canvas_modify_bindings.switch_to_move_mode())

    @classmethod
    def _get_canvas_id_of_state_or_connector_under_new_transition_point(cls, event_x, event_y) -> None:
        for canvas_id in project_manager.canvas.find_overlapping(event_x, event_y, event_x, event_y):
            element_type = project_manager.canvas.type(canvas_id)
            if (element_type == "oval") or (
                element_type == "rectangle" and project_manager.canvas.gettags(canvas_id)[0].startswith("connector")
            ):
                return canvas_id
        return None

    @classmethod
    def _check_if_transition_ends_at_connector(cls, end_state_canvas_id) -> bool:
        if end_state_canvas_id is not None:
            end_state_tags = project_manager.canvas.gettags(end_state_canvas_id)
            for tag in end_state_tags:
                if tag.startswith("connector"):
                    return True
        return False

    @classmethod
    def _add_next_transition_point_(cls, transition_id, coords, event_x, event_y) -> None:
        coords.append(event_x)
        coords.append(event_y)
        project_manager.canvas.coords(transition_id, coords)

    @classmethod
    def _move_transition_end_point_to_the_middle_of_the_end_state(cls, end_state_canvas_id, transition_id):
        end_state_coords = project_manager.canvas.coords(end_state_canvas_id)
        end_state_middle_x = end_state_coords[0] / 2 + end_state_coords[2] / 2
        end_state_middle_y = end_state_coords[1] / 2 + end_state_coords[3] / 2
        transition_coords = project_manager.canvas.coords(transition_id)
        transition_coords[-2] = end_state_middle_x
        transition_coords[-1] = end_state_middle_y
        project_manager.canvas.coords(transition_id, transition_coords)
        return transition_coords

    @classmethod
    def _move_transition_start_and_end_point_to_the_edge_of_the_state_circle(
        cls, start_state_canvas_id, end_state_canvas_id, transition_id
    ):
        start_object_coords = project_manager.canvas.coords(start_state_canvas_id)
        transition_coords = project_manager.canvas.coords(transition_id)
        end_state_coords = project_manager.canvas.coords(end_state_canvas_id)
        start_state_radius = abs(start_object_coords[2] - start_object_coords[0]) // 2
        end_state_radius = abs(end_state_coords[2] - end_state_coords[0]) // 2
        if len(start_object_coords) == 10:  # start-state is reset-entry
            start_state_radius = 0
        if len(transition_coords) == 4:
            vector1 = TransitionLine.shorten_vector(
                start_state_radius,
                transition_coords[0],
                transition_coords[1],
                end_state_radius,
                transition_coords[-2],
                transition_coords[-1],
                1,
                1,
            )
            vector2 = vector1
        elif len(transition_coords) == 6:
            vector1 = TransitionLine.shorten_vector(
                start_state_radius,
                transition_coords[0],
                transition_coords[1],
                end_state_radius,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
            vector2 = TransitionLine.shorten_vector(
                start_state_radius,
                transition_coords[2],
                transition_coords[3],
                end_state_radius,
                transition_coords[-2],
                transition_coords[-1],
                0,
                1,
            )
        else:  # len(transition_coords)==8
            vector1 = TransitionLine.shorten_vector(
                start_state_radius,
                transition_coords[0],
                transition_coords[1],
                end_state_radius,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
            vector2 = TransitionLine.shorten_vector(
                start_state_radius,
                transition_coords[4],
                transition_coords[5],
                end_state_radius,
                transition_coords[-2],
                transition_coords[-1],
                0,
                1,
            )
        transition_coords[0] = vector1[0]
        transition_coords[1] = vector1[1]
        transition_coords[-2] = vector2[2]
        transition_coords[-1] = vector2[3]
        project_manager.canvas.coords(transition_id, transition_coords)
        return transition_coords

    @classmethod
    def _get_unused_priority(cls, priority_dict) -> str:
        priority_of_new_transition = "1"
        used_priorities = []
        for key in priority_dict:
            used_priorities.append(priority_dict[key])
        while True:
            if priority_of_new_transition in used_priorities:
                priority_of_new_transition = str(int(priority_of_new_transition) + 1)
            else:
                return priority_of_new_transition

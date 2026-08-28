"""
Module handling transitions on the canvas.
"""

import math
import tkinter as tk

import constants
from actions import canvas_delete, canvas_editing, canvas_modify_bindings, move_handling_initialization
from elements import condition_action
from project_manager import project_manager


class TransitionLine:
    """
    For each transition at the Canvas a TransitionLine object is created.
    """

    transition_number = 0
    ref_dict = {}
    delta_dict = {}
    diff_dict = {}

    # A new transition object is created by the create() method of the TransitionLine class (see end of file).
    def __init__(self, transition_coords, tags, priority) -> None:
        self.difference_x = 0
        self.difference_y = 0
        self.phi_last = 0
        rectangle_coords = self._determine_position_of_priority_rectangle(transition_coords)
        self.transition_tag = tags[0]  # "transition<n>"
        self.transition_id = project_manager.canvas.create_line(
            transition_coords, arrow="last", fill="blue", smooth=True, tags=tags
        )
        self.priority_text = project_manager.canvas.create_text(
            rectangle_coords,
            text=priority,
            tag=self.transition_tag + "priority",
            font=project_manager.state_name_font,
        )
        self.priority_rectangle = project_manager.canvas.create_rectangle(
            project_manager.canvas.bbox(self.priority_text),
            tag=self.transition_tag + "rectangle",
            fill=constants.STATE_COLOR,
        )
        project_manager.canvas.tag_bind(
            self.transition_tag,
            "<Enter>",
            lambda event: project_manager.canvas.itemconfig(self.transition_tag, width=3),
        )
        project_manager.canvas.tag_bind(
            self.transition_tag,
            "<Leave>",
            lambda event: project_manager.canvas.itemconfig(self.transition_tag, width=1),
        )
        project_manager.canvas.tag_bind(self.transition_tag, "<ButtonRelease-3>", self._show_menu)
        project_manager.canvas.tag_bind(self.priority_text, "<Double-Button-1>", self._edit_priority)
        project_manager.canvas.tag_lower(self.transition_tag)
        if project_manager.canvas.find_withtag("grid_line"):
            project_manager.canvas.tag_raise(self.transition_tag, "grid_line")
        project_manager.canvas.tag_raise(self.priority_text)
        TransitionLine.ref_dict[self.transition_id] = self
        TransitionLine.transition_number += 1

    def _determine_position_of_priority_rectangle(self, transition_coords):
        # Determine middle of the priority rectangle position by calculating a shortened transition:
        priority_middle_x, priority_middle_y, _, _ = TransitionLine._shorten_vector(
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
        menu = tk.Menu(project_manager.canvas, tearoff=0)
        menu.add_command(label="add condition&action", command=lambda: self._add_condition_action(event))
        if TransitionLine._is_loopback_transition(self.transition_tag):
            menu.add_command(label="rotate loopback transition", command=self._rotate_loopback_transition_init)
        else:
            menu.add_command(label="straighten shape", command=self._straighten_shape)
        menu.tk_popup(event.x_root, event.y_root)

    def _add_condition_action(self, event) -> None:
        has_condition_action = False
        connected_to_reset_entry = False
        for tag in project_manager.canvas.gettags(self.transition_tag):
            if tag.startswith("ca_connection"):
                has_condition_action = True
            elif tag == "coming_from_reset_entry":
                connected_to_reset_entry = True
        if not has_condition_action:
            [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
            condition_action.ConditionAction.create(self.transition_tag, event_x, event_y, connected_to_reset_entry)
            project_manager.undo_handling_ref.design_has_changed()

    def _rotate_loopback_transition_init(self) -> None:  # called by menu entry
        TransitionLine.extend_transition_to_state_middle_points(self.transition_tag)
        project_manager.canvas.itemconfig(self.transition_tag, width=3)
        start_x, start_y = self._calculate_canvas_coords_of_menu_mouse_click_event()
        coords = project_manager.canvas.coords(self.transition_tag)
        vector_from_state_middle_point_to_cursor = [-coords[0] + start_x, -coords[1] + start_y]
        self.phi_last = self._calculate_angle_of_vector(vector_from_state_middle_point_to_cursor)
        project_manager.canvas.bind(
            "<Motion>", lambda event: self._rotate_loopback_transition(event, coords[0], coords[1])
        )
        project_manager.canvas.bind(
            "<Button-1>", lambda event: self._rotate_loopback_transition_stop(event, coords, abort=False)
        )
        project_manager.canvas.bind(
            "<Escape>", lambda event: self._rotate_loopback_transition_stop(event, coords, abort=True)
        )

    def _calculate_canvas_coords_of_menu_mouse_click_event(self) -> tuple[float, float]:
        pointer_x_in_canvas = project_manager.canvas.winfo_pointerx() - project_manager.canvas.winfo_rootx()
        pointer_y_in_canvas = project_manager.canvas.winfo_pointery() - project_manager.canvas.winfo_rooty()
        start_x = project_manager.canvas.canvasx(pointer_x_in_canvas)
        start_y = project_manager.canvas.canvasy(pointer_y_in_canvas)
        return start_x, start_y

    def _calculate_angle_of_vector(self, vector) -> float:
        """Calculate angle between x-axis and vector in radians."""
        x, y = vector
        return math.atan2(y, x)

    def _rotate_loopback_transition(self, event, state_middle_x, state_middle_y) -> None:
        cursor_x, cursor_y = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        vector_from_state_middle_point_to_cursor = [-state_middle_x + cursor_x, -state_middle_y + cursor_y]
        phi = self._calculate_angle_of_vector(vector_from_state_middle_point_to_cursor)
        delta_phi = phi - self.phi_last
        self._rotate_transition_by(delta_phi)
        self.phi_last = phi
        TransitionLine._move_priority_rectangle(
            cursor_x,
            cursor_y,
            self.transition_tag,
            project_manager.canvas.coords(self.transition_tag),
            "end",
        )

    def _rotate_loopback_transition_stop(self, event, old_coords, abort) -> None:
        project_manager.canvas.unbind("<Motion>")
        project_manager.canvas.unbind("<Button-1>")
        project_manager.canvas.itemconfig(self.transition_tag, width=1)
        canvas_modify_bindings.switch_to_move_mode()
        if abort:
            project_manager.canvas.coords(self.transition_tag, old_coords)
        TransitionLine.shorten_to_state_border(self.transition_tag)
        if not abort:
            project_manager.undo_handling_ref.design_has_changed()

    def _rotate_transition_by(self, delta_phi) -> None:
        coords = project_manager.canvas.coords(self.transition_tag)
        vector_from_start_to_second_x = coords[2] - coords[0]
        vector_from_start_to_second_y = coords[3] - coords[1]
        vector_from_start_to_third_x = coords[4] - coords[0]
        vector_from_start_to_third_y = coords[5] - coords[1]
        vector_from_start_to_second_rotated_x = (vector_from_start_to_second_x * math.cos(delta_phi)) - (
            vector_from_start_to_second_y * math.sin(delta_phi)
        )
        vector_from_start_to_second_rotated_y = (vector_from_start_to_second_x * math.sin(delta_phi)) + (
            vector_from_start_to_second_y * math.cos(delta_phi)
        )
        vector_from_start_to_third_rotated_x = (vector_from_start_to_third_x * math.cos(delta_phi)) - (
            vector_from_start_to_third_y * math.sin(delta_phi)
        )
        vector_from_start_to_third_rotated_y = (vector_from_start_to_third_x * math.sin(delta_phi)) + (
            vector_from_start_to_third_y * math.cos(delta_phi)
        )
        project_manager.canvas.coords(
            self.transition_tag,
            coords[0],
            coords[1],
            coords[0] + vector_from_start_to_second_rotated_x,
            coords[1] + vector_from_start_to_second_rotated_y,
            coords[0] + vector_from_start_to_third_rotated_x,
            coords[1] + vector_from_start_to_third_rotated_y,
            coords[6],
            coords[7],
        )

    def _straighten_shape(self) -> None:
        start_state_radius = 0
        end_state_radius = 0
        for tag in project_manager.canvas.gettags(self.transition_tag):
            if tag.startswith("coming_from_"):
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
        self._straighten_transition(start_state_radius, end_state_radius)
        project_manager.undo_handling_ref.design_has_changed()

    def _edit_priority(self, event) -> None:
        project_manager.canvas.unbind("<Button-1>")
        project_manager.canvas.unbind_all("<Delete>")
        priority_tag = self.transition_tag + "priority"
        old_text = project_manager.canvas.itemcget(priority_tag, "text")
        text_box = tk.Entry(project_manager.canvas, width=10, justify=tk.CENTER)
        text_box.insert(tk.END, old_text)
        text_box.select_range(0, tk.END)
        text_box.bind("<Return>", lambda event, text_box=text_box: self._update_priority(text_box))
        text_box.bind(
            "<Escape>", lambda event, text_box=text_box, old_text=old_text: self._abort_edit_text(text_box, old_text)
        )
        [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        project_manager.canvas.create_window(event_x, event_y, window=text_box, tag="entry-window")
        text_box.focus_set()

    def _update_priority(self, text_box) -> None:
        project_manager.canvas.delete("entry-window")
        project_manager.canvas.itemconfig(self.transition_tag + "priority", text=text_box.get())
        text_rectangle = project_manager.canvas.bbox(self.transition_tag + "priority")
        project_manager.canvas.coords(self.transition_tag + "rectangle", text_rectangle)
        text_box.destroy()
        project_manager.canvas.tag_raise(self.transition_tag + "rectangle", self.transition_tag)
        project_manager.canvas.tag_raise(self.transition_tag + "priority", self.transition_tag + "rectangle")
        project_manager.undo_handling_ref.design_has_changed()
        project_manager.canvas.bind("<Button-1>", move_handling_initialization.move_initialization)
        project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete())

    def _abort_edit_text(self, text_box, old_text) -> None:
        project_manager.canvas.delete("entry-window")
        project_manager.canvas.itemconfig(self.transition_tag + "priority", text=old_text)
        text_box.destroy()
        project_manager.canvas.tag_raise(self.transition_tag + "rectangle", self.transition_tag)
        project_manager.canvas.tag_raise(self.transition_tag + "priority", self.transition_tag + "rectangle")
        project_manager.canvas.bind("<Button-1>", move_handling_initialization.move_initialization)
        project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete())

    def _straighten_transition(self, start_state_radius, end_state_radius):
        TransitionLine.extend_transition_to_state_middle_points(self.transition_tag)
        old_coords = project_manager.canvas.coords(self.transition_tag)
        new_coords = []
        new_coords.append(old_coords[0])
        new_coords.append(old_coords[1])
        new_coords.append(old_coords[-2])
        new_coords.append(old_coords[-1])
        new_coords = TransitionLine._shorten_vector(
            start_state_radius, new_coords[0], new_coords[1], end_state_radius, new_coords[2], new_coords[3], 1, 1
        )
        project_manager.canvas.coords(self.transition_tag, new_coords)
        # Calculates the position of the priority rectangle by shortening the distance between the first point of
        # the transition and the second point of the transition.
        [priority_middle_x, priority_middle_y, _, _] = TransitionLine._shorten_vector(
            project_manager.priority_distance, new_coords[0], new_coords[1], 0, new_coords[2], new_coords[3], 1, 0
        )
        [rectangle_width_half, rectangle_height_half] = TransitionLine._get_rectangle_dimensions(
            self.transition_tag + "rectangle"
        )
        project_manager.canvas.coords(
            self.transition_tag + "rectangle",
            priority_middle_x - rectangle_width_half,
            priority_middle_y - rectangle_height_half,
            priority_middle_x + rectangle_width_half,
            priority_middle_y + rectangle_height_half,
        )
        project_manager.canvas.coords(self.transition_tag + "priority", priority_middle_x, priority_middle_y)
        project_manager.canvas.tag_raise(self.transition_tag + "rectangle", self.transition_tag)
        project_manager.canvas.tag_raise(self.transition_tag + "priority", self.transition_tag + "rectangle")

    def delete(self) -> None:
        """Remove transition line, priority rect/text, tags, linked condition-action; update ref_dict and visibility."""
        transition_tags = project_manager.canvas.gettags(self.transition_tag)  # get tags before transition is deleted.
        project_manager.canvas.delete(self.transition_tag)
        project_manager.canvas.delete(self.priority_text)
        project_manager.canvas.delete(self.priority_rectangle)
        project_manager.canvas.dtag("all", self.transition_tag + "_start")  # delete: "transition"<integer>"_start"
        project_manager.canvas.dtag("all", self.transition_tag + "_end")  # delete: "transition"<integer>"_end"
        for tag in transition_tags:
            if tag.startswith("ca_connection"):
                ca_window_anchor_tag = tag[:-4] + "_anchor"
                ca_window_canvas_id = project_manager.canvas.find_withtag(ca_window_anchor_tag)[0]
                ref = condition_action.ConditionAction.ref_dict[ca_window_canvas_id]
                ref.delete()
            if tag.startswith("coming_from_"):
                start_state = tag[12:]
                # Adapt visibility after the transition was removed:
                self._adapt_visibility_of_priority_rectangles_at_state(start_state)
        del TransitionLine.ref_dict[self.transition_id]

    def _adapt_visibility_of_priority_rectangles_at_state(self, start_state) -> None:
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
    def move_to(cls, event_x, event_y, line_id, point, first, move_list, last=False) -> None:
        """Move line point (start*/next_to_start/next_to_end/end*) to (event_x, event_y);
        Records the move offset when first is True, else maintains the offset.
        Snaps to grid when last is True to keep being attached to state or connector."""
        # point can be:
        # At transitions           : "start", "next_to_start", "next_to_end", "end"
        # At comment lines         : "start_comment_line", "end_comment_line"
        # At lines to state actions: "start_connection", "end_connection"
        if first is True:
            cls._set_difference(event_x, event_y, line_id, point, move_list)
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + cls.diff_dict[point][0], event_y + cls.diff_dict[point][1]
        # Needed, because the object, to which the transition is connected to, snaps to grid.
        if last is True:
            tags_of_line = project_manager.canvas.gettags(line_id)
            disable_snap_to_grid = False
            for tag in tags_of_line:
                # move_to() is also called for connection to state-action and for comment_line moving,
                # where the startpoint shall not snap to grid.
                if (tag.startswith("connection") or tag.endswith("_comment_line")) and point == "start":
                    disable_snap_to_grid = True
            if disable_snap_to_grid:
                moved_event_x = event_x
                moved_event_y = event_y
            elif point in ("start", "end", "end_comment_line", "end_connection"):
                moved_event_x = project_manager.state_radius * round(event_x / project_manager.state_radius)
                moved_event_y = project_manager.state_radius * round(event_y / project_manager.state_radius)
                if point == "start":
                    # Store the delta caused by snap to grid for "next_to_start" and "next_to_end":
                    cls.delta_dict[point] = (moved_event_x - event_x, moved_event_y - event_y, line_id)
                else:
                    cls.delta_dict[point] = (0, 0, 0)
            else:
                # This is not a start or end point. If a loopback transition is moved together with its state,
                # it is relevant that this transition point is not snapped to the grid, because otherwise
                # the loopback transition could change its shape. Instead it must be moved by the same amount
                # as the start point of the transition when this point snapped to the grid.
                moved_event_x = event_x
                moved_event_y = event_y
                if "start" in cls.delta_dict and cls.delta_dict["start"][2] == line_id:
                    # This fix will be also used, if the transition start point was first moved alone by moving its
                    # connected state, an then a middle point of the transition is moved. But in this case this
                    # small fix does not matter:
                    moved_event_x = event_x + cls.delta_dict["start"][0]
                    moved_event_y = event_y + cls.delta_dict["start"][1]
            event_x, event_y = moved_event_x, moved_event_y
        line_tag = cls._determine_line_tag(line_id)
        project_manager.canvas.tag_lower(line_tag)
        line_coords = cls._move_line(line_tag, event_x, event_y, point)
        if line_tag.startswith("transition"):
            cls._move_priority_rectangle(event_x, event_y, line_tag, line_coords, point)

    @classmethod
    def _set_difference(cls, event_x, event_y, line_id, point, move_list) -> None:
        """Calculate the difference between the event and the transition point to move, if first is True."""
        coords = project_manager.canvas.coords(line_id)
        if (
            project_manager.canvas.type(move_list[0][0]) == "line"  # A transition is moved alone.
            and point in ("start", "end")
        ):
            # Only the start or the end point of a transition is moved, so the line begin shall jump to the cursor:
            cls.diff_dict[point] = (0, 0, line_id)
            return
        # A middle point of a transition is moved or
        # a line is moved, because it is connected to a moving object:
        if point.startswith("start"):
            point_to_move = [coords[0], coords[1]]
        elif point == "next_to_start":
            point_to_move = [coords[2], coords[3]]
        elif point == "next_to_end":
            point_to_move = [coords[-4], coords[-3]]
        elif point.startswith("end"):
            point_to_move = [coords[-2], coords[-1]]
        else:
            print("transition_handling: Fatal, unknown point =", point)
            return
        cls.diff_dict[point] = (-event_x + point_to_move[0], -event_y + point_to_move[1], line_id)

    @classmethod
    def _determine_line_tag(cls, line_id) -> str:
        """Determine the line tag based on the line_id."""
        all_line_tags = project_manager.canvas.gettags(line_id)
        line_tag = ""
        for single_tag in all_line_tags:
            if (
                single_tag.startswith("transition")
                or single_tag.startswith("connection")
                or single_tag.endswith("comment_line")
            ):
                line_tag = single_tag
                break
        return line_tag

    @classmethod
    def _move_line(cls, line_tag, event_x, event_y, point) -> list:
        """Move line and connected condition-action line(s) if existing; lower line under states."""
        coords = project_manager.canvas.coords(line_tag)
        if point.startswith("start"):
            coords[:2] = event_x, event_y
        elif point == "next_to_start":
            coords[2:4] = event_x, event_y
            if cls._is_loopback_transition(line_tag):
                coords[4], coords[5] = cls._get_new_cordinates_of_not_moved_point(
                    event_x, event_y, coords[4], coords[5], coords[6], coords[7]
                )
        elif point == "next_to_end":
            coords[4:6] = event_x, event_y
            if cls._is_loopback_transition(line_tag):
                coords[2], coords[3] = cls._get_new_cordinates_of_not_moved_point(
                    event_x, event_y, coords[2], coords[3], coords[0], coords[1]
                )
        elif point.startswith("end"):
            coords[-2:] = event_x, event_y
        else:
            print("transition_handling: Fatal, unknown point =", point)
        project_manager.canvas.coords(line_tag, coords)
        list_of_grid_line_canvas_ids = project_manager.canvas.find_withtag("grid_line")
        if list_of_grid_line_canvas_ids:
            project_manager.canvas.tag_raise(line_tag, "grid_line")
        return project_manager.canvas.coords(line_tag)

    @classmethod
    def _is_loopback_transition(cls, line_tag) -> bool:
        """Check if the transition is a loopback transition."""
        target_tag_list = project_manager.canvas.find_withtag(line_tag + "_end")
        startp_tag_list = project_manager.canvas.find_withtag(line_tag + "_start")
        return target_tag_list == startp_tag_list

    @classmethod
    def _get_new_cordinates_of_not_moved_point(
        cls, event_x, event_y, not_moved_point_x, not_moved_point_y, start_x, start_y
    ) -> list:
        moved_vector_x = event_x - start_x
        moved_vector_y = event_y - start_y
        moved_vector_length = math.sqrt(moved_vector_x**2 + moved_vector_y**2)
        not_moved_vector_x = not_moved_point_x - start_x
        not_moved_vector_y = not_moved_point_y - start_y
        not_moved_vector_length = math.sqrt(not_moved_vector_x**2 + not_moved_vector_y**2)
        factor = moved_vector_length / not_moved_vector_length
        new_not_moved_vector_x = not_moved_vector_x * factor
        new_not_moved_vector_y = not_moved_vector_y * factor
        new_not_moved_point_x = start_x + new_not_moved_vector_x
        new_not_moved_point_y = start_y + new_not_moved_vector_y
        return new_not_moved_point_x, new_not_moved_point_y

    @classmethod
    def _move_priority_rectangle(cls, event_x, event_y, transition_tag, transition_coords, point) -> None:
        """Move priority rectangle."""
        # The tag "transition_tag + '_start'" is already removed from the old start state when
        # the transition start-point is moved. In all other cases the tag exists.
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
            [priority_middle_x, priority_middle_y, _, _] = TransitionLine._shorten_vector(
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
            [priority_middle_x, priority_middle_y, _, _] = TransitionLine._shorten_vector(
                start_state_radius + project_manager.priority_distance,
                transition_coords[0],
                transition_coords[1],
                0,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
        [rectangle_width_half, rectangle_height_half] = TransitionLine._get_rectangle_dimensions(
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
        if transition_tag.startswith("transition"):
            # When transition_tag starts with "connection" no start point is needed.
            start_coords = project_manager.canvas.coords(transition_tag + "_start")
            # Coords are from a state (circle) or from a connector (rectangle) or from the reset entry (polygon).
            if project_manager.canvas.type(transition_tag + "_start") != "polygon":
                # At the reset entry the transition start point is not modified for moving.
                transition_coords[0] = (start_coords[0] + start_coords[2]) // 2
                transition_coords[1] = (start_coords[1] + start_coords[3]) // 2
        transition_coords[-2] = (end_state_coords[0] + end_state_coords[2]) // 2
        transition_coords[-1] = (end_state_coords[1] + end_state_coords[3]) // 2
        project_manager.canvas.coords(transition_tag, *transition_coords)
        # Hide the line "under" the states:
        project_manager.canvas.tag_lower(transition_tag, transition_tag + "_start")
        project_manager.canvas.tag_lower(transition_tag, transition_tag + "_end")

    @classmethod
    def determine_priorities_of_outgoing_transitions(cls, start_state_canvas_id) -> dict[str, str]:
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
            transition_start_coords = TransitionLine._shorten_vector(
                start_state_radius,
                transition_coords[0],
                transition_coords[1],
                0,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
            transition_end_coords = TransitionLine._shorten_vector(
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
            transition_coords = TransitionLine._remove_duplicate_points(transition_coords)
            project_manager.canvas.coords(transition_tag, transition_coords)
            project_manager.canvas.tag_lower(transition_tag)
            # Move priority rectangle:
            start_state_radius = abs(start_state_coords[2] - start_state_coords[0]) / 2
            [priority_middle_x, priority_middle_y, _, _] = TransitionLine._shorten_vector(
                0 + project_manager.priority_distance,
                transition_coords[0],
                transition_coords[1],
                0,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
            [rectangle_width_half, rectangle_height_half] = TransitionLine._get_rectangle_dimensions(
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

            transition_end_coords = TransitionLine._shorten_vector(
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
    def _remove_duplicate_points(cls, transition_coords) -> list:
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
    def _get_rectangle_dimensions(cls, canvas_id) -> list:
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
    def _shorten_vector(cls, delta0, x0, y0, delta1, x1, y1, modify0, modify1) -> list:
        """Shorten vector x0, y0, x1, y1 by delta0 at start and delta1 at end. modify0, modify1 are either 0 or 1."""
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
    def create(cls, event) -> None:
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
                    tsotag = cls._get_tag_of_start_object(canvas_id)
                    project_manager.canvas.bind(
                        "<Button-1>",
                        lambda evt, t_id=transition_id, c_id=canvas_id, tdf_id=transition_draw_funcid, tsotag=tsotag: (
                            cls._handle_next_added_transition_point(
                                evt,
                                t_id,
                                c_id,
                                tdf_id,
                                tsotag,
                            )
                        ),
                    )
                    project_manager.root.bind_all(
                        "<Escape>",
                        lambda event, transition_id=transition_id, transition_draw_funcid=transition_draw_funcid: (
                            cls._finish_inserting_transition(transition_id, transition_draw_funcid)
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
        elif end_state_canvas_id == start_state_canvas_id and (
            len(transition_coords) in (4, 6) or transition_ends_at_connector
        ):
            # A loopback transition with only 2  points cannot be drawn.
            # A loopback transition with only 3  points creates a transition which cannot be moved properly.
            # A loopback transition to a connector is not allowed.
            # The transition point is not accepted.
            return
        else:
            while project_manager.canvas.find_withtag("transition" + str(TransitionLine.transition_number)):
                # Increase until an unused number is found.
                # This number conflict may happen, if the design was created with an old version of HFE.
                TransitionLine.transition_number += 1
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
            cls._finish_inserting_transition(transition_id, transition_draw_funcid)
            TransitionLine(transition_coords, tags, unused_priority)
            TransitionLine.hide_priority_of_single_outgoing_transitions()
            project_manager.undo_handling_ref.design_has_changed()

    @classmethod
    def _finish_inserting_transition(cls, transition_id, transition_draw_funcid) -> None:
        project_manager.canvas.delete(transition_id)
        # Restore bindings:
        project_manager.canvas.unbind("<Motion>", transition_draw_funcid)
        project_manager.canvas.bind("<Button-1>", TransitionLine.create)
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
            vector1 = TransitionLine._shorten_vector(
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
            vector1 = TransitionLine._shorten_vector(
                start_state_radius,
                transition_coords[0],
                transition_coords[1],
                end_state_radius,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
            vector2 = TransitionLine._shorten_vector(
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
            vector1 = TransitionLine._shorten_vector(
                start_state_radius,
                transition_coords[0],
                transition_coords[1],
                end_state_radius,
                transition_coords[2],
                transition_coords[3],
                1,
                0,
            )
            vector2 = TransitionLine._shorten_vector(
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

"""
Module handling states on the canvas.
"""

import tkinter as tk
from tkinter import messagebox

import canvas_delete
import canvas_editing
import constants
import move_handling_canvas_item
import move_handling_initialization
import undo_handling
from dialogs.color_changer import ColorChanger
from elements import state_action, state_comment, transition
from project_manager import project_manager
from widgets.option_menu import OptionMenu


class States:
    """
    For each state on the canvas a states-object is created.
    """

    state_number = 0
    ref_dict = {}
    difference_x = 0
    difference_y = 0

    def __init__(self, coords, tags, text, fill_color, new_state=False) -> None:
        if new_state:
            States.state_number += 1
        self.state_id = project_manager.canvas.create_oval(
            coords,
            fill=fill_color,
            width=2,
            outline="blue",
            tags=tags,
        )
        state_name = tags[0]
        middle = self._calculate_center(coords)
        self.text_id = project_manager.canvas.create_text(
            middle[0],
            middle[1],
            text=text,
            tags=state_name + "_name",
            font=project_manager.state_name_font,
        )
        project_manager.canvas.tag_bind(
            self.state_id, "<Enter>", lambda event, id=self.state_id: project_manager.canvas.itemconfig(id, width=4)
        )
        project_manager.canvas.tag_bind(
            self.state_id, "<Leave>", lambda event, id=self.state_id: project_manager.canvas.itemconfig(id, width=2)
        )
        project_manager.canvas.tag_bind(self.state_id, "<Button-3>", self._show_menu)
        project_manager.canvas.tag_bind(
            self.state_id,
            "<Button-1>",
            lambda event: move_handling_canvas_item.MoveHandlingCanvasItem(event, self.state_id),
        )
        project_manager.canvas.tag_bind(
            self.text_id,
            "<Button-1>",
            lambda event: move_handling_canvas_item.MoveHandlingCanvasItem(event, self.text_id),
        )
        project_manager.canvas.tag_bind(self.text_id, "<Double-Button-1>", self._edit_state_name)
        project_manager.canvas.tag_bind(self.text_id, "<Button-3>", self._show_menu)
        States.ref_dict[self.state_id] = self

    def _show_menu(self, event) -> None:
        listbox = OptionMenu(
            project_manager.canvas,
            ["add action", "add comment", "change color"],
            height=3,
            bg="lightgrey",
            width=14,
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
        listbox.bind("<Leave>", lambda event, window=window, listbox=listbox: self._close_menu(window, listbox))

    def _edit_state_name(self, event) -> None:
        project_manager.canvas.unbind("<Button-1>")
        project_manager.canvas.unbind_all("<Delete>")
        old_text = project_manager.canvas.itemcget(self.text_id, "text")
        text_box = tk.Entry(project_manager.canvas, width=10, justify=tk.CENTER)
        # text_box = Entry(None, width=10, justify=tk.CENTER) funktioniert auch, unklar, was richtig/besser ist.
        text_box.insert(tk.END, old_text)
        text_box.select_range(0, tk.END)
        text_box.bind("<Return>", lambda event, text_box=text_box: self._update_state_name(text_box))
        text_box.bind(
            "<Escape>",
            lambda event, text_box=text_box, old_text=old_text: self._abort_edit_text(text_box, old_text),
        )
        event_x, event_y = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
        project_manager.canvas.create_window(event_x, event_y, window=text_box, tag="entry-window")
        text_box.focus_set()

    def _close_menu(self, window, listbox) -> None:
        listbox.destroy()
        project_manager.canvas.delete(window)

    def _update_state_name(self, text_box) -> None:
        project_manager.canvas.delete("entry-window")
        new_text = text_box.get()
        text_box.destroy()
        tags = project_manager.canvas.gettags(self.text_id)
        for t in tags:
            if t.startswith("state"):  # Format of text_id tag: 'state' + str(state_number) + "_name"
                state_tag = t[:-5]
                self._show_new_state_name(new_text)
                self._resize_state(state_tag)
        undo_handling.design_has_changed()
        project_manager.canvas.bind("<Button-1>", move_handling_initialization.move_initialization)
        project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete())
        tags = project_manager.canvas.gettags(state_tag)
        for t in tags:
            if t.endswith("_start"):
                transition.TransitionLine.extend_transition_to_state_middle_points(t[:-6])
                transition.TransitionLine.shorten_to_state_border(t[:-6])
            elif t.endswith("_end") and not t.endswith("_comment_line_end"):
                transition.TransitionLine.extend_transition_to_state_middle_points(t[:-4])
                transition.TransitionLine.shorten_to_state_border(t[:-4])

    def _evaluate_menu(self, _event, window, listbox, menu_x, menu_y) -> None:
        selected_entry = listbox.get(listbox.curselection())
        listbox.destroy()
        project_manager.canvas.delete(window)
        if selected_entry == "add action":
            tags = project_manager.canvas.gettags(self.state_id)
            action_block_exists = False
            for tag in tags:
                if tag.startswith("connection"):  # searching for "connection<n>_end"
                    action_block_exists = True
            if not action_block_exists:
                project_manager.canvas.addtag_withtag(
                    "connection" + str(state_action.StateAction.state_action_id) + "_end", self.state_id
                )
                line_tags = (
                    "connection" + str(state_action.StateAction.state_action_id),
                    "connected_to_" + project_manager.canvas.gettags(self.state_id)[0],
                )
                state_action_tags = (
                    "state_action" + str(state_action.StateAction.state_action_id),
                    "connection" + str(state_action.StateAction.state_action_id) + "_start",
                )
                middle_x, middle_y = self._calculate_center(project_manager.canvas.coords(self.state_id))
                line_coords = [menu_x + 100, menu_y, middle_x, middle_y]
                state_action.StateAction(
                    menu_x + 100,
                    menu_y,
                    height=1,
                    width=8,
                    padding=1,
                    tags=state_action_tags,
                    line_coords=line_coords,
                    line_tags=line_tags,
                    increment=True,
                )
                undo_handling.design_has_changed()
        elif selected_entry == "add comment":
            tags = project_manager.canvas.gettags(self.state_id)
            for tag in tags:
                if tag.endswith("comment_line_end"):
                    return  # There is already a comment attached to this state.
            state_coords = project_manager.canvas.coords(self.state_id)
            for tag in tags:
                if tag.startswith("state"):
                    state_identifier = tag
                    project_manager.canvas.addtag_withtag(state_identifier + "_comment_line_end", state_identifier)
                    state_comment.StateComment(
                        menu_x,
                        menu_y,
                        height=1,
                        width=8,
                        padding=1,
                        tags=[state_identifier + "_comment", state_identifier + "_comment_line_start"],
                        line_coords=[
                            menu_x + 100,
                            menu_y,
                            (state_coords[2] + state_coords[0]) / 2,
                            (state_coords[3] + state_coords[1]) / 2,
                        ],
                    )
                    undo_handling.design_has_changed()
        elif selected_entry == "change color":
            new_color = ColorChanger(constants.STATE_COLOR).ask_color()
            project_manager.canvas.itemconfigure(self.state_id, fill=new_color)
            undo_handling.design_has_changed()

    def _abort_edit_text(self, text_box, old_text) -> None:
        project_manager.canvas.delete("entry-window")
        project_manager.canvas.itemconfig(self.text_id, text=old_text)
        text_box.destroy()
        project_manager.canvas.bind("<Button-1>", move_handling_initialization.move_initialization)
        project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete())

    def _show_new_state_name(self, new_text) -> None:
        state_name_list = self._get_list_of_state_names()
        if new_text != "":
            if new_text not in state_name_list:
                project_manager.canvas.itemconfig(self.text_id, text=new_text)
            else:
                messagebox.showerror("Error", "The state name\n" + new_text + "\nis already used at another state.")

    def _get_list_of_state_names(self) -> list:
        state_name_list = []
        all_canvas_ids = project_manager.canvas.find_withtag("all")
        for canvas_id in all_canvas_ids:
            if project_manager.canvas.type(canvas_id) == "oval":
                state_tags = project_manager.canvas.gettags(canvas_id)
                for tag in state_tags:
                    if (
                        tag.startswith("state")
                        and not tag.endswith("_comment_line_end")
                        and project_manager.canvas.find_withtag(tag + "_name")[0] != self.text_id
                    ):
                        state_name_list.append(project_manager.canvas.itemcget(tag + "_name", "text"))
        return state_name_list

    def _resize_state(self, state_tag) -> None:
        state_coords = project_manager.canvas.coords(state_tag)
        state_width = state_coords[2] - state_coords[0]
        size = project_manager.canvas.bbox(self.text_id)
        text_width = (
            size[2] - size[0] + 15
        )  # Make the text a little bit bigger, so that it does not touch the state circle.
        text_width = max(text_width, 2 * project_manager.state_radius)
        difference = text_width - state_width
        state_coords[0] = state_coords[0] - difference // 2
        state_coords[1] = state_coords[1] - difference // 2
        state_coords[2] = state_coords[2] + difference // 2
        state_coords[3] = state_coords[3] + difference // 2
        overlapping_list = project_manager.canvas.find_overlapping(*state_coords)
        state_is_too_big = False
        for canvas_item in overlapping_list:
            if (
                project_manager.canvas.type(canvas_item) not in ["text", "line", "rectangle"]
                and canvas_item != project_manager.canvas.find_withtag(state_tag)[0]
            ):
                state_is_too_big = True
        if not state_is_too_big:
            project_manager.canvas.coords(state_tag, state_coords)

    def delete(self) -> None:
        """Delete state oval and name; delete connected transitions, state-actions, comment lines; update ref_dict."""
        state_tags = project_manager.canvas.gettags(self.state_id)
        for state_tag in state_tags:
            if state_tag.startswith("transition") and state_tag.endswith("_start"):
                canvas_ids = project_manager.canvas.find_withtag(state_tag[:-6])
                if canvas_ids:
                    transition.TransitionLine.ref_dict[canvas_ids[0]].delete()
            elif state_tag.startswith("transition") and state_tag.endswith("_end"):
                canvas_ids = project_manager.canvas.find_withtag(state_tag[:-4])
                if canvas_ids:
                    transition.TransitionLine.ref_dict[canvas_ids[0]].delete()
            elif state_tag.startswith("connection"):
                tags_of_state_action = project_manager.canvas.gettags(state_tag[:-4] + "_start")
                tag_of_state_action = tags_of_state_action[0]  # like "state_action<n>"
                state_action_window_canvas_id = project_manager.canvas.find_withtag(tag_of_state_action)[0]
                ref = state_action.StateAction.ref_dict[state_action_window_canvas_id]
                ref.delete()
            elif state_tag.endswith("_comment_line_end"):
                canvas_id_of_comment = project_manager.canvas.find_withtag(state_tag[:-9])[0]
                ref = state_comment.StateComment.ref_dict[canvas_id_of_comment]
                ref.delete()
        project_manager.canvas.delete(self.state_id)  # delete state
        project_manager.canvas.delete(self.text_id)  # delete state name
        del States.ref_dict[self.state_id]

    @classmethod
    def move_to(cls, event_x, event_y, state_id, first, last) -> None:
        """Reposition state oval and name; snap to grid when last; abort if overlapping another state/connector."""
        if first is True:
            # Calculate the difference between the "anchor" point and the event:
            coords = project_manager.canvas.coords(state_id)
            center = cls._calculate_center(coords)
            cls.difference_x, cls.difference_y = -event_x + center[0], -event_y + center[1]
        if cls._state_is_moved_to_near_to_state_or_connector(state_id, event_x, event_y):
            return
        # When moving the center, keep the distance between event and anchor point constant:
        new_center_x, new_center_y = event_x + cls.difference_x, event_y + cls.difference_y
        if last is True:
            new_center_x, new_center_y = cls._move_center_to_grid(new_center_x, new_center_y)
        text_tag = cls._determine_the_tag_of_the_state_name(state_id)
        state_radius = cls._determine_the_radius_of_the_state(state_id)
        project_manager.canvas.coords(
            state_id,
            new_center_x - state_radius,
            new_center_y - state_radius,
            new_center_x + state_radius,
            new_center_y + state_radius,
        )
        project_manager.canvas.coords(text_tag, new_center_x, new_center_y)
        project_manager.canvas.tag_raise(state_id, "all")
        project_manager.canvas.tag_raise(text_tag, state_id)

    @classmethod
    def _state_is_moved_to_near_to_state_or_connector(cls, moved_item_id, event_x, event_y) -> bool:
        # Keep the distance between event and anchor point constant:
        event_x_mod, event_y_mod = event_x + cls.difference_x, event_y + cls.difference_y
        event_x_mod = project_manager.state_radius * round(event_x_mod / project_manager.state_radius)
        event_y_mod = project_manager.state_radius * round(event_y_mod / project_manager.state_radius)
        state_coords = project_manager.canvas.coords(moved_item_id)
        state_radius = (state_coords[2] - state_coords[0]) // 2
        moved_state_coords = (
            event_x_mod - state_radius,
            event_y_mod - state_radius,
            event_x_mod + state_radius,
            event_y_mod + state_radius,
        )
        overlapping_list = project_manager.canvas.find_overlapping(
            moved_state_coords[0] - project_manager.state_radius / 2,
            moved_state_coords[1] - project_manager.state_radius / 2,
            moved_state_coords[2] + project_manager.state_radius / 2,
            moved_state_coords[3] + project_manager.state_radius / 2,
        )
        for overlapping_item in overlapping_list:
            overlapping_with_connector = False
            tags = project_manager.canvas.gettags(overlapping_item)
            for tag in tags:
                if tag.startswith("connector"):
                    overlapping_with_connector = True
            if overlapping_item != moved_item_id and (
                project_manager.canvas.type(overlapping_item) == "oval" or overlapping_with_connector
            ):
                return True
        return False

    @classmethod
    def _calculate_center(cls, coords) -> list:
        middle_x = (coords[0] + coords[2]) / 2
        middle_y = (coords[1] + coords[3]) / 2
        return [middle_x, middle_y]

    @classmethod
    def _move_center_to_grid(cls, new_center_x, new_center_y):
        new_center_x = project_manager.state_radius * round(new_center_x / project_manager.state_radius)
        new_center_y = project_manager.state_radius * round(new_center_y / project_manager.state_radius)
        return new_center_x, new_center_y

    @classmethod
    def _determine_the_tag_of_the_state_name(cls, state_id):
        state_tag = ""
        tags = project_manager.canvas.gettags(state_id)
        for tag in tags:
            if tag.startswith("state") and not tag.endswith("_comment_line_end"):
                state_tag = tag
        return state_tag + "_name"

    @classmethod
    def _determine_the_radius_of_the_state(cls, state_id):
        state_coords = project_manager.canvas.coords(state_id)
        return (state_coords[2] - state_coords[0]) / 2

    @classmethod
    def insert_state(cls, event) -> None:
        """Create state at event position if not overlapping; warn and abort otherwise."""
        event_x, event_y = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
        if cls.state_overlaps(event_x, event_y):
            messagebox.showwarning(
                "Warning in HDL-FSM-Editor",
                "The state could not be inserted, because it\nwas positioned too close to another object.\nTry again",
            )
            return
        coords = [
            event_x - project_manager.state_radius,
            event_y - project_manager.state_radius,
            event_x + project_manager.state_radius,
            event_y + project_manager.state_radius,
        ]
        States(
            coords,
            tags=["state" + str(States.state_number + 1)],
            text="S" + str(States.state_number + 1),
            fill_color=constants.STATE_COLOR,
            new_state=True,
        )
        # design_has_changed cannot be called by state.States, because state.States must be called
        # when an Undo is performed, which shall not create a new entry in the Undo-Stack.
        undo_handling.design_has_changed()

    @classmethod
    def state_overlaps(cls, event_x, event_y) -> bool:
        """Return True if a state at (event_x, event_y) would overlap any non-grid item."""
        overlapping_items = project_manager.canvas.find_overlapping(
            event_x - project_manager.state_radius,
            event_y - project_manager.state_radius,
            event_x + project_manager.state_radius,
            event_y + project_manager.state_radius,
        )
        for overlapping_item in overlapping_items:
            if "grid_line" not in project_manager.canvas.gettags(overlapping_item):
                return True
        return False

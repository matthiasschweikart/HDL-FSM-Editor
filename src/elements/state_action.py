"""
Handles the state action of all states.
"""

import tkinter as tk
from tkinter import ttk

import canvas_delete
import canvas_editing
import custom_text
import move_handling_canvas_window
import tab_diagram
import undo_handling
from project_manager import project_manager


class StateAction:
    """Implements the state action of a single state."""

    state_action_id = 0
    ref_dict = {}

    def __init__(
        self,
        coord_x,
        coord_y,
        height,
        width,
        padding,
        tags,
        line_coords,
        line_tags,
        increment,
    ) -> None:
        if increment is True:
            StateAction.state_action_id += 1
        self.text_content = None
        self.difference_x = 0
        self.difference_y = 0
        self.borderwidth = 0
        self.frame_id = ttk.Frame(
            project_manager.canvas,
            relief=tk.FLAT,
            borderwidth=self.borderwidth,
            padding=padding,
            style="StateActionsWindow.TFrame",
        )
        self.label_id = ttk.Label(
            self.frame_id,
            text="State actions (combinatorial): ",
            font=("Arial", int(project_manager.label_fontsize)),
            style="StateActionsWindow.TLabel",
        )
        self.text_id = custom_text.CustomText(
            self.frame_id,
            text_type="action",
            height=height,
            width=width,
            undo=True,
            maxundo=-1,
            font=("Courier", int(project_manager.fontsize)),
        )
        self.label_id.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))
        self.text_id.grid(column=0, row=1, sticky=(tk.S, tk.W, tk.E))
        self.window_id = project_manager.canvas.create_window(
            coord_x, coord_y, window=self.frame_id, anchor=tk.W, tags=tags
        )
        self.line_id = project_manager.canvas.create_line(line_coords, dash=(2, 2), tags=line_tags)
        project_manager.canvas.tag_lower(self.line_id)

        self.frame_id.bind("<Enter>", lambda event: self.activate_frame())
        self.frame_id.bind("<Leave>", lambda event: self.deactivate_frame())
        self.frame_id.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(event, self.frame_id, self.window_id),
        )
        self.label_id.bind("<Enter>", lambda event: self.activate_window())
        self.label_id.bind("<Leave>", lambda event: self.deactivate_window())
        self.label_id.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(event, self.label_id, self.window_id),
        )
        self.text_id.bind("<Control-z>", lambda event: self.text_id.undo())
        self.text_id.bind("<Control-Z>", lambda event: self.text_id.redo())
        self.text_id.bind("<Control-e>", lambda event: self._edit_in_external_editor())
        self.text_id.bind("<Control-s>", lambda event: self.update_text())
        self.text_id.bind("<Control-g>", lambda event: self.update_text())
        self.text_id.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        self.text_id.bind("<FocusIn>", lambda event: project_manager.canvas.unbind_all("<Delete>"))
        self.text_id.bind(
            "<FocusOut>",
            lambda event: project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete()),
        )
        ids_list = (self.label_id, self.text_id)
        seq1_list = ("<Control-MouseWheel>", "<Control-Button-4>", "<Control-Button-5>")
        seq2_list = ("<MouseWheel>", "<Button-4>", "<Button-5>")
        for id in ids_list:
            for seq in seq1_list:
                id.bind(seq, lambda event: canvas_editing.zoom_wheel_window_item(event, self.window_id))
            for seq in seq2_list:
                id.bind(seq, tab_diagram.TabDiagram.scroll_wheel)
        StateAction.ref_dict[self.window_id] = self

    def _edit_in_external_editor(self):
        self.text_id.edit_in_external_editor()
        self.update_text()

    def update_text(self) -> None:
        """Sync text_content from widget for 'dirty' checking and save_in_file."""
        # Update self.text_content, so that the <Leave>-check in deactivate_frame() does not signal a design-change and
        # that save_in_file() already reads the new text, entered into the textbox before Control-s/g.
        # To ensure this, save_in_file() waits for idle.
        self.text_content = self.text_id.get("1.0", tk.END)

    def _set_borderwidth(self, borderwidth: int, style: str) -> None:
        diff = self.borderwidth - borderwidth
        self.borderwidth = borderwidth
        self.frame_id.configure(borderwidth=borderwidth, style=style)
        # Compensate for the borderwidth of the frame.
        # I don't know why only the x-coordinate needs compensation.
        pos = project_manager.canvas.coords(self.window_id)
        project_manager.canvas.coords(self.window_id, (pos[0] + diff, pos[1]))

    def activate_frame(self) -> None:
        """Activate window and cache text for dirty checking."""
        self.activate_window()
        self.text_content = self.text_id.get("1.0", tk.END)

    def activate_window(self) -> None:
        """Show state-action window as selected (border and label style)."""
        self._set_borderwidth(1, "StateActionsWindowSelected.TFrame")
        self.label_id.configure(style="StateActionsWindowSelected.TLabel")

    def deactivate_frame(self) -> None:
        """Deactivate window and mark design changed if text was edited."""
        self.deactivate_window()
        if self.text_id.get("1.0", tk.END) != self.text_content:
            undo_handling.design_has_changed()

    def deactivate_window(self) -> None:
        """Clear selection style and focus from the state-action window."""
        project_manager.canvas.focus_set()  # "unfocus" the Text, when the mouse leaves the text.
        self._set_borderwidth(0, style="StateActionsWindow.TFrame")
        self.label_id.configure(style="StateActionsWindow.TLabel")

    def move_to(self, event_x, event_y, first) -> None:
        """Reposition window and connection line;
        Updates the move offset when first is True else maintains the offset."""
        if first:
            # Calculate the difference between the "anchor" point and the event:
            coords = project_manager.canvas.coords(self.window_id)
            self.difference_x, self.difference_y = -event_x + coords[0], -event_y + coords[1]
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + self.difference_x, event_y + self.difference_y
        project_manager.canvas.coords(self.window_id, event_x, event_y)
        # Move the connection line:
        window_tags = project_manager.canvas.gettags(self.window_id)
        for t in window_tags:
            if t.startswith("connection"):  # remove "_start"
                line_tag = t[:-6]
                line_coords = project_manager.canvas.coords(line_tag)
                line_coords[0] = event_x
                line_coords[1] = event_y
                project_manager.canvas.coords(line_tag, line_coords)

    def move_line_point_to(self, event_x, event_y, first) -> None:
        """Move connection line end to (event_x, event_y) snapped to grid; used when state is moved."""
        # Called when the state is moved.
        if first:
            # tags of the window are: ('state_action0', 'connection0_start')
            connection_tag = project_manager.canvas.gettags(self.window_id)[1][:-6]  # remove "_start"
            state_tags = project_manager.canvas.gettags(connection_tag + "_end")
            state_coords = project_manager.canvas.coords(state_tags[0])
            middle_x = (state_coords[0] + state_coords[2]) / 2
            middle_y = (state_coords[1] + state_coords[3]) / 2
            self.difference_x, self.difference_y = -event_x + middle_x, -event_y + middle_y
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + self.difference_x, event_y + self.difference_y
        # Move line end point to grid:
        event_x = project_manager.state_radius * round(event_x / project_manager.state_radius)
        event_y = project_manager.state_radius * round(event_y / project_manager.state_radius)
        line_coords = project_manager.canvas.coords(self.line_id)
        line_coords[2] = event_x
        line_coords[3] = event_y
        project_manager.canvas.coords(self.line_id, line_coords)

    def delete(self):
        """Remove state-action window, connection line, tags, and ref_dict entry."""
        state_number = project_manager.canvas.gettags(self.window_id)[0][12:]  # remove "state_action"
        project_manager.canvas.dtag("all", "connection" + state_number + "_end")  # delete tag "connection<n>_end".
        project_manager.canvas.delete(self.line_id)  # delete connection line
        project_manager.canvas.delete(self.window_id)  # delete state action window
        del custom_text.CustomText.read_variables_of_all_windows[self.text_id]
        del custom_text.CustomText.written_variables_of_all_windows[self.text_id]
        del StateAction.ref_dict[self.window_id]

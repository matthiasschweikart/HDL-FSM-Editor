"""
Handles the combinatorial default actions for all states.
"""

import tkinter as tk
from tkinter import ttk

from actions import canvas_delete, canvas_editing, canvas_modify_bindings, move_handling_canvas_window
from gui import tab_diagram
from project_manager import project_manager
from widgets import custom_text


class StateActionsDefault:
    """
    Handles the combinatorial default actions for all states.
    """

    ref_dict = {}

    def __init__(self, coord_x, coord_y, padding, tags, action) -> None:
        self.text_content = action
        self.difference_x = 0
        self.difference_y = 0
        self.move_rectangle = None
        self.borderwidth = 0
        self.frame_id = ttk.Frame(
            project_manager.canvas,
            relief=tk.FLAT,
            borderwidth=self.borderwidth,
            padding=padding,
            style="StateActionsWindow.TFrame",
        )
        # Create label object inside frame:
        self.label = ttk.Label(
            self.frame_id,
            text="Default state actions (combinatorial): ",
            font=("Arial", int(project_manager.label_fontsize)),
            style="StateActionsWindow.TLabel",
        )
        self.text_id = custom_text.CustomText(
            self.frame_id,
            text_type="action",
            undo=True,
            maxundo=-1,
            font=("Courier", int(project_manager.fontsize)),
        )
        self.label.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E))
        self.text_id.grid(row=1, column=0, sticky=(tk.E, tk.W))
        # Create canvas window for frame and text:
        self.window_id = project_manager.canvas.create_window(
            coord_x, coord_y, window=self.frame_id, anchor=tk.W, tags=tags
        )
        StateActionsDefault.ref_dict[self.window_id] = self
        self.text_id.insert("1.0", action)
        self.text_id.format("element-insertion")

        self.frame_id.bind("<Enter>", lambda event: self._activate_frame())
        self.frame_id.bind("<Leave>", lambda event: self._deactivate_frame())
        self.frame_id.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(event, self.frame_id, self.window_id),
        )
        self.label.bind("<Enter>", lambda event: self._activate_window())
        self.label.bind("<Leave>", lambda event: self._deactivate_window())
        self.label.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(event, self.label, self.window_id),
        )
        self.text_id.bind("<Control-z>", lambda event: self.text_id.undo())
        self.text_id.bind("<Control-Z>", lambda event: self.text_id.redo())
        self.text_id.bind("<Control-e>", lambda event: self._edit_in_external_editor())
        self.text_id.bind("<Control-s>", lambda event: self.update_text())
        self.text_id.bind("<Control-g>", lambda event: self.update_text())
        self.text_id.bind("<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title())
        self.text_id.bind("<FocusIn>", lambda event: project_manager.canvas.unbind_all("<Delete>"))
        self.text_id.bind(
            "<FocusOut>",
            lambda event: project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete()),
        )
        ids_list = (self.label, self.text_id)
        seq1_list = ("<Control-MouseWheel>", "<Control-Button-4>", "<Control-Button-5>")
        seq2_list = ("<MouseWheel>", "<Button-4>", "<Button-5>")
        for single_id in ids_list:
            for seq in seq1_list:
                single_id.bind(seq, lambda event, id=single_id: self._zoom_by_wheel(event, id))
            for seq in seq2_list:
                single_id.bind(seq, tab_diagram.TabDiagram.scroll_wheel)

    def _zoom_by_wheel(self, event, canvas_id) -> None:
        window_coords = project_manager.canvas.coords(self.window_id)
        window_bbox = project_manager.canvas.bbox(self.window_id)
        window_height = window_bbox[3] - window_bbox[1]
        window_root = [window_coords[0], window_coords[1] - window_height / 2]
        event_x = window_root[0] + event.x
        event_y = window_root[1] + event.y
        if canvas_id != self.label:
            event_y += self.label.winfo_height()
        canvas_editing.zoom_wheel(event, event_x, event_y)

    def tag(self) -> None:
        """Set window tag to state_actions_default."""
        project_manager.canvas.itemconfigure(self.window_id, tag="state_actions_default")

    def _edit_in_external_editor(self):
        self.text_id.edit_in_external_editor()
        self.update_text()

    def update_text(self) -> None:
        """Sync text_content from widget for 'dirty' checking and save_in_file."""
        # Update self.text_content, so that the <Leave>-check in _deactivate_frame() does not signal a design-change and
        # that save_in_file() already reads the new text, entered into the textbox before Control-s/g.
        # To ensure this, save_in_file() waits for idle.
        self.text_content = self.text_id.get("1.0", tk.END)

    def _set_borderwidth(self, borderwidth: int, style: str) -> None:
        if project_manager.canvas.find_withtag(self.window_id):  # Delete causes leave-event, but window_id is invalid.
            diff = self.borderwidth - borderwidth
            self.borderwidth = borderwidth
            self.frame_id.configure(borderwidth=borderwidth, style=style)
            # Compensate for the borderwidth of the frame.
            pos = project_manager.canvas.coords(self.window_id)
            project_manager.canvas.coords(self.window_id, (pos[0] + diff, pos[1]))

    def _activate_frame(self) -> None:
        """Activate window and cache text for dirty checking."""
        self._activate_window()
        self.text_content = self.text_id.get("1.0", tk.END)

    def _activate_window(self) -> None:
        """Show state-actions-default window as selected (border and label style)."""
        self._set_borderwidth(1, "StateActionsWindowSelected.TFrame")
        self.label.configure(style="StateActionsWindowSelected.TLabel")

    def _deactivate_frame(self) -> None:
        """Deactivate window and mark design changed if text was edited."""
        self._deactivate_window()
        if self.text_id.get("1.0", tk.END) != self.text_content:
            project_manager.undo_handling_ref.design_has_changed()

    def _deactivate_window(self) -> None:
        """Clear selection style and focus from the state-actions-default window."""
        if not custom_text.CustomText.selection_is_active:
            project_manager.canvas.focus_set()  # "unfocus" the Text, when the mouse leaves the text.
        self._set_borderwidth(0, style="StateActionsWindow.TFrame")
        self.label.configure(style="StateActionsWindow.TLabel")

    def move_to(self, event_x, event_y, first) -> None:
        """Reposition window to (event_x, event_y);
        Updates the move offset when first is True else maintains the offset."""
        if first:
            # Calculate the difference between the "anchor" point and the event:
            coords = project_manager.canvas.coords(self.window_id)
            self.difference_x, self.difference_y = -event_x + coords[0], -event_y + coords[1]
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + self.difference_x, event_y + self.difference_y
        project_manager.canvas.coords(self.window_id, event_x, event_y)

    def delete(self):
        """Remove window, ref_dict entry, and re-enable state_action_default button."""
        del custom_text.CustomText.read_variables_of_all_windows[self.text_id]
        del custom_text.CustomText.written_variables_of_all_windows[self.text_id]
        project_manager.canvas.delete(self.window_id)  # delete window
        del StateActionsDefault.ref_dict[self.window_id]
        project_manager.state_action_default_button.config(state=tk.NORMAL)

    @classmethod
    def create(cls, event) -> None:
        """Create state-actions-default window at event position and disable insert button."""
        project_manager.state_action_default_button.config(state=tk.DISABLED)
        canvas_grid_coordinates_of_the_event = (
            canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        )
        StateActionsDefault(
            canvas_grid_coordinates_of_the_event[0],
            canvas_grid_coordinates_of_the_event[1],
            padding=1,
            tags=("state_actions_default",),
            action="",
        )
        project_manager.undo_handling_ref.design_has_changed()
        canvas_modify_bindings.switch_to_move_mode()

    @classmethod
    def apply_new_font_size(cls) -> None:
        """Apply new font size to all state-actions-default windows."""
        for state_action in StateActionsDefault.ref_dict.values():
            state_action.label.configure(font=("Arial", int(max(1, project_manager.label_fontsize))))
            state_action.text_id.configure(font=("Courier", int(project_manager.fontsize)))
            state_action.text_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))

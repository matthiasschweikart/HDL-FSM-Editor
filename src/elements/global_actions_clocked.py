"""
Handles the global actions window in the diagram.
"""

import tkinter as tk
from tkinter import ttk

from actions import canvas_delete, canvas_editing, canvas_modify_bindings, move_handling_canvas_window
from gui import tab_diagram
from project_manager import project_manager
from widgets import custom_text


class GlobalActionsClocked:
    """
    Handles the global actions clocked window in the diagram.
    """

    global_actions_number = 1
    ref_dict = {}

    def __init__(self, menu_x, menu_y, padding, tags, before, after) -> None:
        self.old_before_text = ""
        self.old_after_text = ""
        self.difference_x = 0
        self.difference_y = 0
        self.borderwidth = 0
        self.frame_id = ttk.Frame(
            project_manager.canvas,
            relief=tk.FLAT,
            borderwidth=self.borderwidth,
            padding=padding,
            style="GlobalActionsWindow.TFrame",
        )
        self.label_before = ttk.Label(
            self.frame_id,
            text="Global actions clocked (executed before running the state machine):",
            font=("Arial", int(project_manager.label_fontsize)),
            style="GlobalActionsWindow.TLabel",
        )
        self.label_after = ttk.Label(
            self.frame_id,
            text="Global actions clocked (executed after running the state machine):",
            font=("Arial", int(project_manager.label_fontsize)),
            style="GlobalActionsWindow.TLabel",
        )
        self.text_before_id = custom_text.CustomText(
            self.frame_id,
            text_type="action",
            undo=True,
            maxundo=-1,
            font=("Courier", int(project_manager.fontsize)),
        )
        self.text_after_id = custom_text.CustomText(
            self.frame_id,
            text_type="action",
            undo=True,
            maxundo=-1,
            font=("Courier", int(project_manager.fontsize)),
        )
        self.label_before.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E))
        self.text_before_id.grid(row=1, column=0, sticky=(tk.E, tk.W))
        self.label_after.grid(row=2, column=0, sticky=(tk.E, tk.W))
        self.text_after_id.grid(row=3, column=0, sticky=(tk.E, tk.W, tk.S))
        # Create canvas window for frame:
        self.window_id = project_manager.canvas.create_window(
            menu_x, menu_y, window=self.frame_id, anchor=tk.W, tags=tags
        )
        GlobalActionsClocked.ref_dict[self.window_id] = self
        self.text_before_id.insert("1.0", before)
        self.text_before_id.format("element-insertion")
        self.text_after_id.insert("1.0", after)
        self.text_after_id.format("element-insertion")

        self.canvas_enter_func_id = None

        self.funcid_frame_enter = self.frame_id.bind("<Enter>", lambda event: self._start_editing())
        self.frame_id.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(event, self.frame_id, self.window_id),
        )

        self.funcid_label_before_enter = self.label_before.bind("<Enter>", lambda event: self._start_editing())
        self.label_before.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(
                event, self.label_before, self.window_id
            ),
        )
        self.funcid_label_after_enter = self.label_after.bind("<Enter>", lambda event: self._start_editing())
        self.label_after.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(event, self.label_after, self.window_id),
        )

        self.funcid_text_before_enter = self.text_before_id.bind("<Enter>", lambda event: self._start_editing())
        self.text_before_id.bind("<Control-e>", lambda event: self._edit_before_in_external_editor())
        self.text_before_id.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )
        self.text_before_id.bind("<FocusIn>", lambda event: project_manager.canvas.unbind_all("<Delete>"))

        self.funcid_text_after_enter = self.text_after_id.bind("<Enter>", lambda event: self._start_editing())
        self.text_after_id.bind("<Control-e>", lambda event: self._edit_after_in_external_editor())
        self.text_after_id.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )
        self.text_after_id.bind("<FocusIn>", lambda event: project_manager.canvas.unbind_all("<Delete>"))

        ids_list = (self.label_before, self.label_after, self.text_before_id, self.text_after_id)
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
        if canvas_id != self.label_before:
            event_y += self.label_before.winfo_height()
            if canvas_id != self.text_before_id:
                event_y += self.text_before_id.winfo_height()
                if canvas_id != self.label_after:
                    event_y += self.label_after.winfo_height()
        canvas_editing.zoom_wheel(event, event_x, event_y)

    def _edit_before_in_external_editor(self):
        self._update_old_before_text()
        self.text_before_id.edit_in_external_editor()

    def _edit_after_in_external_editor(self):
        self._update_old_after_text()
        self.text_after_id.edit_in_external_editor()

    def _update_old_before_text(self):
        self.old_before_text = self.text_before_id.get("1.0", tk.END)

    def _update_old_after_text(self):
        self.old_after_text = self.text_after_id.get("1.0", tk.END)

    def _old_text_differs_from_current_text(self) -> bool:
        return (
            self.text_before_id.get("1.0", tk.END) != self.old_before_text
            or self.text_after_id.get("1.0", tk.END) != self.old_after_text
        )

    def _start_editing(self) -> None:
        if self.funcid_frame_enter is not None:
            self.frame_id.unbind("<Enter>", self.funcid_frame_enter)
            self.funcid_frame_enter = None
        if self.funcid_label_before_enter is not None:
            self.label_before.unbind("<Enter>", self.funcid_label_before_enter)
            self.funcid_label_before_enter = None
        if self.funcid_label_after_enter is not None:
            self.label_after.unbind("<Enter>", self.funcid_label_after_enter)
            self.funcid_label_after_enter = None
        if self.funcid_text_before_enter is not None:
            self.text_before_id.unbind("<Enter>", self.funcid_text_before_enter)
            self.funcid_text_before_enter = None
        if self.funcid_text_after_enter is not None:
            self.text_after_id.unbind("<Enter>", self.funcid_text_after_enter)
            self.funcid_text_after_enter = None
        # The binding for 'Motion' must be added with '+', as 'store_mouse_position' is also bound to 'Motion':
        self.canvas_enter_func_id = project_manager.canvas.bind("<Motion>", lambda event: self._stop_editing(), "+")
        self._update_old_before_text()
        self._update_old_after_text()
        self._set_borderwidth(1, "WindowSelected.TFrame")
        self.label_before.configure(style="WindowSelected.TLabel")
        self.label_after.configure(style="WindowSelected.TLabel")

    def _stop_editing(self) -> None:
        project_manager.canvas.unbind("<Motion>", self.canvas_enter_func_id)
        project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete())
        if not custom_text.CustomText.selection_is_active:
            project_manager.canvas.focus_set()  # "unfocus" the Text, when the mouse leaves the text.
        self.funcid_frame_enter = self.frame_id.bind("<Enter>", lambda event: self._start_editing())
        self.funcid_label_before_enter = self.label_before.bind("<Enter>", lambda event: self._start_editing())
        self.funcid_label_after_enter = self.label_after.bind("<Enter>", lambda event: self._start_editing())
        self.funcid_text_before_enter = self.text_before_id.bind("<Enter>", lambda event: self._start_editing())
        self.funcid_text_after_enter = self.text_after_id.bind("<Enter>", lambda event: self._start_editing())
        if self._old_text_differs_from_current_text():
            project_manager.undo_handling_ref.design_has_changed()
        self._set_borderwidth(0, style="Window.TFrame")
        self.label_before.configure(style="Window.TLabel")
        self.label_after.configure(style="Window.TLabel")

    def _set_borderwidth(self, borderwidth: int, style: str) -> None:
        if project_manager.canvas.find_withtag(self.window_id):  # Delete causes leave-event, but window_id is invalid.
            diff = self.borderwidth - borderwidth
            self.borderwidth = borderwidth
            self.frame_id.configure(borderwidth=borderwidth, style=style)
            # Compensate for the borderwidth of the frame.
            pos = project_manager.canvas.coords(self.window_id)
            project_manager.canvas.coords(self.window_id, (pos[0] + diff, pos[1]))

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
        """Remove window, ref_dict entry, and re-enable global_action_clocked button."""
        del custom_text.CustomText.read_variables_of_all_windows[self.text_before_id]
        del custom_text.CustomText.written_variables_of_all_windows[self.text_before_id]
        del custom_text.CustomText.read_variables_of_all_windows[self.text_after_id]
        del custom_text.CustomText.written_variables_of_all_windows[self.text_after_id]
        project_manager.canvas.delete(self.window_id)
        del GlobalActionsClocked.ref_dict[self.window_id]
        project_manager.global_action_clocked_button.config(state=tk.NORMAL)

    @classmethod
    def create(cls, event) -> None:
        """Create clocked global-actions window at event position."""
        project_manager.global_action_clocked_button.config(state=tk.DISABLED)
        canvas_grid_coordinates_of_the_event = (
            canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
        )
        GlobalActionsClocked(
            canvas_grid_coordinates_of_the_event[0],
            canvas_grid_coordinates_of_the_event[1],
            padding=1,
            tags=("global_actions1",),
            before="",
            after="",
        )
        project_manager.undo_handling_ref.design_has_changed()
        canvas_modify_bindings.switch_to_move_mode()

    @classmethod
    def apply_new_font_size(cls) -> None:
        """Apply new font size to all clocked global-actions windows."""
        for global_action_clocked in GlobalActionsClocked.ref_dict.values():
            global_action_clocked.label_before.configure(font=("Arial", int(max(1, project_manager.label_fontsize))))
            global_action_clocked.label_after.configure(font=("Arial", int(max(1, project_manager.label_fontsize))))
            global_action_clocked.text_before_id.configure(font=("Courier", int(project_manager.fontsize)))
            global_action_clocked.text_before_id.configure_hdl_text_tags(
                font=("Courier", int(project_manager.fontsize))
            )
            global_action_clocked.text_after_id.configure(font=("Courier", int(project_manager.fontsize)))
            global_action_clocked.text_after_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))

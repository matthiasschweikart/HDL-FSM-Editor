"""
This class provides all methods needed to create and handle a Canvas window and all its included tkinter widgets.
The window contains pairs of label and text widgets in vertical order, which are specified in dictionary entry_dicts.
"""

import tkinter as tk
from tkinter import ttk

from gui import tab_diagram
from project_manager import project_manager
from widgets import custom_text


class CanvasWindow:
    """
    The content of the Canvas window is defined by a list of dictionaries:
    entry_dicts = [{"label_text" : str, "text_type" : str, "text" : str},
                   {"label_text" : str, "text_type" : str, "text" : str}, ...]
    """

    def __init__(
        self,
        window_x,
        window_y,
        tags,
        padding,
        move_handling_class,
        canvas_delete_class,
        zoom_wheel_function,
        entry_dicts,
        additional_move_func,
    ) -> None:
        self.difference_x = 0
        self.difference_y = 0
        self.borderwidth = 0
        self.additional_move_func = additional_move_func
        self.old_text = ["" for _ in range(len(entry_dicts))]
        self.funcid_canvas_enter = None
        self.funcid_frame_enter = None
        self.funcids_label_enter = []
        self.funcids_text_enter = []
        self.frame_id = self._create_frame_for_label_and_text_widgets(padding)
        self._add_bindings_to_frame(move_handling_class, canvas_delete_class)
        self.label_ids = []
        self.text_ids = []
        for entry_dict in entry_dicts:
            self._add_label_and_text_widget_to_frame(entry_dict)
        self._add_bindings_to_labels_and_text_widgets(move_handling_class, canvas_delete_class, zoom_wheel_function)
        self._show_all_text_widgets()
        if len(self.text_ids) > 1:
            self._hide_empty_text_widgets()
        self.window_id = project_manager.canvas.create_window(
            window_x, window_y, window=self.frame_id, tags=tags, anchor=tk.W
        )

    def _create_frame_for_label_and_text_widgets(self, padding):
        return ttk.Frame(
            project_manager.canvas, relief=tk.FLAT, borderwidth=self.borderwidth, padding=padding, style="Window.TFrame"
        )

    def _add_label_and_text_widget_to_frame(self, entry_dict):
        label_id = ttk.Label(
            self.frame_id,
            text=entry_dict["label_text"],
            font=("Arial", int(project_manager.label_fontsize)),
            style="Window.TLabel",
        )
        self.label_ids.append(label_id)
        custom_text_id = custom_text.CustomText(
            self.frame_id,
            text_type=entry_dict["text_type"],
            takefocus=0,
            undo=True,
            maxundo=-1,
            font=("Courier", int(project_manager.fontsize)),
        )
        self.text_ids.append(custom_text_id)
        custom_text_id.insert("1.0", entry_dict["text"])
        custom_text_id.format("element-insertion")

    def _add_bindings_to_frame(self, move_handling_class, canvas_delete_class):
        self.funcid_frame_enter = self.frame_id.bind("<Enter>", lambda event: self._start_editing(canvas_delete_class))
        self.frame_id.bind(
            "<Button-1>",
            # lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(event, self.frame_id, self.window_id),
            lambda event: move_handling_class(event, self.frame_id, self.window_id),
        )

    def _add_bindings_to_labels_and_text_widgets(self, move_handling_class, canvas_delete_class, zoom_wheel_function):
        for label_id in self.label_ids:
            self.funcids_label_enter.append(
                label_id.bind("<Enter>", lambda event: self._start_editing(canvas_delete_class))
            )
            label_id.bind(
                "<Button-1>", lambda event, label_id=label_id: move_handling_class(event, label_id, self.window_id)
            )
        for i, text_id in enumerate(self.text_ids):
            self.funcids_text_enter.append(
                text_id.bind("<Enter>", lambda event: self._start_editing(canvas_delete_class))
            )
            text_id.bind("<Control-e>", lambda event, i=i, text_id=text_id: self._edit_in_external_editor(i, text_id))
            text_id.bind("<FocusIn>", lambda event: project_manager.canvas.unbind_all("<Delete>"))
        seq1_list = ("<Control-MouseWheel>", "<Control-Button-4>", "<Control-Button-5>")
        seq2_list = ("<MouseWheel>", "<Button-4>", "<Button-5>")
        for canvas_id in self.label_ids + self.text_ids:
            for seq in seq1_list:
                canvas_id.bind(
                    seq,
                    lambda event, custom_text_id=canvas_id: self._zoom_by_wheel(
                        event, custom_text_id, zoom_wheel_function
                    ),
                )
            for seq in seq2_list:
                canvas_id.bind(seq, tab_diagram.TabDiagram.scroll_wheel)

    def _show_all_text_widgets(self) -> None:
        for i, label_id in enumerate(self.label_ids):
            label_id.grid(row=2 * i, column=0, sticky=(tk.W, tk.E))
            self.text_ids[i].grid(row=2 * i + 1, column=0, sticky=(tk.W, tk.E))

    def _hide_empty_text_widgets(self) -> None:
        all_empty = all(text_id.get("1.0", tk.END) == "\n" for text_id in self.text_ids)
        if not all_empty:
            for i, text_id in enumerate(self.text_ids):
                if text_id.get("1.0", tk.END) == "\n":
                    self.label_ids[i].grid_forget()
                    self.text_ids[i].grid_forget()

    def _start_editing(self, canvas_delete_class) -> None:
        self._show_all_text_widgets()
        self._unbind_all_enter_bindings()
        # The binding for 'Motion' must be added with '+', as 'store_mouse_position' is also bound to 'Motion':
        self.funcid_canvas_enter = project_manager.canvas.bind(
            "<Motion>", lambda event: self._stop_editing(canvas_delete_class), "+"
        )
        for i, text_id in enumerate(self.text_ids):
            self.old_text[i] = text_id.get("1.0", tk.END)
        self._show_window_as_selected()
        self._prepare_deletion_by_delete_key(canvas_delete_class)

    def _stop_editing(self, canvas_delete_class) -> None:
        if len(self.text_ids) > 1:
            self._hide_empty_text_widgets()
        project_manager.canvas.unbind("<Motion>", self.funcid_canvas_enter)
        self._restore_original_bindings(canvas_delete_class)
        if not custom_text.CustomText.selection_is_active:
            project_manager.canvas.focus_set()  # "unfocus" the Text, when the mouse leaves the text.
        if self._old_text_differs_from_current_text():
            project_manager.undo_handling_ref.design_has_changed()
        self._show_window_as_deselected()

    def _unbind_all_enter_bindings(self) -> None:
        if self.funcid_frame_enter is not None:
            self.frame_id.unbind("<Enter>", self.funcid_frame_enter)
            self.funcid_frame_enter = None
        for i, func_id in enumerate(self.funcids_label_enter):
            if func_id is not None:
                self.label_ids[i].unbind("<Enter>", func_id)
                self.funcids_label_enter[i] = None
        for i, func_id in enumerate(self.funcids_text_enter):
            if func_id is not None:
                self.text_ids[i].unbind("<Enter>", func_id)
                self.funcids_text_enter[i] = None

    def _show_window_as_selected(self) -> None:
        self._set_borderwidth(1, "WindowSelected.TFrame")
        for label_id in self.label_ids:
            label_id.configure(style="WindowSelected.TLabel")

    def _show_window_as_deselected(self) -> None:
        self._set_borderwidth(0, "Window.TFrame")
        for label_id in self.label_ids:
            label_id.configure(style="Window.TLabel")

    def _restore_original_bindings(self, canvas_delete_class) -> None:
        project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete_class())
        self.funcid_frame_enter = self.frame_id.bind("<Enter>", lambda event: self._start_editing(canvas_delete_class))
        for i, label_id in enumerate(self.label_ids):
            self.funcids_label_enter[i] = label_id.bind(
                "<Enter>", lambda event: self._start_editing(canvas_delete_class)
            )
        for i, text_id in enumerate(self.text_ids):
            self.funcids_text_enter[i] = text_id.bind("<Enter>", lambda event: self._start_editing(canvas_delete_class))

    def _old_text_differs_from_current_text(self) -> bool:
        return any(text_id.get("1.0", tk.END) != self.old_text[i] for i, text_id in enumerate(self.text_ids))

    def _set_borderwidth(self, borderwidth: int, style: str) -> None:
        """Set the borderwidth of the frame and adjust the position of the window accordingly."""
        # Delete calls _stop_editing, which calls set_borderwidth, but window_id is already invalid:
        if project_manager.canvas.find_withtag(self.window_id):
            diff = self.borderwidth - borderwidth
            self.borderwidth = borderwidth
            self.frame_id.configure(borderwidth=borderwidth, style=style)
            # Compensate for the borderwidth of the frame.
            pos = project_manager.canvas.coords(self.window_id)
            project_manager.canvas.coords(self.window_id, (pos[0] + diff, pos[1]))

    def _prepare_deletion_by_delete_key(self, canvas_delete_class) -> None:
        # Change canvas_x/y_coordinate stored in CanvasDelete to be able to delete this window by the delete-key.
        # CanvasDelete.store_mouse_position() stops working inside this (and all) Canvas window item and therefore
        # the coordinates must be changed to be for sure located inside this window when the delete key is pressed:
        window_canvas_coords = project_manager.canvas.coords(self.window_id)
        # The window anchor is tk.W, so the window-x-coordinate must be increased to be for sure inside the window.
        # The window-y-coordinate is already inside the window, as the anchor is in the middle of the window height:
        canvas_delete_class.canvas_x_coordinate = window_canvas_coords[0] + project_manager.state_radius
        canvas_delete_class.canvas_y_coordinate = window_canvas_coords[1]

    def _edit_in_external_editor(self, i, custom_text_id):
        self.old_text[i] = custom_text_id.get("1.0", tk.END)
        custom_text_id.edit_in_external_editor()

    def _update_old_text(self, custom_text_id):
        self.old_text[custom_text_id] = custom_text_id.get("1.0", tk.END)

    def _zoom_by_wheel(self, event, canvas_id, zoom_wheel_function) -> None:
        window_coords = project_manager.canvas.coords(self.window_id)
        window_bbox = project_manager.canvas.bbox(self.window_id)
        window_height = window_bbox[3] - window_bbox[1]
        window_root = [window_coords[0], window_coords[1] - window_height / 2]
        event_x = window_root[0] + event.x
        event_y = window_root[1] + event.y
        for i, label_id in enumerate(self.label_ids):
            if canvas_id != label_id:
                event_y += label_id.winfo_height()
                if canvas_id != self.text_ids[i]:
                    event_y += self.text_ids[i].winfo_height()
                else:
                    break
            else:
                break
        zoom_wheel_function(event, event_x, event_y)

    def _delete_read_and_written_variables(self) -> None:
        for text_id in self.text_ids:
            del custom_text.CustomText.read_variables_of_all_windows[text_id]
            del custom_text.CustomText.written_variables_of_all_windows[text_id]

    def move_to(self, event_x, event_y, first) -> None:
        """Reposition window and connecting line to (event_x, event_y); maintain anchor offset when first is True."""
        if first is True:
            # Calculate the difference between the "anchor" point and the event:
            coords = project_manager.canvas.coords(self.window_id)
            self.difference_x, self.difference_y = -event_x + coords[0], -event_y + coords[1]
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + self.difference_x, event_y + self.difference_y
        project_manager.canvas.coords(self.window_id, event_x, event_y)
        if self.additional_move_func is not None:
            self.additional_move_func(event_x, event_y)

    def apply_new_font_size_to_canvas_window(self) -> None:
        """Apply new font size to all label and text widgets of this window."""
        for label_id in self.label_ids:
            label_id.configure(font=("Arial", int(max(1, project_manager.label_fontsize))))
        for text_id in self.text_ids:
            text_id.configure(font=("Courier", int(project_manager.fontsize)))
            text_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))

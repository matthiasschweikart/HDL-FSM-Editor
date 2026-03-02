"""
This class handles the condition&action box which can be activated for each transition.

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


class ConditionAction:
    """This class handles the condition&action box which can be activated for each transition."""

    conditionaction_id = 0
    ref_dict = {}

    def __init__(
        self,
        menu_x,
        menu_y,
        connected_to_reset_entry,
        height,
        width,
        padding,
        tags,
        condition,
        action,
        line_coords,
        line_tags,
        increment,
    ) -> None:
        if increment is True:
            ConditionAction.conditionaction_id += 1
        self.difference_x = 0
        self.difference_y = 0
        self.action_text = action
        self.condition_text = condition
        self.borderwidth = 0
        self.frame_id = ttk.Frame(
            project_manager.canvas, relief=tk.FLAT, borderwidth=self.borderwidth, padding=padding, style="Window.TFrame"
        )
        self.condition_label = ttk.Label(
            self.frame_id,
            text="Transition condition: ",
            font=("Arial", int(project_manager.label_fontsize)),
            style="Window.TLabel",
        )
        self.condition_id = custom_text.CustomText(
            self.frame_id,
            text_type="condition",
            takefocus=0,
            height=height,
            width=width,
            undo=True,
            maxundo=-1,
            font=("Courier", int(project_manager.fontsize)),
        )
        self.action_label = ttk.Label(
            self.frame_id,
            text="Transition actions (asynchronous):" if connected_to_reset_entry else "Transition actions (clocked):",
            font=("Arial", int(project_manager.label_fontsize)),
            style="Window.TLabel",
        )
        self.action_id = custom_text.CustomText(
            self.frame_id,
            text_type="action",
            takefocus=0,
            height=height,
            width=width,
            undo=True,
            maxundo=-1,
            font=("Courier", int(project_manager.fontsize)),
        )
        self.window_id = project_manager.canvas.create_window(
            menu_x, menu_y, window=self.frame_id, tags=tags, anchor=tk.W
        )
        self.line_id = project_manager.canvas.create_line(
            menu_x,
            menu_y,
            line_coords[2],
            line_coords[3],
            dash=(2, 2),
            state=tk.HIDDEN,
            tag=line_tags,
        )
        project_manager.canvas.tag_lower(self.line_id)

        self.condition_id.insert("1.0", self.condition_text)
        self.condition_id.format()
        self.action_id.insert("1.0", self.action_text)
        self.action_id.format()
        self._show_condition_and_action()

        # The method _deactivate_frame() can not be bound to the Frame-leave-Event, because otherwise at moving the
        # cursor exactly at the frame would cause a flickering because of toggling between shrinked and full box.
        # Instead the method _deactivate_frame() is bound dynamically to the Canvas-Enter event in _activate_frame():
        self.frame_enter_func_id = self.frame_id.bind("<Enter>", lambda event: self._activate_frame())
        self.frame_id.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(event, self.frame_id, self.window_id),
        )
        self.canvas_enter_func_id = None
        self.condition_label.bind("<Enter>", lambda event: self._select_window())
        self.condition_label.bind("<Leave>", lambda event: self._deselect_window())
        self.condition_label.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(
                event, self.condition_label, self.window_id
            ),
        )
        self.action_label.bind("<Enter>", lambda event: self._select_window())
        self.action_label.bind("<Leave>", lambda event: self._deselect_window())
        self.action_label.bind(
            "<Button-1>",
            lambda event: move_handling_canvas_window.MoveHandlingCanvasWindow(
                event, self.action_label, self.window_id
            ),
        )
        self.condition_id.bind("<Control-z>", lambda event: self.condition_id.undo())
        self.condition_id.bind("<Control-Z>", lambda event: self.condition_id.redo())
        self.condition_id.bind("<Control-e>", lambda event: self._edit_condition_in_external_editor())
        self.condition_id.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        self.condition_id.bind("<Control-s>", lambda event: self._update_condition())  # Update self.text at "save".
        self.condition_id.bind("<Control-g>", lambda event: self._update_condition())  # Update self.text at "generate".
        self.condition_id.bind("<FocusIn>", lambda event: project_manager.canvas.unbind_all("<Delete>"))
        self.condition_id.bind(
            "<FocusOut>",
            lambda event: project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete()),
        )
        self.action_id.bind("<Control-z>", lambda event: self.action_id.undo())
        self.action_id.bind("<Control-Z>", lambda event: self.action_id.redo())
        self.action_id.bind("<Control-e>", lambda event: self._edit_action_in_external_editor())
        self.action_id.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        self.action_id.bind("<Control-s>", lambda event: self._update_action())  # Update self.text at "save".
        self.action_id.bind("<Control-g>", lambda event: self._update_action())  # Update self.text at "generate".
        self.action_id.bind("<FocusIn>", lambda event: project_manager.canvas.unbind_all("<Delete>"))
        self.action_id.bind(
            "<FocusOut>",
            lambda event: project_manager.canvas.bind_all("<Delete>", lambda event: canvas_delete.CanvasDelete()),
        )
        ids_list = (self.condition_label, self.action_label, self.condition_id, self.action_id)
        seq1_list = ("<Control-MouseWheel>", "<Control-Button-4>", "<Control-Button-5>")
        seq2_list = ("<MouseWheel>", "<Button-4>", "<Button-5>")
        for id in ids_list:
            for seq in seq1_list:
                id.bind(seq, lambda event: canvas_editing.zoom_wheel_window_item(event, self.window_id))
            for seq in seq2_list:
                id.bind(seq, tab_diagram.TabDiagram.scroll_wheel)

        # Create dictionary for translating the canvas-id of the canvas-window into a reference to this object:
        ConditionAction.ref_dict[self.window_id] = self

    def _show_condition_and_action(self) -> None:
        self.condition_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.condition_id.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.action_label.grid(row=2, column=0, sticky=(tk.W, tk.E))
        self.action_id.grid(row=3, column=0, sticky=(tk.W, tk.E))

    def _activate_frame(self) -> None:
        self._select_window()
        self._show_condition_and_action()
        self.action_text = self.action_id.get("1.0", tk.END)
        self.condition_text = self.condition_id.get("1.0", tk.END)
        if self.frame_enter_func_id is not None:
            self.frame_id.unbind("<Enter>", self.frame_enter_func_id)
            self.frame_enter_func_id = None
        # The binding for 'Motion' must be added with '+', as 'store_mouse_position' is also bound to 'Motion':
        self.canvas_enter_func_id = project_manager.canvas.bind("<Motion>", lambda event: self._deactivate_frame(), "+")

    def _set_borderwidth(self, borderwidth: int, style: str) -> None:
        diff = self.borderwidth - borderwidth
        self.borderwidth = borderwidth
        self.frame_id.configure(borderwidth=borderwidth, style=style)
        # Compensate for the borderwidth of the frame.
        pos = project_manager.canvas.coords(self.window_id)
        project_manager.canvas.coords(self.window_id, (pos[0] + diff, pos[1]))

    def _select_window(self) -> None:
        self._set_borderwidth(1, "WindowSelected.TFrame")
        self.condition_label.configure(style="WindowSelected.TLabel")
        self.action_label.configure(style="WindowSelected.TLabel")

    def _deactivate_frame(self) -> None:
        self._deselect_window()
        if self.canvas_enter_func_id is not None:
            project_manager.canvas.unbind("<Motion>", self.canvas_enter_func_id)
            self.canvas_enter_func_id = None
        self.frame_enter_func_id = self.frame_id.bind("<Enter>", lambda event: self._activate_frame())
        self._hide_empty_condition_or_action()

    def _deselect_window(self) -> None:
        project_manager.canvas.focus_set()  # "unfocus" the Text, when the mouse leaves the text.
        self._set_borderwidth(0, style="Window.TFrame")
        self.condition_label.configure(style="Window.TLabel")
        self.action_label.configure(style="Window.TLabel")

    def _edit_condition_in_external_editor(self):
        self.condition_id.edit_in_external_editor()
        self._update_condition()

    def _update_condition(self):
        # Update self.condition_text, so that the <Leave>-check in deactivate() does not signal a design-change and
        # that save_in_file() already reads the new text, entered into the textbox before Control-s/g.
        # To ensure this, save_in_file() waits for idle.
        self.condition_text = self.condition_id.get("1.0", tk.END)

    def _edit_action_in_external_editor(self):
        self.action_id.edit_in_external_editor()
        self._update_action()

    def _update_action(self):
        # Update self.action_text, so that the <Leave>-check in deactivate() does not signal a design-change and
        # that save_in_file() already reads the new text, entered into the textbox before Control-s/g.
        # To ensure this, save_in_file() waits for idle.
        self.action_text = self.action_id.get("1.0", tk.END)

    def _hide_empty_condition_or_action(self) -> None:
        if (
            self.condition_id.get("1.0", tk.END) != self.condition_text
            or self.action_id.get("1.0", tk.END) != self.action_text
        ):
            undo_handling.design_has_changed()
        if self.condition_id.get("1.0", tk.END) == "\n" and self.action_id.get("1.0", tk.END) != "\n":
            self.condition_label.grid_forget()
            self.condition_id.grid_forget()
        if self.condition_id.get("1.0", tk.END) != "\n" and self.action_id.get("1.0", tk.END) == "\n":
            self.action_label.grid_forget()
            self.action_id.grid_forget()

    def change_descriptor_to(self, text) -> None:
        """Set the action label text (e.g. 'asynchronous' or 'synchronous')."""
        self.action_label.config(
            text=text
        )  # Used for switching between "asynchronous" and "synchronous" (clocked) transition.

    def move_to(self, event_x, event_y, first) -> None:
        """Reposition window and connecting line to (event_x, event_y); maintain anchor offset when first is True."""
        if first is True:
            # Calculate the difference between the "anchor" point and the event:
            coords = project_manager.canvas.coords(self.window_id)
            self.difference_x, self.difference_y = -event_x + coords[0], -event_y + coords[1]
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + self.difference_x, event_y + self.difference_y
        project_manager.canvas.coords(self.window_id, event_x, event_y)
        # Move the line which connects the window to the transition:
        line_coords = project_manager.canvas.coords(self.line_id)
        line_coords[0] = event_x
        line_coords[1] = event_y
        project_manager.canvas.coords(self.line_id, line_coords)
        project_manager.canvas.itemconfig(self.line_id, state=tk.NORMAL)

    def hide_line(self) -> None:
        """Hide the canvas line connecting this condition-action window to the transition."""
        project_manager.canvas.itemconfig(self.line_id, state=tk.HIDDEN)

    def delete(self):
        """Remove condition-action window, line, and ref_dict entries; delete linked transition if connector-based."""
        number = project_manager.canvas.gettags(self.window_id)[0][16:]  # extract <n> from "condition_action<n>"
        del custom_text.CustomText.read_variables_of_all_windows[self.condition_id]
        del custom_text.CustomText.written_variables_of_all_windows[self.condition_id]
        del custom_text.CustomText.read_variables_of_all_windows[self.action_id]
        del custom_text.CustomText.written_variables_of_all_windows[self.action_id]
        project_manager.canvas.delete(self.window_id)
        project_manager.canvas.delete(self.line_id)
        project_manager.canvas.dtag("all", "ca_connection" + number + "_end")
        del ConditionAction.ref_dict[self.window_id]

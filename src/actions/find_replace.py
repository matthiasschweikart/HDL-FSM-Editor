"""
This class implements the "find" and "replace" feature.
"""

import re
import tkinter as tk
from tkinter import messagebox

from actions import canvas_editing
from constants import GuiTab
from project_manager import project_manager


class FindReplace:
    """
    The methods _search_in_canvas_text() and _search_in_entry_widget() use <string>.find(), re.findall() and re.sub().
    All other search-methods use text_widget.search() for find and replace.
    In order to have identical behaviour in _search_in_canvas_text() and _search_in_entry_widget(),
    there the search_string/replace_string are "escaped".
    """

    _active_dialog: "tk.Toplevel | None" = None

    def __init__(self, search_string, replace_string, replace, in_hdl=False) -> None:
        if FindReplace._active_dialog is not None and FindReplace._active_dialog.winfo_exists():
            FindReplace._active_dialog.destroy()  # close any dialog waiting for user input
        self.count = 0
        self.number_of_hits_all = 0
        self.search_pattern = search_string.get()
        self.replace_pattern = replace_string.get()
        self.replace = replace
        self._first_time_showing_dialog = True
        if self.search_pattern == "":
            messagebox.showinfo("HDL-FSM-Editor", "No search is performed because you search for an empty string.")
            return
        if in_hdl:
            text_field = {"tab": GuiTab.GENERATED_HDL, "ref": project_manager.tab_hdl_ref.hdl_frame_text, "update": ""}
            continue_search = self._search_in_text_field(text_field)
            if not continue_search:
                return
        else:
            continue_search = self._search_in_diagram()
            if not continue_search:
                return
            continue_search = self._search_in_all_text_fields()  # but not in the text fields of diagram tab
            if not continue_search:
                return
            continue_search = self._search_in_all_entry_widgets()
            if not continue_search:
                return
        if replace:
            project_manager.undo_handling_ref.design_has_changed()
            messagebox.showinfo("HDL-FSM-Editor", "Number of replacements = " + str(self.number_of_hits_all))
        else:
            messagebox.showinfo("HDL-FSM-Editor", "Number of hits = " + str(self.number_of_hits_all))

    def _search_in_diagram(self) -> bool:
        all_canvas_items = project_manager.canvas.find_all()
        continue_search = True
        for item in all_canvas_items:
            if project_manager.canvas.type(item) == "window":
                continue_search = self._search_in_all_text_fields_of_canvas_window(item)
            elif project_manager.canvas.type(item) == "text":
                continue_search = self._search_in_canvas_text(item)
            if continue_search is False:
                break
        return continue_search

    def _search_in_all_text_fields(self) -> bool:
        continue_search = True
        text_fields = []
        if project_manager.language.get() == "VHDL":
            text_fields.append(
                {
                    "tab": GuiTab.INTERFACE,
                    "ref": project_manager.tab_interface_ref.interface_packages_text,
                    "update": "Ports",
                }
            )
        text_fields.append(
            {
                "tab": GuiTab.INTERFACE,
                "ref": project_manager.tab_interface_ref.interface_generics_text,
                "update": "Generics",
            }
        )
        text_fields.append(
            {"tab": GuiTab.INTERFACE, "ref": project_manager.tab_interface_ref.interface_ports_text, "update": "Ports"}
        )
        if project_manager.language.get() == "VHDL":
            text_fields.append(
                {
                    "tab": GuiTab.INTERNALS,
                    "ref": project_manager.tab_internals_ref.internals_packages_text,
                    "update": "",
                }
            )
        text_fields.append(
            {
                "tab": GuiTab.INTERNALS,
                "ref": project_manager.tab_internals_ref.internals_architecture_text,
                "update": "",
            }
        )
        text_fields.append(
            {
                "tab": GuiTab.INTERNALS,
                "ref": project_manager.tab_internals_ref.internals_process_clocked_text,
                "update": "",
            }
        )
        text_fields.append(
            {
                "tab": GuiTab.INTERNALS,
                "ref": project_manager.tab_internals_ref.internals_process_combinatorial_text,
                "update": "",
            }
        )
        text_fields.append(
            {"tab": GuiTab.GENERATED_HDL, "ref": project_manager.tab_hdl_ref.hdl_frame_text, "update": ""}
        )
        for text_field in text_fields:
            if continue_search:
                continue_search = self._search_in_text_field(text_field)
        return continue_search

    def _search_in_all_entry_widgets(self):
        continue_search = True
        for entry_widget_info in project_manager.entry_widgets:
            if continue_search:
                continue_search = self._search_in_entry_widget(entry_widget_info)
        return continue_search

    def _search_in_all_text_fields_of_canvas_window(self, item) -> bool:
        for text_id in project_manager.canvas_windows_ref_dict[item].text_ids:
            text_field = {"tab": GuiTab.DIAGRAM, "ref": text_id, "update": "", "window_id": item}
            continue_search = self._search_in_text_field(text_field)
            if not continue_search:
                break
        return continue_search

    def _search_in_canvas_text(self, item) -> bool:
        text = project_manager.canvas.itemcget(item, "text")
        start = 0
        continue_search = True
        while True:
            hit_begin = text.find(self.search_pattern, start, len(text))
            if hit_begin == -1:
                break
            if self.replace:
                # All hits are replaced in 1 action:
                search_pattern_escaped = re.escape(self.search_pattern)
                replace_pattern_escaped = re.escape(self.replace_pattern)
                self.number_of_hits_all += len(re.findall(search_pattern_escaped, text, flags=re.IGNORECASE))
                text = re.sub(search_pattern_escaped, replace_pattern_escaped, text, flags=re.IGNORECASE)
                project_manager.canvas.itemconfigure(item, text=text)
                start = len(text)  # The search-pattern cannot be found again in the next loop.
            else:
                self.number_of_hits_all += 1
                self._move_in_foreground(GuiTab.DIAGRAM)
                if start == 0:
                    fontspec = project_manager.canvas.itemcget(item, "font")
                    size = tk.font.Font(font=fontspec).cget("size")
                    factor = 20 / size  # Zoom factor to make the text 20 pixels high
                    object_center = project_manager.canvas.coords(item)
                    project_manager.grid_drawer.remove_grid()
                    canvas_editing.canvas_zoom(object_center, factor)
                    project_manager.grid_drawer.draw_grid()
                project_manager.canvas.select_from(item, hit_begin)
                project_manager.canvas.select_to(item, hit_begin + len(self.search_pattern) - 1)
                continue_search = self._ask_continue()
                if continue_search is False:
                    break
                start = hit_begin + len(self.search_pattern)
            if start == hit_begin:
                messagebox.showinfo(
                    "HDL-FSM-Editor", "Search in canvas text is aborted as for unknown reason no progress happens."
                )
                break
        return continue_search

    def _search_in_text_field(self, text_field) -> bool:
        count = tk.IntVar()
        start = "1.0"
        continue_search = True
        while True:
            index = text_field["ref"].search(
                self.search_pattern, start, tk.END, count=count, regexp=True, nocase=1
            )  # index = "line.column"
            if index == "" or count.get() == 0:
                break
            if self.replace:
                if text_field["ref"].cget("state") != tk.DISABLED:
                    self.number_of_hits_all += 1
                    end_index = index + "+" + str(len(self.search_pattern)) + " chars"
                    text_field["ref"].delete(index, end_index)
                    text_field["ref"].insert(index, self.replace_pattern)
                    start = index + "+" + str(len(self.replace_pattern)) + " chars"
                    if text_field["tab"] == GuiTab.INTERFACE:
                        if text_field["update"] == "Generics":
                            text_field["ref"].update_custom_text_class_generics_list()
                        else:  # kind=="ports"
                            text_field["ref"].update_custom_text_class_ports_list()
                    elif text_field["tab"] == GuiTab.INTERNALS:
                        text_field["ref"].update_custom_text_class_signals_list()
                        text_field["ref"].update_custom_text_functions_list()
                    elif text_field["tab"] == GuiTab.DIAGRAM:
                        text_field["ref"].format_after_idle(None)
                else:
                    break
            else:
                self.number_of_hits_all += 1
                self._move_in_foreground(text_field["tab"])
                text_field["ref"].tag_add("hit", index, index + " + " + str(count.get()) + " chars")
                text_field["ref"].tag_configure("hit", background="skyblue")
                if text_field["tab"] == GuiTab.DIAGRAM and start == "1.0":
                    object_coords = project_manager.canvas.bbox(text_field["window_id"])
                    object_coords_new = []
                    object_coords_new.append(object_coords[0] - 0.1 * (object_coords[2] - object_coords[0]))
                    object_coords_new.append(object_coords[1] - 0.1 * (object_coords[3] - object_coords[1]))
                    object_coords_new.append(object_coords[2] + 0.1 * (object_coords[2] - object_coords[0]))
                    object_coords_new.append(object_coords[3] + 0.1 * (object_coords[3] - object_coords[1]))
                    canvas_editing.view_rectangle(object_coords_new, check_fit=False)
                else:
                    text_field["ref"].see(index)
                continue_search = self._ask_continue()
                text_field["ref"].tag_delete("hit")
                if not continue_search:
                    break
                start = index + " + " + str(count.get()) + " chars"
        return continue_search

    def _search_in_entry_widget(self, entry_widget_info) -> bool:
        value = entry_widget_info["stringvar"].get()
        start = 0
        continue_search = True
        while True:
            hit_begin = value.find(self.search_pattern, start, len(value))
            if hit_begin == -1:
                break
            if self.replace:
                # All hits are replaced in 1 action:
                search_pattern_escaped = re.escape(self.search_pattern)
                replace_pattern_escaped = re.escape(self.replace_pattern)
                self.number_of_hits_all += len(re.findall(search_pattern_escaped, value, flags=re.IGNORECASE))
                value = re.sub(search_pattern_escaped, replace_pattern_escaped, value, flags=re.IGNORECASE)
                entry_widget_info["stringvar"].set(value)
                start = len(value)  # The search-pattern cannot be found again in the next loop.
            else:
                self.number_of_hits_all += 1
                self._move_in_foreground(GuiTab.CONTROL)
                entry_widget_info["entry"].select_range(hit_begin, hit_begin + len(self.search_pattern))
                continue_search = self._ask_continue()
                if continue_search is False:
                    break
                start = hit_begin + len(self.search_pattern)
            if start == hit_begin:
                messagebox.showinfo(
                    "HDL-FSM-Editor",
                    "Search in entry field of Control-tab is aborted as for unknown reason no progress happens.",
                )
                break
        return continue_search

    def _ask_continue(self) -> bool:
        """Non-modal Yes/No dialog that keeps the main window responsive."""
        dialog = tk.Toplevel()  # open new window
        dialog.wm_attributes("-topmost", True)
        dialog.title("Continue")
        dialog.resizable(False, False)
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.bind("<Escape>", lambda _: dialog.destroy())
        FindReplace._active_dialog = dialog  # Store the reference so that the window can be closed by another search.
        answer = tk.BooleanVar(value=False)
        self._show_continue_dialog(dialog, answer)
        dialog.wait_window(dialog)  # Waits until the dialog is closed by the user, but keeps the main window responsive
        return answer.get()

    def _show_continue_dialog(self, dialog, answer) -> None:
        tk.Label(dialog, text="Find next?", padx=10, pady=8).grid()
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(pady=(0, 8))
        yes_button = tk.Button(btn_frame, text="Yes", width=8, command=lambda: (answer.set(True), dialog.destroy()))
        yes_button.bind("<Return>", lambda _: (answer.set(True), dialog.destroy()))
        yes_button.focus_set()  # Set initial keyboard focus to the "Yes" button
        yes_button.grid(row=0, column=0, padx=30)
        not_button = tk.Button(btn_frame, text="No", width=8, command=dialog.destroy)
        not_button.grid(row=0, column=1, padx=30)
        if self._first_time_showing_dialog:
            self._first_time_showing_dialog = False
        else:
            self._move_dialog_under_mouse_cursor(dialog)

    def _move_dialog_under_mouse_cursor(self, dialog):
        dialog.update_idletasks()  # Ensure the dialog is fully rendered before it can be interacted with
        x, y = project_manager.root.winfo_pointerxy()
        geometry_parts = dialog.geometry().split("+")
        geometry_dimensions = geometry_parts[0].split("x")  # e.g., "200x100"
        dialog.geometry(f"+{x - int(geometry_dimensions[0]) // 4}+{y - int(geometry_dimensions[1])}")

    def _move_in_foreground(self, tab: GuiTab) -> None:
        notebook_ids = project_manager.notebook.tabs()
        for notebook_id in notebook_ids:
            if project_manager.notebook.tab(notebook_id, option="text") == tab.value:
                project_manager.notebook.select(notebook_id)

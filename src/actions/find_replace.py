"""
This class implements the "find" and "replace" feature.
"""

import re
import tkinter as tk
from tkinter import messagebox

from actions import canvas_editing
from constants import GuiTab
from elements import (
    condition_action,
    global_actions_clocked,
    global_actions_combinatorial,
    state_action,
    state_actions_default,
    state_comment,
)
from project_manager import project_manager


class FindReplace:
    """
    The methods _search_in_canvas_text() and _search_in_entry_widget() use <string>.find(), re.findall() and re.sub().
    All other search-methods use text_widget.search() for find and replace.
    In order to have identical behaviour in _search_in_canvas_text() and _search_in_entry_widget(),
    there the search_string/replace_string are "escaped".
    """

    def __init__(self, search_string, replace_string, replace, in_hdl=False) -> None:
        self.number_of_hits_all = 0
        self.search_pattern = search_string.get()
        self.replace_pattern = replace_string.get()
        self.replace = replace
        if self.search_pattern == "":
            messagebox.showinfo("HDL-FSM-Editor", "The search is aborted because you searched for an empty string.")
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
            continue_search = self._search_in_all_text_fields()
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
                text_ids = self._get_text_ids_of_canvas_window(item)
                continue_search = self._search_in_all_text_fields_of_canvas_window(item, text_ids)
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
                    "ref": project_manager.tab_interface_ref.interface_package_text,
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
                {"tab": GuiTab.INTERNALS, "ref": project_manager.tab_internals_ref.internals_package_text, "update": ""}
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

    def _get_text_ids_of_canvas_window(self, item) -> list:
        text_ids = []
        if item in state_action.StateAction.ref_dict:
            text_ids.append(state_action.StateAction.ref_dict[item].text_id)
        elif item in condition_action.ConditionAction.ref_dict:
            text_ids.append(condition_action.ConditionAction.ref_dict[item].condition_id)
            text_ids.append(condition_action.ConditionAction.ref_dict[item].action_id)
        elif item in global_actions_clocked.GlobalActionsClocked.ref_dict:
            text_ids.append(global_actions_clocked.GlobalActionsClocked.ref_dict[item].text_before_id)
            text_ids.append(global_actions_clocked.GlobalActionsClocked.ref_dict[item].text_after_id)
        elif item in global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict:
            text_ids.append(global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict[item].text_id)
        elif item in state_actions_default.StateActionsDefault.ref_dict:
            text_ids.append(state_actions_default.StateActionsDefault.ref_dict[item].text_id)
        elif item in state_comment.StateComment.ref_dict:
            text_ids.append(state_comment.StateComment.ref_dict[item].text_id)
        return text_ids

    def _search_in_all_text_fields_of_canvas_window(self, item, text_ids_of_actions) -> bool:
        for text_id in text_ids_of_actions:
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
                project_manager.canvas.select_from(item, hit_begin)
                project_manager.canvas.select_to(item, hit_begin + len(self.search_pattern) - 1)
                object_coords = project_manager.canvas.bbox(item)
                canvas_editing.view_rectangle(object_coords, check_fit=False)
                object_center = project_manager.canvas.coords(item)
                canvas_editing.canvas_zoom(object_center, 0.25)
                continue_search = messagebox.askyesno("Continue", "Find next")
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
                    elif text_field["tab"] == GuiTab.DIAGRAM:
                        text_field["ref"].format_after_idle(None)
                else:
                    break
            else:
                self.number_of_hits_all += 1
                self._move_in_foreground(text_field["tab"])
                text_field["ref"].tag_add("hit", index, index + " + " + str(count.get()) + " chars")
                text_field["ref"].tag_configure("hit", background="blue")
                start = index + " + " + str(count.get()) + " chars"
                if text_field["tab"] == GuiTab.DIAGRAM:
                    object_coords = project_manager.canvas.bbox(text_field["window_id"])
                    object_coords_new = []
                    object_coords_new.append(object_coords[0] - 100)
                    object_coords_new.append(object_coords[1] - 100)
                    object_coords_new.append(object_coords[2] + 300)
                    object_coords_new.append(object_coords[3] + 300)
                    canvas_editing.view_rectangle(object_coords_new, check_fit=False)
                else:
                    text_field["ref"].see(index)
                continue_search = messagebox.askyesno("Continue", "Find next")
                text_field["ref"].tag_remove("hit", index, index + " + " + str(count.get()) + " chars")
                if not continue_search:
                    break
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
                continue_search = messagebox.askyesno("Continue", "Find next")
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

    def _move_in_foreground(self, tab: GuiTab) -> None:
        notebook_ids = project_manager.notebook.tabs()
        for notebook_id in notebook_ids:
            if project_manager.notebook.tab(notebook_id, option="text") == tab.value:
                project_manager.notebook.select(notebook_id)

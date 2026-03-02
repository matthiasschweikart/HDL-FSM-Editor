"""
This module contains all methods needed for reading and writing from or to a file.
"""

import json
import os
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Any

import canvas_editing
import constants
import custom_text
import tag_plausibility
import undo_handling
import update_hdl_tab
import write_data_creator
from constants import GuiTab
from elements import (
    condition_action,
    connector,
    global_actions_clocked,
    global_actions_combinatorial,
    reset_entry,
    state,
    state_action,
    state_actions_default,
    state_comment,
    transition,
)
from project_manager import project_manager

# Pylint expects this to be a constant with uppercase naming.
_write_data_creator_ref = None  # pylint: disable=invalid-name # module-level mutable ref


def ask_save_unsaved_changes(title) -> str:
    """
    Ask user what to do with unsaved changes.
    Returns: 'save', 'discard', or 'cancel'
    """
    result = messagebox.askyesnocancel(
        "HDL-FSM-Editor",
        f"There are unsaved changes in design:\n{title[:-1]}\nDo you want to save them?",
        default="cancel",
        icon="warning",
    )
    if result is True:
        return "save"
    if result is False:
        return "discard"
    return "cancel"


def save_as() -> None:
    """Prompt for save-as path and save the project to the chosen file."""
    old_previous_file = project_manager.previous_file
    project_manager.previous_file = project_manager.current_file
    project_manager.current_file = asksaveasfilename(
        defaultextension=".hfe",
        initialfile=project_manager.module_name.get(),
        filetypes=(("HDL-FSM-Editor files", "*.hfe"), ("all files", "*.*")),
    )
    if project_manager.current_file not in ((), ""):
        dir_name, file_name = os.path.split(project_manager.current_file)
        project_manager.root.title(f"{file_name} ({dir_name})")
        save_in_file(project_manager.current_file)
    else:
        project_manager.current_file = project_manager.previous_file
        project_manager.previous_file = old_previous_file


def save() -> None:
    """Save project to current file, or prompt for path if never saved before."""
    # Use state manager instead of global variables
    project_manager.previous_file = project_manager.current_file
    if project_manager.current_file == "":
        project_manager.current_file = asksaveasfilename(
            defaultextension=".hfe",
            initialfile=project_manager.module_name.get(),
            filetypes=(("HDL-FSM-Editor files", "*.hfe"), ("all files", "*.*")),
        )
    if project_manager.current_file != "":
        dir_name, file_name = os.path.split(project_manager.current_file)
        project_manager.root.title(f"{file_name} ({dir_name})")
        project_manager.root.after_idle(
            save_in_file, project_manager.current_file
        )  # Wait for the handling of all possible events.


def open_file() -> None:
    """Prompt for an .hfe file and open it."""
    filename_new = askopenfilename(filetypes=(("HDL-FSM-Editor files", "*.hfe"), ("all files", "*.*")))
    if filename_new != "":
        success = new_design()
        if success:
            open_file_with_name(filename_new, is_script_mode=False)


def new_design() -> bool:
    """Clear current design after optional save; return False if user cancels."""
    title = project_manager.root.title()
    if title.endswith("*"):
        action = ask_save_unsaved_changes(title)
        if action == "cancel":
            return False
        if action == "save":
            save()
            # Check if save was successful (current_file is not empty)
            if project_manager.current_file == "":
                return False

    _clear_design()
    return True


def _clear_design() -> bool:
    global _write_data_creator_ref
    project_manager.current_file = ""
    project_manager.module_name.set("")
    project_manager.reset_signal_name.set("")
    project_manager.clock_signal_name.set("")
    project_manager.interface_package_text.delete("1.0", tk.END)
    project_manager.interface_generics_text.delete("1.0", tk.END)
    project_manager.interface_ports_text.delete("1.0", tk.END)
    project_manager.internals_package_text.delete("1.0", tk.END)
    project_manager.internals_architecture_text.delete("1.0", tk.END)
    project_manager.internals_process_clocked_text.delete("1.0", tk.END)
    project_manager.internals_process_combinatorial_text.delete("1.0", tk.END)
    project_manager.hdl_frame_text.config(state=tk.NORMAL)
    project_manager.hdl_frame_text.delete("1.0", tk.END)
    project_manager.hdl_frame_text.config(state=tk.DISABLED)
    project_manager.canvas.delete("all")
    state.States.state_number = 0
    transition.TransitionLine.transition_number = 0
    project_manager.reset_entry_button.config(state=tk.NORMAL)
    connector.ConnectorInstance.connector_number = 0
    condition_action.ConditionAction.conditionaction_id = 0
    condition_action.ConditionAction.ref_dict = {}
    state_action.StateAction.state_action_id = 0
    state_action.StateAction.ref_dict = {}
    state_actions_default.StateActionsDefault.ref_dict = {}
    project_manager.state_action_default_button.config(state=tk.NORMAL)
    project_manager.global_action_clocked_button.config(state=tk.NORMAL)
    project_manager.global_action_combinatorial_button.config(state=tk.NORMAL)
    global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict = {}
    global_actions_clocked.GlobalActionsClocked.ref_dict = {}
    project_manager.state_radius = 20.0
    project_manager.priority_distance = 14
    project_manager.reset_entry_size = 40
    canvas_editing.canvas_x_coordinate = 0
    canvas_editing.canvas_y_coordinate = 0
    project_manager.fontsize = 10
    project_manager.label_fontsize = 8
    project_manager.state_name_font.configure(size=int(project_manager.fontsize))
    project_manager.include_timestamp_in_output.set(True)
    project_manager.root.title("unnamed")
    project_manager.grid_drawer.draw_grid()
    if _write_data_creator_ref is None:
        _write_data_creator_ref = write_data_creator.WriteDataCreator(project_manager.state_radius)
    _write_data_creator_ref.store_as_compare_object(None)
    return True


########################################################################################################################


def save_in_file(save_filename) -> None:  # Called at saving and at every design change (writing to .tmp-file)
    """Serialize project to the given .hfe file (or .tmp)."""
    global _write_data_creator_ref
    allowed_element_names_in_design_dictionary = (
        "state",
        "text",
        "line",
        "polygon",
        "rectangle",
        "window_state_action_block",
        "window_state_comment",
        "window_condition_action_block",
        "window_global_actions",
        "window_global_actions_combinatorial",
        "window_state_actions_default",
    )
    if _write_data_creator_ref is None:
        _write_data_creator_ref = write_data_creator.WriteDataCreator(project_manager.state_radius)
    if not save_filename.endswith(".tmp"):
        zoom_factor = _write_data_creator_ref.zoom_graphic_to_standard_size(project_manager.state_radius)
    design_dictionary = _save_design_to_dict(allowed_element_names_in_design_dictionary)
    if not save_filename.endswith(".tmp"):
        _write_data_creator_ref.zoom_graphic_back_to_actual_size(zoom_factor)
        design_dictionary = _write_data_creator_ref.round_and_sort_data(
            design_dictionary, allowed_element_names_in_design_dictionary
        )
    old_cursor = project_manager.root.cget(
        "cursor"
    )  # may be different from "arrow" at design changes (writing to .tmp-file)
    project_manager.root.config(cursor="watch")
    try:
        with open(save_filename, "w", encoding="utf-8") as fileobject:
            json.dump(design_dictionary, fileobject, indent=4, default=str, ensure_ascii=False)
        if not save_filename.endswith(".tmp") and os.path.isfile(f"{project_manager.previous_file}.tmp"):
            os.remove(f"{project_manager.previous_file}.tmp")
        project_manager.root.config(cursor=old_cursor)
    except Exception as _:
        project_manager.root.config(cursor=old_cursor)
        messagebox.showerror("Error in HDL-FSM-Editor", f"Writing to file {save_filename} caused exception ")
    if not tag_plausibility.TagPlausibility().get_tag_status_is_okay():
        project_manager.root.config(cursor=old_cursor)
        messagebox.showerror("Error", "The database is corrupt.\nDo not use the written file.\nSee details at STDOUT.")


def _save_design_to_dict(allowed_element_names_in_design_dictionary) -> dict[str, Any]:
    design_dictionary = {}
    _save_control_data(design_dictionary)
    _save_interface_data(design_dictionary)
    _save_internals_data(design_dictionary)
    _save_log_config(design_dictionary)
    _save_canvas_data(design_dictionary, allowed_element_names_in_design_dictionary)

    return design_dictionary


def _save_control_data(design_dictionary: dict[str, Any]) -> None:
    design_dictionary["modulename"] = project_manager.module_name.get()
    design_dictionary["language"] = project_manager.language.get()
    design_dictionary["generate_path"] = project_manager.generate_path_value.get()
    design_dictionary["additional_sources"] = project_manager.additional_sources_value.get()
    design_dictionary["working_directory"] = project_manager.working_directory_value.get()
    design_dictionary["number_of_files"] = project_manager.select_file_number_text.get()
    design_dictionary["reset_signal_name"] = project_manager.reset_signal_name.get()
    design_dictionary["clock_signal_name"] = project_manager.clock_signal_name.get()
    design_dictionary["compile_cmd"] = project_manager.compile_cmd.get()
    design_dictionary["edit_cmd"] = project_manager.edit_cmd.get()
    design_dictionary["include_timestamp_in_output"] = project_manager.include_timestamp_in_output.get()


def _save_interface_data(design_dictionary: dict[str, Any]) -> None:
    design_dictionary["interface_package"] = project_manager.interface_package_text.get("1.0", f"{tk.END}-1 chars")
    design_dictionary["interface_generics"] = project_manager.interface_generics_text.get("1.0", f"{tk.END}-1 chars")
    design_dictionary["interface_ports"] = project_manager.interface_ports_text.get("1.0", f"{tk.END}-1 chars")


def _save_internals_data(design_dictionary: dict[str, Any]) -> None:
    design_dictionary["internals_package"] = project_manager.internals_package_text.get("1.0", f"{tk.END}-1 chars")
    design_dictionary["internals_architecture"] = project_manager.internals_architecture_text.get(
        "1.0", f"{tk.END}-1 chars"
    )
    design_dictionary["internals_process"] = project_manager.internals_process_clocked_text.get(
        "1.0", f"{tk.END}-1 chars"
    )
    design_dictionary["internals_process_combinatorial"] = project_manager.internals_process_combinatorial_text.get(
        "1.0", f"{tk.END}-1 chars"
    )


def _save_log_config(design_dictionary: dict[str, Any]) -> None:
    if project_manager.language.get() == "VHDL":
        design_dictionary["regex_message_find"] = project_manager.regex_message_find_for_vhdl
    else:
        design_dictionary["regex_message_find"] = project_manager.regex_message_find_for_verilog
    design_dictionary["regex_file_name_quote"] = project_manager.regex_file_name_quote
    design_dictionary["regex_file_line_number_quote"] = project_manager.regex_file_line_number_quote


def _save_canvas_data(design_dictionary: dict[str, Any], allowed_element_names_in_design_dictionary) -> None:
    design_dictionary["diagram_background_color"] = project_manager.diagram_background_color.get()
    design_dictionary["state_number"] = state.States.state_number
    design_dictionary["transition_number"] = transition.TransitionLine.transition_number
    design_dictionary["connector_number"] = connector.ConnectorInstance.connector_number
    design_dictionary["conditionaction_id"] = condition_action.ConditionAction.conditionaction_id
    design_dictionary["mytext_id"] = state_action.StateAction.state_action_id
    design_dictionary["state_radius"] = project_manager.state_radius
    design_dictionary["reset_entry_size"] = project_manager.reset_entry_size
    design_dictionary["priority_distance"] = project_manager.priority_distance
    design_dictionary["fontsize"] = project_manager.fontsize
    design_dictionary["label_fontsize"] = project_manager.label_fontsize
    # design_dictionary["visible_center"] = get_visible_center_as_string()
    # design_dictionary["sash_positions"] = main_window.sash_positions
    for element_name in allowed_element_names_in_design_dictionary:
        design_dictionary[element_name] = []
    items = project_manager.canvas.find_all()
    for i in items:
        item_type = project_manager.canvas.type(i)
        if item_type == "oval":
            design_dictionary["state"].append(
                [project_manager.canvas.coords(i), _gettags(i), project_manager.canvas.itemcget(i, "fill")]
            )
        elif item_type == "text":
            design_dictionary["text"].append(
                [project_manager.canvas.coords(i), _gettags(i), project_manager.canvas.itemcget(i, "text")]
            )
        elif item_type == "line" and "grid_line" not in _gettags(i):
            design_dictionary["line"].append([project_manager.canvas.coords(i), _gettags(i)])
        elif item_type == "polygon":
            design_dictionary["polygon"].append([project_manager.canvas.coords(i), _gettags(i)])
        elif item_type == "rectangle":
            design_dictionary["rectangle"].append([project_manager.canvas.coords(i), _gettags(i)])
        elif item_type == "window":
            _save_window_item(design_dictionary, i)


def _gettags(i):
    return [x for x in project_manager.canvas.gettags(i) if x != "current"]


def _save_window_item(design_dictionary: dict[str, Any], canvas_id: int) -> None:
    coords = project_manager.canvas.coords(canvas_id)
    tags = _gettags(canvas_id)
    if canvas_id in state_action.StateAction.ref_dict:
        ref = state_action.StateAction.ref_dict[canvas_id]
        design_dictionary["window_state_action_block"].append(
            [coords, ref.text_id.get("1.0", f"{tk.END}-1 chars"), tags]
        )
    elif canvas_id in state_comment.StateComment.ref_dict:
        ref = state_comment.StateComment.ref_dict[canvas_id]
        design_dictionary["window_state_comment"].append([coords, ref.text_id.get("1.0", f"{tk.END}-1 chars"), tags])
    elif canvas_id in condition_action.ConditionAction.ref_dict:
        ref = condition_action.ConditionAction.ref_dict[canvas_id]
        design_dictionary["window_condition_action_block"].append(
            [
                coords,
                ref.condition_id.get("1.0", f"{tk.END}-1 chars"),
                ref.action_id.get("1.0", f"{tk.END}-1 chars"),
                tags,
            ]
        )
    elif canvas_id in global_actions_clocked.GlobalActionsClocked.ref_dict:
        ref = global_actions_clocked.GlobalActionsClocked.ref_dict[canvas_id]
        design_dictionary["window_global_actions"].append(
            [
                coords,
                ref.text_before_id.get("1.0", f"{tk.END}-1 chars"),
                ref.text_after_id.get("1.0", f"{tk.END}-1 chars"),
                tags,
            ]
        )
    elif canvas_id in global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict:
        ref = global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict[canvas_id]
        design_dictionary["window_global_actions_combinatorial"].append(
            [coords, ref.text_id.get("1.0", f"{tk.END}-1 chars"), tags]
        )
    elif canvas_id in state_actions_default.StateActionsDefault.ref_dict:
        ref = state_actions_default.StateActionsDefault.ref_dict[canvas_id]
        design_dictionary["window_state_actions_default"].append(
            [coords, ref.text_id.get("1.0", f"{tk.END}-1 chars"), tags]
        )
    else:
        print("file_handling: Fatal, unknown dictionary key ", canvas_id)


def open_file_with_name(read_filename, is_script_mode) -> None:
    """Load project from the given file; resolve path and show errors for script vs GUI."""
    replaced_read_filename = _resolve_read_filename(read_filename, is_script_mode)
    project_manager.root.config(cursor="watch")
    try:
        _do_load_file(read_filename, replaced_read_filename, is_script_mode)
    except FileNotFoundError:
        project_manager.root.config(cursor="arrow")
        _show_load_error(
            is_script_mode,
            "Error: File " + read_filename + " could not be found.",
            f"File {read_filename} could not be found.",
        )
    except ValueError:  # includes JSONDecodeError
        project_manager.root.config(cursor="arrow")
        _show_load_error(
            is_script_mode,
            "Error: File " + read_filename + " has wrong format.",
            f"File \n{read_filename}\nhas wrong format.",
        )


def _resolve_read_filename(read_filename: str, is_script_mode: bool) -> str:
    if os.path.isfile(f"{read_filename}.tmp") and not is_script_mode:
        answer = messagebox.askyesno(
            "HDL-FSM-Editor",
            f"Found BackUp-File\n{read_filename}.tmp\n"
            "This file remains after a HDL-FSM-Editor crash and contains all latest changes.\n"
            "Shall this file be read?",
        )
        if answer:
            return f"{read_filename}.tmp"
    return read_filename


def _show_load_error(is_script_mode: bool, print_msg: str, msgbox_msg: str) -> None:
    if is_script_mode:
        print(print_msg)
    else:
        messagebox.showerror("Error", msgbox_msg)


def _do_load_file(read_filename: str, replaced_read_filename: str, is_script_mode: bool) -> None:
    global _write_data_creator_ref
    with open(replaced_read_filename, encoding="utf-8") as fileobject:
        data = fileobject.read()
    project_manager.current_file = read_filename
    design_dictionary = json.loads(data)
    if _write_data_creator_ref is None:
        _write_data_creator_ref = write_data_creator.WriteDataCreator(project_manager.state_radius)
    _write_data_creator_ref.store_as_compare_object(design_dictionary)
    _load_design_from_dict(design_dictionary)
    if os.path.isfile(f"{read_filename}.tmp") and not is_script_mode:
        os.remove(f"{read_filename}.tmp")

    # Final cleanup
    undo_handling.stack = []
    # Loading the design created by "traces" some stack-entries, which are removed here:
    undo_handling.stack_write_pointer = 0
    project_manager.undo_button.config(state="disabled")

    # Put the read design into stack[0]:
    undo_handling.design_has_changed()  # Initialize the stack with the read design.
    project_manager.root.update()
    dir_name, file_name = os.path.split(read_filename)
    project_manager.root.title(f"{file_name} ({dir_name})")
    if not is_script_mode:
        update_ref = update_hdl_tab.UpdateHdlTab(
            design_dictionary["language"],
            design_dictionary["number_of_files"],
            read_filename,
            design_dictionary["generate_path"],
            design_dictionary["modulename"],
        )
        project_manager.date_of_hdl_file_shown_in_hdl_tab = update_ref.get_date_of_hdl_file()
        project_manager.date_of_hdl_file2_shown_in_hdl_tab = update_ref.get_date_of_hdl_file2()
        project_manager.notebook.show_tab(GuiTab.DIAGRAM)
        project_manager.root.after_idle(canvas_editing.view_all)
    project_manager.root.config(cursor="arrow")
    if not tag_plausibility.TagPlausibility().get_tag_status_is_okay():
        if is_script_mode:
            print("Error: File " + read_filename + " has wrong format.")
        else:
            messagebox.showerror("Error", f"File \n{read_filename}\nhas wrong format.")


def _load_design_from_dict(design_dictionary: dict[str, Any]) -> None:
    custom_text.CustomText.read_variables_of_all_windows.clear()
    custom_text.CustomText.written_variables_of_all_windows.clear()
    # Bring the notebook tab with the diagram into the foreground
    project_manager.notebook.show_tab(GuiTab.DIAGRAM)

    _load_control_data(design_dictionary)
    _load_interface_data(design_dictionary)
    _load_internals_data(design_dictionary)
    _load_log_config(design_dictionary)
    _load_canvas_data(design_dictionary)
    _load_canvas_elements(design_dictionary)


def _load_control_data(design_dictionary: dict[str, Any]) -> None:
    """Load control data including module name, language, paths, and signal names."""
    project_manager.module_name.set(design_dictionary["modulename"])
    old_language = project_manager.language.get()
    project_manager.language.set(design_dictionary["language"])
    if design_dictionary["language"] != old_language:
        project_manager.tab_control_ref.switch_language_mode()
    project_manager.generate_path_value.set(design_dictionary["generate_path"])
    project_manager.additional_sources_value.set(design_dictionary.get("additional_sources", ""))
    project_manager.working_directory_value.set(design_dictionary.get("working_directory", ""))
    # For Verilog and SystemVerilog, always use single file mode regardless of what's in the file
    if design_dictionary["language"] in ["Verilog", "SystemVerilog"]:
        project_manager.select_file_number_text.set(1)
    else:
        project_manager.select_file_number_text.set(design_dictionary["number_of_files"])
    project_manager.reset_signal_name.set(design_dictionary["reset_signal_name"])
    project_manager.clock_signal_name.set(design_dictionary["clock_signal_name"])
    project_manager.compile_cmd.set(design_dictionary["compile_cmd"])
    project_manager.edit_cmd.set(design_dictionary["edit_cmd"])
    project_manager.include_timestamp_in_output.set(design_dictionary.get("include_timestamp_in_output", True))


def _load_interface_data(design_dictionary: dict[str, Any]) -> None:
    """Load interface data including package, generics, and ports text."""
    project_manager.interface_package_text.insert("1.0", design_dictionary["interface_package"])
    project_manager.interface_generics_text.insert("1.0", design_dictionary["interface_generics"])
    project_manager.interface_ports_text.insert("1.0", design_dictionary["interface_ports"])

    # Update highlight tags and custom text class lists
    project_manager.interface_package_text.update_highlight_tags(
        10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
    )
    project_manager.interface_generics_text.update_highlight_tags(
        10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
    )
    project_manager.interface_ports_text.update_highlight_tags(
        10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
    )
    project_manager.interface_generics_text.update_custom_text_class_generics_list()
    project_manager.interface_ports_text.update_custom_text_class_ports_list()


def _load_internals_data(design_dictionary: dict[str, Any]) -> None:
    """Load internals data including package, architecture, and process text."""
    project_manager.internals_package_text.insert("1.0", design_dictionary["internals_package"])
    project_manager.internals_architecture_text.insert("1.0", design_dictionary["internals_architecture"])
    project_manager.internals_process_clocked_text.insert("1.0", design_dictionary["internals_process"])
    project_manager.internals_process_combinatorial_text.insert(
        "1.0", design_dictionary["internals_process_combinatorial"]
    )

    # Update highlight tags and custom text class lists
    project_manager.internals_package_text.update_highlight_tags(
        10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
    )
    project_manager.internals_architecture_text.update_highlight_tags(
        10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
    )
    project_manager.internals_process_clocked_text.update_highlight_tags(
        10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
    )
    project_manager.internals_process_combinatorial_text.update_highlight_tags(
        10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
    )
    project_manager.internals_architecture_text.update_custom_text_class_signals_list()
    project_manager.internals_process_clocked_text.update_custom_text_class_signals_list()
    project_manager.internals_process_combinatorial_text.update_custom_text_class_signals_list()


def _load_log_config(design_dictionary: dict[str, Any]) -> None:
    """Load regex configuration for log parsing."""

    if "regex_message_find" in design_dictionary:
        if design_dictionary["language"] == "VHDL":
            project_manager.regex_message_find_for_vhdl = design_dictionary["regex_message_find"]
        else:
            project_manager.regex_message_find_for_verilog = design_dictionary["regex_message_find"]
        project_manager.regex_file_name_quote = design_dictionary["regex_file_name_quote"]
        project_manager.regex_file_line_number_quote = design_dictionary["regex_file_line_number_quote"]


def _load_canvas_data(design_dictionary: dict[str, Any]) -> None:
    """Load canvas-related data including colors, dimensions, and UI state."""
    # Load diagram background color
    project_manager.diagram_background_color.set(design_dictionary.get("diagram_background_color", "white"))
    project_manager.canvas.configure(bg=project_manager.diagram_background_color.get())

    # Load canvas editing parameters
    state.States.state_number = design_dictionary["state_number"]
    transition.TransitionLine.transition_number = design_dictionary["transition_number"]
    connector.ConnectorInstance.connector_number = design_dictionary["connector_number"]
    condition_action.ConditionAction.conditionaction_id = design_dictionary["conditionaction_id"]
    state_action.StateAction.state_action_id = design_dictionary["mytext_id"]

    # Load canvas visual parameters
    project_manager.state_radius = design_dictionary["state_radius"]
    project_manager.reset_entry_size = int(design_dictionary["reset_entry_size"])  # stored as float in dictionary
    project_manager.priority_distance = int(design_dictionary["priority_distance"])  # stored as float in dictionary
    project_manager.fontsize = design_dictionary["fontsize"]
    project_manager.state_name_font.configure(size=int(project_manager.fontsize))
    project_manager.label_fontsize = design_dictionary["label_fontsize"]
    # shift_visible_center_to_window_center(design_dictionary["visible_center"])
    shift_visible_center_to_window_center(get_visible_center_as_string())


def _single_outgoing_transition_id(tags: list[str]) -> str | None:
    """Return transition id (without _start) if exactly one outgoing transition tag, else None."""
    count = 0
    transition_identifier = ""
    for tag in tags:
        if tag.startswith("transition") and tag.endswith("_start"):
            transition_identifier = tag.replace("_start", "")
            count += 1
    return transition_identifier if count == 1 else None


def _load_canvas_states(design_dictionary: dict[str, Any]) -> list[str]:
    """Load state elements; return list of single-outgoing transition ids to hide."""
    hide_list = []
    for definition in design_dictionary["state"]:
        coords = definition[0]
        tags = definition[1]
        fill_color = definition[2] if len(definition) == 3 else constants.STATE_COLOR
        single_id = _single_outgoing_transition_id(tags)
        if single_id:
            hide_list.append(single_id)
        state.States(coords, tags, "dummy", fill_color)
    return hide_list


def _load_canvas_polygons(design_dictionary: dict[str, Any]) -> list[str]:
    """Load polygon (reset) elements; return list of single-outgoing transition ids to hide."""
    hide_list = []
    for definition in design_dictionary["polygon"]:
        coords = definition[0]
        tags = definition[1]
        reset_entry.ResetEntry(coords, tags)
        single_id = _single_outgoing_transition_id(tags)
        if single_id:
            hide_list.append(single_id)
    return hide_list


def _load_canvas_text_elements(design_dictionary: dict[str, Any], transition_dict: dict[str, Any]) -> None:
    """Load text elements (state names, reset text, priority numbers) into canvas and transition_dict."""
    for definition in design_dictionary["text"]:
        tags = definition[1]
        text = definition[2]
        text_is_state_name = False
        text_is_reset_text = False
        for t in tags:
            if t.startswith("state"):  # state<nr>_name
                text_is_state_name = True
                state_tag = t[:-5]
                project_manager.canvas.itemconfigure(state_tag + "_name", text=text, tags=tags)
            elif t.startswith("reset_text"):
                text_is_reset_text = True
        if not text_is_state_name and not text_is_reset_text:  # priority number
            for t in tags:
                if t.startswith("transition"):
                    transition_tag = t[:-8]
                    if transition_tag not in transition_dict:
                        transition_dict[transition_tag] = {}
                    transition_dict[transition_tag]["prio-item"] = {"text": text}


def _load_canvas_lines(
    design_dictionary: dict[str, Any],
    state_comment_line_dictionary: dict[str, Any],
    state_action_line_dictionary: dict[str, Any],
    condition_action_line_dictionary: dict[str, Any],
    transition_dict: dict[str, Any],
) -> None:
    """Load line elements into the given line dicts and transition_dict."""
    for definition in design_dictionary["line"]:
        coords = definition[0]
        tags = definition[1]
        for t in tags:
            if t.startswith("ca_connection"):  # line to condition&action block
                condition_action_line_dictionary[t] = {"coords": coords, "tags": tags}
                break
            if t.startswith("connection"):  # line to state action
                state_action_line_dictionary[t] = {"coords": coords, "tags": tags}
                break
            if t.endswith("_comment_line"):  # line to state comment
                state_comment_line_dictionary[t[:-5]] = {"coords": coords}
            if t.startswith("transition"):
                if tags[0] not in transition_dict:
                    transition_dict[tags[0]] = {}
                transition_dict[tags[0]]["line-item"] = {"coords": coords, "tags": tags}
                break


def _load_canvas_rectangles(design_dictionary: dict[str, Any]) -> list[str]:
    """Load rectangle elements (connector, priority-box); return single-outgoing transition ids to hide."""
    hide_list = []
    for definition in design_dictionary["rectangle"]:
        coords = definition[0]
        tags = definition[1]
        for t in tags:
            if t.startswith("connector"):
                connector.ConnectorInstance(coords, tags)
                single_id = _single_outgoing_transition_id(tags)
                if single_id:
                    hide_list.append(single_id)
                break
    return hide_list


def _load_canvas_elements(design_dictionary: dict[str, Any]) -> None:
    """Load all canvas elements including states, transitions, text, and windows."""
    transition_ids = []
    ids_of_rectangles_to_raise = []
    priority_ids = []
    hide_priority_rectangle_list: list[str] = []
    transition_dict: dict[str, Any] = {}
    state_comment_line_dictionary: dict[str, Any] = {}
    state_action_line_dictionary: dict[str, Any] = {}
    condition_action_line_dictionary: dict[str, Any] = {}

    hide_priority_rectangle_list.extend(_load_canvas_states(design_dictionary))
    hide_priority_rectangle_list.extend(_load_canvas_polygons(design_dictionary))
    _load_canvas_text_elements(design_dictionary, transition_dict)
    _load_canvas_lines(
        design_dictionary,
        state_comment_line_dictionary,
        state_action_line_dictionary,
        condition_action_line_dictionary,
        transition_dict,
    )
    hide_priority_rectangle_list.extend(_load_canvas_rectangles(design_dictionary))

    _load_transitions_from_dict(transition_dict)
    _load_window_elements(
        design_dictionary, state_comment_line_dictionary, state_action_line_dictionary, condition_action_line_dictionary
    )

    # Sort the display order for the transition priorities:
    for transition_id in transition_ids:
        project_manager.canvas.tag_raise(transition_id)
    for rectangle_id in ids_of_rectangles_to_raise:
        project_manager.canvas.tag_raise(rectangle_id)
    for priority_id in priority_ids:
        project_manager.canvas.tag_raise(priority_id)
    for transition_identifer in hide_priority_rectangle_list:
        project_manager.canvas.itemconfigure(f"{transition_identifer}priority", state=tk.HIDDEN)
        project_manager.canvas.itemconfigure(f"{transition_identifer}rectangle", state=tk.HIDDEN)


def _load_transitions_from_dict(transition_dict):
    """Load transitions from the provided transition dictionary."""
    for _, single_transition_dict in transition_dict.items():
        transition_coords = single_transition_dict["line-item"]["coords"]
        tags = single_transition_dict["line-item"]["tags"]
        priority = single_transition_dict["prio-item"]["text"]
        transition.TransitionLine(transition_coords, tags, priority, new_transition=False)
    transition.TransitionLine.hide_priority_of_single_outgoing_transitions()


def _load_window_elements(
    design_dictionary: dict[str, Any],
    state_comment_line_dictionary: dict[str, Any],
    state_action_line_dictionary: dict[str, Any],
    condition_action_line_dictionary: dict[str, Any],
) -> None:
    """Load all window elements including state actions, comments, and global actions."""
    # Load state action blocks
    for definition in design_dictionary["window_state_action_block"]:
        coords = definition[0]
        text = definition[1]
        tags = definition[2]
        for t in tags:
            if t.startswith("connection"):
                line_tag = t[:-6]
                line_coords = state_action_line_dictionary[line_tag]["coords"]
                line_tags = state_action_line_dictionary[line_tag]["tags"]
                action_ref = state_action.StateAction(
                    coords[0],
                    coords[1],
                    height=1,
                    width=8,
                    padding=1,
                    tags=tags,
                    line_coords=line_coords,
                    line_tags=line_tags,
                    increment=False,
                )
                action_ref.text_content = text + "\n"
                action_ref.text_id.insert("1.0", text)
                action_ref.text_id.format()

    # Load state comments
    for definition in design_dictionary.get("window_state_comment", []):
        coords = definition[0]
        text = definition[1]
        tags = definition[2]
        line_coords = state_comment_line_dictionary[tags[0]]["coords"]
        comment_ref = state_comment.StateComment(
            coords[0] - 100, coords[1], height=1, width=8, padding=1, tags=tags, line_coords=line_coords
        )
        project_manager.canvas.itemconfigure(comment_ref.window_id, tag=tags)
        comment_ref.text_content = text + "\n"
        comment_ref.text_id.insert("1.0", text)
        comment_ref.text_id.format()

    _load_condition_action_blocks(design_dictionary, condition_action_line_dictionary)

    # Load global actions
    for definition in design_dictionary["window_global_actions"]:
        coords = definition[0]
        text_before = definition[1]
        text_after = definition[2]
        tags = definition[3]
        global_actions_ref = global_actions_clocked.GlobalActionsClocked(
            coords[0], coords[1], height=1, width=8, padding=1, tags=tags
        )
        global_actions_ref.text_before_id.text_before_content = text_before + "\n"
        global_actions_ref.text_before_id.insert("1.0", text_before)
        global_actions_ref.text_before_id.format()
        global_actions_ref.text_after_id.text_after_content = text_after + "\n"
        global_actions_ref.text_after_id.insert("1.0", text_after)
        global_actions_ref.text_after_id.format()

    # Load global actions combinatorial
    for definition in design_dictionary["window_global_actions_combinatorial"]:
        coords = definition[0]
        text = definition[1]
        tags = definition[2]
        action_ref = global_actions_combinatorial.GlobalActionsCombinatorial(
            coords[0], coords[1], height=1, width=8, padding=1, tags=tags
        )
        action_ref.text_content = text + "\n"
        action_ref.text_id.insert("1.0", text)
        action_ref.text_id.format()

    # Load state actions default
    for definition in design_dictionary["window_state_actions_default"]:
        coords = definition[0]
        text = definition[1]
        tags = definition[2]
        action_ref = state_actions_default.StateActionsDefault(
            coords[0], coords[1], height=1, width=8, padding=1, tags=tags
        )
        action_ref.text_content = text + "\n"
        action_ref.text_id.insert("1.0", text)
        action_ref.text_id.format()

    _update_window_element_button_states()


def _load_condition_action_blocks(
    design_dictionary: dict[str, Any],
    condition_action_line_dictionary: dict[str, Any],
) -> None:
    """Load condition/action window blocks from design dict."""
    for definition in design_dictionary["window_condition_action_block"]:
        coords = definition[0]
        condition = definition[1]
        action = definition[2]
        tags = definition[3]
        connected_to_reset_entry = any(t == "connected_to_reset_transition" for t in tags)
        for t in tags:
            if t.startswith("ca_connection") and t.endswith("_anchor"):
                ca_connection = t[:-7]
                line_coords = condition_action_line_dictionary[ca_connection]["coords"]
                line_tags = condition_action_line_dictionary[ca_connection]["tags"]
                condition_action_ref = condition_action.ConditionAction(
                    coords[0],
                    coords[1],
                    connected_to_reset_entry,
                    height=1,
                    width=8,
                    padding=1,
                    tags=tags,
                    condition=condition,
                    action=action,
                    line_coords=line_coords,
                    line_tags=line_tags,
                    increment=False,
                )
                cond_empty = condition_action_ref.condition_id.get("1.0", tk.END) == "\n"
                action_empty = condition_action_ref.action_id.get("1.0", tk.END) == "\n"
                if cond_empty and not action_empty:
                    condition_action_ref.condition_label.grid_forget()
                    condition_action_ref.condition_id.grid_forget()
                if not cond_empty and action_empty:
                    condition_action_ref.action_label.grid_forget()
                    condition_action_ref.action_id.grid_forget()


def _update_window_element_button_states() -> None:
    """Enable or disable window element buttons depending on whether certain canvas items exist."""
    button_mapping = [
        # (canvas_tag, project_manager_button_attribute)
        ("global_actions1", "global_action_clocked_button"),
        ("global_actions_combinatorial1", "global_action_combinatorial_button"),
        ("state_actions_default", "state_action_default_button"),
        ("reset_entry", "reset_entry_button"),
    ]

    for canvas_tag, button_attr_name in button_mapping:
        element_exists = bool(project_manager.canvas.find_withtag(canvas_tag))
        button = getattr(project_manager, button_attr_name)
        # Enable if element is not found on canvas, disable otherwise
        button_state = tk.DISABLED if element_exists else tk.NORMAL
        button.config(state=button_state)


def get_visible_center_as_string() -> str:
    """Return the canvas visible center coordinates as a space-separated string."""
    visible_rectangle = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    visible_center = [
        (visible_rectangle[0] + visible_rectangle[2]) / 2,
        (visible_rectangle[1] + visible_rectangle[3]) / 2,
    ]
    visible_center_string = ""
    for value in visible_center:
        visible_center_string += str(value) + " "
    return visible_center_string


def shift_visible_center_to_window_center(new_visible_center_string) -> None:
    """Pan canvas so the given center string becomes the current window center."""
    new_visible_center = []
    new_visible_center_string_array = new_visible_center_string.split()
    for entry in new_visible_center_string_array:
        new_visible_center.append(float(entry))
    actual_visible_rectangle = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    actual_visible_center = [
        (actual_visible_rectangle[0] + actual_visible_rectangle[2]) / 2,
        (actual_visible_rectangle[1] + actual_visible_rectangle[3]) / 2,
    ]
    project_manager.canvas.scan_mark(int(new_visible_center[0]), int(new_visible_center[1]))
    project_manager.canvas.scan_dragto(int(actual_visible_center[0]), int(actual_visible_center[1]), gain=1)

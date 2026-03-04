"""
This module contains all methods needed for reading and writing from or to a file.
"""

import json
import os
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

import file_handling_load
import file_handling_save
import tag_plausibility
import undo_handling
import update_hdl_tab
from actions import canvas_editing
from constants import GuiTab
from elements import (
    condition_action,
    connector,
    global_actions_clocked,
    global_actions_combinatorial,
    state,
    state_action,
    state_actions_default,
    transition,
)
from project_manager import project_manager


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
    clear_design()
    project_manager.root.title("unnamed")
    project_manager.grid_drawer.draw_grid()
    project_manager.write_data_creator_ref.store_as_compare_object(None)
    return True


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


def clear_design():
    """Clear the current design from canvas and all variables; reset to initial state."""
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


def save_in_file(save_filename) -> None:  # Called at saving and at every design change (writing to .tmp-file)
    """Serialize project to the given .hfe file (or .tmp)."""
    if not save_filename.endswith(".tmp"):
        zoom_factor = project_manager.write_data_creator_ref.zoom_graphic_to_standard_size(project_manager.state_radius)
    design_dictionary = file_handling_save.save_design_to_dict()
    if not save_filename.endswith(".tmp"):
        project_manager.write_data_creator_ref.zoom_graphic_back_to_actual_size(zoom_factor)
        design_dictionary = project_manager.write_data_creator_ref.round_and_sort_data(design_dictionary)
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
    except Exception as _:  # pylint: disable=broad-except
        project_manager.root.config(cursor=old_cursor)
        messagebox.showerror("Error in HDL-FSM-Editor", f"Writing to file {save_filename} caused exception ")
    if not tag_plausibility.TagPlausibility().get_tag_status_is_okay():
        project_manager.root.config(cursor=old_cursor)
        messagebox.showerror("Error", "The database is corrupt.\nDo not use the written file.\nSee details at STDOUT.")


def open_file() -> None:
    """Prompt for an .hfe file and open it."""
    filename_new = askopenfilename(filetypes=(("HDL-FSM-Editor files", "*.hfe"), ("all files", "*.*")))
    if filename_new != "":
        success = new_design()
        if success:
            open_file_with_name(filename_new, is_script_mode=False)


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


def _do_load_file(read_filename: str, replaced_read_filename: str, is_script_mode: bool) -> None:
    with open(replaced_read_filename, encoding="utf-8") as fileobject:
        data = fileobject.read()
    project_manager.current_file = read_filename
    design_dictionary = json.loads(data)
    project_manager.write_data_creator_ref.store_as_compare_object(design_dictionary)
    file_handling_load.load_design_from_dict(design_dictionary)
    if os.path.isfile(f"{read_filename}.tmp") and not is_script_mode:
        os.remove(f"{read_filename}.tmp")

    # Final cleanup
    undo_handling.stack = []
    # Loading the design created by "traces" some stack-entries, which are removed here:
    undo_handling.stack_write_pointer = 0
    project_manager.undo_button.config(state="disabled")

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
    # Put the read design into stack[0] (after view_all):
    project_manager.root.after_idle(undo_handling.design_has_changed)  # Initialize the stack with the read design.
    project_manager.root.config(cursor="arrow")
    if not tag_plausibility.TagPlausibility().get_tag_status_is_okay():
        if is_script_mode:
            print("Error: File " + read_filename + " has wrong format.")
        else:
            messagebox.showerror("Error", f"File \n{read_filename}\nhas wrong format.")


def _show_load_error(is_script_mode: bool, print_msg: str, msgbox_msg: str) -> None:
    if is_script_mode:
        print(print_msg)
    else:
        messagebox.showerror("Error", msgbox_msg)


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

"""all for saving"""

import tkinter as tk
from typing import Any

from elements import (
    condition_action,
    connector,
    global_actions_clocked,
    global_actions_combinatorial,
    state,
    state_action,
    state_actions_default,
    state_comment,
    transition,
)
from project_manager import project_manager
from widgets import config


def save_design_to_dict() -> dict[str, Any]:
    """Create a design dictionary containing all necessary information to save the current design."""
    design_dictionary = {}
    _save_control_data(design_dictionary)
    _save_interface_data(design_dictionary)
    _save_internals_data(design_dictionary)
    _save_log_config(design_dictionary)
    save_canvas_data(design_dictionary)
    return design_dictionary


def _save_control_data(design_dictionary: dict[str, Any]) -> None:
    design_dictionary["modulename"] = project_manager.module_name.get()
    design_dictionary["language"] = project_manager.language.get()
    design_dictionary["generate_path"] = project_manager.generate_path_value.get()
    design_dictionary["additional_sources"] = project_manager.additional_sources_value.get()
    design_dictionary["working_directory"] = project_manager.working_directory_value.get()
    design_dictionary["diagram_background_color"] = project_manager.diagram_background_color.get()
    design_dictionary["number_of_files"] = project_manager.select_file_number_text.get()
    design_dictionary["reset_signal_name"] = project_manager.reset_signal_name.get()
    design_dictionary["clock_signal_name"] = project_manager.clock_signal_name.get()
    design_dictionary["compile_cmd"] = project_manager.compile_cmd.get()
    design_dictionary["edit_cmd"] = project_manager.edit_cmd.get()
    design_dictionary["include_timestamp_in_output"] = project_manager.include_timestamp_in_output.get()


def _save_interface_data(design_dictionary: dict[str, Any]) -> None:
    design_dictionary["interface_package"] = project_manager.tab_interface_ref.interface_packages_text.get(
        "1.0", f"{tk.END}-1 chars"
    )
    design_dictionary["interface_generics"] = project_manager.tab_interface_ref.interface_generics_text.get(
        "1.0", f"{tk.END}-1 chars"
    )
    design_dictionary["interface_ports"] = project_manager.tab_interface_ref.interface_ports_text.get(
        "1.0", f"{tk.END}-1 chars"
    )


def _save_internals_data(design_dictionary: dict[str, Any]) -> None:
    design_dictionary["internals_package"] = project_manager.tab_internals_ref.internals_packages_text.get(
        "1.0", f"{tk.END}-1 chars"
    )
    design_dictionary["internals_architecture"] = project_manager.tab_internals_ref.internals_architecture_text.get(
        "1.0", f"{tk.END}-1 chars"
    )
    design_dictionary["internals_process"] = project_manager.tab_internals_ref.internals_process_clocked_text.get(
        "1.0", f"{tk.END}-1 chars"
    )
    design_dictionary["internals_process_combinatorial"] = (
        project_manager.tab_internals_ref.internals_process_combinatorial_text.get("1.0", f"{tk.END}-1 chars")
    )


def _save_log_config(design_dictionary: dict[str, Any]) -> None:
    if project_manager.language.get() == "VHDL":
        design_dictionary["regex_message_find"] = project_manager.regex_message_find_for_vhdl
    else:
        design_dictionary["regex_message_find"] = project_manager.regex_message_find_for_verilog
    design_dictionary["regex_file_name_quote"] = project_manager.regex_file_name_quote
    design_dictionary["regex_file_line_number_quote"] = project_manager.regex_file_line_number_quote


def save_canvas_data(design_dictionary: dict[str, Any]) -> None:
    """Save the canvas data to the given design dictionary."""
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
    for element_name in config.ELEMENT_NAMES_IN_DESIGN_DICTIONARY:
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


def _gettags(i):
    return [x for x in project_manager.canvas.gettags(i) if x != "current"]

"""all to load"""

import tkinter as tk
from typing import Any

import constants
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
from widgets import custom_text


def load_design_from_dict(design_dictionary: dict[str, Any]) -> None:
    """Load the design from the given design dictionary."""
    custom_text.CustomText.read_variables_of_all_windows.clear()
    custom_text.CustomText.written_variables_of_all_windows.clear()
    # Bring the notebook tab with the diagram into the foreground
    project_manager.notebook.show_tab(GuiTab.DIAGRAM)

    _load_control_data(design_dictionary)
    _load_interface_data(design_dictionary)
    _load_internals_data(design_dictionary)
    _load_canvas_data(design_dictionary)
    _load_canvas_elements(design_dictionary)
    _load_canvas_ids(design_dictionary)  # must be done after changing the IDs by _load_canvas_elements().
    _load_log_config(design_dictionary)
    custom_text.CustomText.update_highlight_tags_in_all_texts()


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
    project_manager.tab_interface_ref.interface_package_text.insert("1.0", design_dictionary["interface_package"])
    project_manager.tab_interface_ref.interface_generics_text.insert("1.0", design_dictionary["interface_generics"])
    project_manager.tab_interface_ref.interface_ports_text.insert("1.0", design_dictionary["interface_ports"])
    project_manager.tab_interface_ref.interface_generics_text.update_custom_text_class_generics_list()
    project_manager.tab_interface_ref.interface_ports_text.update_custom_text_class_ports_list()


def _load_internals_data(design_dictionary: dict[str, Any]) -> None:
    """Load internals data including package, architecture, and process text."""
    project_manager.tab_internals_ref.internals_package_text.insert("1.0", design_dictionary["internals_package"])
    project_manager.tab_internals_ref.internals_architecture_text.insert(
        "1.0", design_dictionary["internals_architecture"]
    )
    project_manager.tab_internals_ref.internals_process_clocked_text.insert(
        "1.0", design_dictionary["internals_process"]
    )
    project_manager.tab_internals_ref.internals_process_combinatorial_text.insert(
        "1.0", design_dictionary["internals_process_combinatorial"]
    )
    project_manager.tab_internals_ref.internals_architecture_text.update_custom_text_class_signals_list()
    project_manager.tab_internals_ref.internals_architecture_text.update_custom_text_functions_list()
    project_manager.tab_internals_ref.internals_process_clocked_text.update_custom_text_class_signals_list()
    project_manager.tab_internals_ref.internals_process_combinatorial_text.update_custom_text_class_signals_list()


def _load_canvas_data(design_dictionary: dict[str, Any]) -> None:
    """Load canvas-related data including colors, dimensions, and UI state."""
    # Load diagram background color
    project_manager.diagram_background_color.set(design_dictionary.get("diagram_background_color", "white"))
    project_manager.canvas.configure(bg=project_manager.diagram_background_color.get())

    # Load canvas visual parameters
    project_manager.state_radius = design_dictionary["state_radius"]
    project_manager.reset_entry_size = int(design_dictionary["reset_entry_size"])  # stored as float in dictionary
    project_manager.priority_distance = int(design_dictionary["priority_distance"])  # stored as float in dictionary
    project_manager.fontsize = design_dictionary["fontsize"]
    project_manager.state_name_font.configure(size=int(project_manager.fontsize))
    project_manager.label_fontsize = design_dictionary["label_fontsize"]


def _load_canvas_ids(design_dictionary: dict[str, Any]) -> None:
    """Load IDs for all elements."""
    state.States.state_number = design_dictionary["state_number"]
    transition.TransitionLine.transition_number = design_dictionary["transition_number"]
    connector.ConnectorInstance.connector_number = design_dictionary["connector_number"]
    condition_action.ConditionAction.conditionaction_id = design_dictionary["conditionaction_id"]
    state_action.StateAction.state_action_id = design_dictionary["mytext_id"]


def _load_canvas_elements(design_dict: dict[str, Any]) -> None:
    """Load all canvas elements including states, transitions, text, and windows."""
    hide_priority_rectangle_list: list[str] = []
    transition_dict: dict[str, Any] = {}
    state_comment_line_dict: dict[str, Any] = {}
    state_act_line_dict: dict[str, Any] = {}
    cond_act_line_dict: dict[str, Any] = {}
    hide_priority_rectangle_list.extend(_load_canvas_states(design_dict))
    hide_priority_rectangle_list.extend(_load_canvas_polygons(design_dict))
    _load_canvas_text_elements(design_dict, transition_dict)
    _distribute_lines(design_dict, state_comment_line_dict, state_act_line_dict, cond_act_line_dict, transition_dict)
    hide_priority_rectangle_list.extend(_load_canvas_rectangles(design_dict))
    _load_transitions_from_dict(transition_dict)
    _load_state_action_blocks(design_dict, state_act_line_dict)
    _load_state_comment_blocks(design_dict, state_comment_line_dict)
    _load_condition_action_blocks(design_dict, cond_act_line_dict)
    _load_global_actions_clocked(design_dict)
    _load_global_actions_combinatorial(design_dict)
    _load_state_actions_default(design_dict)
    _update_window_element_button_states()
    # Eliminate inaccuracies:
    for transition_tag in transition_dict:
        transition.TransitionLine.extend_transition_to_state_middle_points(transition_tag)
        transition.TransitionLine.shorten_to_state_border(transition_tag)
    for transition_identifer in hide_priority_rectangle_list:
        project_manager.canvas.itemconfigure(f"{transition_identifer}priority", state=tk.HIDDEN)
        project_manager.canvas.itemconfigure(f"{transition_identifer}rectangle", state=tk.HIDDEN)


def _load_log_config(design_dictionary: dict[str, Any]) -> None:
    """Load regex configuration for log parsing."""

    if "regex_message_find" in design_dictionary:
        if design_dictionary["language"] == "VHDL":
            project_manager.regex_message_find_for_vhdl = design_dictionary["regex_message_find"]
        else:
            project_manager.regex_message_find_for_verilog = design_dictionary["regex_message_find"]
        project_manager.regex_file_name_quote = design_dictionary["regex_file_name_quote"]
        project_manager.regex_file_line_number_quote = design_dictionary["regex_file_line_number_quote"]


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


def _distribute_lines(
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


def _load_transitions_from_dict(transition_dict: dict[str, Any]) -> None:
    """Load transitions from the provided transition dictionary."""
    for _, single_transition_dict in transition_dict.items():
        transition_coords = single_transition_dict["line-item"]["coords"]
        tags = single_transition_dict["line-item"]["tags"]
        priority = single_transition_dict["prio-item"]["text"]
        transition.TransitionLine(transition_coords, tags, priority)
    transition.TransitionLine.hide_priority_of_single_outgoing_transitions()


def _load_state_action_blocks(design_dictionary: dict[str, Any], state_action_line_dictionary: dict[str, Any]) -> None:
    for definition in design_dictionary["window_state_action_block"]:
        coords = definition[0]
        text = definition[1]
        tags = definition[2]
        for t in tags:
            if t.startswith("connection"):
                line_tag = t[:-6]
                line_coords = state_action_line_dictionary[line_tag]["coords"]
                line_tags = state_action_line_dictionary[line_tag]["tags"]
                state_action.StateAction(
                    coords[0],
                    coords[1],
                    padding=1,
                    tags=tags,
                    line_coords=line_coords,
                    line_tags=line_tags,
                    action=text,
                )


def _load_state_comment_blocks(
    design_dictionary: dict[str, Any], state_comment_line_dictionary: dict[str, Any]
) -> None:
    for definition in design_dictionary.get("window_state_comment", []):
        coords = definition[0]
        text = definition[1]
        tags = definition[2]
        line_coords = state_comment_line_dictionary[tags[0]]["coords"]
        state_comment.StateComment(
            coords[0] - 100, coords[1], padding=1, tags=tags, line_coords=line_coords, comment=text
        )


def _load_global_actions_clocked(design_dictionary: dict[str, Any]) -> None:
    for definition in design_dictionary["window_global_actions"]:
        coords = definition[0]
        text_before = definition[1]
        text_after = definition[2]
        tags = definition[3]
        global_actions_clocked.GlobalActionsClocked(
            coords[0], coords[1], padding=1, tags=tags, before=text_before, after=text_after
        )


def _load_global_actions_combinatorial(design_dictionary: dict[str, Any]) -> None:
    for definition in design_dictionary["window_global_actions_combinatorial"]:
        coords = definition[0]
        text = definition[1]
        tags = definition[2]
        global_actions_combinatorial.GlobalActionsCombinatorial(
            coords[0], coords[1], padding=1, tags=tags, actions=text
        )


def _load_state_actions_default(design_dictionary: dict[str, Any]) -> None:
    for definition in design_dictionary["window_state_actions_default"]:
        coords = definition[0]
        text = definition[1]
        tags = definition[2]
        state_actions_default.StateActionsDefault(coords[0], coords[1], padding=1, tags=tags, action=text)


def _load_condition_action_blocks(
    design_dictionary: dict[str, Any], condition_action_line_dictionary: dict[str, Any]
) -> None:
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
                condition_action.ConditionAction(
                    coords[0],
                    coords[1],
                    connected_to_reset_entry,
                    padding=1,
                    tags=tags,
                    condition=condition,
                    action=action,
                    line_coords=line_coords,
                    line_tags=line_tags,
                )
                break


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


def _single_outgoing_transition_id(tags: list[str]) -> str | None:
    """Return transition id (without _start) if exactly one outgoing transition tag, else None."""
    count = 0
    transition_identifier = ""
    for tag in tags:
        if tag.startswith("transition") and tag.endswith("_start"):
            transition_identifier = tag.replace("_start", "")
            count += 1
    return transition_identifier if count == 1 else None

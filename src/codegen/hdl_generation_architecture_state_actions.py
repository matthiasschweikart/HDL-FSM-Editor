"""
All methods needed for the state action process in VHDL or Verilog
"""

import re
import tkinter as tk

from codegen import hdl_generation_library, sensitivity_check
from project_manager import project_manager

from .exceptions import GenerationError


def create_state_action_process(file_name, file_line_number, state_tag_list_sorted) -> tuple:
    """Returns the state action process as string and the updated file_line_number."""
    default_state_actions = _get_default_state_actions()
    state_action_list = _create_state_action_list(
        state_tag_list_sorted
    )  # Each entry is : ["state_name", "state_actions", "state_action_reference"]
    if default_state_actions == "" and _state_actions_contain_only_null_for_each_state(state_action_list):
        return "", file_line_number
    # Get from Interface/Ports and from Internals/Architecture Declarations:
    all_possible_sensitivity_entries = create_a_list_with_all_possible_sensitivity_entries()
    variable_declarations = hdl_generation_library.get_text_from_text_widget(
        project_manager.tab_internals_ref.internals_process_combinatorial_text
    )
    if project_manager.language.get() == "VHDL":
        state_action_process, file_line_number = _create_state_action_process_for_vhdl(
            file_name,
            file_line_number,
            state_action_list,
            default_state_actions,
            all_possible_sensitivity_entries,
            variable_declarations,
        )
    else:
        state_action_process, file_line_number = _create_state_action_process_for_verilog(
            file_name,
            file_line_number,
            state_action_list,
            default_state_actions,
            all_possible_sensitivity_entries,
            variable_declarations,
        )
    return state_action_process, file_line_number


def _state_actions_contain_only_null_for_each_state(state_action_list) -> bool:
    return all(entry[1] == "null;\n" for entry in state_action_list)


def _create_state_action_process_for_vhdl(
    file_name,
    file_line_number,
    state_action_list,
    default_state_actions,
    all_possible_sensitivity_entries,
    variable_declarations,
) -> tuple:
    state_action_process = "p_state_actions: process "
    sensitivity_list = (
        _create_sensitivity_list(
            len(state_action_process), state_action_list, default_state_actions, all_possible_sensitivity_entries
        )
        + "\n"
    )
    state_action_process += sensitivity_list
    project_manager.link_dict_ref.add(
        file_name,
        file_line_number,
        "",
        sensitivity_list.count("\n"),
        None,
    )
    file_line_number += sensitivity_list.count("\n")

    state_action_process += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, variable_declarations)
    number_of_lines = variable_declarations.count("\n")
    if number_of_lines != 0:
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_internals_tab",
            number_of_lines,
            project_manager.tab_internals_ref.internals_process_combinatorial_text,
        )
        file_line_number += number_of_lines
    state_action_process += "begin\n"
    file_line_number += 1

    state_action_process += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, default_state_actions)
    number_of_lines = default_state_actions.count("\n")
    if number_of_lines != 0:
        item_ids = project_manager.canvas.find_withtag("state_actions_default")
        reference_to_default_state_actions_custom_text = project_manager.canvas_windows_ref_dict[item_ids[0]]
        file_line_number += 1  # default_state_actions starts always with "-- Default State Actions:"
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_diagram_tab",
            number_of_lines - 1,
            reference_to_default_state_actions_custom_text.text_ids[0],
        )
        file_line_number += number_of_lines - 1

    state_action_process += "    -- State Actions:\n"
    state_action_process += "    case state is\n"
    file_line_number += 2

    for state_action_entry in state_action_list:
        when_entry = _create_when_entry(state_action_entry)
        state_action_process += hdl_generation_library.indent_text_by_the_given_number_of_tabs(2, when_entry)
        file_line_number += 1  # A when_entry starts always with "when ..."
        number_of_lines = when_entry.count("\n")
        project_manager.link_dict_ref.add(
            file_name, file_line_number, "custom_text_in_diagram_tab", number_of_lines - 1, state_action_entry[2]
        )
        file_line_number += number_of_lines - 1

    state_action_process += "    end case;\n"
    state_action_process += "end process;\n"
    file_line_number += 2
    return state_action_process, file_line_number


def _create_state_action_process_for_verilog(
    file_name,
    file_line_number,
    state_action_list,
    default_state_actions,
    all_possible_sensitivity_entries,
    variable_declarations,
) -> tuple:
    state_action_process = "always @"
    sensitivity_list = (
        _create_sensitivity_list(
            len(state_action_process), state_action_list, default_state_actions, all_possible_sensitivity_entries
        )
        + " begin: p_state_actions\n"
    )
    state_action_process += sensitivity_list
    project_manager.link_dict_ref.add(
        file_name,
        file_line_number,
        "",
        sensitivity_list.count("\n"),
        None,
    )
    file_line_number += sensitivity_list.count("\n")

    if variable_declarations != "":
        state_action_process += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, variable_declarations)
        number_of_new_lines = variable_declarations.count("\n")
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_internals_tab",
            number_of_new_lines,
            project_manager.tab_internals_ref.internals_process_combinatorial_text,
        )
        file_line_number += number_of_new_lines

    state_action_process += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, default_state_actions)
    number_of_lines = default_state_actions.count("\n")
    if number_of_lines != 0:
        item_ids = project_manager.canvas.find_withtag("state_actions_default")
        reference_to_default_state_actions_custom_text = project_manager.canvas_windows_ref_dict[item_ids[0]]
        file_line_number += 1  # default_state_actions starts always with "-- Default State Actions:"
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_diagram_tab",
            number_of_lines - 1,
            reference_to_default_state_actions_custom_text.text_id,
        )
        file_line_number += number_of_lines - 1

    state_action_process += "    // State Actions:\n"
    state_action_process += "    case (state)\n"
    file_line_number += 2

    for state_action_entry in state_action_list:
        when_entry = _create_when_entry(state_action_entry)
        number_of_lines = when_entry.count("\n")
        state_action_process += hdl_generation_library.indent_text_by_the_given_number_of_tabs(2, when_entry)
        if number_of_lines == 2 and when_entry.endswith("    ;\n"):  # Empty state action
            file_line_number += 2
        else:
            file_line_number += 1  # A when_entry starts always with "<State-Name: ..."
            project_manager.link_dict_ref.add(
                file_name,
                file_line_number,
                "custom_text_in_diagram_tab",
                number_of_lines - 2,  # a when entry always ends with "end"
                state_action_entry[2],
            )
            file_line_number += number_of_lines - 1

    state_action_process += "        default:\n"
    state_action_process += "            ;\n"
    state_action_process += "    endcase\n"
    state_action_process += "end\n"
    file_line_number += 4
    return state_action_process, file_line_number


def create_a_list_with_all_possible_sensitivity_entries() -> list:
    """Returns a list with all possible sensitivity list entries."""
    all_port_declarations = project_manager.tab_interface_ref.interface_ports_text.get("1.0", tk.END).lower()
    readable_ports_list = get_all_readable_ports(all_port_declarations, check=True)
    all_signal_declarations = project_manager.tab_internals_ref.internals_architecture_text.get("1.0", tk.END).lower()
    signals_list = _get_all_signals(all_signal_declarations)
    signals_list.extend(readable_ports_list)
    return signals_list


def _create_state_action_list(state_tag_list_sorted):
    state_action_list = []
    for state_tag in state_tag_list_sorted:
        state_action_text = "null;\n"
        state_action_reference = None
        for tag_of_state in project_manager.canvas.gettags(state_tag):
            if tag_of_state.startswith("connection") and tag_of_state.endswith(
                "_end"
            ):  # This is a tag which exists only at states.
                connection_name = tag_of_state[:-4]
                state_action_ids = project_manager.canvas.find_withtag(connection_name + "_start")
                if state_action_ids:
                    ref = project_manager.canvas_windows_ref_dict[state_action_ids[0]]
                    state_action_text = ref.text_ids[0].get("1.0", tk.END)
                    state_action_reference = ref.text_ids[0]
                    break
        state_name = project_manager.canvas.itemcget(state_tag + "_name", "text")
        state_action_list.append([state_name, state_action_text, state_action_reference])
    return state_action_list


def _create_sensitivity_list(start, state_action_list, default_state_actions, all_possible_sensitivity_entries) -> str:
    default_state_actions_separated = hdl_generation_library.convert_hdl_lines_into_a_searchable_string(
        default_state_actions
    )
    default_state_actions_separated = _remove_left_hand_sides(default_state_actions_separated)
    default_state_actions_separated = _remove_record_element_names(default_state_actions_separated)
    added_entries = []
    sensitivity_list = "("
    number_of_characters_added_since_last_new_line = start
    for entry in all_possible_sensitivity_entries:
        if " " + entry + " " in default_state_actions_separated:
            added_entries.append(entry)
            sensitivity_list += entry + ", "
            number_of_characters_added_since_last_new_line += len(entry) + 2
            if number_of_characters_added_since_last_new_line > 80:
                sensitivity_list += "\n"
                number_of_characters_added_since_last_new_line = 0
    for list_entry in state_action_list:
        state_action_separated = hdl_generation_library.convert_hdl_lines_into_a_searchable_string(list_entry[1])
        state_action_separated = _remove_left_hand_sides(state_action_separated)
        state_action_separated = _remove_record_element_names(state_action_separated)
        for entry in all_possible_sensitivity_entries:
            if " " + entry + " " in state_action_separated and entry not in added_entries:
                added_entries.append(entry)
                sensitivity_list += entry + ", "
                number_of_characters_added_since_last_new_line += len(entry) + 2
                if number_of_characters_added_since_last_new_line > 80:
                    sensitivity_list += "\n"
                    number_of_characters_added_since_last_new_line = 0
    sensitivity_list += "state)"
    return sensitivity_list


def _remove_left_hand_sides(state_action_text) -> str:
    if project_manager.language.get() == "VHDL":
        new_list = sensitivity_check.SensitivityCheck.replace_targets_in_vhdl_body(state_action_text.split())
    else:
        new_list = sensitivity_check.SensitivityCheck.replace_targets_in_verilog_body(state_action_text.split())
    return " ".join(new_list)


def _remove_record_element_names(state_action_text) -> str:
    state_action_text = re.sub(r"\..*?\s", " ", state_action_text)
    return state_action_text


def _get_default_state_actions() -> str:
    item_ids = project_manager.canvas.find_withtag("state_actions_default")
    if item_ids == ():
        return ""
    ref = project_manager.canvas_windows_ref_dict[item_ids[0]]
    comment = "--" if project_manager.language.get() == "VHDL" else "//"
    return comment + " Default State Actions:\n" + ref.text_ids[0].get("1.0", tk.END)


def _create_when_entry(state_action_entry) -> str:
    if project_manager.language.get() == "VHDL":
        when_entry = "when " + state_action_entry[0] + "=>\n"
        when_entry += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, state_action_entry[1])
    else:
        if state_action_entry[1].startswith("null;"):
            when_entry = state_action_entry[0] + ":\n"
            when_entry += "    ;\n"
        else:
            when_entry = state_action_entry[0] + ": begin\n"
            when_entry += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, state_action_entry[1])
            when_entry += "end\n"
    return when_entry


def get_all_readable_ports(all_port_declarations, check) -> list:
    """Returns a list with the names of all readable ports.
    If check is True, an error is raised if an illegal port declaration is found.
    """
    port_declaration_list = _create_list_of_declarations(all_port_declarations)
    readable_port_list = []
    for declaration in port_declaration_list:
        if declaration != "" and not declaration.isspace():
            inputs = _get_all_readable_port_names(
                declaration, check
            )  # One declaration can contain a comma separated list of names!
            if inputs != "":
                readable_port_list.extend(inputs.split(","))
    return readable_port_list


def get_all_writable_ports(all_port_declarations) -> list:
    """Returns a list with the names of all writable ports."""
    port_declaration_list = _create_list_of_declarations(all_port_declarations)
    writeable_port_list = []
    for declaration in port_declaration_list:
        if declaration != "" and not declaration.isspace():
            outputs = _get_all_writable_port_names(declaration)
            if outputs != "":
                writeable_port_list.extend(outputs.split(","))
    return writeable_port_list


def _create_list_of_declarations(all_declarations):
    all_declarations_without_comments = hdl_generation_library.remove_comments_and_returns(all_declarations)
    all_declarations_separated = hdl_generation_library.surround_character_by_blanks(
        ":", all_declarations_without_comments
    )  # only needed for VHDL
    split_char = ";" if project_manager.language.get() == "VHDL" else ","
    return all_declarations_separated.split(split_char)


def get_all_port_types(all_port_declarations) -> list:
    """Returns a list with the type-names of all ports."""
    port_declaration_list = _create_list_of_declarations(all_port_declarations)
    port_types_list = []
    for declaration in port_declaration_list:
        if (
            declaration != ""
            and not declaration.isspace()
            and (" in " in declaration or " out " in declaration or " inout " in declaration)
        ):
            port_type = re.sub(".* in |.* out |.* inout ", "", declaration, flags=re.I | re.DOTALL)
            port_type = re.sub("\\(.*", "", port_type, flags=re.I | re.DOTALL)
            port_type = re.sub(";", "", port_type)
            if port_type != "" and not port_type.isspace():
                port_type = re.sub("\\s", "", port_type)
                port_types_list.append(port_type)
    return port_types_list


def get_all_generic_names(all_generic_declarations) -> list:
    """Returns a list with the names of all generics."""
    generic_declaration_list = _create_list_of_declarations(all_generic_declarations)
    generic_name_list = []
    for declaration in generic_declaration_list:
        if declaration != "" and not declaration.isspace():
            if project_manager.language.get() == "VHDL":
                generic_name = re.sub(" : .*", "", declaration, flags=re.I | re.DOTALL)
                generic_name = re.sub(r"(^|\s+)constant ", "", generic_name, flags=re.I | re.DOTALL)
                generic_name = re.sub("\\s", "", generic_name)
            else:  # Verilog
                generic_name = re.sub("=.*", "", declaration, flags=re.I | re.DOTALL)
                generic_name = re.sub("\\s", "", generic_name)
            generic_name_list.append(generic_name)
    return generic_name_list


def _get_all_readable_port_names(declaration, check) -> str:
    port_names = ""
    if " in " in declaration and project_manager.language.get() == "VHDL":
        if ":" not in declaration:
            if check is True:
                raise GenerationError(
                    "Error",
                    [
                        f'There is an illegal port declaration, which will be ignored: "{declaration}"',
                        "VHDL may be corrupted.",
                    ],
                )
        else:
            port_names = re.sub(":.*", "", declaration)
    elif " input " in declaration and project_manager.language.get() != "VHDL":
        declaration = re.sub(" input ", " ", declaration, flags=re.I)
        declaration = re.sub(" reg ", " ", declaration, flags=re.I)
        declaration = re.sub(" logic ", " ", declaration, flags=re.I)
        port_names = re.sub(" \\[.*?\\] ", " ", declaration)
    else:
        return ""
    port_names_without_blanks = re.sub(" ", "", port_names)
    return port_names_without_blanks


def _get_all_writable_port_names(declaration) -> str:
    port_names = ""
    if " out " in declaration and project_manager.language.get() == "VHDL":
        if ":" in declaration:
            port_names = re.sub(":.*", "", declaration)
    elif " output " in declaration and project_manager.language.get() != "VHDL":
        declaration = re.sub(" output ", " ", declaration, flags=re.I)
        declaration = re.sub(" reg ", " ", declaration, flags=re.I)
        declaration = re.sub(" logic ", " ", declaration, flags=re.I)
        declaration = re.sub(" unsigned ", " ", declaration, flags=re.I)
        declaration = re.sub(" signed ", " ", declaration, flags=re.I)
        port_names = re.sub(" \\[.*?\\] ", " ", declaration)
    else:
        return ""
    port_names_without_blanks = re.sub(" ", "", port_names)
    return port_names_without_blanks


def _get_all_signals(all_signal_declarations) -> list:
    all_signal_declarations_without_comments = hdl_generation_library.remove_comments_and_returns(
        all_signal_declarations
    )
    all_signal_declarations_without_comments = hdl_generation_library.remove_functions(
        all_signal_declarations_without_comments
    )
    all_signal_declarations_without_comments = hdl_generation_library.remove_type_declarations(
        all_signal_declarations_without_comments
    )
    all_signal_declarations_separated = hdl_generation_library.surround_character_by_blanks(
        ":", all_signal_declarations_without_comments
    )
    signal_declaration_list = all_signal_declarations_separated.split(";")
    signal_declaration_list_extended = _add_blank_at_the_beginning_of_each_line(
        signal_declaration_list
    )  # needed for search of " signal "
    signals_list = []
    if project_manager.language.get() == "VHDL":
        for declaration in signal_declaration_list_extended:
            if declaration != "" and not declaration.isspace():
                if " signal " not in declaration and " constant " not in declaration:
                    raise GenerationError(
                        "Error",
                        [
                            f'There is an illegal signal declaration, which will be ignored: "{declaration}"',
                            "VHDL may be corrupted.",
                        ],
                    )
                signals = _get_the_signal_names(declaration)
                if signals != "":
                    signals_list.extend(signals.split(","))
    else:
        for declaration in signal_declaration_list_extended:
            if declaration != "" and not declaration.isspace():
                if (
                    " integer " not in declaration
                    and " reg " not in declaration
                    and " wire " not in declaration
                    and " logic " not in declaration
                ):
                    raise GenerationError(
                        "Error",
                        [
                            f'There is an illegal signal declaration, which will be ignored: "{declaration}"',
                            "Verilog may be corrupted.",
                        ],
                    )
                declaration = re.sub(" reg ", " ", declaration, flags=re.I)
                declaration = re.sub(" wire ", " ", declaration, flags=re.I)
                declaration = re.sub(" logic ", " ", declaration, flags=re.I)
                declaration = re.sub(" \\[.*?\\]", " ", declaration, flags=re.I)
                if declaration != "":
                    signals_list.extend(declaration.split(","))
    return signals_list


def _add_blank_at_the_beginning_of_each_line(signal_declaration_list) -> list:
    signal_declaration_list_extended = []
    for d in signal_declaration_list:
        signal_declaration_list_extended.append(re.sub("^", " ", d))
    return signal_declaration_list_extended


def _get_the_signal_names(declaration):
    if " constant " in declaration:
        return ""
    signal_names = re.sub(":.*", "", declaration)
    signal_names_alone = re.sub(" signal ", "", signal_names, flags=re.I)
    signal_names_without_blanks = re.sub(" ", "", signal_names_alone)
    return signal_names_without_blanks

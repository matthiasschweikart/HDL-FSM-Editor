"""
This module provides a method for creating the architecture part of a VHDL file.
"""

from codegen import (
    hdl_generation_architecture_state_actions,
    hdl_generation_architecture_state_sequence,
    hdl_generation_library,
)
from project_manager import project_manager


def create_architecture(file_name, file_line_number, state_tag_list_sorted) -> None:
    """Build VHDL architecture body and write it; update file_line_number and link dict for navigation."""
    architecture = ""

    package_statements = hdl_generation_library.get_text_from_text_widget(project_manager.internals_package_text)
    architecture += package_statements
    number_of_new_lines = package_statements.count("\n")
    project_manager.link_dict_ref.add(
        file_name,
        file_line_number,
        "custom_text_in_internals_tab",
        number_of_new_lines,
        project_manager.internals_package_text,
    )
    file_line_number += number_of_new_lines

    architecture += "\n"
    architecture += "architecture fsm of " + project_manager.module_name.get() + " is\n"
    architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(
        1, _create_type_definition_for_the_state_signal(state_tag_list_sorted)
    )
    architecture += "    signal state : t_state;\n"
    file_line_number += 4

    signal_declarations = hdl_generation_library.get_text_from_text_widget(project_manager.internals_architecture_text)
    architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, signal_declarations)
    number_of_new_lines = signal_declarations.count("\n")
    project_manager.link_dict_ref.add(
        file_name,
        file_line_number,
        "custom_text_in_internals_tab",
        number_of_new_lines,
        project_manager.internals_architecture_text,
    )
    file_line_number += number_of_new_lines

    architecture += "begin\n"
    file_line_number += 1
    architecture += (
        "    p_states: process ("
        + project_manager.reset_signal_name.get()
        + ", "
        + project_manager.clock_signal_name.get()
        + ")\n"
    )
    project_manager.link_dict_ref.add(file_name, file_line_number, "Control-Tab", 1, "reset_and_clock_signal_name")
    file_line_number += 1

    variable_declarations = hdl_generation_library.get_text_from_text_widget(
        project_manager.internals_process_clocked_text
    )
    architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(2, variable_declarations)
    number_of_new_lines = variable_declarations.count("\n")
    project_manager.link_dict_ref.add(
        file_name,
        file_line_number,
        "custom_text_in_internals_tab",
        number_of_new_lines,
        project_manager.internals_process_clocked_text,
    )
    file_line_number += number_of_new_lines

    architecture += "    begin\n"
    file_line_number += 1

    [reset_condition, reset_action, reference_to_reset_condition_custom_text, reference_to_reset_action_custom_text] = (
        hdl_generation_library.create_reset_condition_and_reset_action()
    )
    if reset_condition is None:
        return  # No further actions make sense, as always a reset condition must exist.
    if reset_condition.count("\n") == 0:
        architecture += "        if " + reset_condition + " then\n"
    else:
        reset_condition_list = reset_condition.split("\n")
        for index, line in enumerate(reset_condition_list):
            if index == 0:
                architecture += "        if " + line + "\n"
            else:
                architecture += "           " + line + "\n"
        architecture += "        then\n"
    number_of_new_lines = reset_condition.count("\n") + 1  # No return after the last line of the condition
    project_manager.link_dict_ref.add(
        file_name,
        file_line_number,
        "custom_text_in_diagram_tab",
        number_of_new_lines,
        reference_to_reset_condition_custom_text,
    )
    file_line_number += number_of_new_lines

    architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(3, reset_action)
    # reset_action starts always with "state <=", which is not a line entered by the user,
    # and therefore cannot be linked:
    file_line_number += 1
    number_of_new_lines = reset_action.count("\n") - 1
    project_manager.link_dict_ref.add(
        file_name,
        file_line_number,
        "custom_text_in_diagram_tab",
        number_of_new_lines,
        reference_to_reset_action_custom_text,
    )
    file_line_number += number_of_new_lines

    architecture += "        elsif rising_edge(" + project_manager.clock_signal_name.get() + ") then\n"
    project_manager.link_dict_ref.add(file_name, file_line_number, "Control-Tab", 1, "reset_and_clock_signal_name")
    file_line_number += 1

    reference_to_global_actions_before_custom_text, global_actions_before = (
        hdl_generation_library.create_global_actions_before()
    )
    if global_actions_before != "":
        global_actions_before = "-- Global Actions before:\n" + global_actions_before
        architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(3, global_actions_before)
        # global_actions_before starts always with "-- Global Actions before:", which is not a line entered by the user,
        # and therefore cannot be linked:
        file_line_number += 1
        number_of_new_lines = global_actions_before.count("\n") - 1
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_diagram_tab",
            number_of_new_lines,
            reference_to_global_actions_before_custom_text,
        )
        file_line_number += number_of_new_lines

    architecture += "            -- State Machine:\n"
    architecture += "            case state is\n"
    file_line_number += 2
    transition_specifications = hdl_generation_library.extract_transition_specifications_from_the_graph(
        state_tag_list_sorted
    )
    state_sequence, file_line_number = hdl_generation_architecture_state_sequence.create_vhdl_for_the_state_sequence(
        transition_specifications, file_name, file_line_number
    )
    architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(4, state_sequence)
    architecture += "            end case;\n"
    file_line_number += 1

    reference_to_global_actions_after_custom_text, global_actions_after = (
        hdl_generation_library.create_global_actions_after()
    )
    if global_actions_after != "":
        global_actions_after = "-- Global Actions after:\n" + global_actions_after
        architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(3, global_actions_after)
        # global_actions_before starts always with "-- Global Actions after:", which is not a line entered by the user,
        # and therefore cannot be linked:
        file_line_number += 1
        number_of_new_lines = global_actions_after.count("\n") - 1
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_diagram_tab",
            number_of_new_lines,
            reference_to_global_actions_after_custom_text,
        )
        file_line_number += number_of_new_lines

    architecture += "        end if;\n"
    architecture += "    end process;\n"
    file_line_number += 2
    state_actions_process, file_line_number = hdl_generation_architecture_state_actions.create_state_action_process(
        file_name, file_line_number, state_tag_list_sorted
    )
    architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, state_actions_process)

    reference_to_concurrent_actions_custom_text, concurrent_actions = hdl_generation_library.create_concurrent_actions()
    if concurrent_actions != "":
        concurrent_actions = "-- Global Actions combinatorial:\n" + concurrent_actions
        architecture += hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, concurrent_actions)
        # concurrent_actions starts always with "-- Global Actions combinatorial:", which is not a line entered by
        # the user, and therefore cannot be linked:
        file_line_number += 1
        number_of_new_lines = concurrent_actions.count("\n") - 1
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_diagram_tab",
            number_of_new_lines,
            reference_to_concurrent_actions_custom_text,
        )
        file_line_number += number_of_new_lines

    architecture += "end architecture;\n"
    file_line_number += 1
    return architecture


def _create_type_definition_for_the_state_signal(state_tag_list_sorted) -> None:
    list_of_all_state_names = [
        project_manager.canvas.itemcget(state_tag + "_name", "text") for state_tag in state_tag_list_sorted
    ]
    if list_of_all_state_names != []:
        type_definition = "type t_state is ("
        list_of_all_state_names_reduced_by_last_entry = list_of_all_state_names[:-1]
        state_counter = 0
        for state_name in list_of_all_state_names_reduced_by_last_entry:
            type_definition += state_name + ", "
            state_counter += 1
            if state_counter == 10:
                state_counter = 0
                type_definition = type_definition[:-1]
                type_definition += "\n"
        type_definition += list_of_all_state_names[-1] + ");\n"
        return type_definition
    return "type t_state is ();\n"

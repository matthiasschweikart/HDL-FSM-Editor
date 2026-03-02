"""
Methods needed for HDL generation
"""

import os
import tkinter as tk
import traceback
from datetime import datetime
from tkinter import messagebox

import file_handling
import tag_plausibility
from codegen import hdl_generation_architecture, hdl_generation_library, hdl_generation_module
from codegen.hdl_generation_config import GenerationConfig
from constants import GuiTab
from elements import state_comment
from project_manager import project_manager

from .exceptions import GenerationError
from .list_separation_check import ListSeparationCheck

# Pylint expects this to be a constant with uppercase naming.
last_line_number_of_file1 = 0  # pylint: disable=invalid-name # module-level mutable


def run_hdl_generation(write_to_file, is_script_mode: bool = False) -> bool:
    """Run HDL generation with current config; show errors in GUI or print in script mode. Return True on success."""
    config = GenerationConfig.from_main_window()
    state_tag_list_sorted = _create_sorted_state_tag_list(is_script_mode)
    success = False
    try:
        _generate_hdl(config, write_to_file, state_tag_list_sorted)
        success = True
    except GenerationError as e:
        if is_script_mode:
            print(f"{e.caption}:\n{e.message}")
        else:
            messagebox.showerror(e.caption, e.message)
    except Exception:
        if not is_script_mode:
            messagebox.showerror("Unexpected Error", "An unexpected error occurred.\nSee details at STDOUT.")
        print(traceback.format_exc())

    return success


def _generate_hdl(config: GenerationConfig, write_to_file: bool, state_tag_list_sorted: list) -> None:
    errors = config.validate()
    if errors:
        raise GenerationError("Error in HDL-FSM-Editor", errors)

    if not tag_plausibility.TagPlausibility().get_tag_status_is_okay():
        raise GenerationError(
            "Error", ["The database is corrupt. Therefore, no HDL is generated.", "See details at STDOUT."]
        )
    if project_manager.root.title().endswith("*"):
        file_handling.save()

    # Create header with timestamp if enabled
    at_timestamp = f" at {datetime.today().ctime()}" if config.include_timestamp else ""
    if config.language == "VHDL":
        header = f"-- Created by HDL-FSM-Editor{at_timestamp}\n"
    else:
        header = f"// Created by HDL-FSM-Editor{at_timestamp}\n"

    _create_hdl(config, header, write_to_file, state_tag_list_sorted)


def _create_hdl(config, header, write_to_file, state_tag_list_sorted) -> None:
    file_name, file_name_architecture = _get_file_names(config)

    project_manager.link_dict_ref.clear_link_dict(file_name)
    if file_name_architecture:
        project_manager.link_dict_ref.clear_link_dict(file_name_architecture)
    file_line_number = 3  # Line 1 = Filename, Line 2 = Header

    if config.language == "VHDL":
        entity, file_line_number = _create_entity(config, file_name, file_line_number)
        if file_name_architecture == "":  # All VHDL is written in 1 file.
            file_to_use = file_name
            file_line_number_to_use = file_line_number
        else:
            file_to_use = file_name_architecture
            file_line_number_to_use = 3
        architecture = hdl_generation_architecture.create_architecture(
            file_to_use, file_line_number_to_use, state_tag_list_sorted
        )
    else:
        entity, file_line_number = _create_module_ports(config, file_name, file_line_number)
        architecture = hdl_generation_module.create_module_logic(file_name, file_line_number, state_tag_list_sorted)
    if architecture is None:
        return  # No further actions required, because when writing to a file, always an architecture must exist.
    # write_hdl_file must be called even if hdl is not needed, as write_hdl_file sets last_line_number_of_file1,
    # which is read by Linking:
    hdl = _write_hdl_file(config, write_to_file, header, entity, architecture, file_name, file_name_architecture)
    if write_to_file is True:
        _copy_hdl_into_generated_hdl_tab(hdl, file_name, file_name_architecture)


# TODO: This should not be here!
def _copy_hdl_into_generated_hdl_tab(hdl, file_name, file_name_architecture) -> None:
    project_manager.date_of_hdl_file_shown_in_hdl_tab = os.path.getmtime(file_name)
    if file_name_architecture != "":
        project_manager.date_of_hdl_file2_shown_in_hdl_tab = os.path.getmtime(file_name_architecture)
    project_manager.hdl_frame_text.config(state=tk.NORMAL)
    project_manager.hdl_frame_text.delete("1.0", tk.END)
    project_manager.hdl_frame_text.insert("1.0", hdl)
    project_manager.hdl_frame_text.update_highlight_tags(
        10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
    )
    project_manager.hdl_frame_text.config(state=tk.DISABLED)
    project_manager.notebook.show_tab(GuiTab.GENERATED_HDL)


def _create_entity(config, file_name, file_line_number) -> tuple:
    entity = ""

    package_statements = hdl_generation_library.get_text_from_text_widget(project_manager.interface_package_text)
    entity += package_statements
    number_of_new_lines = package_statements.count("\n")
    project_manager.link_dict_ref.add(
        file_name,
        file_line_number,
        "custom_text_in_interface_tab",
        number_of_new_lines,
        project_manager.interface_package_text,
    )
    file_line_number += number_of_new_lines

    entity += "\n"
    file_line_number += 1

    entity += "entity " + config.module_name + " is\n"
    project_manager.link_dict_ref.add(file_name, file_line_number, "Control-Tab", 1, "module_name")
    file_line_number += 1

    generic_declarations = hdl_generation_library.get_text_from_text_widget(project_manager.interface_generics_text)
    generic_declarations = ListSeparationCheck(generic_declarations, "VHDL").get_fixed_list()
    if generic_declarations != "":
        generic_declarations = (
            "    generic (\n"
            + hdl_generation_library.indent_text_by_the_given_number_of_tabs(2, generic_declarations)
            + "    );\n"
        )
        file_line_number += 1  # switch to first line with generic value.
        number_of_new_lines = generic_declarations.count("\n") - 2  # Subtract first and last line
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_interface_tab",
            number_of_new_lines,
            project_manager.interface_generics_text,
        )
        file_line_number += number_of_new_lines + 1
    entity += generic_declarations

    port_declarations = hdl_generation_library.get_text_from_text_widget(project_manager.interface_ports_text)
    port_declarations = ListSeparationCheck(port_declarations, "VHDL").get_fixed_list()
    if port_declarations != "":
        port_declarations = (
            "    port (\n"
            + hdl_generation_library.indent_text_by_the_given_number_of_tabs(2, port_declarations)
            + "    );\n"
        )
        file_line_number += 1  # switch to first line with port.
        number_of_new_lines = port_declarations.count("\n") - 2  # Subtract first and last line
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_interface_tab",
            number_of_new_lines,
            project_manager.interface_ports_text,
        )
        file_line_number += number_of_new_lines + 1
    entity += port_declarations

    entity += "end entity;\n"
    file_line_number += 1
    return entity, file_line_number


def _create_module_ports(config, file_name, file_line_number) -> tuple:
    module = ""
    file_line_number = 3  # Line 1 = Filename, Line 2 = Header
    module += "module " + config.module_name + "\n"
    project_manager.link_dict_ref.add(file_name, file_line_number, "Control-Tab", 1, "module_name")
    file_line_number += 1

    parameters = hdl_generation_library.get_text_from_text_widget(project_manager.interface_generics_text)
    parameters = ListSeparationCheck(parameters, "Verilog").get_fixed_list()
    if parameters != "":
        parameters = (
            "    #(parameter\n"
            + hdl_generation_library.indent_text_by_the_given_number_of_tabs(1, parameters)
            + "    )\n"
        )
        file_line_number += 1  # switch to first line with parameters.
        number_of_new_lines = parameters.count("\n") - 2  # Subtract first and last line
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_interface_tab",
            number_of_new_lines,
            project_manager.interface_generics_text,
        )
        file_line_number += number_of_new_lines + 1
        module += parameters

    ports = hdl_generation_library.get_text_from_text_widget(project_manager.interface_ports_text)
    ports = ListSeparationCheck(ports, "Verilog").get_fixed_list()
    if ports != "":
        ports = "    (\n" + hdl_generation_library.indent_text_by_the_given_number_of_tabs(2, ports) + "    );\n"
        number_of_new_lines = ports.count("\n") - 2  # Subtract first and last line
        file_line_number += 1  # switch to first line with port.
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_interface_tab",
            number_of_new_lines,
            project_manager.interface_ports_text,
        )
        file_line_number += number_of_new_lines + 1
        module += ports
    return module, file_line_number


def _write_hdl_file(config, write_to_file, header, entity, architecture, path_name, path_name_architecture) -> str:
    global last_line_number_of_file1
    _, name_of_file = os.path.split(path_name)
    if config.select_file_number == 1:
        if config.language == "VHDL":
            comment_string = "--"
        elif config.language == "Verilog":
            comment_string = "//"
        else:
            comment_string = "//"
        content = comment_string + " Filename: " + name_of_file + "\n"
        content += header
        content += entity
        content += architecture
        if write_to_file:
            with open(path_name, "w", encoding="utf-8") as fileobject:
                fileobject.write(content)
        last_line_number_of_file1 = content.count("\n") + 1  # For example: 3 lines are separated by 2 returns.
        project_manager.size_of_file1_line_number = (
            len(str(last_line_number_of_file1)) + 2
        )  # "+2" because of string ": "
        project_manager.size_of_file2_line_number = 0
        content_with_numbers = _add_line_numbers(content)
    else:
        content1 = "-- Filename: " + name_of_file + "\n"
        content1 += header
        content1 += entity
        if write_to_file:
            with open(path_name, "w", encoding="utf-8") as fileobject:
                fileobject.write(content1)
        last_line_number_of_file1 = content1.count("\n") + 1  # For example: 3 lines are separated by 2 returns.
        project_manager.size_of_file1_line_number = (
            len(str(last_line_number_of_file1)) + 2
        )  # "+2" because of string ": "
        _, name_of_architecture_file = os.path.split(path_name_architecture)
        content2 = "-- Filename: " + name_of_architecture_file + "\n"
        content2 += header
        content2 += architecture
        if write_to_file:
            with open(path_name_architecture, "w", encoding="utf-8") as fileobject:
                fileobject.write(content2)
        content_with_numbers1 = _add_line_numbers(content1)
        content_with_numbers2 = _add_line_numbers(content2)
        content_with_numbers = content_with_numbers1 + content_with_numbers2
        project_manager.size_of_file2_line_number = (
            len(str(content_with_numbers.count("\n"))) + 2
        )  # "+2" because of string ": "
    return content_with_numbers


def _get_file_names(config) -> tuple:
    # For Verilog and SystemVerilog, always generate single files regardless of number_of_files setting
    if config.language in ["Verilog", "SystemVerilog"]:
        file_type = ".v" if config.language == "Verilog" else ".sv"
        file_name = config.generate_path + "/" + config.module_name + file_type
        file_name_architecture = ""
    elif config.select_file_number == 1:
        # VHDL single file
        file_name = config.generate_path + "/" + config.module_name + ".vhd"
        file_name_architecture = ""
    else:
        # VHDL two files
        file_name = config.generate_path + "/" + config.module_name + "_e.vhd"
        file_name_architecture = config.generate_path + "/" + config.module_name + "_fsm.vhd"
    return file_name, file_name_architecture


def _add_line_numbers(text) -> str:
    text_lines = text.split("\n")
    text_length_as_string = str(len(text_lines))
    number_of_needed_digits_as_string = str(len(text_length_as_string))
    content_with_numbers = ""
    for line_number, line in enumerate(text_lines, start=1):
        content_with_numbers += format(line_number, "0" + number_of_needed_digits_as_string + "d") + ": " + line + "\n"
    return content_with_numbers


def _create_sorted_state_tag_list(is_script_mode) -> list:
    state_tag_dict_with_prio = {}
    state_tag_list = []
    reg_ex_for_state_tag = re.compile("^state[0-9]+$")
    for canvas_id in project_manager.canvas.find_all():
        for tag in project_manager.canvas.gettags(canvas_id):
            if reg_ex_for_state_tag.match(tag):
                single_element_list = project_manager.canvas.find_withtag(tag + "_comment")
                if not single_element_list:
                    state_tag_list.append(tag)
                else:
                    reference_to_state_comment_window = state_comment.StateComment.ref_dict[single_element_list[0]]
                    state_comments = reference_to_state_comment_window.text_id.get("1.0", "end - 1 chars")
                    state_comments_list = state_comments.split("\n")
                    first_line_of_state_comments = state_comments_list[0].strip()
                    if first_line_of_state_comments == "":
                        state_tag_list.append(tag)
                    else:
                        first_line_is_a_number = bool(all(c in "0123456789" for c in first_line_of_state_comments))
                        if not first_line_is_a_number:
                            state_tag_list.append(tag)
                        else:
                            if int(first_line_of_state_comments) in state_tag_dict_with_prio:
                                state_tag_list.append(tag)
                                if is_script_mode:
                                    print(
                                        "Warning in HDL-FSM-Editor: "
                                        + "The state '"
                                        + project_manager.canvas.itemcget(tag + "_name", "text")
                                        + "' uses the order-number "
                                        + first_line_of_state_comments
                                        + " which is already used at another state."
                                    )
                                else:
                                    messagebox.showwarning(
                                        "Warning in HDL-FSM-Editor",
                                        "The state '"
                                        + project_manager.canvas.itemcget(tag + "_name", "text")
                                        + "' uses the order-number "
                                        + first_line_of_state_comments
                                        + " which is already used at another state.",
                                    )
                            else:
                                state_tag_dict_with_prio[int(first_line_of_state_comments)] = tag
    for _, tag in sorted(state_tag_dict_with_prio.items(), reverse=True):
        state_tag_list.insert(0, tag)
    return state_tag_list

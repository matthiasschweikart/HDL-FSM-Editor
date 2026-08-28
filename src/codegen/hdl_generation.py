"""
Methods needed for HDL generation
"""

import os
import re
import tkinter as tk
import traceback
from datetime import datetime
from tkinter import messagebox

import file_handling
import tag_plausibility
import update_hdl_tab
from constants import GuiTab
from project_manager import project_manager

from . import hdl_generation_architecture, hdl_generation_library, hdl_generation_module, sensitivity_check_hfe
from .exceptions import GenerationError
from .hdl_generation_config import GenerationConfig
from .list_separation_check import ListSeparationCheck


class HdlGeneration:
    """Class for HDL generation methods."""

    last_line_number_of_file1 = 0

    def __init__(self, write_to_file, is_script_mode: bool = False):
        """Run HDL generation with current config; show errors in GUI or print in script mode."""
        config = GenerationConfig.from_main_window()
        state_tag_list_sorted = self._create_sorted_state_tag_list(is_script_mode)
        self._success = False
        try:
            self._generate_hdl(config, write_to_file, state_tag_list_sorted, is_script_mode)
            self._success = True
        except GenerationError as e:
            if is_script_mode:
                print(f"{e.caption}:\n{e.message}")
            else:
                messagebox.showerror(e.caption, e.message)
        except Exception:  # pylint: disable=broad-except
            if not is_script_mode:
                messagebox.showerror("Unexpected Error", "An unexpected error occurred.\nSee details at STDOUT.")
            print(traceback.format_exc())

    @property
    def success(self) -> bool:
        """Get the success status of the HDL generation."""
        return self._success

    def _generate_hdl(
        self, config: GenerationConfig, write_to_file: bool, state_tag_list_sorted: list, is_script_mode: bool
    ) -> None:
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

        self._create_hdl(config, header, write_to_file, state_tag_list_sorted, is_script_mode)

    def _create_hdl(self, config, header, write_to_file, state_tag_list_sorted, is_script_mode) -> None:
        # Use same path source as UI (GenerationConfig.get_primary_file / get_architecture_file)
        # so link dict keys match has_link() lookups in tab_hdl and tab_log.
        file_name = config.get_primary_file()
        file_name_architecture = config.get_architecture_file() or ""

        project_manager.link_dict_ref.clear_link_dict(file_name)
        if file_name_architecture:
            project_manager.link_dict_ref.clear_link_dict(file_name_architecture)
        file_line_number = 3  # Line 1 = Filename, Line 2 = Header

        if config.language == "VHDL":
            entity, file_line_number = self._create_entity(config, file_name, file_line_number)
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
            entity, file_line_number = self._create_module_ports(config, file_name, file_line_number)
            architecture = hdl_generation_module.create_module_logic(file_name, file_line_number, state_tag_list_sorted)
        if architecture is None:
            return  # No further actions required, because when writing to a file, always an architecture must exist.
        # write_hdl_file must be called even if hdl is not needed, as write_hdl_file
        # sets HdlGeneration.last_line_number_of_file1, which is read by Linking:
        ent, arch = self._write_hdl_file(
            config, write_to_file, header, entity, architecture, file_name, file_name_architecture
        )
        if write_to_file is True:
            project_manager.date_of_hdl_file_shown_in_hdl_tab = os.path.getmtime(file_name)
            if file_name_architecture != "":
                project_manager.date_of_hdl_file2_shown_in_hdl_tab = os.path.getmtime(file_name_architecture)
            update_hdl_tab.UpdateHdlTab.copy_into_hdl_tab(ent, arch)
            project_manager.notebook.show_tab(GuiTab.GENERATED_HDL)
            if not is_script_mode:
                project_manager.tab_log_ref.log_frame_text.config(state=tk.NORMAL)
                project_manager.tab_log_ref.log_frame_text.insert(
                    tk.END,
                    "\n++++++++++++++++++++++++++++++++++++++ "
                    + datetime.today().ctime()
                    + " +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                    + "HDL was generated: "
                    + config.module_name
                    + "\nHDL generation ready.\n",
                )
                project_manager.tab_log_ref.log_frame_text.config(state=tk.DISABLED)
            sensitivity_check_hfe.SensitivityCheckHfe(is_script_mode)

    def _create_entity(self, config, file_name, file_line_number) -> tuple:
        entity = ""

        package_statements = hdl_generation_library.get_text_from_text_widget(
            project_manager.tab_interface_ref.interface_packages_text
        )
        entity += package_statements
        number_of_new_lines = package_statements.count("\n")
        project_manager.link_dict_ref.add(
            file_name,
            file_line_number,
            "custom_text_in_interface_tab",
            number_of_new_lines,
            project_manager.tab_interface_ref.interface_packages_text,
        )
        file_line_number += number_of_new_lines

        entity += "\n"
        file_line_number += 1

        entity += "entity " + config.module_name + " is\n"
        project_manager.link_dict_ref.add(file_name, file_line_number, "Control-Tab", 1, "module_name")
        file_line_number += 1

        generic_declarations = hdl_generation_library.get_text_from_text_widget(
            project_manager.tab_interface_ref.interface_generics_text
        )
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
                project_manager.tab_interface_ref.interface_generics_text,
            )
            file_line_number += number_of_new_lines + 1
        entity += generic_declarations

        port_declarations = hdl_generation_library.get_text_from_text_widget(
            project_manager.tab_interface_ref.interface_ports_text
        )
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
                project_manager.tab_interface_ref.interface_ports_text,
            )
            file_line_number += number_of_new_lines + 1
        entity += port_declarations

        entity += "end entity;\n"
        file_line_number += 1
        return entity, file_line_number

    def _create_module_ports(self, config, file_name, file_line_number) -> tuple:
        module = ""
        file_line_number = 3  # Line 1 = Filename, Line 2 = Header
        module += "module " + config.module_name + "\n"
        project_manager.link_dict_ref.add(file_name, file_line_number, "Control-Tab", 1, "module_name")
        file_line_number += 1

        parameters = hdl_generation_library.get_text_from_text_widget(
            project_manager.tab_interface_ref.interface_generics_text
        )
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
                project_manager.tab_interface_ref.interface_generics_text,
            )
            file_line_number += number_of_new_lines + 1
            module += parameters

        ports = hdl_generation_library.get_text_from_text_widget(project_manager.tab_interface_ref.interface_ports_text)
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
                project_manager.tab_interface_ref.interface_ports_text,
            )
            file_line_number += number_of_new_lines + 1
            module += ports
        return module, file_line_number

    def _write_hdl_file(
        self, config, write_to_file, header, entity, architecture, path_name, path_name_architecture
    ) -> str:
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
            HdlGeneration.last_line_number_of_file1 = (
                content.count("\n") + 1
            )  # For example: 3 lines are separated by 2 returns.
            project_manager.size_of_file1_line_number = (
                len(str(HdlGeneration.last_line_number_of_file1)) + 2
            )  # "+2" because of string ": "
            project_manager.size_of_file2_line_number = 0
            content_with_numbers1 = self._add_line_numbers(content)
            content_with_numbers2 = ""
        else:
            content1 = "-- Filename: " + name_of_file + "\n"
            content1 += header
            content1 += entity
            if write_to_file:
                with open(path_name, "w", encoding="utf-8") as fileobject:
                    fileobject.write(content1)
            HdlGeneration.last_line_number_of_file1 = (
                content1.count("\n") + 1
            )  # For example: 3 lines are separated by 2 returns.
            project_manager.size_of_file1_line_number = (
                len(str(HdlGeneration.last_line_number_of_file1)) + 2
            )  # "+2" because of string ": "
            _, name_of_architecture_file = os.path.split(path_name_architecture)
            content2 = "-- Filename: " + name_of_architecture_file + "\n"
            content2 += header
            content2 += architecture
            if write_to_file:
                with open(path_name_architecture, "w", encoding="utf-8") as fileobject:
                    fileobject.write(content2)
            content_with_numbers1 = self._add_line_numbers(content1)
            content_with_numbers2 = self._add_line_numbers(content2)
            content_with_numbers = content_with_numbers1 + content_with_numbers2
            project_manager.size_of_file2_line_number = (
                len(str(content_with_numbers.count("\n"))) + 2
            )  # "+2" because of string ": "
        return content_with_numbers1, content_with_numbers2

    def _add_line_numbers(self, text) -> str:
        text_lines = text.split("\n")
        text_length_as_string = str(len(text_lines))
        number_of_needed_digits_as_string = str(len(text_length_as_string))
        content_with_numbers = ""
        for line_number, line in enumerate(text_lines, start=1):
            content_with_numbers += (
                format(line_number, "0" + number_of_needed_digits_as_string + "d") + ": " + line + "\n"
            )
        return content_with_numbers

    def _create_sorted_state_tag_list(self, is_script_mode) -> list:
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
                        reference_to_state_comment_window = project_manager.canvas_windows_ref_dict[
                            single_element_list[0]
                        ]
                        state_comments = reference_to_state_comment_window.text_ids[0].get("1.0", "end - 1 chars")
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

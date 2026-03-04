"""
This module implements all methods executes the compile command stored in the Control-tab.
"""

import os
import re
import shlex
import subprocess
import tkinter as tk
from datetime import datetime
from os.path import exists
from tkinter import messagebox

from constants import GuiTab
from project_manager import project_manager


def compile_hdl() -> None:
    """Run the compile command and show output in the compile message tab."""
    project_manager.notebook.show_tab(GuiTab.COMPILE_MSG)
    if (
        project_manager.working_directory_value.get() != ""
        and not project_manager.working_directory_value.get().isspace()
    ):
        try:
            os.chdir(project_manager.working_directory_value.get())
        except FileNotFoundError:
            messagebox.showerror(
                "Error", "The working directory\n" + project_manager.working_directory_value.get() + "\ndoes not exist."
            )
            return
    project_manager.log_frame_text.config(state=tk.NORMAL)
    project_manager.log_frame_text.insert(
        tk.END,
        "\n++++++++++++++++++++++++++++++++++++++ "
        + datetime.today().ctime()
        + " +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n",
    )
    project_manager.log_frame_text.config(state=tk.DISABLED)
    start_time = datetime.now()
    commands = _get_command_list()
    # print("compile_handling: commands =", commands)
    for command in commands:
        success = _execute(command)
        if not success:
            break
    end_time = datetime.now()
    project_manager.log_frame_text.config(state=tk.NORMAL)
    _insert_line_in_log("Finished user commands from Control-Tab after " + str(end_time - start_time) + ".\n")
    project_manager.log_frame_text.config(state=tk.DISABLED)


def _execute(command) -> bool:
    command_array = shlex.split(command)  # Does not split quoted sub-strings with blanks.
    command_array_new = _replace_variables(command_array)
    if command_array_new is None:
        return False
    for command_part in command_array_new:
        _insert_line_in_log(command_part + " ")
    _insert_line_in_log("\n")
    try:
        with subprocess.Popen(
            command_array_new,
            text=True,  # Decoding is done by Popen.
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as process:
            for line in process.stdout:  # Terminates when process.stdout is closed.
                if line != "\n":  # VHDL report-statements cause empty lines which mess up the protocol.
                    _insert_line_in_log(line)
    except FileNotFoundError:
        command_string = ""
        for word in command_array_new:
            command_string += word + " "
        messagebox.showerror(
            "Error in HDL-FSM-Editor", "FileNotFoundError caused by compile command:\n" + command_string
        )
        return False
    return True


def _get_command_list():
    command_string_tmp = project_manager.compile_cmd.get()
    command_string = command_string_tmp.replace(";", " ; ")
    return command_string.split(";")


def _replace_variables(command_array) -> list | None:
    command_array_new = []
    handlers = {
        "$file": _replace_file_var,
        "$file1": _replace_file1_var,
        "$file2": _replace_file2_var,
        "$name": _replace_name_var,
    }
    for entry in command_array:
        handler = handlers.get(entry)
        if handler is not None:
            result = handler()
            if result is None:
                return None
            command_array_new.append(result)
        else:
            command_array_new.append(entry)
    return command_array_new


def _replace_file_var() -> str | None:
    if project_manager.select_file_number_text.get() == 2:
        messagebox.showerror(
            "Error",
            'The compile command uses $file, but the "2 files mode" is selected, '
            "so only $file1 and $file2 are allowed.",
        )
        return None
    language = project_manager.language.get()
    extension = ".vhd" if language == "VHDL" else (".v" if language == "Verilog" else ".sv")
    file_name = project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + extension
    if not exists(file_name):
        messagebox.showerror("Error", "Compile is not possible, HDL file " + file_name + " does not exist.")
        return None
    return file_name


def _replace_file1_var() -> str | None:
    if project_manager.select_file_number_text.get() == 1:
        messagebox.showerror(
            "Error",
            'The compile command uses $file1, but the "1 files mode" is selected, so only $file is allowed).',
        )
        return None
    file_name = project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + "_e.vhd"
    if not exists(file_name):
        messagebox.showerror("Error", "Compile is not possible, as HDL file" + file_name + " does not exist.")
        return None
    return file_name


def _replace_file2_var() -> str | None:
    if project_manager.select_file_number_text.get() == 1:
        messagebox.showerror(
            "Error",
            'The compile command uses $file2, but the "1 files mode" is selected, so only $file is allowed).',
        )
        return None
    file_name = project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + "_fsm.vhd"
    if not exists(file_name):
        messagebox.showerror("Error", "Compile is not possible, as HDL file" + file_name + " does not exist.")
        return None
    return file_name


def _replace_name_var() -> str:
    return project_manager.module_name.get()


def _insert_line_in_log(line) -> None:
    if project_manager.language.get() == "VHDL":
        # search for compiler-message with ":<line-number>:<column-number>:":
        regex_message_find = project_manager.regex_message_find_for_vhdl
    else:
        regex_message_find = project_manager.regex_message_find_for_verilog
    try:
        match_object_of_message = re.match(regex_message_find, line)
    except re.error as e:
        print("Error in HDL-FSM-Editor by regular expression", repr(e))
        return

    line_low = line.lower()
    project_manager.log_frame_text.config(state=tk.NORMAL)
    if match_object_of_message is not None or " error " in line_low or " warning " in line_low:
        # Add line together with color-tag to the text:
        if project_manager.language.get() == "VHDL" and "report note" in line_low:
            project_manager.log_frame_text.insert(tk.END, line, ("message_green"))
        else:
            project_manager.log_frame_text.insert(tk.END, line, ("message_red"))
    else:
        project_manager.log_frame_text.insert(tk.END, line)
    project_manager.log_frame_text.config(state=tk.DISABLED)
    project_manager.log_frame_text.see(tk.END)

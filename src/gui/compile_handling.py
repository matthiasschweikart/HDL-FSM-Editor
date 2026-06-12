"""
This module implements all methods executes the compile command stored in the Control-tab.
"""

import os
import pathlib
import re
import shlex
import subprocess
import tkinter as tk
from datetime import datetime
from os.path import exists
from tkinter import messagebox

from constants import GuiTab
from project_manager import project_manager
from utils.exec_like_bash import parse_command_string, run_command_list
from utils.hdl_paths import get_hdl_output_paths
from utils.var_expansion import expand_generate_path, expand_variables_in_list, find_git_root


def compile_hdl() -> None:
    """Run the compile command and show output in the compile message tab."""
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
    project_manager.notebook.show_tab(GuiTab.COMPILE_MSG)
    project_manager.tab_log_ref.log_frame_text.config(state=tk.NORMAL)
    project_manager.tab_log_ref.log_frame_text.insert(
        tk.END,
        "\n++++++++++++++++++++++++++++++++++++++ "
        + datetime.today().ctime()
        + " +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n",
    )
    project_manager.tab_log_ref.log_frame_text.config(state=tk.DISABLED)
    project_manager.tab_log_ref.log_frame_text.see(tk.END)
    project_manager.tab_log_ref.log_frame_text.focus_set()
    project_manager.root.update()  # Wait until the user can see the log.
    start_time = datetime.now()
    commands = _get_command_list()
    if commands is None:
        messagebox.showerror("Error", "Unbalanced braces in compile command: missing '}' or unexpected '}'.")
        return
    run_command_list(commands, execute=_execute)
    end_time = datetime.now()
    project_manager.tab_log_ref.log_frame_text.config(state=tk.NORMAL)
    _insert_line_in_log("Finished user commands from Control-Tab after " + str(end_time - start_time) + ".\n")
    project_manager.tab_log_ref.log_frame_text.config(state=tk.DISABLED)


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
    except Exception:  # pylint: disable=broad-except
        command_string = ""
        for word in command_array_new:
            command_string += word + " "
        messagebox.showerror(
            "Error in HDL-FSM-Editor", "An error occurred while executing the compile command:\n" + command_string
        )
        return False
    return True


def _get_command_list() -> list[tuple[str | None, str | list]] | None:
    """Parse compile command into list of (op, cmd). op is None/';'/'&&'/'||', cmd is str or list (group).
    Returns None on parse error (e.g. unbalanced braces)."""
    return parse_command_string(project_manager.compile_cmd.get())


def _replace_variables(command_array) -> list | None:
    try:
        internal_vars = _get_internal_variables()
        return expand_variables_in_list(command_array, internal_vars, error_on_missing=True, use_environ=True)
    except KeyError as e:
        missing_key = e.args[0]
        number_of_files = project_manager.select_file_number_text.get()

        if missing_key == "file" and number_of_files == 2:
            messagebox.showerror(
                "Error",
                "The compile command uses $file, but the "
                '"2 files mode" is selected, so only $file1 and $file2 are allowed.',
            )
        elif (missing_key == "file1" or missing_key == "file2") and number_of_files == 1:
            messagebox.showerror(
                "Error",
                "The compile command uses $file1 or $file2, but the "
                '"1 files mode" is selected, so only $file is allowed.',
            )
        else:
            messagebox.showerror("Error", f"Variable '{missing_key}' not found")
        return None


def _get_internal_variables():
    """Get the current internal variables and validate."""

    internal_vars = {}
    internal_vars["name"] = project_manager.module_name.get()

    file_mode = project_manager.select_file_number_text.get()
    language = project_manager.language.get()
    raw_path = project_manager.generate_path_value.get()
    hfe_file_path = project_manager.current_file
    base_path = expand_generate_path(raw_path, hfe_file_path)
    module_name = project_manager.module_name.get()

    internal_vars["git_root"] = lambda _: find_git_root(hfe_file_path)
    internal_vars["hfe_file_dir"] = lambda _: pathlib.Path(hfe_file_path).parent.as_posix()

    paths = get_hdl_output_paths(base_path, module_name, language, file_mode)
    if not paths:
        messagebox.showerror("Error", "Compile is not possible: invalid output path or module name.")
        return None
    if len(paths) == 1:
        internal_vars["file"] = paths[0]
        if not exists(paths[0]):
            messagebox.showerror("Error", "Compile is not possible, HDL file " + paths[0] + " does not exist.")
            return None
    else:
        internal_vars["file1"] = paths[0]
        internal_vars["file2"] = paths[1]
        if not exists(paths[0]):
            messagebox.showerror("Error", "Compile is not possible, as HDL file " + paths[0] + " does not exist.")
            return None
        if not exists(paths[1]):
            messagebox.showerror("Error", "Compile is not possible, as HDL file " + paths[1] + " does not exist.")
            return None

    return internal_vars


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
    project_manager.tab_log_ref.log_frame_text.config(state=tk.NORMAL)
    if match_object_of_message is not None or " error " in line_low or " warning " in line_low:
        # Add line together with color-tag to the text:
        if project_manager.language.get() == "VHDL" and "report note" in line_low:
            project_manager.tab_log_ref.log_frame_text.insert(tk.END, line, ("message_green"))
        else:
            project_manager.tab_log_ref.log_frame_text.insert(tk.END, line, ("message_red"))
    else:
        project_manager.tab_log_ref.log_frame_text.insert(tk.END, line)
    project_manager.tab_log_ref.log_frame_text.config(state=tk.DISABLED)
    project_manager.tab_log_ref.log_frame_text.see(tk.END)
    project_manager.root.update()

"""
Copies the generated HDL into the HDL-tab if the HDL is younger than the hfe-file.
"""

import os
import tkinter as tk
from tkinter import messagebox

from codegen import hdl_generation
from project_manager import project_manager


class UpdateHdlTab:
    """
    Copies the generated HDL into the HDL-tab if the HDL is younger than the hfe-file.
    Not called in batch mode.
    """

    def __init__(self, language, number_of_files, readfile, generate_path, module_name) -> None:
        self.date_of_hdl_file = 0.0  # Default-Value, used when hdl-file not exists.
        self.date_of_hdl_file2 = 0.0  # Default-Value, used when hdl-file not exists.
        if language == "VHDL":
            if number_of_files == 1:
                hdlfilename = generate_path + "/" + module_name + ".vhd"
                hdlfilename_architecture = None
            else:
                hdlfilename = generate_path + "/" + module_name + "_e.vhd"
                hdlfilename_architecture = generate_path + "/" + module_name + "_fsm.vhd"
        else:  # verilog
            hdlfilename = generate_path + "/" + module_name + ".v"
            hdlfilename_architecture = None
        # Compare modification time of HDL file against modification_time of design file (.hse):
        project_manager.hdl_frame_text.config(state=tk.NORMAL)
        project_manager.hdl_frame_text.delete("1.0", tk.END)
        project_manager.hdl_frame_text.insert("1.0", "")
        project_manager.hdl_frame_text.config(state=tk.DISABLED)
        hdl = ""
        if self.__hdl_is_up_to_date(readfile, hdlfilename, hdlfilename_architecture, show_message=False):
            # print("HDL-file exists and is 'newer' than the design-file =", self.date_of_hdl_file)
            try:
                with open(hdlfilename, encoding="utf-8") as fileobject:
                    entity = fileobject.read()
                hdl += self.__add_line_numbers(entity)
            except FileNotFoundError:
                messagebox.showerror(
                    "Error in HDL-FSM-Editor", "File " + hdlfilename + " could not be opened for copying into HDL-Tab."
                )
            if hdlfilename_architecture is not None:
                # HDL-file exists and was generated after the design-file was saved.
                try:
                    with open(hdlfilename_architecture, encoding="utf-8") as fileobject:
                        arch = fileobject.read()
                    hdl += self.__add_line_numbers(arch)
                except FileNotFoundError:
                    messagebox.showerror(
                        "Error in HDL-FSM-Editor",
                        "File "
                        + hdlfilename_architecture
                        + " (architecture-file) could not be opened for copying into HDL-Tab.",
                    )
            # Create hdl without writing to file for Link-Generation:
            hdl_generation.run_hdl_generation(write_to_file=False, is_script_mode=False)
        project_manager.hdl_frame_text.config(state=tk.NORMAL)
        project_manager.hdl_frame_text.insert("1.0", hdl)
        project_manager.hdl_frame_text.config(state=tk.DISABLED)
        project_manager.hdl_frame_text.update_highlight_tags(
            10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
        )

    def __hdl_is_up_to_date(self, path_name, hdlfilename, hdlfilename_architecture, show_message) -> bool:
        if not os.path.isfile(path_name):
            messagebox.showerror(
                "Error in HDL-FSM-Editor", "The HDL-FSM-Editor project file " + path_name + " is missing."
            )
            return False
        if not os.path.isfile(hdlfilename):
            if show_message:
                messagebox.showerror("Error in HDL-FSM-Editor", "The file " + hdlfilename + " is missing.")
            return False
        if hdlfilename_architecture is not None and not os.path.isfile(hdlfilename_architecture):
            if show_message:
                messagebox.showerror(
                    "Error in HDL-FSM-Editor",
                    "The entity-file exists, but the architecture file\n" + hdlfilename_architecture + " is missing.",
                )
            return False
        self.date_of_hdl_file = os.path.getmtime(hdlfilename)
        if hdlfilename_architecture is not None:
            self.date_of_hdl_file2 = os.path.getmtime(hdlfilename_architecture)
        if self.date_of_hdl_file < os.path.getmtime(path_name):
            if show_message:
                messagebox.showerror(
                    "Error in HDL-FSM-Editor",
                    "The file\n" + hdlfilename + "\nis older than\n" + path_name + "\nPlease generate HDL again.",
                )
            return False
        if hdlfilename_architecture is not None and self.date_of_hdl_file2 < os.path.getmtime(path_name):
            if show_message:
                messagebox.showerror(
                    "Error in HDL-FSM-Editor",
                    "The architecture file\n"
                    + hdlfilename_architecture
                    + "\nis older than\n"
                    + path_name
                    + "\nPlease generate HDL again.",
                )
            return False
        return True

    def __add_line_numbers(self, text) -> str:
        text_lines = text.split("\n")
        text_length_as_string = str(len(text_lines))
        number_of_needed_digits_as_string = str(len(text_length_as_string))
        content_with_numbers = ""
        for line_number, line in enumerate(text_lines, start=1):
            content_with_numbers += (
                format(line_number, "0" + number_of_needed_digits_as_string + "d") + ": " + line + "\n"
            )
        return content_with_numbers

    def get_date_of_hdl_file(self) -> float:
        """Return modification date of the first generated HDL file."""
        return self.date_of_hdl_file

    def get_date_of_hdl_file2(self) -> float:
        """Return modification date of the second generated HDL file (e.g. architecture)."""
        return self.date_of_hdl_file2

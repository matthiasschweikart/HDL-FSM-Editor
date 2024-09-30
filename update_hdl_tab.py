"""
Copies the generated HDL into the HDL-tab if the HDL is younger than the hfe-file.
"""
import os
import tkinter as tk
from tkinter import messagebox
import main_window
import hdl_generation

class UpdateHdlTab():
    def __init__(self, language, number_of_files, readfile, generate_path, module_name):
        if language=="VHDL":
            if number_of_files==1:
                filename = generate_path + "/" + module_name + ".vhd"
                filename_architecture = None
            else:
                filename              = generate_path + "/" + module_name + "_e.vhd"
                filename_architecture = generate_path + "/" + module_name + "_fsm.vhd"
        else: # verilog
            filename = generate_path + "/" + module_name + ".v"
            filename_architecture = None
        # Compare modification time of HDL file against modification_time of design file (.hse):
        hdl = ""
        if not self.hdl_must_be_generated(readfile, filename, filename_architecture, show_message=False):
            # HDL-file(s) exists and are "newer" than the design-file.
            try:
                fileobject = open(filename, 'r', encoding="utf-8")
                entity = fileobject.read()
                fileobject.close()
                hdl += self._add_line_numbers(entity)
                # self.last_line_number_of_file1 = hdl.count("\n")
                # self.size_of_file1_line_number = len(str(self.last_line_number_of_file1)) + 2 # "+2" because of string ": "
                # self.size_of_file2_line_number = 0
            except FileNotFoundError:
                messagebox.showerror("Error in HDL-FSM-Editor", "File " + filename + " could not be opened for copying into HDL-Tab.")
            if number_of_files==2:
                # HDL-file exists and was generated after the design-file was saved.
                try:
                    fileobject = open(filename_architecture, 'r', encoding="utf-8")
                    arch = fileobject.read()
                    fileobject.close()
                    hdl += self._add_line_numbers(arch)
                    #self.size_of_file2_line_number = len(str(hdl.count("\n"))) + 2 # "+2" because of string ": "
                except FileNotFoundError:
                    messagebox.showwarning("Error in HDL-FSM-Editor", "File " + filename + " (architecture-file) could not be opened for copying into HDL-Tab.")
            hdl_generation.run_hdl_generation(write_to_file=False)
        else:
            # No HDL was found which could be loaded into HDL-tab, so clear the HDL-tab:
            main_window.hdl_frame_text.config(state=tk.NORMAL)
            main_window.hdl_frame_text.insert("1.0", "")
            main_window.hdl_frame_text.config(state=tk.DISABLED)

    def hdl_must_be_generated(self, path_name, hdlfilename, hdlfilename_architecture, show_message):
        if not os.path.isfile(path_name):
            messagebox.showerror("Error in HDL-FSM-Editor", "The HDL-FSM-Editor project file " + path_name + " is missing.")
            return True
        if not os.path.isfile(hdlfilename):
            if show_message:
                messagebox.showerror("Error in HDL-FSM-Editor", "The file "   + hdlfilename + " is missing.")
            return True
        if os.path.getmtime(hdlfilename)<os.path.getmtime(path_name):
            if show_message:
                messagebox.showerror("Error in HDL-FSM-Editor", "The file\n" + hdlfilename + "\nis older than\n" + path_name + "\nPlease generate HDL again.")
            return True
        if hdlfilename_architecture is not None:
            if not os.path.isfile(hdlfilename_architecture):
                if show_message:
                    messagebox.showerror("Error in HDL-FSM-Editor", "The architecture file "   + hdlfilename_architecture + " is missing.")
                return True
            if os.path.getmtime(hdlfilename_architecture)<os.path.getmtime(path_name):
                if show_message:
                    messagebox.showerror("Error in HDL-FSM-Editor", "The file\n" + hdlfilename_architecture + "\nis older than\n" + path_name + "\nPlease generate HDL again.")
                return True
        return False

    def _add_line_numbers(self, text):
        text_lines = text.split("\n")
        text_length_as_string = str(len(text_lines))
        number_of_needed_digits_as_string = str(len(text_length_as_string))
        content_with_numbers = ""
        for line_number, line in enumerate(text_lines, start=1):
            content_with_numbers += format(line_number, "0" + number_of_needed_digits_as_string + "d") + ": " + line + "\n"
        return content_with_numbers

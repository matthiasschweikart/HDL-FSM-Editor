import subprocess
from tkinter import *
from os.path import exists
from tkinter import messagebox
from datetime import datetime
import os


import main_window

def compile():
    if main_window.working_directory_value.get()!="" and not main_window.working_directory_value.get().isspace():
        try:
            os.chdir(main_window.working_directory_value.get())
        except FileNotFoundError:
            messagebox.showerror("Error", "The working directory\n" + main_window.working_directory_value.get() + "\ndoes not exist.")
            return
    show_compile_messages_tab()
    main_window.log_frame_text.config(state=NORMAL)
    main_window.log_frame_text.insert(END, "\n++++++++++++++++++++++++++++++++++++++ " + datetime.today().ctime() +" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    main_window.log_frame_text.config(state=DISABLED)
    commands = get_command_list()
    #print("compile_handling: commands =", commands)
    for command in commands:
        execute(command)

def execute(command):
    command_array_new = replace_variables_and_convert_into_list(command)
    #print("command_array_new =", command_array_new)
    if command_array_new is None:
        return
    try:
        process = subprocess.Popen(command_array_new,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    except FileNotFoundError:
        command_new_string = ""
        for c in command_array_new:
            command_new_string += c + " "
        messagebox.showerror("Error", "Error in compile command: " + command_new_string)
        return
    stdout, stderr = process.communicate()
    copy_into_compile_messages_tab(stdout, stderr, command_array_new)

def show_compile_messages_tab():
    notebook_ids = main_window.notebook.tabs()
    for id in notebook_ids:
        if main_window.notebook.tab(id, option="text")=="Compile Messages":
            main_window.notebook.select(id)

def get_command_list():
    command_string_tmp = main_window.compile_cmd.get()
    command_string = command_string_tmp.replace(";", " ; ")
    return command_string.split(";")

def replace_variables_and_convert_into_list(command):
    command_array_new = []
    command_array = command.split()
    for command in command_array:
        if command=="$file":
            if main_window.select_file_number_text.get()==2:
                messagebox.showerror("Error", 'The compile command uses $file, but the "2 files mode" is selected, so only $file1 and $file2 are allowed.')
                return
            language = main_window.language.get()
            if language=="VHDL":
                extension = ".vhd"
            elif language=="Verilog":
                extension = ".v"
            else:
                extension = ".sv"
            file_name = main_window.generate_path_value.get() + "/" + main_window.module_name.get() + extension
            if not exists(file_name):
                messagebox.showerror("Error", "Compile is not possible, HDL file " + file_name + " does not exist.")
                return
            command_array_new.append(file_name)
        elif command=="$file1":
            if main_window.select_file_number_text.get()==1:
                messagebox.showerror("Error", 'The compile command uses $file1, but the "1 files mode" is selected, so only $file is allowed).')
                return
            file_name1 = main_window.generate_path_value.get() + "/" + main_window.module_name.get() + "_e.vhd"
            if not exists(file_name1):
                messagebox.showerror("Error", "Compile is not possible, as HDL file" + file_name1 + " does not exist.")
                return
            command_array_new.append(file_name1)
        elif command=="$file2":
            if main_window.select_file_number_text.get()==1:
                messagebox.showerror("Error", 'The compile command uses $file2, but the "1 files mode" is selected, so only $file is allowed).')
                return
            file_name2 = main_window.generate_path_value.get() + "/" + main_window.module_name.get() + "_fsm.vhd"
            if not exists(file_name2):
                messagebox.showerror("Error", "Compile is not possible, as HDL file" + file_name2 + " does not exist.")
                return
            command_array_new.append(file_name2)
        elif command=="$name":
            command_array_new.append(main_window.module_name.get())
        else:
            command_array_new.append(command)
    return command_array_new

def copy_into_compile_messages_tab(stdout, stderr, command_array_new):
    main_window.log_frame_text.config(state=NORMAL)
    for part in command_array_new:
        main_window.log_frame_text.insert(END, part + " ")
    main_window.log_frame_text.insert(END, "\n")
    main_window.log_frame_text.insert(END, "STDERR:\n")
    main_window.log_frame_text.insert(END, stderr)
    main_window.log_frame_text.insert(END, "STDOUT:\n")
    main_window.log_frame_text.insert(END, stdout)
    main_window.log_frame_text.insert(END, "=========================================================================\n")
    main_window.log_frame_text.config(state=DISABLED)
    main_window.log_frame_text.see(END)

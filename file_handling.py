"""
This module contains all methods needed for reading and writing from or to a file.
"""
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
import os
import re
import json

import state_handling
import transition_handling
import canvas_editing
import state_action_handling
import state_actions_default
import condition_action_handling
import connector_handling
import reset_entry_handling
import global_actions
import global_actions_handling
import undo_handling
import global_actions_combinatorial
import main_window
import custom_text
import state_comment
import update_hdl_tab
import constants

filename = ""

def save_as():
    global filename
    filename = asksaveasfilename(defaultextension=".hfe",
                                 initialfile = main_window.module_name.get(),
                                 filetypes=(("HDL-FSM-Editor files","*.hfe"),("all files","*.*")))
    if filename!="":
        save_in_file_new(filename)

def save():
    global filename
    if filename=="":
        filename = asksaveasfilename(defaultextension=".hfe",
                                     initialfile = main_window.module_name.get(),
                                     filetypes=(("HDL-FSM-Editor files","*.hfe"),("all files","*.*")))
    if filename!="":
        save_in_file_new(filename)

def write_coords(fileobject, canvas_id):
    coords = main_window.canvas.coords(canvas_id)
    for c in coords:
        fileobject.write(str(c) + " ")

def write_tags(fileobject, canvas_id):
    tags = main_window.canvas.gettags(canvas_id)
    for t in tags:
        fileobject.write(str(t) + " ")

def open_file_old():
    filename_new = askopenfilename(filetypes=(("HDL-FSM-Editor files","*.hfe"),("all files","*.*")))
    if filename_new!="":
        removed = remove_old_design()
        if removed:
            open_file_with_name(filename_new)

def open_file():
    filename_new = askopenfilename(filetypes=(("HDL-FSM-Editor files","*.hfe"),("all files","*.*")))
    if filename_new!="":
        removed = remove_old_design()
        if removed:
            open_file_with_name_new(filename_new)

def open_file_with_name(read_filename):
    custom_text.CustomText.read_variables_of_all_windows.clear()
    custom_text.CustomText.written_variables_of_all_windows.clear()
    # Bring the notebook tab with the graphic into the foreground:
    notebook_ids = main_window.notebook.tabs()
    for notebook_id in notebook_ids:
        if main_window.notebook.tab(notebook_id, option="text")=="Diagram":
            main_window.notebook.select(notebook_id)
    # Read the design from the file:
    fileobject = open(read_filename, 'r', encoding="utf-8")
    for line in fileobject:
        if   line.startswith("modulename|"):
            main_window.module_name.set(line[11:-1])
        elif line.startswith("language|"):
            old_language = main_window.language.get()
            main_window.language.set(line[9:-1])
            if line[9:1]!=old_language:
                main_window.switch_language_mode()
        elif line.startswith("generate_path|"):
            main_window.generate_path_value.set(line[14:-1])
        elif line.startswith("working_directory|"):
            main_window.working_directory_value.set(line[18:-1])
        elif line.startswith("number_of_files|"):
            main_window.select_file_number_text.set(int(line[16:-1]))
        elif line.startswith("reset_signal_name|"):
            main_window.reset_signal_name.set(line[18:-1])
        elif line.startswith("clock_signal_name|"):
            main_window.clock_signal_name.set(line[18:-1])
        elif line.startswith("compile_cmd|"):
            main_window.compile_cmd.set(line[12:-1])
        elif line.startswith("edit_cmd|"):
            main_window.edit_cmd.set(line[9:-1])
        elif line.startswith("interface_package|"):
            rest_of_line   = remove_keyword_from_line(line,"interface_package|")
            data           = get_data(rest_of_line, fileobject)
            main_window.interface_package_text.insert("1.0", data)
            main_window.interface_package_text.update_highlight_tags(10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        elif line.startswith("interface_generics|"):
            rest_of_line   = remove_keyword_from_line(line,"interface_generics|")
            data           = get_data(rest_of_line, fileobject)
            main_window.interface_generics_text.insert("1.0", data)
            main_window.interface_generics_text.update_highlight_tags(10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
            main_window.interface_generics_text.update_custom_text_class_generics_list()
        elif line.startswith("interface_ports|"):
            rest_of_line   = remove_keyword_from_line(line,"interface_ports|")
            data           = get_data(rest_of_line, fileobject)
            main_window.interface_ports_text.insert("1.0", data)
            main_window.interface_ports_text.update_highlight_tags(10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
            main_window.interface_ports_text.update_custom_text_class_ports_list()
        elif line.startswith("internals_package|"):
            rest_of_line   = remove_keyword_from_line(line,"internals_package|")
            data           = get_data(rest_of_line, fileobject)
            main_window.internals_package_text.insert("1.0", data)
            main_window.internals_package_text.update_highlight_tags(10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        elif line.startswith("internals_architecture|"):
            rest_of_line   = remove_keyword_from_line(line,"internals_architecture|")
            data           = get_data(rest_of_line, fileobject)
            main_window.internals_architecture_text.insert("1.0", data)
            main_window.internals_architecture_text.update_highlight_tags(10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
            main_window.internals_architecture_text.update_custom_text_class_signals_list()
        elif line.startswith("internals_process|"):
            rest_of_line   = remove_keyword_from_line(line,"internals_process|")
            data           = get_data(rest_of_line, fileobject)
            main_window.internals_process_clocked_text.insert("1.0", data)
            main_window.internals_process_clocked_text.update_highlight_tags(10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
            main_window.internals_process_clocked_text.update_custom_text_class_signals_list()
        elif line.startswith("internals_process_combinatorial|"):
            rest_of_line   = remove_keyword_from_line(line,"internals_process_combinatorial|")
            data           = get_data(rest_of_line, fileobject)
            main_window.internals_process_combinatorial_text.insert("1.0", data)
            main_window.internals_process_combinatorial_text.update_highlight_tags(10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
            main_window.internals_process_combinatorial_text.update_custom_text_class_signals_list()
        elif line.startswith("state_number|"):                                  # The state_number (as transition_number, connector_number, ...) must be restored,
            rest_of_line   = remove_keyword_from_line(line,"state_number|")     # otherwise it could happen, that 2 states get both the tag "state1".
            state_handling.state_number = int(rest_of_line)
        elif line.startswith("transition_number|"):
            rest_of_line   = remove_keyword_from_line(line,"transition_number|")
            transition_handling.transition_number = int(rest_of_line)
        elif line.startswith("reset_entry_number|"):
            rest_of_line   = remove_keyword_from_line(line,"reset_entry_number|")
            reset_entry_handling.reset_entry_number = int(rest_of_line)
            if reset_entry_handling.reset_entry_number==0:
                main_window.reset_entry_button.config(state=tk.NORMAL)
            else:
                main_window.reset_entry_button.config(state=tk.DISABLED)
        elif line.startswith("connector_number|"):
            rest_of_line   = remove_keyword_from_line(line,"connector_number|")
            connector_handling.connector_number = int(rest_of_line)
        elif line.startswith("conditionaction_id|"):
            rest_of_line   = remove_keyword_from_line(line,"conditionaction_id|")
            condition_action_handling.ConditionAction.conditionaction_id = int(rest_of_line)
        elif line.startswith("mytext_id|"):
            rest_of_line   = remove_keyword_from_line(line,"mytext_id|")
            state_action_handling.MyText.mytext_id = int(rest_of_line)
        elif line.startswith("global_actions_number|"):
            rest_of_line   = remove_keyword_from_line(line,"global_actions_number|")
            global_actions_handling.global_actions_clocked_number = int(rest_of_line)
            if global_actions_handling.global_actions_clocked_number==0:
                main_window.global_action_clocked_button.config(state=tk.NORMAL)
            else:
                main_window.global_action_clocked_button.config(state=tk.DISABLED)
        elif line.startswith("state_actions_default_number|"):
            rest_of_line   = remove_keyword_from_line(line,"state_actions_default_number|")
            global_actions_handling.state_actions_default_number = int(rest_of_line)
            if global_actions_handling.state_actions_default_number==0:
                main_window.state_action_default_button.config(state=tk.NORMAL)
            else:
                main_window.state_action_default_button.config(state=tk.DISABLED)
        elif line.startswith("global_actions_combinatorial_number|"):
            rest_of_line   = remove_keyword_from_line(line,"global_actions_combinatorial_number|")
            global_actions_handling.global_actions_combinatorial_number = int(rest_of_line)
            if global_actions_handling.global_actions_combinatorial_number==0:
                main_window.global_action_combinatorial_button.config(state=tk.NORMAL)
            else:
                main_window.global_action_combinatorial_button.config(state=tk.DISABLED)
        elif line.startswith("state_radius|"):
            rest_of_line   = remove_keyword_from_line(line,"state_radius|")
            canvas_editing.state_radius = float(rest_of_line)
        elif line.startswith("reset_entry_size|"):
            rest_of_line   = remove_keyword_from_line(line,"reset_entry_size|")
            canvas_editing.reset_entry_size = int(float(rest_of_line))
        elif line.startswith("priority_distance|"):
            rest_of_line   = remove_keyword_from_line(line,"priority_distance|")
            canvas_editing.priority_distance = int(float(rest_of_line))
        elif line.startswith("fontsize|"):
            rest_of_line   = remove_keyword_from_line(line,"fontsize|")
            fontsize = float(rest_of_line)
            canvas_editing.fontsize = fontsize
            canvas_editing.state_name_font.configure(size=int(fontsize))
        elif line.startswith("label_fontsize|"):
            rest_of_line   = remove_keyword_from_line(line,"label_fontsize|")
            canvas_editing.label_fontsize = float(rest_of_line)
        elif line.startswith("visible_center|"):
            rest_of_line   = remove_keyword_from_line(line,"visible_center|")
            canvas_editing.shift_visible_center_to_window_center(rest_of_line)
        elif line.startswith("state|"):
            rest_of_line   = remove_keyword_from_line(line,"state|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            state_id = main_window.canvas.create_oval(coords, fill=constants.STATE_COLOR, width=2, outline='blue', tags=tags)
            main_window.canvas.tag_bind(state_id,"<Enter>"   , lambda event, id=state_id : main_window.canvas.itemconfig(id, width=4))
            main_window.canvas.tag_bind(state_id,"<Leave>"   , lambda event, id=state_id : main_window.canvas.itemconfig(id, width=2))
            main_window.canvas.tag_bind(state_id,"<Button-3>", lambda event, id=state_id : state_handling.show_menu(event, id))
        elif line.startswith("polygon|"):
            rest_of_line   = remove_keyword_from_line(line,"polygon|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            polygon_id = main_window.canvas.create_polygon(coords, fill='red', outline='orange', tags=tags)
            main_window.canvas.tag_bind(polygon_id,"<Enter>", lambda event, id=polygon_id : main_window.canvas.itemconfig(id, width=2))
            main_window.canvas.tag_bind(polygon_id,"<Leave>", lambda event, id=polygon_id : main_window.canvas.itemconfig(id, width=1))
        elif line.startswith("text|"):
            rest_of_line   = remove_keyword_from_line(line,"text|")
            tags = ()
            entries = rest_of_line.split()
            coords = []
            coords.append(float(entries[0]))
            coords.append(float(entries[1]))
            text      = entries[2]
            for e in entries[3:]:
                tags = tags + (e,)
            text_id  = main_window.canvas.create_text(coords, text=text, tags=tags, font=canvas_editing.state_name_font)
            for t in tags:
                if t.startswith("transition"):
                    main_window.canvas.tag_bind(text_id, "<Double-Button-1>", lambda event, transition_tag=t[:-8]  : transition_handling.edit_priority(event, transition_tag))
                else:
                    main_window.canvas.tag_bind(text_id, "<Double-Button-1>", lambda event, text_id=text_id : state_handling.edit_state_name(event, text_id))
        elif line.startswith("line|"):
            rest_of_line   = remove_keyword_from_line(line,"line|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            trans_id = main_window.canvas.create_line(coords, smooth=True, fill="blue", tags=tags)
            main_window.canvas.tag_lower(trans_id) # Lines are always "under" the priority rectangles.
            main_window.canvas.tag_bind(trans_id, "<Enter>",  lambda event, trans_id=trans_id : main_window.canvas.itemconfig(trans_id, width=3))
            main_window.canvas.tag_bind(trans_id, "<Leave>",  lambda event, trans_id=trans_id : main_window.canvas.itemconfig(trans_id, width=1))
            for t in tags:
                if t.startswith("connected_to_transition"):
                    main_window.canvas.itemconfig(trans_id, dash=(2,2), state=tk.HIDDEN)
                elif t.startswith("connected_to_state"):
                    main_window.canvas.itemconfig(trans_id, dash=(2,2))
                elif t.startswith("transition"):
                    main_window.canvas.itemconfig(trans_id, arrow='last')
                    main_window.canvas.tag_bind(trans_id,"<Button-3>",lambda event, id=trans_id : transition_handling.show_menu(event, id))
        elif line.startswith("rectangle|"): # Used as connector or as priority entry.
            rest_of_line   = remove_keyword_from_line(line,"rectangle|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            rectangle_color = constants.STATE_COLOR
            for t in tags:
                if t.startswith("connector"):
                    rectangle_color = constants.CONNECTOR_COLOR
            canvas_id = main_window.canvas.create_rectangle(coords, tag=tags, fill=rectangle_color)
            main_window.canvas.tag_raise(canvas_id) # priority rectangles are always in "foreground"
        elif line.startswith("window_state_action_block|"):
            rest_of_line = remove_keyword_from_line(line,"window_state_action_block|")
            text         = get_data(rest_of_line, fileobject)
            coords = []
            tags = ()
            last_line = fileobject.readline()
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            action_ref = state_action_handling.MyText(coords[0]-100, coords[1], height=1, width=8, padding=1, increment=False)
            action_ref.text_id.insert("1.0", text)
            action_ref.text_id.format()
            main_window.canvas.itemconfigure(action_ref.window_id,tag=tags)
        elif line.startswith("window_condition_action_block|"):
            rest_of_line = remove_keyword_from_line(line,"window_condition_action_block|")
            condition    = get_data(rest_of_line, fileobject)
            next_line    = fileobject.readline()
            action       = get_data(next_line, fileobject)
            coords = []
            tags = ()
            last_line = fileobject.readline()
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            connected_to_reset_entry = False
            for t in tags:
                if t=="connected_to_reset_transition":
                    connected_to_reset_entry = True
            condition_action_ref = condition_action_handling.ConditionAction(coords[0], coords[1], connected_to_reset_entry, height=1, width=8, padding=1, increment=False)
            condition_action_ref.condition_id.insert("1.0", condition)
            condition_action_ref.condition_id.format()
            condition_action_ref.action_id.insert("1.0", action)
            condition_action_ref.action_id.format()
            if condition_action_ref.condition_id.get("1.0", tk.END)=="\n" and condition_action_ref.action_id.get("1.0", tk.END)!="\n":
                condition_action_ref.condition_label.grid_forget()
                condition_action_ref.condition_id.grid_forget()
            if condition_action_ref.condition_id.get("1.0", tk.END)!="\n" and condition_action_ref.action_id.get("1.0", tk.END)=="\n":
                condition_action_ref.action_label.grid_forget()
                condition_action_ref.action_id.grid_forget()
            main_window.canvas.itemconfigure(condition_action_ref.window_id,tag=tags)
        elif line.startswith("window_global_actions|"):
            rest_of_line = remove_keyword_from_line(line,"window_global_actions|")
            text_before  = get_data(rest_of_line, fileobject)
            next_line    = fileobject.readline()
            text_after   = get_data(next_line, fileobject)
            coords = []
            tags = ()
            last_line = fileobject.readline()
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            global_actions_ref = global_actions.GlobalActions(coords[0], coords[1], height=1, width=8, padding=1)
            global_actions_ref.text_before_id.insert("1.0", text_before)
            global_actions_ref.text_before_id.format()
            global_actions_ref.text_after_id.insert("1.0", text_after)
            global_actions_ref.text_after_id.format()
            main_window.canvas.itemconfigure(global_actions_ref.window_id,tag=tags)
        elif line.startswith("window_global_actions_combinatorial|"):
            rest_of_line = remove_keyword_from_line(line,"window_global_actions_combinatorial|")
            text         = get_data(rest_of_line, fileobject)
            coords = []
            tags = ()
            last_line = fileobject.readline()
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            action_ref = global_actions_combinatorial.GlobalActionsCombinatorial(coords[0], coords[1], height=1, width=8, padding=1)
            action_ref.text_id.insert("1.0", text)
            action_ref.text_id.format()
            main_window.canvas.itemconfigure(action_ref.window_id,tag=tags)
        elif line.startswith("window_state_actions_default|"):
            rest_of_line = remove_keyword_from_line(line,"window_state_actions_default|")
            text         = get_data(rest_of_line, fileobject)
            coords = []
            tags = ()
            last_line = fileobject.readline()
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            action_ref = state_actions_default.StateActionsDefault(coords[0], coords[1], height=1, width=8, padding=1)
            action_ref.text_id.insert("1.0", text)
            action_ref.text_id.format()
            main_window.canvas.itemconfigure(action_ref.window_id,tag=tags)
    fileobject.close()
    undo_handling.stack = []
    undo_handling.stack_write_pointer = 0
    undo_handling.design_has_changed() # Initialize the stack with the read design.
    #main_window.root.update()
    dir_name, file_name = os.path.split(read_filename)
    main_window.root.title(file_name + " (" + dir_name + ")")
    main_window.canvas.after_idle(canvas_editing.view_all)
    #main_window.interface_ports_text.format() # Call format() at this object, as it is for sure existing, and activate in this way the not_read/written highlighting.
    #canvas_editing.priority_distance = 1.5*canvas_editing.state_radius

def remove_old_design():
    global filename
    title = main_window.root.title()
    if title.endswith("*"):
        discard = messagebox.askokcancel("Exit", "There are unsaved changes, do you want to discard them?", default="cancel")
        if discard is False:
            return False
    filename =""
    main_window.root.title("unnamed")
    main_window.module_name.set("")
    main_window.reset_signal_name.set("")
    main_window.clock_signal_name.set("")
    main_window.interface_package_text.delete("1.0", tk.END)
    main_window.interface_generics_text.delete("1.0", tk.END)
    main_window.interface_ports_text.delete("1.0", tk.END)
    main_window.internals_package_text.delete("1.0", tk.END)
    main_window.internals_architecture_text.delete("1.0", tk.END)
    main_window.internals_process_clocked_text.delete("1.0", tk.END)
    main_window.internals_process_combinatorial_text.delete("1.0", tk.END)
    main_window.hdl_frame_text.config(state=tk.NORMAL)
    main_window.hdl_frame_text.delete("1.0", tk.END)
    main_window.hdl_frame_text.config(state=tk.DISABLED)
    main_window.log_frame_text.config(state=tk.NORMAL)
    main_window.log_frame_text.delete("1.0", tk.END)
    main_window.log_frame_text.config(state=tk.DISABLED)
    main_window.canvas.delete("all")
    state_handling.state_number = 0
    transition_handling.transition_number = 0
    reset_entry_handling.reset_entry_number = 0
    main_window.reset_entry_button.config(state=tk.NORMAL)
    connector_handling.connector_number = 0
    condition_action_handling.ConditionAction.conditionaction_id = 0
    condition_action_handling.ConditionAction.dictionary = {}
    state_action_handling.MyText.mytext_id = 0
    state_action_handling.MyText.mytext_dict = {}
    state_actions_default.StateActionsDefault.dictionary = {}
    global_actions_handling.state_actions_default_number = 0
    main_window.state_action_default_button.config(state=tk.NORMAL)
    global_actions_handling.global_actions_clocked_number = 0
    main_window.global_action_clocked_button.config(state=tk.NORMAL)
    global_actions_handling.global_actions_combinatorial_number = 0
    main_window.global_action_combinatorial_button.config(state=tk.NORMAL)
    global_actions_combinatorial.GlobalActionsCombinatorial.dictionary = {}
    global_actions.GlobalActions.dictionary = {}
    canvas_editing.state_radius = 20.0
    canvas_editing.priority_distance = 14
    canvas_editing.reset_entry_size = 40
    canvas_editing.canvas_x_coordinate = 0
    canvas_editing.canvas_y_coordinate = 0
    canvas_editing.fontsize = 10
    canvas_editing.label_fontsize = 8
    canvas_editing.state_name_font.configure(size=int(canvas_editing.fontsize))
    return True

def remove_keyword_from_line(line, keyword):
    return line[len(keyword):]

def get_data(rest_of_line, fileobject):
    length_of_data = get_length_info_from_line(rest_of_line)
    first_data     = remove_length_info(rest_of_line)
    data           = get_remaining_data(fileobject, length_of_data, first_data)
    return data

def get_length_info_from_line(rest_of_line):
    return int(re.sub("\|.*","",rest_of_line))

def remove_length_info(rest_of_line):
    return re.sub(".*\|","", rest_of_line)

def get_remaining_data(fileobject, length_of_data, first_data):
    data = first_data
    while len(data)<length_of_data:
        data = data + fileobject.readline()
    return data[:-1]

def print_canvas():
    #all = main_window.canvas.bbox("all")
    print_filename = main_window.generate_path_value.get() + "/" + main_window.module_name.get() + ".eps"
    #main_window.canvas.postscript(file=filename, colormode="color", x=all[0], y=all[1], width=all[2]-all[0], height=all[3]-all[1])
    main_window.canvas.postscript(file=print_filename, colormode="color")

#########################################################################################################################################

def save_in_file_new(save_filename):
    dir_name, file_name = os.path.split(save_filename)
    main_window.root.title(file_name + " (" + dir_name + ")")
    fileobject = open(save_filename,'w', encoding="utf-8")
    design_dictionary = {}
    design_dictionary["modulename"]                          = main_window.module_name.get()
    design_dictionary["language"]                            = main_window.language.get()
    design_dictionary["generate_path"]                       = main_window.generate_path_value.get()
    design_dictionary["working_directory"]                   = main_window.working_directory_value.get()
    design_dictionary["number_of_files"]                     = main_window.select_file_number_text.get()
    design_dictionary["reset_signal_name"]                   = main_window.reset_signal_name.get()
    design_dictionary["clock_signal_name"]                   = main_window.clock_signal_name.get()
    design_dictionary["compile_cmd"]                         = main_window.compile_cmd.get()
    design_dictionary["edit_cmd"]                            = main_window.edit_cmd.get()
    design_dictionary["diagram_background_color"]            = main_window.diagram_background_color.get()
    design_dictionary["state_number"]                        = state_handling.state_number
    design_dictionary["transition_number"]                   = transition_handling.transition_number
    design_dictionary["reset_entry_number"]                  = reset_entry_handling.reset_entry_number
    design_dictionary["connector_number"]                    = connector_handling.connector_number
    design_dictionary["conditionaction_id"]                  = condition_action_handling.ConditionAction.conditionaction_id
    design_dictionary["mytext_id"]                           = state_action_handling.MyText.mytext_id
    design_dictionary["global_actions_number"]               = global_actions_handling.global_actions_clocked_number
    design_dictionary["state_actions_default_number"]        = global_actions_handling.state_actions_default_number
    design_dictionary["global_actions_combinatorial_number"] = global_actions_handling.global_actions_combinatorial_number
    design_dictionary["state_radius"]                        = canvas_editing.state_radius
    design_dictionary["reset_entry_size"]                    = canvas_editing.reset_entry_size
    design_dictionary["priority_distance"]                   = canvas_editing.priority_distance
    design_dictionary["fontsize"]                            = canvas_editing.fontsize
    design_dictionary["label_fontsize"]                      = canvas_editing.label_fontsize
    design_dictionary["visible_center"]                      = canvas_editing.get_visible_center_as_string()
    design_dictionary["interface_package"]                   = main_window.interface_package_text.get              ("1.0",tk.END + "-1 chars")
    design_dictionary["interface_generics"]                  = main_window.interface_generics_text.get             ("1.0",tk.END + "-1 chars")
    design_dictionary["interface_ports"]                     = main_window.interface_ports_text.get                ("1.0",tk.END + "-1 chars")
    design_dictionary["internals_package"]                   = main_window.internals_package_text.get              ("1.0",tk.END + "-1 chars")
    design_dictionary["internals_architecture"]              = main_window.internals_architecture_text.get         ("1.0",tk.END + "-1 chars")
    design_dictionary["internals_process"]                   = main_window.internals_process_clocked_text.get      ("1.0",tk.END + "-1 chars")
    design_dictionary["internals_process_combinatorial"]     = main_window.internals_process_combinatorial_text.get("1.0",tk.END + "-1 chars")
    design_dictionary["state"]                               = []
    design_dictionary["text"]                                = []
    design_dictionary["line"]                                = []
    design_dictionary["polygon"]                             = []
    design_dictionary["rectangle"]                           = []
    design_dictionary["window_state_action_block"]           = []
    design_dictionary["window_state_comment"]                = []
    design_dictionary["window_condition_action_block"]       = []
    design_dictionary["window_global_actions"]               = []
    design_dictionary["window_global_actions_combinatorial"] = []
    design_dictionary["window_state_actions_default"]        = []
    if main_window.language.get()=="VHDL":
        design_dictionary["regex_message_find"]              = main_window.regex_message_find_for_vhdl
    else:
        design_dictionary["regex_message_find"]              = main_window.regex_message_find_for_verilog
    design_dictionary["regex_file_name_quote"]               = main_window.regex_file_name_quote
    design_dictionary["regex_file_line_number_quote"]        = main_window.regex_file_line_number_quote


    items = main_window.canvas.find_all()
    for i in items:
        if main_window.canvas.type(i)=='oval':
            design_dictionary["state"].append     ([main_window.canvas.coords(i), main_window.canvas.gettags(i), main_window.canvas.itemcget(i, "fill")])
        elif main_window.canvas.type(i)=="text":
            design_dictionary["text"].append      ([main_window.canvas.coords(i), main_window.canvas.gettags(i), main_window.canvas.itemcget(i, "text")])
        elif main_window.canvas.type(i)=="line":
            design_dictionary["line"].append      ([main_window.canvas.coords(i), main_window.canvas.gettags(i)])
        elif main_window.canvas.type(i)=="polygon":
            design_dictionary["polygon"].append   ([main_window.canvas.coords(i), main_window.canvas.gettags(i)])
        elif main_window.canvas.type(i)=="rectangle":
            design_dictionary["rectangle"].append ([main_window.canvas.coords(i), main_window.canvas.gettags(i)])
        elif main_window.canvas.type(i)=="window":
            if i in state_action_handling.MyText.mytext_dict:
                design_dictionary["window_state_action_block"].append       ([main_window.canvas.coords(i),
                                                                            state_action_handling.MyText.mytext_dict[i].text_id.get("1.0", tk.END + "-1 chars"),
                                                                            main_window.canvas.gettags(i)])
            elif i in state_comment.StateComment.dictionary:
                design_dictionary["window_state_comment"].append            ([main_window.canvas.coords(i),
                                                                            state_comment.StateComment.dictionary[i].text_id.get("1.0", tk.END + "-1 chars"),
                                                                            main_window.canvas.gettags(i)])
            elif i in condition_action_handling.ConditionAction.dictionary:
                design_dictionary["window_condition_action_block"].append   ([main_window.canvas.coords(i),
                                                                            condition_action_handling.ConditionAction.dictionary[i].condition_id.get("1.0", tk.END + "-1 chars"),
                                                                            condition_action_handling.ConditionAction.dictionary[i].action_id.get("1.0", tk.END + "-1 chars"),
                                                                            main_window.canvas.gettags(i)])
            elif i in global_actions.GlobalActions.dictionary:
                design_dictionary["window_global_actions"].append           ([main_window.canvas.coords(i),
                                                                            global_actions.GlobalActions.dictionary[i].text_before_id.get("1.0", tk.END + "-1 chars"),
                                                                            global_actions.GlobalActions.dictionary[i].text_after_id.get("1.0", tk.END + "-1 chars"),
                                                                            main_window.canvas.gettags(i)])
            elif i in global_actions_combinatorial.GlobalActionsCombinatorial.dictionary:
                design_dictionary["window_global_actions_combinatorial"].append([main_window.canvas.coords(i),
                                                                            global_actions_combinatorial.GlobalActionsCombinatorial.dictionary[i].text_id.get("1.0",tk.END+"-1 chars"),
                                                                            main_window.canvas.gettags(i)])
            elif i in state_actions_default.StateActionsDefault.dictionary:
                design_dictionary["window_state_actions_default"].append    ([main_window.canvas.coords(i),
                                                                            state_actions_default.StateActionsDefault.dictionary[i].text_id.get("1.0", tk.END + "-1 chars"),
                                                                            main_window.canvas.gettags(i)])
            else:
                print("file_handling: Fatal, unknown dictionary key ", i)
    fileobject.write(json.dumps(design_dictionary, indent=4, default=str))
    fileobject.close()

def open_file_with_name_new(read_filename):
    global filename
    try:
        fileobject = open(read_filename, 'r', encoding="utf-8")
        data = fileobject.read()
        fileobject.close()
        filename = read_filename
        design_dictionary = json.loads(data)
        custom_text.CustomText.read_variables_of_all_windows.clear()
        custom_text.CustomText.written_variables_of_all_windows.clear()
        # Bring the notebook tab with the graphic into the foreground:
        notebook_ids = main_window.notebook.tabs()
        for notebook_id in notebook_ids:
            if main_window.notebook.tab(notebook_id, option="text")=="Diagram":
                main_window.notebook.select(notebook_id)
        # Read the design from the file:
        transition_ids = []
        ids_of_rectangles_to_raise  = []
        priority_ids   = []
        main_window.module_name.set(design_dictionary["modulename"])
        old_language = main_window.language.get()
        main_window.language.set(design_dictionary["language"])
        if design_dictionary["language"]!=old_language:
            main_window.switch_language_mode()
        main_window.generate_path_value.set    (design_dictionary["generate_path"])
        if "working_directory" in design_dictionary:
            main_window.working_directory_value.set(design_dictionary["working_directory"])
        else:
            main_window.working_directory_value.set("")
        main_window.select_file_number_text.set(design_dictionary["number_of_files"])
        main_window.reset_signal_name.set      (design_dictionary["reset_signal_name"])
        main_window.clock_signal_name.set      (design_dictionary["clock_signal_name"])
        main_window.compile_cmd.set            (design_dictionary["compile_cmd"])
        main_window.edit_cmd.set               (design_dictionary["edit_cmd"])
        if "diagram_background_color" in design_dictionary:
            diagram_background_color = design_dictionary["diagram_background_color"]
            main_window.diagram_background_color.set(diagram_background_color)
        else:
            diagram_background_color = "white"
        main_window.canvas.configure(bg=diagram_background_color)
        main_window.interface_package_text.insert              ("1.0", design_dictionary["interface_package"])
        main_window.interface_generics_text.insert             ("1.0", design_dictionary["interface_generics"])
        main_window.interface_ports_text.insert                ("1.0", design_dictionary["interface_ports"])
        main_window.internals_package_text.insert              ("1.0", design_dictionary["internals_package"])
        main_window.internals_architecture_text.insert         ("1.0", design_dictionary["internals_architecture"])
        main_window.internals_process_clocked_text.insert      ("1.0", design_dictionary["internals_process"])
        main_window.internals_process_combinatorial_text.insert("1.0", design_dictionary["internals_process_combinatorial"])
        if "regex_message_find" in design_dictionary:
            if design_dictionary["language"]=="VHDL":
                main_window.regex_message_find_for_vhdl    = design_dictionary["regex_message_find"]
            else:
                main_window.regex_message_find_for_verilog = design_dictionary["regex_message_find"]
            main_window.regex_file_name_quote        = design_dictionary["regex_file_name_quote"]
            main_window.regex_file_line_number_quote = design_dictionary["regex_file_line_number_quote"]
        main_window.interface_package_text.update_highlight_tags              (10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        main_window.interface_generics_text.update_highlight_tags             (10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        main_window.interface_ports_text.update_highlight_tags                (10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        main_window.internals_package_text.update_highlight_tags              (10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        main_window.internals_architecture_text.update_highlight_tags         (10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        main_window.internals_process_clocked_text.update_highlight_tags      (10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        main_window.internals_process_combinatorial_text.update_highlight_tags(10, ["not_read" , "not_written" , "control" , "datatype" , "function" , "comment"])
        main_window.interface_generics_text.update_custom_text_class_generics_list            ()
        main_window.interface_ports_text.update_custom_text_class_ports_list                  ()
        main_window.internals_architecture_text.update_custom_text_class_signals_list         ()
        main_window.internals_process_clocked_text.update_custom_text_class_signals_list      ()
        main_window.internals_process_combinatorial_text.update_custom_text_class_signals_list()
        state_handling.state_number = design_dictionary["state_number"]
        transition_handling.transition_number = design_dictionary["transition_number"]
        reset_entry_handling.reset_entry_number = design_dictionary["reset_entry_number"]
        if reset_entry_handling.reset_entry_number==0:
            main_window.reset_entry_button.config(state=tk.NORMAL)
        else:
            main_window.reset_entry_button.config(state=tk.DISABLED)
        connector_handling.connector_number                          = design_dictionary["connector_number"]
        condition_action_handling.ConditionAction.conditionaction_id = design_dictionary["conditionaction_id"]
        state_action_handling.MyText.mytext_id                       = design_dictionary["mytext_id"]
        global_actions_handling.global_actions_clocked_number        = design_dictionary["global_actions_number"]
        if global_actions_handling.global_actions_clocked_number==0:
            main_window.global_action_clocked_button.config(state=tk.NORMAL)
        else:
            main_window.global_action_clocked_button.config(state=tk.DISABLED)
        global_actions_handling.state_actions_default_number         = design_dictionary["state_actions_default_number"]
        if global_actions_handling.state_actions_default_number==0:
            main_window.state_action_default_button.config(state=tk.NORMAL)
        else:
            main_window.state_action_default_button.config(state=tk.DISABLED)
        global_actions_handling.global_actions_combinatorial_number  = design_dictionary["global_actions_combinatorial_number"]
        if global_actions_handling.global_actions_combinatorial_number==0:
            main_window.global_action_combinatorial_button.config(state=tk.NORMAL)
        else:
            main_window.global_action_combinatorial_button.config(state=tk.DISABLED)
        canvas_editing.state_radius                                  = design_dictionary["state_radius"]
        canvas_editing.reset_entry_size                              = int(design_dictionary["reset_entry_size"]) # stored as float in dictionary
        canvas_editing.priority_distance                             = int(design_dictionary["priority_distance"])# stored as float in dictionary
        canvas_editing.fontsize                                      = design_dictionary["fontsize"]
        canvas_editing.state_name_font.configure(size=int(canvas_editing.fontsize))
        canvas_editing.label_fontsize                                = design_dictionary["label_fontsize"]
        canvas_editing.shift_visible_center_to_window_center(design_dictionary["visible_center"])
        hide_priority_rectangle_list = []
        for definition in design_dictionary["state"]:
            coords = definition[0]
            tags   = definition[1]
            if len(definition)==3:
                fill_color = definition[2]
            else:
                fill_color = constants.STATE_COLOR
            number_of_outgoing_transitions = 0
            for tag in tags:
                if tag.startswith("transition") and tag.endswith("_start"):
                    transition_identifier = tag.replace("_start", "")
                    number_of_outgoing_transitions += 1
            if number_of_outgoing_transitions==1:
                hide_priority_rectangle_list.append(transition_identifier)
            state_id = main_window.canvas.create_oval(coords, fill=fill_color, width=2, outline='blue', tags=tags)
            main_window.canvas.tag_bind(state_id,"<Enter>"   , lambda event, id=state_id : main_window.canvas.itemconfig(id, width=4))
            main_window.canvas.tag_bind(state_id,"<Leave>"   , lambda event, id=state_id : main_window.canvas.itemconfig(id, width=2))
            main_window.canvas.tag_bind(state_id,"<Button-3>", lambda event, id=state_id : state_handling.show_menu(event, id))
        for definition in design_dictionary["polygon"]: # Reset symbol
            coords = definition[0]
            tags   = definition[1]
            polygon_id = main_window.canvas.create_polygon(coords, fill='red', outline='orange', tags=tags)
            main_window.canvas.tag_bind(polygon_id,"<Enter>", lambda event, id=polygon_id : main_window.canvas.itemconfig(id, width=2))
            main_window.canvas.tag_bind(polygon_id,"<Leave>", lambda event, id=polygon_id : main_window.canvas.itemconfig(id, width=1))
            number_of_outgoing_transitions = 0
            for tag in tags:
                if tag.startswith("transition") and tag.endswith("_start"):
                    transition_identifier = tag.replace("_start", "")
                    number_of_outgoing_transitions += 1
            if number_of_outgoing_transitions==1:
                hide_priority_rectangle_list.append(transition_identifier)
        for definition in design_dictionary["text"]:
            coords = definition[0]
            tags   = definition[1]
            text   = definition[2]
            text_id  = main_window.canvas.create_text(coords, text=text, tags=tags, font=canvas_editing.state_name_font)
            for t in tags:
                if t.startswith("transition"):
                    priority_ids.append(text_id)
                    main_window.canvas.tag_bind(text_id, "<Double-Button-1>", lambda event, transition_tag=t[:-8]  : transition_handling.edit_priority(event, transition_tag))
                else:
                    main_window.canvas.tag_bind(text_id, "<Double-Button-1>", lambda event, text_id=text_id : state_handling.edit_state_name(event, text_id))
        for definition in design_dictionary["line"]:
            coords = definition[0]
            tags   = definition[1]
            trans_id = main_window.canvas.create_line(coords, smooth=True, fill="blue", tags=tags)
            main_window.canvas.tag_lower(trans_id) # Lines are always "under" the priority rectangles.
            main_window.canvas.tag_bind(trans_id, "<Enter>",  lambda event, trans_id=trans_id : main_window.canvas.itemconfig(trans_id, width=3))
            main_window.canvas.tag_bind(trans_id, "<Leave>",  lambda event, trans_id=trans_id : main_window.canvas.itemconfig(trans_id, width=1))
            for t in tags:
                if t.startswith("connected_to_transition"):
                    main_window.canvas.itemconfig(trans_id, dash=(2,2), fill="black", state=tk.HIDDEN)
                elif t.startswith("connected_to_state") or t.endswith("_comment_line"):
                    main_window.canvas.itemconfig(trans_id, dash=(2,2), fill="black")
                elif t.startswith("transition"):
                    main_window.canvas.itemconfig(trans_id, arrow='last')
                    main_window.canvas.tag_bind(trans_id,"<Button-3>",lambda event, id=trans_id : transition_handling.show_menu(event, id))
        for definition in design_dictionary["rectangle"]:
            coords = definition[0]
            tags   = definition[1]
            rectangle_color = constants.STATE_COLOR
            for t in tags:
                if t.startswith("connector"):
                    rectangle_color = constants.CONNECTOR_COLOR
            if rectangle_color==constants.CONNECTOR_COLOR:
                number_of_outgoing_transitions = 0
                for tag in tags:
                    if tag.startswith("transition") and tag.endswith("_start"):
                        transition_identifier = tag.replace("_start", "")
                        number_of_outgoing_transitions += 1
                if number_of_outgoing_transitions==1:
                    hide_priority_rectangle_list.append(transition_identifier)
            canvas_id = main_window.canvas.create_rectangle(coords, tag=tags, fill=rectangle_color)
            if rectangle_color==constants.STATE_COLOR: # priority rectangle
                ids_of_rectangles_to_raise.append(canvas_id)
            #main_window.canvas.tag_raise(id) # priority rectangles are always in "foreground"
        for definition in design_dictionary["window_state_action_block"]:
            coords = definition[0]
            text   = definition[1]
            tags   = definition[2]
            action_ref = state_action_handling.MyText(coords[0]-100, coords[1], height=1, width=8, padding=1, increment=False)
            action_ref.text_id.insert("1.0", text)
            action_ref.text_id.format()
            main_window.canvas.itemconfigure(action_ref.window_id,tag=tags)
        if "window_state_comment" in design_dictionary: # HDL-FSM-versions before 4.2 did not support state-comments.
            for definition in design_dictionary["window_state_comment"]:
                coords = definition[0]
                text   = definition[1]
                tags   = definition[2]
                comment_ref = state_comment.StateComment(coords[0]-100, coords[1], height=1, width=8, padding=1)
                comment_ref.text_id.insert("1.0", text)
                comment_ref.text_id.format()
                main_window.canvas.itemconfigure(comment_ref.window_id,tag=tags)
        for definition in design_dictionary["window_condition_action_block"]:
            coords    = definition[0]
            condition = definition[1]
            action    = definition[2]
            tags      = definition[3]
            connected_to_reset_entry = False
            for t in tags:
                if t=="connected_to_reset_transition":
                    connected_to_reset_entry = True
            condition_action_ref = condition_action_handling.ConditionAction(coords[0], coords[1], connected_to_reset_entry, height=1, width=8, padding=1, increment=False)
            condition_action_ref.condition_id.insert("1.0", condition)
            condition_action_ref.condition_id.format()
            condition_action_ref.action_id.insert("1.0", action)
            condition_action_ref.action_id.format()
            if condition_action_ref.condition_id.get("1.0", tk.END)=="\n" and condition_action_ref.action_id.get("1.0", tk.END)!="\n":
                condition_action_ref.condition_label.grid_forget()
                condition_action_ref.condition_id.grid_forget()
            if condition_action_ref.condition_id.get("1.0", tk.END)!="\n" and condition_action_ref.action_id.get("1.0", tk.END)=="\n":
                condition_action_ref.action_label.grid_forget()
                condition_action_ref.action_id.grid_forget()
            main_window.canvas.itemconfigure(condition_action_ref.window_id,tag=tags)
        for definition in design_dictionary["window_global_actions"]:
            coords      = definition[0]
            text_before = definition[1]
            text_after  = definition[2]
            tags        = definition[3]
            global_actions_ref = global_actions.GlobalActions(coords[0], coords[1], height=1, width=8, padding=1)
            global_actions_ref.text_before_id.insert("1.0", text_before)
            global_actions_ref.text_before_id.format()
            global_actions_ref.text_after_id.insert("1.0", text_after)
            global_actions_ref.text_after_id.format()
            main_window.canvas.itemconfigure(global_actions_ref.window_id,tag=tags)
        for definition in design_dictionary["window_global_actions_combinatorial"]:
            coords = definition[0]
            text   = definition[1]
            tags   = definition[2]
            action_ref = global_actions_combinatorial.GlobalActionsCombinatorial(coords[0], coords[1], height=1, width=8, padding=1)
            action_ref.text_id.insert("1.0", text)
            action_ref.text_id.format()
            main_window.canvas.itemconfigure(action_ref.window_id,tag=tags)
        for definition in design_dictionary["window_state_actions_default"]:
            coords = definition[0]
            text   = definition[1]
            tags   = definition[2]
            action_ref = state_actions_default.StateActionsDefault(coords[0], coords[1], height=1, width=8, padding=1)
            action_ref.text_id.insert("1.0", text)
            action_ref.text_id.format()
            main_window.canvas.itemconfigure(action_ref.window_id,tag=tags)
        # Sort the display order for the transition priorities:
        for transition_id in transition_ids:
            main_window.canvas.tag_raise(transition_id)
        for rectangle_id in ids_of_rectangles_to_raise:
            main_window.canvas.tag_raise(rectangle_id)
        for priority_id in priority_ids:
            main_window.canvas.tag_raise(priority_id)
        for transition_identifer in hide_priority_rectangle_list:
            main_window.canvas.itemconfigure(transition_identifer + 'priority' , state=tk.HIDDEN)
            main_window.canvas.itemconfigure(transition_identifer + 'rectangle', state=tk.HIDDEN)
        undo_handling.stack = []
        undo_handling.stack_write_pointer = 0
        undo_handling.design_has_changed() # Initialize the stack with the read design.
        main_window.root.update()
        dir_name, file_name = os.path.split(read_filename)
        main_window.root.title(file_name + " (" + dir_name + ")")
        #canvas_editing.priority_distance = 1.5*canvas_editing.state_radius
        update_hdl_tab.UpdateHdlTab(design_dictionary["language"     ], design_dictionary["number_of_files"], read_filename,
                                    design_dictionary["generate_path"], design_dictionary["modulename"     ])
        main_window.show_tab("Diagram")
        main_window.canvas.after_idle(canvas_editing.view_all)
    except FileNotFoundError:
        messagebox.showerror("Error", "File " + read_filename + " could not be found.")
    except ValueError: # includes JSONDecodeError
        messagebox.showerror("Error", "File \n" + read_filename + "\nhas wrong format.\nProbably a HDL-FSM-Editor file format Version 1.")

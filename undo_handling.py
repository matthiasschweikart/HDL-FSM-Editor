from tkinter import *
import re
import state_handling
import transition_handling
import canvas_editing
import state_action_handling
import state_actions_default
import condition_action_handling
import connector_handling
import reset_entry_handling
import global_actions
import global_actions_combinatorial
import global_actions_handling
import main_window
#import inspect

stack = []
stack_write_pointer = 0

def modify_window_title():
    #print("modify_window_title: caller =", inspect.stack()[1][3])
    title = main_window.root.title()
    if title=="tk":
        main_window.root.title("unnamed")
    elif not title.endswith("*"):
        title += "*"
        main_window.root.title(title)

def design_has_changed():
    #print("design_has_changed: caller =", inspect.stack()[1][3])
    add_changes_to_design_stack()
    modify_window_title()

def undo():
    global stack_write_pointer
    # As <Control-z> is bound with the bind_all-command to the diagram, this binding must be ignored, when
    # the focus is on a customtext-widget: Then a Control-z must change the text and must not change the diagram.
    focus = str(main_window.canvas.focus_get())
    if (not "customtext" in focus and stack_write_pointer>1):
        stack_write_pointer -= 2
        set_diagram_to_version_selected_by_stack_pointer()
        stack_write_pointer += 1
        #print("Undo                       : After undo,    stack_write_pointer =", stack_write_pointer)
        if stack_write_pointer==1:
            title = main_window.root.title()
            if title.endswith("*"):
                main_window.root.title(title[:-1])

def redo():
    global stack_write_pointer
    # As <Control-Z> is bound with the bind_all-command to the diagram, this binding must be ignored, when
    # the focus is on the customtext-widget: Then a Control-Z must change the text and must not change the diagram.
    focus = str(main_window.canvas.focus_get())
    if (not "customtext" in focus and stack_write_pointer<len(stack)):
        set_diagram_to_version_selected_by_stack_pointer()
        stack_write_pointer += 1
        #print("Redo                       : After redo,    stack_write_pointer =", stack_write_pointer)

def add_changes_to_design_stack():
    global stack
    global stack_write_pointer
    remove_stack_entries_from_write_pointer_to_the_end_of_the_stack()
    new_design = get_complete_design_as_text_object()
    stack.append(new_design)
    stack_write_pointer += 1

def remove_stack_entries_from_write_pointer_to_the_end_of_the_stack():
    global stack
    if len(stack)>stack_write_pointer:
        del stack[stack_write_pointer:]

def get_complete_design_as_text_object ():
    design = ""
    design += "modulename|"                          + main_window.module_name.get()                                    + "\n"
    design += "language|"                            + main_window.language.get()                                       + "\n"
    design += "generate_path|"                       + main_window.generate_path_value.get()                            + "\n"
    design += "working_directory|"                   + main_window.working_directory_value.get()                        + "\n"
    design += "number_of_files|"                     + str(main_window.select_file_number_text.get())                   + "\n"
    design += "reset_signal_name|"                   + main_window.reset_signal_name.get()                              + "\n"
    design += "clock_signal_name|"                   + main_window.clock_signal_name.get()                              + "\n"
    design += "state_number|"                        + str(state_handling.state_number)                                 + "\n"
    design += "transition_number|"                   + str(transition_handling.transition_number)                       + "\n"
    design += "connector_number|"                    + str(connector_handling.connector_number)                         + "\n"
    design += "reset_entry_number|"                  + str(reset_entry_handling.reset_entry_number)                     + "\n"
    design += "conditionaction_id|"                  + str(condition_action_handling.ConditionAction.conditionaction_id)+ "\n"
    design += "mytext_id|"                           + str(state_action_handling.MyText.mytext_id)                      + "\n"
    design += "state_actions_default_number|"        + str(global_actions_handling.state_actions_default_number)        + "\n"
    design += "global_actions_number|"               + str(global_actions_handling.global_actions_clocked_number)       + "\n"
    design += "global_actions_combinatorial_number|" + str(global_actions_handling.global_actions_combinatorial_number) + "\n"
    design += "reset_entry_size|"                    + str(canvas_editing.reset_entry_size)                             + "\n"
    design += "state_radius|"                        + str(canvas_editing.state_radius)                                 + "\n"
    design += "priority_distance|"                   + str(canvas_editing.priority_distance)                            + "\n"
    design += "fontsize|"                            + str(canvas_editing.fontsize)                                     + "\n"
    design += "label_fontsize|"                      + str(canvas_editing.label_fontsize)                               + "\n"
    design += "visible_center|"                      + canvas_editing.get_visible_center_as_string()                    + "\n"
    design += "interface_package|"               + str(len(main_window.interface_package_text.get              ("1.0",END))-1) + "|" + main_window.interface_package_text.get              ("1.0",END)
    design += "interface_generics|"              + str(len(main_window.interface_generics_text.get             ("1.0",END))-1) + "|" + main_window.interface_generics_text.get             ("1.0",END)
    design += "interface_ports|"                 + str(len(main_window.interface_ports_text.get                ("1.0",END))-1) + "|" + main_window.interface_ports_text.get                ("1.0",END)
    design += "internals_package|"               + str(len(main_window.internals_package_text.get              ("1.0",END))-1) + "|" + main_window.internals_package_text.get              ("1.0",END)
    design += "internals_architecture|"          + str(len(main_window.internals_architecture_text.get         ("1.0",END))-1) + "|" + main_window.internals_architecture_text.get         ("1.0",END)
    design += "internals_process|"               + str(len(main_window.internals_process_clocked_text.get      ("1.0",END))-1) + "|" + main_window.internals_process_clocked_text.get      ("1.0",END)
    design += "internals_process_combinatorial|" + str(len(main_window.internals_process_combinatorial_text.get("1.0",END))-1) + "|" + main_window.internals_process_combinatorial_text.get("1.0",END)
    items = main_window.canvas.find_all()
    print_tags = False
    for i in items:
        if main_window.canvas.type(i)=='oval':
            design += "state|"
            design += get_coords(i)
            design += get_tags  (i)
            design += "\n"
        elif main_window.canvas.type(i)=="text":
            design += "text|"
            design += get_coords(i)
            design += main_window.canvas.itemcget(i, "text") + " "
            design += get_tags  (i)
            design += "\n"
        elif main_window.canvas.type(i)=="line":
            design += "line|"
            design += get_coords(i)
            design += get_tags  (i)
            design += "\n"
        elif main_window.canvas.type(i)=="polygon":
            design += "polygon|"
            design += get_coords(i)
            design += get_tags  (i)
            design += "\n"
        elif main_window.canvas.type(i)=="rectangle":
            design += "rectangle|"
            design += get_coords(i)
            design += get_tags  (i)
            design += "\n"
        elif main_window.canvas.type(i)=="window":
            if i in state_action_handling.MyText.mytext_dict:
                design += "window_state_action_block|"
                text = state_action_handling.MyText.mytext_dict[i].text_id.get("1.0", END)
                design += str(len(text)) + "|"
                design += text
                design += get_coords(i)
            elif i in condition_action_handling.ConditionAction.dictionary:
                design += "window_condition_action_block|"
                text = condition_action_handling.ConditionAction.dictionary[i].condition_id.get("1.0", END)
                design += str(len(text)) + "|"
                design += text
                text = condition_action_handling.ConditionAction.dictionary[i].action_id.get("1.0", END)
                design += str(len(text)) + "|"
                design += text
                design += get_coords(i)
                print_tags = True
            elif i in global_actions.GlobalActions.dictionary:
                design += "window_global_actions|"
                text_before = global_actions.GlobalActions.dictionary[i].text_before_id.get("1.0", END)
                design += str(len(text_before)) + "|"
                design += text_before
                text_after = global_actions.GlobalActions.dictionary[i].text_after_id.get("1.0", END)
                design += str(len(text_after)) + "|"
                design += text_after
                design += get_coords(i)
            elif i in global_actions_combinatorial.GlobalActionsCombinatorial.dictionary:
                design += "window_global_actions_combinatorial|"
                text = global_actions_combinatorial.GlobalActionsCombinatorial.dictionary[i].text_id.get("1.0", END)
                design += str(len(text)) + "|"
                design += text
                design += get_coords(i)
            elif i in state_actions_default.StateActionsDefault.dictionary:
                design += "window_state_actions_default|"
                text = state_actions_default.StateActionsDefault.dictionary[i].text_id.get("1.0", END)
                design += str(len(text)) + "|"
                design += text
                design += get_coords(i)
            else:
                print("get_complete_design_as_text_object: Fatal, unknown dictionary key ", i, main_window.canvas.type(i))
            design += get_tags(i)
            if print_tags is True:
                print_tags = False
            design += " \n"
    return design
def get_coords(id):
        coords = main_window.canvas.coords(id)
        coords_string = ""
        for c in coords:
            coords_string += str(c) + " "
        return coords_string
def get_tags(id):
        tags = main_window.canvas.gettags(id)
        tags_string = ""
        for t in tags:
            tags_string += str(t) + " "
        #print("get_tags: tags_string =", tags_string)
        return tags_string
line_index = 0
def set_diagram_to_version_selected_by_stack_pointer():
    global line_index
    # Remove the old design:
    state_action_handling.MyText.mytext_dict = {}
    condition_action_handling.ConditionAction.dictionary = {}
    main_window.canvas.delete("all")
    # Bring the notebook tab with the diagram into the foreground:
    notebook_ids = main_window.notebook.tabs()
    for id in notebook_ids:
        if main_window.notebook.tab(id, option="text")=="Graph":
            main_window.notebook.select(id)
    # Read the design from the stack:
    design = stack[stack_write_pointer]
    # Convert the string stored in "design" into a list (bit provide a return at each line end, to have the same format as when reading from a file):
    lines_without_return = design.split("\n")
    lines = []
    for line in lines_without_return:
        lines.append(line + "\n")
    # Build the new design:
    line_index = 0
    while line_index<len(lines):
        if lines[line_index].startswith("state_number|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"state_number|")
            state_handling.state_number = int(rest_of_line)
        elif lines[line_index].startswith("transition_number|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"transition_number|")
            transition_handling.transition_number = int(rest_of_line)
        elif lines[line_index].startswith("reset_entry_number|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"reset_entry_number|")
            reset_entry_handling.reset_entry_number = int(rest_of_line)
            if reset_entry_handling.reset_entry_number==0:
                main_window.reset_entry_button.config(state=NORMAL)
            else:
                main_window.reset_entry_button.config(state=DISABLED)
        elif lines[line_index].startswith("connector_number|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"connector_number|")
            connector_handling.connector_number = int(rest_of_line)
        elif lines[line_index].startswith("conditionaction_id|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"conditionaction_id|")
            condition_action_handling.ConditionAction.conditionaction_id = int(rest_of_line)
        elif lines[line_index].startswith("mytext_id|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"mytext_id|")
            state_action_handling.MyText.mytext_id = int(rest_of_line)
        elif lines[line_index].startswith("state_actions_default_number|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"state_actions_default_number|")
            global_actions_handling.state_actions_default_number = int(rest_of_line)
            if global_actions_handling.state_actions_default_number==0:
                main_window.state_action_default_button.config(state=NORMAL)
            else:
                main_window.state_action_default_button.config(state=DISABLED)
        elif lines[line_index].startswith("global_actions_number|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"global_actions_number|")
            global_actions_handling.global_actions_clocked_number = int(rest_of_line)
            if global_actions_handling.global_actions_clocked_number==0:
                main_window.global_action_clocked_button.config(state=NORMAL)
            else:
                main_window.global_action_clocked_button.config(state=DISABLED)
        elif lines[line_index].startswith("global_actions_combinatorial_number|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"global_actions_combinatorial_number|")
            global_actions_handling.global_actions_combinatorial_number = int(rest_of_line)
            if global_actions_handling.global_actions_combinatorial_number==0:
                main_window.global_action_combinatorial_button.config(state=NORMAL)
            else:
                main_window.global_action_combinatorial_button.config(state=DISABLED)
        elif lines[line_index].startswith("state_radius|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"state_radius|")
            canvas_editing.state_radius = float(rest_of_line)
        elif lines[line_index].startswith("reset_entry_size|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"reset_entry_size|")
            canvas_editing.reset_entry_size = int(float(rest_of_line))
        elif lines[line_index].startswith("priority_distance|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"priority_distance|")
            canvas_editing.priority_distance = int(float(rest_of_line))
        elif lines[line_index].startswith("fontsize|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"fontsize|")
            fontsize = float(rest_of_line)
            canvas_editing.fontsize = fontsize
            canvas_editing.state_name_font.configure(size=int(fontsize))
        elif lines[line_index].startswith("label_fontsize|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"label_fontsize|")
            canvas_editing.label_fontsize = float(rest_of_line)
        elif lines[line_index].startswith("visible_center|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"visible_center|")
            canvas_editing.shift_visible_center_to_window_center(rest_of_line)
        elif lines[line_index].startswith("state|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"state|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            state_id = main_window.canvas.create_oval(coords, fill='cyan', width=2, outline='blue', tags=tags)
            main_window.canvas.tag_bind(state_id,"<Enter>"    , lambda event, id=state_id : main_window.canvas.itemconfig(id, width=4))
            main_window.canvas.tag_bind(state_id,"<Leave>"    , lambda event, id=state_id : main_window.canvas.itemconfig(id, width=2))
            main_window.canvas.tag_bind(state_id,"<Button-3>" , lambda event, id=state_id : state_handling.show_menu(event, id))
        elif lines[line_index].startswith("polygon|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"polygon|")
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
        elif lines[line_index].startswith("text|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"text|")
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
                    main_window.canvas.tag_bind(text_id, "<Double-Button-1>", lambda event, priority_tag=t  : transition_handling.edit_priority(event, priority_tag))
                else:
                    main_window.canvas.tag_bind(text_id, "<Double-Button-1>", lambda event, text_id=text_id : state_handling.edit_state_name(event, text_id))
        elif lines[line_index].startswith("line|"):
            rest_of_line   = remove_keyword_from_line(lines[line_index],"line|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            trans_id = main_window.canvas.create_line(coords, fill="blue", smooth=True, tags=tags)
            main_window.canvas.tag_lower(trans_id) # Lines are always "under" the priority rectangles.
            main_window.canvas.tag_bind(trans_id, "<Enter>",  lambda event, trans_id=trans_id : main_window.canvas.itemconfig(trans_id, width=3))
            main_window.canvas.tag_bind(trans_id, "<Leave>",  lambda event, trans_id=trans_id : main_window.canvas.itemconfig(trans_id, width=1))
            for t in tags:
                if t.startswith("connected_to_transition"):
                    main_window.canvas.itemconfig(trans_id, dash=(2,2), state=HIDDEN)
                elif t.startswith("connected_to_state"):
                    main_window.canvas.itemconfig(trans_id, dash=(2,2))
                elif t.startswith("transition"):
                    main_window.canvas.itemconfig(trans_id, arrow='last')
                    main_window.canvas.tag_bind(trans_id,"<Button-3>",lambda event, id=trans_id : transition_handling.show_menu(event, id))
        elif lines[line_index].startswith("rectangle|"): # Used as connector or as priority entry.
            rest_of_line   = remove_keyword_from_line(lines[line_index],"rectangle|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            rectangle_color = 'cyan'
            for t in tags:
                if t.startswith("connector"):
                    rectangle_color = 'violet'
            id = main_window.canvas.create_rectangle(coords, tag=tags, fill=rectangle_color)
            main_window.canvas.tag_raise(id) # priority rectangles are always in "foreground"
        elif lines[line_index].startswith("window_state_action_block|"): # state_action
            rest_of_line = remove_keyword_from_line(lines[line_index],"window_state_action_block|")
            text         = get_data(rest_of_line, lines)
            coords = []
            tags = ()
            line_index += 1
            last_line = lines[line_index]
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
        elif lines[line_index].startswith("window_condition_action_block|"):
            rest_of_line = remove_keyword_from_line(lines[line_index],"window_condition_action_block|")
            condition    = get_data(rest_of_line, lines)
            line_index += 1
            next_line    = lines[line_index]
            action       = get_data(next_line, lines)
            coords = []
            tags = ()
            line_index += 1
            last_line = lines[line_index]
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
            if condition_action_ref.condition_id.get("1.0", END)=="\n" and condition_action_ref.action_id.get("1.0", END)!="\n":
                condition_action_ref.condition_label.grid_forget()
                condition_action_ref.condition_id.grid_forget()
            if condition_action_ref.condition_id.get("1.0", END)!="\n" and condition_action_ref.action_id.get("1.0", END)=="\n":
                condition_action_ref.action_label.grid_forget()
                condition_action_ref.action_id.grid_forget()
            main_window.canvas.itemconfigure(condition_action_ref.window_id,tag=tags)
        elif lines[line_index].startswith("window_global_actions|"):
            rest_of_line = remove_keyword_from_line(lines[line_index],"window_global_actions|")
            text_before  = get_data(rest_of_line, lines)
            line_index   += 1
            next_line    = lines[line_index]
            text_after   = get_data(next_line, lines)
            coords = []
            tags = ()
            line_index += 1
            last_line = lines[line_index]
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
        elif lines[line_index].startswith("window_global_actions_combinatorial|"):
            rest_of_line = remove_keyword_from_line(lines[line_index],"window_global_actions_combinatorial|")
            text         = get_data(rest_of_line, lines)
            coords = []
            tags = ()
            line_index += 1
            last_line = lines[line_index]
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
        elif lines[line_index].startswith("window_state_actions_default|"):
            rest_of_line = remove_keyword_from_line(lines[line_index],"window_state_actions_default|")
            text         = get_data(rest_of_line, lines)
            coords = []
            tags = ()
            line_index += 1
            last_line = lines[line_index]
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
        line_index += 1

def remove_keyword_from_line(line, keyword):
    return line[len(keyword):]

def get_data(rest_of_line, lines):
    length_of_data = get_length_info_from_line(rest_of_line)
    first_data     = remove_length_info(rest_of_line)
    data           = get_remaining_data(lines, length_of_data, first_data)
    return data
def get_length_info_from_line(rest_of_line):
    return int(re.sub("\|.*","",rest_of_line))

def remove_length_info(rest_of_line):
    return re.sub(".*\|","", rest_of_line)

def get_remaining_data(lines, length_of_data, first_data):
    global line_index
    data = first_data
    while(len(data)<length_of_data):
        line_index += 1
        data = data + lines[line_index]
    return data[:-1]

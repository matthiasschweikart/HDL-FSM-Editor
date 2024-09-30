"""
This module contains all methods to create the main-window of the HDL-FSM-Editor.
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import sys
import argparse
from os.path import exists
import urllib.request
import re


import canvas_modify_bindings
import canvas_editing
import file_handling
import move_handling_initialization
import hdl_generation
import undo_handling
import custom_text
import compile_handling
import constants
import link_dictionary

VERSION = "4.3"
header_string ="HDL-FSM-Editor\nVersion " + VERSION + "\nCreated by Matthias Schweikart\nContact: matthias.schweikart@gmx.de"

state_action_default_button        = None
global_action_clocked_button       = None
global_action_combinatorial_button = None
reset_entry_button                 = None

root = None
notebook = None
module_name = None
language = None
generate_path_value = None
working_directory_value = None
select_file_number_text = None
reset_signal_name = None
clock_signal_name = None
compile_cmd = None
edit_cmd = None
interface_package_text = None
interface_generics_text = None
interface_ports_text = None
internals_package_text = None
internals_architecture_text = None
internals_process_clocked_text = None
internals_process_combinatorial_text = None
canvas = None
hdl_frame_text = None
log_frame_text = None

select_file_number_label = None
select_file_number_frame = None
interface_package_label = None
interface_package_scroll = None
interface_generics_label = None
interface_ports_label = None
internals_package_label = None
internals_package_scroll = None
internals_architecture_label = None
internals_process_clocked_label = None
internals_process_combinatorial_label = None
compile_cmd_docu = None
debug_active = None
regex_dialog = None
regex_message_find_for_vhdl      = "(.*?):([0-9]+):[0-9]+:.*"
regex_message_find_for_verilog   = "(.*?):([0-9]+):.*"
regex_file_name_quote        = "\\1"
regex_file_line_number_quote = "\\2"
regex_dialog_entry = None
regex_dialog_filename_entry = None
regex_dialog_linenumber_entry = None
regex_error_happened = False
line_number_under_pointer_log_tab = 0
line_number_under_pointer_hdl_tab = 0
func_id_jump1 = None
func_id_jump2 = None
size_of_file1_line_number = 0
size_of_file2_line_number = 0
func_id_jump = None
module_name_entry = None
clock_signal_name_entry = None

keyword_color = {"not_read": "red", "not_written": "red", "control": "green4", "datatype": "brown", "function": "violet", "comment": "blue"}
keywords = constants.vhdl_keywords

def read_message():
    try:
        source  = urllib.request.urlopen("http://www.hdl-fsm-editor.de/message.txt")
        message = source.read()
        print(message.decode())
    except urllib.error.URLError:
        print("No message was found.")
    except ConnectionRefusedError:
        pass

def check_version():
    try:
        print("Checking for a newer version ...")
        source = urllib.request.urlopen("http://www.hdl-fsm-editor.de/index.php")
        website_source = str(source.read())
        version_start = website_source.find("Version")
        new_version = website_source[version_start:version_start+24]
        end_index   = new_version.find("(")
        new_version = new_version[:end_index]
        new_version = re.sub(" ", "", new_version)
        if new_version!="Version" + VERSION:
            print("Please update to the new version of HDL-FSM-Editor available at http://www.hdl-fsm-editor.de")
        else:
            print("Your version of HDL-FSM-Editor is up to date.")
    except urllib.error.URLError:
        print("HDL-FSM-Editor version could not be checked, as you are offline.")

def evaluate_commandline_parameters():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("filename", nargs='?')
    argument_parser.add_argument("-no_version_check", action="store_true", help="HDL-FSM-Editor will not check for a newer version at start.")
    argument_parser.add_argument("-no_message"      , action="store_true", help="HDL-FSM-Editor will not check for a message at start.")
    argument_parser.add_argument("-generate_hdl"    , action="store_true", help="HDL-FSM-Editor will generate HDL and exit.")
    args = argument_parser.parse_args()
    if not args.no_version_check:
        check_version()
    if not args.no_message:
        read_message()
    if args.filename is not None:
        if not exists(args.filename):
            messagebox.showerror("Error in HDL-SCHEM-Editor", "File " + args.filename + " was not found.")
        else:
            file_handling.filename = args.filename
            file_handling.open_file_with_name_new(args.filename)
            if args.generate_hdl:
                hdl_generation.run_hdl_generation(write_to_file=True)
                sys.exit()
    root.wm_deiconify()
    return

def close_tool():
    title = root.title()
    if title.endswith("*"):
        discard = messagebox.askokcancel("Exit", "There are unsaved changes, do you want to discard them?", default="cancel")
        if discard is True:
            sys.exit()
    else:
        sys.exit()

def create_root():
    global root
    # The top window:
    root = tk.Tk()
    root.withdraw() # Because it could be batch-mode because of "-generate_hdl" switch.
    # Configure the grid field where the notebook will be placed in, so that the notebook is resized at window resize:
    root.columnconfigure(0, weight=1)
    root.rowconfigure   (1, weight=1)
    root.grid()
    link_dictionary.LinkDictionary(root)

def create_menu_bar():
    menue_frame = ttk.Frame(root, borderwidth=2, relief=tk.RAISED)
    menue_frame.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

    file_menu_button = ttk.Menubutton(menue_frame, text="File", style="Window.TMenubutton")
    file_menu = tk.Menu(file_menu_button)
    file_menu_button.configure(menu=file_menu)
    file_menu.add_command(label="New",      accelerator="Ctrl+n", command=file_handling.remove_old_design  , font=("Arial", 10))
    file_menu.add_command(label="Open ...", accelerator="Ctrl+o", command=file_handling.open_file          , font=("Arial", 10))
    file_menu.add_command(label="Open Version 1 file ...",        command=file_handling.open_file_old      , font=("Arial", 10))
    file_menu.add_command(label="Save",     accelerator="Ctrl+s", command=file_handling.save               , font=("Arial", 10))
    file_menu.add_command(label="Save as ...",                    command=file_handling.save_as            , font=("Arial", 10))
    #ile_menu.add_command(label="Print",                          command=file_handling.print_canvas       , font=("Arial", 10))
    file_menu.add_command(label="Exit",                           command=sys.exit                         , font=("Arial", 10))

    hdl_menu_button = ttk.Menubutton(menue_frame, text="HDL", style="Window.TMenubutton")
    hdl_menu = tk.Menu(hdl_menu_button)
    hdl_menu_button.configure(menu=hdl_menu)
    hdl_menu.add_command(label="Generate", accelerator="Ctrl+g", command=lambda: hdl_generation.run_hdl_generation(write_to_file=True), font=("Arial", 10))
    hdl_menu.add_command(label="Compile" , accelerator="Ctrl+p", command=compile_handling.compile         , font=("Arial", 10))

    search_frame = ttk.Frame(menue_frame, borderwidth=2)#, relief=RAISED)
    search_string = tk.StringVar()
    search_string.set("")
    search_button       = ttk.Button(search_frame, text="Find",  command=lambda : canvas_editing.find(search_string), style='Find.TButton')
    search_string_entry = ttk.Entry (search_frame, width=23, textvariable=search_string)
    search_string_entry.bind('<Return>', lambda event : canvas_editing.find(search_string))
    search_button.bind      ('<Return>', lambda event : canvas_editing.find(search_string))
    search_string_entry.grid (row=0, column=0)
    search_button.grid       (row=0, column=1)

    info_menu_button = ttk.Menubutton(menue_frame, text="Info", style="Window.TMenubutton")
    info_menu = tk.Menu(info_menu_button)
    info_menu_button.configure(menu=info_menu)
    info_menu.add_command(label="About", command=lambda : messagebox.showinfo("About:", header_string), font=("Arial", 10))

    notebook.bind("<<NotebookTabChanged>>", lambda event : enable_undo_redo_if_diagram_tab_is_active_else_disable())

    file_menu_button.grid    (row=0, column=0)
    hdl_menu_button.grid     (row=0, column=1)
    search_frame.grid        (row=0, column=2)
    info_menu_button.grid    (row=0, column=3, sticky=tk.E)
    menue_frame.columnconfigure(2, weight=1)
    menue_frame.columnconfigure(3, weight=1)

    # Bindings of the menus:
    root.bind_all("<Control-o>", lambda event : file_handling.open_file())
    root.bind_all("<Control-s>", lambda event : file_handling.save())
    root.bind_all("<Control-g>", lambda event : hdl_generation.run_hdl_generation(write_to_file=True))
    root.bind_all("<Control-n>", lambda event : file_handling.remove_old_design())
    root.bind_all("<Control-p>", lambda event : compile_handling.compile())
    root.bind_all('<Control-f>', lambda event : search_string_entry.focus_set())

def create_notebook():
    global notebook
    notebook = ttk.Notebook(root, padding=5)
    notebook.grid(column=0, row=1, sticky=(tk.N,tk.W,tk.E,tk.S))

def create_control_notebook_tab():
    global module_name, language, generate_path_value, working_directory_value, select_file_number_text, reset_signal_name, clock_signal_name, compile_cmd
    global select_file_number_label, select_file_number_frame, compile_cmd_docu, edit_cmd, module_name_entry, clock_signal_name_entry

    control_frame = ttk.Frame(notebook, takefocus=False)
    control_frame.grid()

    module_name = tk.StringVar()
    module_name.set("")
    module_name_label  = ttk.Label (control_frame, text="Module-Name:", padding=5)
    module_name_entry  = ttk.Entry (control_frame, width=23, textvariable=module_name)
    module_name_label.grid (row=0, column=0, sticky=tk.W)
    module_name_entry.grid (row=0, column=1, sticky=tk.W)
    module_name_entry.select_clear()

    language = tk.StringVar()
    language.set("VHDL")
    language_label    = ttk.Label   (control_frame, text="Language:", padding=5)
    language_combobox = ttk.Combobox(control_frame, textvariable=language, values=("VHDL", "Verilog", "SystemVerilog"), state="readonly")
    language_combobox.bind("<<ComboboxSelected>>", lambda event : switch_language_mode())
    language_label.grid   (row=1, column=0, sticky=tk.W)
    language_combobox.grid(row=1, column=1, sticky=tk.W)

    generate_path_value = tk.StringVar(value="")
    generate_path_value.trace('w', show_path_has_changed)
    generate_path_label  = ttk.Label (control_frame, text="Path for generated HDL:", padding=5)
    generate_path_entry  = ttk.Entry (control_frame, textvariable=generate_path_value, width=80)
    generate_path_button = ttk.Button(control_frame, text="Select...",  command=set_path, style='Path.TButton')
    generate_path_label.grid (row=2, column=0, sticky=tk.W)
    generate_path_entry.grid (row=2, column=1, sticky=(tk.W,tk.E))
    generate_path_button.grid(row=2, column=2, sticky=(tk.W,tk.E))
    control_frame.columnconfigure((2,0), weight=0)
    control_frame.columnconfigure((2,1), weight=1)
    control_frame.columnconfigure((2,2), weight=0)

    select_file_number_text = tk.IntVar()
    select_file_number_text.set(2)
    select_file_number_label = ttk.Label(control_frame, text="Select for generation:", padding=5)
    select_file_number_frame = ttk.Frame(control_frame)
    select_file_number_radio_button1 = ttk.Radiobutton(select_file_number_frame, takefocus=False, variable=select_file_number_text, text="1 file" , value=1)
    select_file_number_radio_button2 = ttk.Radiobutton(select_file_number_frame, takefocus=False, variable=select_file_number_text, text="2 files", value=2)
    select_file_number_label.grid        (row=3, column=0, sticky=tk.W)
    select_file_number_frame.grid        (row=3, column=1, sticky=tk.W)
    select_file_number_radio_button1.grid(row=0, column=1, sticky=tk.W)
    select_file_number_radio_button2.grid(row=0, column=2, sticky=tk.W)

    reset_signal_name = tk.StringVar()
    reset_signal_name.set("")
    reset_signal_name_label  = ttk.Label (control_frame, text="Name of asynchronous reset input port:", padding=5)
    reset_signal_name_entry  = ttk.Entry (control_frame, width=23, textvariable=reset_signal_name)
    reset_signal_name_entry.bind ("<Key>", lambda event : undo_handling.modify_window_title())
    reset_signal_name_label.grid (row=4, column=0, sticky=tk.W)
    reset_signal_name_entry.grid (row=4, column=1, sticky=tk.W)

    clock_signal_name = tk.StringVar()
    clock_signal_name.set("")
    clock_signal_name_label  = ttk.Label (control_frame, text="Name of clock input port:", padding=5)
    clock_signal_name_entry  = ttk.Entry (control_frame, width=23, textvariable=clock_signal_name)
    clock_signal_name_entry.bind ("<Key>", lambda event : undo_handling.modify_window_title())
    clock_signal_name_label.grid (row=5, column=0, sticky=tk.W)
    clock_signal_name_entry.grid (row=5, column=1, sticky=tk.W)

    compile_cmd = tk.StringVar()
    compile_cmd.set("ghdl -a $file1 $file2; ghdl -e $name; ghdl -r $name")
    compile_cmd_label  = ttk.Label (control_frame, text="Compile command:", padding=5)
    compile_cmd_entry  = ttk.Entry (control_frame, width=23, textvariable=compile_cmd)
    compile_cmd_label.grid (row=6, column=0, sticky=tk.W)
    compile_cmd_entry.grid (row=6, column=1, sticky=(tk.W,tk.E))
    control_frame.columnconfigure((6,0), weight=0)
    control_frame.columnconfigure((6,1), weight=1)

    compile_cmd_docu  = ttk.Label (control_frame,
                        text="Variables for compile command:\n$file1\t= Entity-File\n$file2\t= Architecture-File\n$file\t= File with Entity and Architecture\n$name\t= Module Name",
                        padding=5)
    compile_cmd_docu.grid (row=7, column=1, sticky=tk.W)
    control_frame.columnconfigure((7,0), weight=0)
    control_frame.columnconfigure((7,1), weight=1)

    edit_cmd = tk.StringVar()
    edit_cmd.set("C:/Program Files/Notepad++/notepad++.exe -nosession -multiInst")
    edit_cmd_label  = ttk.Label (control_frame, text="Edit command (executed by Ctrl+e):", padding=5)
    edit_cmd_entry  = ttk.Entry (control_frame, width=23, textvariable=edit_cmd)
    edit_cmd_label.grid (row=8, column=0, sticky=tk.W)
    edit_cmd_entry.grid (row=8, column=1, sticky=(tk.W,tk.E))
    control_frame.columnconfigure((8,0), weight=0)
    control_frame.columnconfigure((8,1), weight=1)

    working_directory_value = tk.StringVar(value="")
    working_directory_value.trace('w', show_path_has_changed)
    working_directory_label  = ttk.Label (control_frame, text="Working directory:", padding=5)
    working_directory_entry  = ttk.Entry (control_frame, textvariable=working_directory_value, width=80)
    working_directory_button = ttk.Button(control_frame, text="Select...",  command=set_working_directory, style='Path.TButton')
    working_directory_label.grid (row=9, column=0, sticky=tk.W)
    working_directory_entry.grid (row=9, column=1, sticky=(tk.W,tk.E))
    working_directory_button.grid(row=9, column=2, sticky=(tk.W,tk.E))
    control_frame.columnconfigure((9,0), weight=0)
    control_frame.columnconfigure((9,1), weight=1)
    control_frame.columnconfigure((9,2), weight=0)

    notebook.add(control_frame, sticky=tk.N+tk.E+tk.W+tk.S, text="Control")

def set_path():
    path = askdirectory()
    if path!="" and not path.isspace():
        generate_path_value.set(path)

def set_working_directory():
    path = askdirectory()
    if path!="" and not path.isspace():
        working_directory_value.set(path)

def create_interface_notebook_tab():
    global interface_package_text, interface_generics_text, interface_ports_text
    global interface_package_label, interface_package_scroll
    global interface_generics_label, interface_ports_label

    interface_frame = ttk.Frame(notebook)
    interface_frame.grid()
    interface_frame.columnconfigure(0, weight=1)
    interface_frame.rowconfigure   (0, weight=0)
    interface_frame.rowconfigure   (1, weight=1)
    interface_frame.rowconfigure   (2, weight=0)
    interface_frame.rowconfigure   (3, weight=1)
    interface_frame.rowconfigure   (4, weight=0)
    interface_frame.rowconfigure   (5, weight=10)

    interface_package_label  = ttk.Label             (interface_frame, text="Packages:", padding=5)
    interface_package_text   = custom_text.CustomText(interface_frame, type="package", height=3, width=10, undo=True, font=("Courier", 10))
    interface_package_text.bind ("<Control-Z>"     , lambda event : interface_package_text.edit_redo())
    interface_package_text.bind ("<<TextModified>>", lambda event : undo_handling.modify_window_title())
    interface_package_text.bind ("<Key>"           , lambda event, id=interface_package_text : handle_key(event, id))
    interface_package_scroll = ttk.Scrollbar         (interface_frame, orient=tk.VERTICAL, cursor='arrow', command=interface_package_text.yview)
    interface_package_text.config(yscrollcommand=interface_package_scroll.set)

    interface_generics_label = ttk.Label             (interface_frame, text="Generics:", padding=5)
    interface_generics_text  = custom_text.CustomText(interface_frame, type="generics", height=3, width=10, undo=True, font=("Courier", 10))
    interface_generics_text.bind("<Control-Z>"      , lambda event : interface_generics_text.edit_redo())
    interface_generics_text.bind("<<TextModified>>" , lambda event : undo_handling.modify_window_title())
    interface_generics_text.bind("<Key>"            , lambda event, id=interface_generics_text : handle_key_at_generics(id))
    interface_generics_scroll= ttk.Scrollbar         (interface_frame, orient=tk.VERTICAL, cursor='arrow', command=interface_generics_text.yview)
    interface_generics_text.config(yscrollcommand=interface_generics_scroll.set)

    interface_ports_label    = ttk.Label             (interface_frame, text="Ports:"   , padding=5)
    interface_ports_text     = custom_text.CustomText(interface_frame, type="ports", height=3, width=10, undo=True, font=("Courier", 10))
    interface_ports_text.bind   ("<Control-z>"      , lambda event : interface_ports_text.undo())
    interface_ports_text.bind   ("<Control-Z>"      , lambda event : interface_ports_text.redo())
    interface_ports_text.bind   ("<<TextModified>>" , lambda event : undo_handling.modify_window_title())
    interface_ports_text.bind   ("<Key>"            , lambda event, id=interface_ports_text : handle_key_at_ports(id))
    interface_ports_scroll   = ttk.Scrollbar         (interface_frame, orient=tk.VERTICAL, cursor='arrow', command=interface_ports_text.yview)
    interface_ports_text.config(yscrollcommand=interface_ports_scroll.set)

    interface_package_label.grid  (row=0, column=0, sticky=tk.W) # "W" nötig, damit Text links bleibt
    interface_package_text.grid   (row=1, column=0, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
    interface_package_scroll.grid (row=1, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
    interface_generics_label.grid (row=2, column=0, sticky=tk.W)
    interface_generics_text.grid  (row=3, column=0, sticky=(tk.N,tk.W,tk.E,tk.S))
    interface_generics_scroll.grid(row=3, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
    interface_ports_label.grid    (row=4, column=0, sticky=tk.W)
    interface_ports_text.grid     (row=5, column=0, sticky=(tk.N,tk.W,tk.E,tk.S))
    interface_ports_scroll.grid   (row=5, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird

    notebook.add(interface_frame, sticky=tk.N+tk.E+tk.W+tk.S, text="Interface")

def create_internals_notebook_tab():
    global internals_package_text, internals_architecture_text, internals_process_clocked_text, internals_process_combinatorial_text
    global internals_package_label, internals_package_scroll
    global internals_architecture_label, internals_process_clocked_label, internals_process_combinatorial_label
    internals_frame = ttk.Frame(notebook)
    internals_frame.grid()
    internals_frame.columnconfigure(0, weight=1)
    internals_frame.rowconfigure   (0, weight=0)
    internals_frame.rowconfigure   (1, weight=1)
    internals_frame.rowconfigure   (2, weight=0)
    internals_frame.rowconfigure   (3, weight=10)
    internals_frame.rowconfigure   (4, weight=0)
    internals_frame.rowconfigure   (5, weight=1)
    internals_frame.rowconfigure   (6, weight=0)
    internals_frame.rowconfigure   (7, weight=1)

    internals_package_label     = ttk.Label             (internals_frame, text="Packages:", padding=5)
    internals_package_text      = custom_text.CustomText(internals_frame, type="package", height=3, width=10, undo=True, font=("Courier", 10))
    internals_package_text.bind("<Control-Z>"     , lambda event : internals_package_text.edit_redo())
    internals_package_text.bind("<<TextModified>>", lambda event : undo_handling.modify_window_title())
    internals_package_text.bind("<Key>"           , lambda event, id=internals_package_text : handle_key(event, id))
    internals_package_scroll    = ttk.Scrollbar         (internals_frame, orient=tk.VERTICAL, cursor='arrow', command=internals_package_text.yview)
    internals_package_text.config(yscrollcommand=internals_package_scroll.set)

    internals_architecture_label = ttk.Label             (internals_frame, text="Architecture Declarations:", padding=5)
    internals_architecture_text  = custom_text.CustomText(internals_frame, type="declarations", height=3, width=10, undo=True, font=("Courier", 10))
    internals_architecture_text.bind("<Control-z>"     , lambda event : internals_architecture_text.undo())
    internals_architecture_text.bind("<Control-Z>"     , lambda event : internals_architecture_text.redo())
    internals_architecture_text.bind("<<TextModified>>", lambda event : undo_handling.modify_window_title())
    internals_architecture_text.bind("<Key>"           , lambda event, id=internals_architecture_text : handle_key_at_declarations(id))
    internals_architecture_scroll= ttk.Scrollbar         (internals_frame, orient=tk.VERTICAL, cursor='arrow', command=internals_architecture_text.yview)
    internals_architecture_text.config(yscrollcommand=internals_architecture_scroll.set)

    internals_process_clocked_label      = ttk.Label             (internals_frame, text="Variable Declarations for clocked process:"   , padding=5)
    internals_process_clocked_text       = custom_text.CustomText(internals_frame, type="variable", height=3, width=10, undo=True, font=("Courier", 10))
    internals_process_clocked_text.bind("<Control-z>"     , lambda event : internals_process_clocked_text.undo())
    internals_process_clocked_text.bind("<Control-Z>"     , lambda event : internals_process_clocked_text.redo())
    internals_process_clocked_text.bind("<<TextModified>>", lambda event : undo_handling.modify_window_title())
    internals_process_clocked_text.bind("<Key>"           , lambda event, id=internals_process_clocked_text : handle_key_at_declarations(id))
    internals_process_clocked_scroll     = ttk.Scrollbar         (internals_frame, orient=tk.VERTICAL, cursor='arrow', command=internals_process_clocked_text.yview)
    internals_process_clocked_text.config(yscrollcommand=internals_process_clocked_scroll.set)

    internals_process_combinatorial_label      = ttk.Label             (internals_frame, text="Variable Declarations for combinatorial process:"   , padding=5)
    internals_process_combinatorial_text       = custom_text.CustomText(internals_frame, type="variable", height=3, width=10, undo=True, font=("Courier", 10))
    internals_process_combinatorial_text.bind("<Control-z>"     , lambda event : internals_process_combinatorial_text.undo())
    internals_process_combinatorial_text.bind("<Control-Z>"     , lambda event : internals_process_combinatorial_text.redo())
    internals_process_combinatorial_text.bind("<<TextModified>>", lambda event : undo_handling.modify_window_title())
    internals_process_combinatorial_text.bind("<Key>"           , lambda event, id=internals_process_combinatorial_text : handle_key_at_declarations(id))
    internals_process_combinatorial_scroll     = ttk.Scrollbar         (internals_frame, orient=tk.VERTICAL, cursor='arrow', command=internals_process_combinatorial_text.yview)
    internals_process_combinatorial_text.config(yscrollcommand=internals_process_combinatorial_scroll.set)

    internals_package_label.grid               (row=0, column=0, sticky=tk.W) # "W" nötig, damit Text links bleibt
    internals_package_text.grid                (row=1, column=0, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
    internals_package_scroll.grid              (row=1, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
    internals_architecture_label.grid          (row=2, column=0, sticky=tk.W)
    internals_architecture_text.grid           (row=3, column=0, sticky=(tk.N,tk.W,tk.E,tk.S))
    internals_architecture_scroll.grid         (row=3, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
    internals_process_clocked_label.grid       (row=4, column=0, sticky=tk.W)
    internals_process_clocked_text.grid        (row=5, column=0, sticky=(tk.N,tk.W,tk.E,tk.S))
    internals_process_clocked_scroll.grid      (row=5, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
    internals_process_combinatorial_label.grid (row=6, column=0, sticky=tk.W)
    internals_process_combinatorial_text.grid  (row=7, column=0, sticky=(tk.N,tk.W,tk.E,tk.S))
    internals_process_combinatorial_scroll.grid(row=7, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird

    notebook.add(internals_frame, sticky=tk.N+tk.E+tk.W+tk.S, text="Internals")

def create_diagram_notebook_tab():
    global canvas
    global state_action_default_button
    global global_action_clocked_button
    global global_action_combinatorial_button
    global reset_entry_button

    diagram_frame = ttk.Frame(notebook, borderwidth=0, relief='flat')
    diagram_frame.grid()
    diagram_frame.columnconfigure(0, weight=1) # tkinter method (grid_columnconfigure is tcl method)
    diagram_frame.rowconfigure   (0, weight=1)
    notebook.add(diagram_frame, sticky=tk.N+tk.E+tk.W+tk.S, text="Diagram")

    # Create the elements of the drawing area:
    h = ttk.Scrollbar(diagram_frame, orient=tk.HORIZONTAL, cursor='arrow', style='Horizontal.TScrollbar')
    v = ttk.Scrollbar(diagram_frame, orient=tk.VERTICAL  , cursor='arrow')
    canvas = tk.Canvas(diagram_frame, borderwidth=0, scrollregion=(-100000, -100000, 100000, 100000), xscrollcommand=h.set, yscrollcommand=v.set, highlightthickness=0)
    h['command'] = canvas.xview
    v['command'] = canvas.yview
    button_frame = ttk.Frame(diagram_frame, padding="3 3 3 3", borderwidth=1)

    # Layout of the drawing area:
    canvas.grid      (column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
    h.grid           (column=0, row=1, sticky=(tk.W,tk.E))     # The sticky argument extends the scrollbar, so that a "shift" is possible.
    v.grid           (column=1, row=0, sticky=(tk.N,tk.S))     # The sticky argument extends the scrollbar, so that a "shift" is possible.
    button_frame.grid(column=0, row=2, sticky=(tk.S,tk.W,tk.E))

    # Implement the buttons of the drawing area:
    undo_redo_frame = ttk.Frame(button_frame, borderwidth=2)
    undo_button = ttk.Button(undo_redo_frame, text="Undo (Ctrl-z)",  command=undo_handling.undo, style='Undo.TButton')
    redo_button = ttk.Button(undo_redo_frame, text="Redo(Ctrl-Z)" ,  command=undo_handling.redo, style='Redo.TButton')
    undo_button.grid(row=0, column=0)
    redo_button.grid(row=0, column=1)

    action_frame = ttk.Frame(button_frame, borderwidth=2)
    state_action_default_button        = ttk.Button(action_frame, text='Default State Actions (combinatorial)' , style='DefaultStateActions.TButton')
    global_action_clocked_button       = ttk.Button(action_frame, text='Global Actions (clocked)'              , style='GlobalActionsClocked.TButton')
    global_action_combinatorial_button = ttk.Button(action_frame, text='Global Actions (combinatorial)'        , style='GlobalActionsCombinatorial.TButton')
    state_action_default_button.grid       (row=0, column=0)
    global_action_clocked_button.grid      (row=0, column=1)
    global_action_combinatorial_button.grid(row=0, column=2)

    new_transition_button              = ttk.Button(button_frame,text='new Transition'                        , style='NewTransition.TButton')
    new_state_button                   = ttk.Button(button_frame,text='new State'                             , style="NewState.TButton")
    new_connector_button               = ttk.Button(button_frame,text='new Connector'                         , style="NewConnector.TButton")
    reset_entry_button                 = ttk.Button(button_frame,text='Reset Entry'                           , style='ResetEntry.TButton')
    view_all_button                    = ttk.Button(button_frame,text='view all'                              , style='View.TButton')
    view_area_button                   = ttk.Button(button_frame,text='view area'                             , style='View.TButton')
    plus_button                        = ttk.Button(button_frame,text='+'                                     , style='View.TButton')
    minus_button                       = ttk.Button(button_frame,text='-'                                     , style='View.TButton')

    # Layout of the button area:
    new_state_button.grid                  (row=0, column=0)
    new_transition_button.grid             (row=0, column=1)
    new_connector_button.grid              (row=0, column=2)
    reset_entry_button.grid                (row=0, column=3)
    action_frame.grid                      (row=0, column=4)
    undo_redo_frame.grid                   (row=0, column=5)
    view_all_button.grid                   (row=0, column=6, sticky=tk.E)
    view_area_button.grid                  (row=0, column=7)
    plus_button.grid                       (row=0, column=8)
    minus_button.grid                      (row=0, column=9)
    button_frame.columnconfigure(4, weight=1)
    button_frame.columnconfigure(5, weight=1)

    # Bindings of the drawing area:
    root.bind_all                          ('<Escape>'  , lambda event: canvas_modify_bindings.switch_to_move_mode())
    new_state_button.bind                  ('<Button-1>', lambda event: canvas_modify_bindings.switch_to_state_insertion())
    new_transition_button.bind             ('<Button-1>', lambda event: canvas_modify_bindings.switch_to_transition_insertion())
    new_connector_button.bind              ('<Button-1>', lambda event: canvas_modify_bindings.switch_to_connector_insertion())
    reset_entry_button.bind                ('<Button-1>', lambda event: canvas_modify_bindings.switch_to_reset_entry_insertion())
    state_action_default_button.bind       ('<Button-1>', lambda event: canvas_modify_bindings.switch_to_state_action_default_insertion())
    global_action_clocked_button.bind      ('<Button-1>', lambda event: canvas_modify_bindings.switch_to_global_action_clocked_insertion())
    global_action_combinatorial_button.bind('<Button-1>', lambda event: canvas_modify_bindings.switch_to_global_action_combinatorial_insertion())
    view_area_button.bind                  ('<Button-1>', lambda event: canvas_modify_bindings.switch_to_view_area())
    view_all_button.bind                   ('<Button-1>', lambda event: canvas_editing.view_all())
    plus_button.bind                       ('<Button-1>', lambda event: canvas_editing.zoom_plus())
    minus_button.bind                      ('<Button-1>', lambda event: canvas_editing.zoom_minus())

    canvas.bind_all('<Delete>'            , lambda event: canvas_editing.delete())
    canvas.bind    ('<Button-1>'          , move_handling_initialization.move_initialization)
    canvas.bind    ('<Motion>'            , canvas_editing.store_mouse_position)
    canvas.bind    ("<Control-MouseWheel>", canvas_editing.zoom_wheel          ) # MouseWheel used at Windows.
    canvas.bind    ("<Control-Button-4>"  , canvas_editing.zoom_wheel          ) # MouseWheel-Scroll-Up used at Linux.
    canvas.bind    ("<Control-Button-5>"  , canvas_editing.zoom_wheel          ) # MouseWheel-Scroll-Down used at Linux.
    canvas.bind    ('<Control-Button-1>'  , canvas_editing.scroll_start        )
    canvas.bind    ('<Control-B1-Motion>' , canvas_editing.scroll_move         )
    canvas.bind    ("<MouseWheel>"        , canvas_editing.scroll_wheel        )
    canvas.bind    ('<Button-3>'          , canvas_editing.start_view_rectangle)

    canvas_editing.create_font_for_state_names()

def enable_undo_redo_if_diagram_tab_is_active_else_disable():
    if notebook.index(notebook.select())==3:
        # undo_button.config(state=NORMAL)
        # redo_button.config(state=NORMAL)
        canvas.bind_all("<Control-z>", lambda event : undo_handling.undo())
        canvas.bind_all("<Control-Z>", lambda event : undo_handling.redo())
    else:
        # undo_button.config(state=DISABLED)
        # redo_button.config(state=DISABLED)
        canvas.unbind_all("<Control-z>") # necessary, because if you type Control-z when another tab is active,
        canvas.unbind_all("<Control-Z>") # then in the diagram tab an undo would take place.

def create_hdl_notebook_tab():
    global hdl_frame_text
    hdl_frame = ttk.Frame(notebook)
    hdl_frame.grid()
    hdl_frame.columnconfigure(0, weight=1)
    hdl_frame.rowconfigure   (0, weight=1)

    hdl_frame_text = custom_text.CustomText(hdl_frame, type="generated", undo=False, font=("Courier", 10))
    hdl_frame_text.grid(row=0, column=0, sticky=(tk.N,tk.W,tk.E,tk.S))
    hdl_frame_text.columnconfigure((0,0), weight=1)
    hdl_frame_text.config(state=tk.DISABLED)

    hdl_frame_text_scroll = ttk.Scrollbar (hdl_frame, orient=tk.VERTICAL, cursor='arrow', command=hdl_frame_text.yview)
    hdl_frame_text.config(yscrollcommand=hdl_frame_text_scroll.set)
    hdl_frame_text_scroll.grid   (row=0, column=1, sticky=(tk.W,tk.E,tk.S,tk.N))

    hdl_frame_text.bind("<Motion>", cursor_move_hdl_tab)

    notebook.add(hdl_frame, sticky=tk.N+tk.E+tk.W+tk.S, text="generated HDL")

def create_log_notebook_tab():
    global log_frame_text, debug_active
    log_frame = ttk.Frame(notebook)
    log_frame.grid()
    log_frame.columnconfigure(0, weight=1)
    log_frame.rowconfigure   (1, weight=1)

    log_frame_button_frame = ttk.Frame(log_frame)
    log_frame_text = custom_text.CustomText(log_frame, type="log", undo=False)
    log_frame_button_frame.grid(row=0, column=0, sticky=(tk.W,tk.E))
    log_frame_text        .grid(row=1, column=0, sticky=(tk.N,tk.W,tk.E,tk.S))
    log_frame_text.columnconfigure((0,0), weight=1)
    log_frame_text.config(state=tk.DISABLED)

    log_frame_regex_button = ttk.Button(log_frame_button_frame, takefocus=False, text="Define Regex for Hyperlinks" , style="Find.TButton")
    log_frame_regex_button.grid(row=0, column=0, sticky=tk.W)
    log_frame_regex_button.bind('<Button-1>', edit_regex)

    log_frame_text_scroll = ttk.Scrollbar (log_frame, orient=tk.VERTICAL, cursor='arrow', command=log_frame_text.yview)
    log_frame_text.config(yscrollcommand=log_frame_text_scroll.set)
    log_frame_text_scroll.grid(row=1, column=1, sticky=(tk.W,tk.E,tk.S,tk.N))

    log_frame_text.bind("<Motion>", cursor_move_log_tab)

    notebook.add(log_frame, sticky=tk.N+tk.E+tk.W+tk.S, text="Compile Messages")
    debug_active = tk.IntVar()
    debug_active.set(1) # 1: inactive, 2: active

def edit_regex(*_):
    global regex_dialog, regex_dialog_entry, regex_dialog_filename_entry, regex_dialog_linenumber_entry
    regex_dialog                  = tk.Toplevel()
    regex_dialog.title("Enter Regex for Python:")
    regex_dialog_header           = ttk.Label(regex_dialog, text="Regex for finding a message with\ngroup for file-name and\ngroup for line-number:", justify="left")
    regex_dialog_entry            = ttk.Entry(regex_dialog)
    regex_dialog_identifier_frame = ttk.Frame(regex_dialog)
    regex_button_frame            = ttk.Frame(regex_dialog)
    regex_dialog_header          .grid(row=0, sticky=(tk.W,tk.E))
    regex_dialog_entry           .grid(row=1, sticky=(tk.W,tk.E))
    regex_dialog_identifier_frame.grid(row=2)
    regex_button_frame           .grid(row=3, sticky=(tk.W,tk.E))
    regex_dialog_filename_label   = ttk.Label (regex_dialog_identifier_frame, text="Group identifier for file-name:", justify="left")
    regex_dialog_filename_entry   = ttk.Entry (regex_dialog_identifier_frame, width=40)
    regex_dialog_linenumber_label = ttk.Label (regex_dialog_identifier_frame, text="Group identifier for line-number:", justify="left")
    regex_dialog_linenumber_entry = ttk.Entry (regex_dialog_identifier_frame, width=40)
    regex_dialog_filename_label  .grid(row=0, column=0, sticky=tk.W)
    regex_dialog_filename_entry  .grid(row=0, column=1)
    regex_dialog_linenumber_label.grid(row=1, column=0, sticky=tk.W)
    regex_dialog_linenumber_entry.grid(row=1, column=1)
    regex_dialog_store_button     = ttk.Button(regex_button_frame, text="Store" , command=regex_store)
    regex_dialog_cancel_button    = ttk.Button(regex_button_frame, text="Cancel", command=regex_cancel)
    debug_stdout_label            = ttk.Label (regex_button_frame, text="Debug Regex at STDOUT:", padding=5)
    debug_stdout_frame            = ttk.Frame (regex_button_frame)
    regex_dialog_store_button    .grid(row=0, column=0)
    regex_dialog_cancel_button   .grid(row=0, column=1)
    debug_stdout_label           .grid(row=0, column=2, sticky=tk.W)
    debug_stdout_frame           .grid(row=0, column=3, sticky=tk.W)
    debug_stdout_radio_button1 = ttk.Radiobutton(debug_stdout_frame, takefocus=False, variable=debug_active, text="Inactive" , value=1)
    debug_stdout_radio_button2 = ttk.Radiobutton(debug_stdout_frame, takefocus=False, variable=debug_active, text="Active"   , value=2)
    debug_stdout_radio_button1.grid(row=0, column=1, sticky=tk.W)
    debug_stdout_radio_button2.grid(row=0, column=2, sticky=tk.W)
    if language.get()=="VHDL":
        regex_dialog_entry.insert(0, regex_message_find_for_vhdl)
    else:
        regex_dialog_entry.insert(0, regex_message_find_for_verilog)
    regex_dialog_filename_entry  .insert(0, regex_file_name_quote)
    regex_dialog_linenumber_entry.insert(0, regex_file_line_number_quote)

def regex_store():
    global regex_message_find_for_vhdl, regex_message_find_for_verilog, regex_file_name_quote, regex_file_line_number_quote, regex_error_happened
    if language.get()=="VHDL":
        regex_message_find_for_vhdl = regex_dialog_entry.get()
    else:
        regex_message_find_for_verilog = regex_dialog_entry.get()
    regex_file_name_quote        = regex_dialog_filename_entry  .get()
    regex_file_line_number_quote = regex_dialog_linenumber_entry.get()
    undo_handling.design_has_changed()
    regex_error_happened = False
    regex_dialog.destroy()

def regex_cancel():
    regex_dialog.destroy()

def cursor_move_hdl_tab(*_):
    global line_number_under_pointer_hdl_tab, func_id_jump
    if hdl_frame_text.get("1.0", tk.END + "- 1 char")=="":
        return
    # Determine current cursor position:
    delta_x = hdl_frame_text.winfo_pointerx() - hdl_frame_text.winfo_rootx()
    delta_y = hdl_frame_text.winfo_pointery() - hdl_frame_text.winfo_rooty()
    index_string = hdl_frame_text.index(f"@{delta_x},{delta_y}")
    # Determine current line number:
    line_number = int(re.sub(r"\..*", "", index_string))
    if line_number!=line_number_under_pointer_hdl_tab:
        #print("cursor_move_hdl_tab: line_number =", line_number)
        hdl_frame_text.tag_delete("underline")
        file_name, file_name_architecture = hdl_generation.get_file_names()
        if line_number>hdl_generation.last_line_number_of_file1:
            line_number_in_file = line_number - hdl_generation.last_line_number_of_file1
            selected_file = file_name_architecture
            start_index   = size_of_file2_line_number
            #print("In architect: selected_file, start_index =", selected_file, start_index, line_number_in_file)
        else:
            line_number_in_file = line_number
            selected_file = file_name
            start_index   = size_of_file1_line_number
        while hdl_frame_text.get(str(line_number) + '.' + str(start_index-1))==' ':
            start_index += 1
        if selected_file in link_dictionary.LinkDictionary.link_dict_reference.link_dict: # Can for example happen with empty architecture or module content.
            if line_number_in_file in link_dictionary.LinkDictionary.link_dict_reference.link_dict[selected_file]:
                hdl_frame_text.tag_add("underline", str(line_number) + "." + str(start_index-1), str(line_number+1) + ".0" )
                hdl_frame_text.tag_config("underline", underline=1)
                func_id_jump = hdl_frame_text.bind("<Control-Button-1>",
                                                            lambda event : link_dictionary.LinkDictionary.link_dict_reference.jump_to_source(selected_file,
                                                                                                                                            line_number_in_file))
            else:
                hdl_frame_text.unbind("<Button-1>", func_id_jump)
                func_id_jump = None
        line_number_under_pointer_hdl_tab = line_number

def cursor_move_log_tab(*_):
    global func_id_jump1, func_id_jump2, regex_error_happened, line_number_under_pointer_log_tab
    if log_frame_text.get("1.0", tk.END + "- 1 char")=="":
        return
    if debug_active.get()==2:
        debug = True
    else:
        debug = False
    # Determine current cursor position:
    delta_x = log_frame_text.winfo_pointerx() - log_frame_text.winfo_rootx()
    delta_y = log_frame_text.winfo_pointery() - log_frame_text.winfo_rooty()
    index_string = log_frame_text.index(f"@{delta_x},{delta_y}")
    # Determine current line number:
    line_number = int(re.sub(r"\..*", "", index_string))
    if line_number!=line_number_under_pointer_log_tab and regex_error_happened is False:
        log_frame_text.tag_delete("underline")
        if language.get()=="VHDL":
            regex_message_find = regex_message_find_for_vhdl
        else:
            regex_message_find = regex_message_find_for_verilog
        content_of_line = log_frame_text.get(str(line_number) + ".0", str(line_number+1) + ".0")
        content_of_line = content_of_line[:-1] # Remove return
        match_object_of_message = re.match(regex_message_find, content_of_line)
        if debug:
            print("\nUsed Regex                         : ", regex_message_find)
        if match_object_of_message is not None:
            file_name = re.sub(regex_message_find, regex_file_name_quote, content_of_line)
            if debug:
                print("Regex found line                   : ", content_of_line)
                print("Regex found filename (group 1)     :", '"' + file_name + '"')
            try:
                file_line_number_string = re.sub(regex_message_find, regex_file_line_number_quote, content_of_line)
                if file_line_number_string!=content_of_line:
                    file_line_number = int(file_line_number_string)
                    if debug:
                        print("Regex found line-number (group 2)  :", '"' + file_line_number_string + '"')
                else:
                    if debug:
                        print("Regex found no line-number         : Getting line-number by group 2 did not work.")
                    return
                if file_name in link_dictionary.LinkDictionary.link_dict_reference.link_dict: # For example ieee source files are not a key in link_dict.
                    if file_line_number in link_dictionary.LinkDictionary.link_dict_reference.link_dict[file_name]:
                        if debug:
                            print("Filename and line-number are found in Link-Dictionary.")
                        log_frame_text.tag_add("underline", str(line_number) + ".0", str(line_number+1) + ".0" )
                        log_frame_text.tag_config("underline", underline=1, foreground="red")
                        func_id_jump1 = log_frame_text.bind("<Control-Button-1>",
                                                                    lambda event : link_dictionary.LinkDictionary.link_dict_reference.jump_to_source(file_name,
                                                                                                                                                    file_line_number))
                        func_id_jump2 = log_frame_text.bind("<Alt-Button-1>",
                                                                    lambda event : link_dictionary.LinkDictionary.link_dict_reference.jump_to_hdl(file_name,
                                                                                                                                                file_line_number))
                    else:
                        if debug:
                            print("Filename is found in Link-Dictionary but line-number not.")
                            # Add only tag (for coloring in red), but don't underline as no link exists.
                        log_frame_text.tag_add("underline", str(line_number) + ".0", str(line_number+1) + ".0" )
                else:
                    if debug:
                        print("Filename is not found in Link-Dictionary.")
            #except re.error:
            except Exception as e:
                regex_error_happened = True
                messagebox.showerror("Error in HDL-SCHEM-Editor by regular expression", repr(e))
        else:
            if debug:
                print("Regex did not match line           : ", content_of_line)
            if func_id_jump1 is not None:
                log_frame_text.unbind("<Button-1>", func_id_jump1)
            if func_id_jump2 is not None:
                log_frame_text.unbind("<Button-1>", func_id_jump2)
            func_id_jump1 = None
            func_id_jump2 = None
        line_number_under_pointer_log_tab = line_number


def switch_language_mode():
    global keywords, keyword_color
    keyword_color = {"not_read": "orange", "not_written": "red", "control": "green4", "datatype": "brown", "function": "violet", "comment": "blue"}
    new_language = language.get()
    if new_language=="VHDL":
        keywords = constants.vhdl_keywords
        # enable 2 files mode
        select_file_number_text.set(2)
        select_file_number_label.grid        (row=3, column=0, sticky=tk.W)
        select_file_number_frame.grid        (row=3, column=1, sticky=tk.W)
         # Interface: Enable VHDL-package text field
        interface_package_label.grid  (row=0, column=0, sticky=tk.W) # "W" nötig, damit Text links bleibt
        interface_package_text.grid   (row=1, column=0, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
        interface_package_scroll.grid (row=1, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
        # Interface: Adapt documentation for generics and ports
        interface_generics_label.config(text="Generics:")
        interface_ports_label.config   (text="Ports:")
        # Internals: Enable VHDL-package text field
        internals_package_label.grid  (row=0, column=0, sticky=tk.W) # "W" nötig, damit Text links bleibt
        internals_package_text.grid   (row=1, column=0, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
        internals_package_scroll.grid (row=1, column=1, sticky=(tk.W,tk.E,tk.S,tk.N)) # "W,E" nötig, damit Text tatsächlich breiter wird
        # Internals: Architecture-Declarations, 2*Variable Declarations umbenennen
        internals_architecture_label.config         (text="Architecture Declarations:")
        internals_process_clocked_label.config      (text="Variable Declarations for clocked process:")
        internals_process_combinatorial_label.config(text="Variable Declarations for combinatorial process:")
        # Modify compile command:
        compile_cmd.set("ghdl -a $file1 $file2; ghdl -e $name; ghdl -r $name")
        compile_cmd_docu.config(text=
                            "Variables for compile command:\n$file1\t= Entity-File\n$file2\t= Architecture-File\n$file\t= File with Entity and Architecture\n$name\t= Entity Name")
    else: # "Verilog" or "SystemVerilog"
        keywords = constants.verilog_keywords
        # Control: disable 2 files mode
        select_file_number_text.set(1)
        select_file_number_label.grid_forget()
        select_file_number_frame.grid_forget()
        # Interface: Remove VHDL-package text field
        interface_package_label.grid_forget()
        interface_package_text.grid_forget()
        interface_package_text.delete("1.0", tk.END)
        interface_package_scroll.grid_forget()
        # Interface: Adapt documentation for generics and ports
        interface_generics_label.config(text="Parameters:")
        interface_ports_label.config   (text="Ports:")
        # Internals: Remove VHDL-package text field
        internals_package_label.grid_forget()
        internals_package_text.grid_forget()
        internals_package_text.delete("1.0", tk.END)
        internals_package_scroll.grid_forget()
        # Internals: Architecture-Declarations umbenennen, 2*Variable Declarations umbenennen
        internals_architecture_label.config(text="Internal Declarations:")
        internals_process_clocked_label.config(text="Local Variable Declarations for clocked always process (not supported by all Verilog compilers):")
        internals_process_combinatorial_label.config(text="Local Variable Declarations for combinatorial always process (not supported by all Verilog compilers):")
        # Modify compile command:
        if new_language=="Verilog":
            compile_cmd.set("iverilog -o $name $file; vvp $name")
        else:
            compile_cmd.set("iverilog -g2012 -o $name $file; vvp $name")
        compile_cmd_docu.config(text="Variables for compile command:\n$file\t= Module-File\n$name\t= Module Name")





def handle_key(event, custom_text_ref):
    custom_text_ref.after_idle(custom_text_ref.update_highlight_tags, canvas_editing.fontsize, ["control" , "datatype" , "function" , "comment"])

def handle_key_at_ports(custom_text_ref):
    custom_text_ref.after_idle(update_custom_text_instance_of_ports, custom_text_ref)
def update_custom_text_instance_of_ports(custom_text_ref):
    custom_text_ref.update_custom_text_class_ports_list()
    custom_text_ref.update_highlighting()

def handle_key_at_generics(custom_text_ref):
    custom_text_ref.after_idle(update_custom_text_instance_of_generics, custom_text_ref)
def update_custom_text_instance_of_generics(custom_text_ref):
    custom_text_ref.update_custom_text_class_generics_list()
    custom_text_ref.update_highlighting()

def handle_key_at_declarations(custom_text_ref):
    custom_text_ref.after_idle(custom_text_ref.update_custom_text_class_signals_list)
    custom_text_ref.after_idle(custom_text_ref.update_highlighting)

def show_path_has_changed(*_):
    undo_handling.design_has_changed()

def show_tab(tab):
    notebook_ids = notebook.tabs()
    for tab_id in notebook_ids:
        if notebook.tab(tab_id, option="text")==tab:
            notebook.select(tab_id)

def highlight_item(hdl_item_type, *_):
    # This method must have the same name as the method custom_text.CustomText.highlight_item.
    # It is called, when in the "generated HDL"-tab module-name, reset-name or clock-name are clicked per mouse to jump to its declaration.
    if hdl_item_type=="module_name":
        module_name_entry.select_range(0, tk.END)
    elif hdl_item_type=="reset_and_clock_signal_name":
        clock_signal_name_entry.select_range(0, tk.END)

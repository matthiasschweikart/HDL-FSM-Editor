"""This class generates the menu bar of the tool."""

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

import compile_handling
import constants
import file_handling
import find_replace
import undo_handling
import update_hdl_tab
from codegen import hdl_generation
from dialogs import help_selection, help_shortcuts
from project_manager import project_manager


class MenuBar:
    """This object creates the menu bar of the tool and manages its functionality."""

    def __init__(self, row, column) -> None:
        menue_frame = ttk.Frame(project_manager.root, borderwidth=2, relief=tk.RAISED)
        menue_frame.grid(column=column, row=row, sticky="nsew")
        menue_frame.columnconfigure(2, weight=1)  # The column with the title expands.

        file_menu_button = ttk.Menubutton(menue_frame, text="File", style="Window.TMenubutton")
        file_menu = tk.Menu(file_menu_button)
        file_menu_button.configure(menu=file_menu)
        file_menu.add_command(label="New", accelerator="Ctrl+n", command=file_handling.new_design, font=("Arial", 10))
        file_menu.add_command(
            label="Open ...", accelerator="Ctrl+o", command=file_handling.open_file, font=("Arial", 10)
        )
        file_menu.add_command(label="Save", accelerator="Ctrl+s", command=file_handling.save, font=("Arial", 10))
        file_menu.add_command(label="Save as ...", command=file_handling.save_as, font=("Arial", 10))
        file_menu.add_command(label="Exit", command=self._close_tool, font=("Arial", 10))
        project_manager.root.protocol("WM_DELETE_WINDOW", self._close_tool)

        hdl_menu_button = ttk.Menubutton(menue_frame, text="HDL", style="Window.TMenubutton")
        hdl_menu = tk.Menu(hdl_menu_button)
        hdl_menu_button.configure(menu=hdl_menu)
        hdl_menu.add_command(
            label="Generate",
            accelerator="Ctrl+g",
            command=lambda: hdl_generation.run_hdl_generation(write_to_file=True),
            font=("Arial", 10),
        )
        hdl_menu.add_command(
            label="Compile", accelerator="Ctrl+p", command=compile_handling.compile_hdl, font=("Arial", 10)
        )

        tool_title = ttk.Label(menue_frame, text="HDL-FSM-Editor", font=("Arial", 15))

        search_string = tk.StringVar()
        search_string.set("")
        replace_string = tk.StringVar()
        replace_string.set("")
        search_frame = ttk.Frame(menue_frame, borderwidth=2)
        search_button = ttk.Button(
            search_frame,
            text="Find",
            command=lambda: find_replace.FindReplace(search_string, replace_string, replace=False),
            style="Find.TButton",
        )
        search_string_entry = ttk.Entry(search_frame, width=23, textvariable=search_string)
        replace_string_entry = ttk.Entry(search_frame, width=23, textvariable=replace_string)
        replace_button = ttk.Button(
            search_frame,
            text="Find & Replace",
            command=lambda: find_replace.FindReplace(search_string, replace_string, replace=True),
            style="Find.TButton",
        )
        search_string_entry.bind(
            "<Return>", lambda event: find_replace.FindReplace(search_string, replace_string, replace=False)
        )
        search_button.bind(
            "<Return>", lambda event: find_replace.FindReplace(search_string, replace_string, replace=False)
        )
        replace_string_entry.bind(
            "<Return>", lambda event: find_replace.FindReplace(search_string, replace_string, replace=True)
        )
        replace_button.bind(
            "<Return>", lambda event: find_replace.FindReplace(search_string, replace_string, replace=True)
        )
        search_string_entry.grid(row=0, column=0)
        search_button.grid(row=0, column=1)
        replace_string_entry.grid(row=0, column=2)
        replace_button.grid(row=0, column=3)

        help_menu = tk.Menu(project_manager.root, tearoff=0)
        help_menu.add_command(
            label="Editing Shortcuts",
            command=help_shortcuts.ShortCutsDialog,
            font=("Arial", 10),
        )
        help_menu.add_command(
            label="Text Selection",
            command=help_selection.SelectionDialog,
            font=("Arial", 10),
        )

        info_menu_button = ttk.Menubutton(menue_frame, text="Info", style="Window.TMenubutton")
        info_menu = tk.Menu(info_menu_button)
        info_menu_button.configure(menu=info_menu)
        info_menu.add_cascade(
            label="Help",
            menu=help_menu,
            font=("Arial", 10),
        )
        info_menu.add_command(
            label="About", command=lambda: messagebox.showinfo("About:", constants.HEADER_STRING), font=("Arial", 10)
        )

        project_manager.notebook.bind("<<NotebookTabChanged>>", lambda event: self._handle_notebook_tab_changed_event())

        file_menu_button.grid(row=0, column=0)
        hdl_menu_button.grid(row=0, column=1)
        tool_title.grid(row=0, column=2)
        search_frame.grid(row=0, column=3)
        info_menu_button.grid(row=0, column=4)

        # Bindings of the menus:
        project_manager.root.bind_all("<Control-o>", lambda event: file_handling.open_file())
        project_manager.root.bind_all("<Control-s>", lambda event: file_handling.save())
        project_manager.root.bind_all(
            "<Control-g>", lambda event: hdl_generation.run_hdl_generation(write_to_file=True)
        )
        project_manager.root.bind_all("<Control-n>", lambda event: file_handling.new_design())
        project_manager.root.bind_all("<Control-p>", lambda event: compile_handling.compile_hdl())
        project_manager.root.bind_all("<Control-f>", lambda event: search_string_entry.focus_set())
        project_manager.root.bind_all("<Control-O>", lambda event: self._capslock_warning("O"))
        project_manager.root.bind_all("<Control-S>", lambda event: self._capslock_warning("S"))
        project_manager.root.bind_all("<Control-G>", lambda event: self._capslock_warning("G"))
        project_manager.root.bind_all("<Control-N>", lambda event: self._capslock_warning("N"))
        project_manager.root.bind_all("<Control-P>", lambda event: self._capslock_warning("P"))
        project_manager.root.bind_all("<Control-F>", lambda event: self._capslock_warning("F"))

    def _handle_notebook_tab_changed_event(self) -> None:
        self._enable_undo_redo_if_diagram_tab_is_active_else_disable()
        self._update_hdl_tab_if_necessary()

    def _enable_undo_redo_if_diagram_tab_is_active_else_disable(self) -> None:
        if project_manager.notebook.index(project_manager.notebook.select()) == 3:
            project_manager.canvas.bind_all("<Control-z>", lambda event: undo_handling.undo())
            project_manager.canvas.bind_all("<Control-Z>", lambda event: undo_handling.redo())
        else:
            project_manager.canvas.unbind_all(
                "<Control-z>"
            )  # necessary, because if you type Control-z when another tab is active,
            project_manager.canvas.unbind_all("<Control-Z>")  # then in the diagram tab an undo would take place.

    def _update_hdl_tab_if_necessary(self) -> None:
        if project_manager.notebook.index(project_manager.notebook.select()) == 4:
            if project_manager.language.get() == "VHDL":
                if project_manager.select_file_number_text.get() == 1:
                    hdlfilename = (
                        project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + ".vhd"
                    )
                    hdlfilename2 = ""
                else:
                    hdlfilename = (
                        project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + "_e.vhd"
                    )
                    hdlfilename2 = (
                        project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + "_fsm.vhd"
                    )
            else:  # verilog
                hdlfilename = project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + ".v"
                hdlfilename2 = ""

            if (
                os.path.isfile(hdlfilename)
                and project_manager.date_of_hdl_file_shown_in_hdl_tab < os.path.getmtime(hdlfilename)
            ) or (
                project_manager.select_file_number_text.get() == 2
                and os.path.isfile(hdlfilename2)
                and project_manager.date_of_hdl_file2_shown_in_hdl_tab < os.path.getmtime(hdlfilename2)
            ):
                answer = messagebox.askquestion(
                    "Warning in HDL-FSM-Editor3",
                    "The HDL was modified by another tool. Shall it be reloaded?",
                    default="yes",
                )
                if answer == "yes":
                    update_ref = update_hdl_tab.UpdateHdlTab(
                        project_manager.language.get(),
                        project_manager.select_file_number_text.get(),
                        project_manager.current_file,
                        project_manager.generate_path_value.get(),
                        project_manager.module_name.get(),
                    )
                    project_manager.date_of_hdl_file_shown_in_hdl_tab = update_ref.get_date_of_hdl_file()
                    project_manager.date_of_hdl_file2_shown_in_hdl_tab = update_ref.get_date_of_hdl_file2()

    def _capslock_warning(self, character):
        messagebox.showwarning(
            "Warning in HDL-FSM-Editor",
            "The character " + character + " is not bound to any action.\nPerhaps Capslock is active?",
        )

    def _close_tool(self) -> None:
        """Prompt to save if dirty, remove .tmp file if present, then exit the application."""
        title = project_manager.root.title()
        if title.endswith("*"):
            action = file_handling.ask_save_unsaved_changes(title)
            if action == "cancel":
                return
            if action == "save":
                file_handling.save()
                # Check if save was successful (current_file is not empty)
                if project_manager.current_file == "":
                    return
        if os.path.isfile(project_manager.current_file + ".tmp"):
            os.remove(project_manager.current_file + ".tmp")
        sys.exit()

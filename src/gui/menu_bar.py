"""This class generates the menu bar of the tool."""

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import constants
import file_handling
from actions import find_replace
from codegen import hdl_generation
from dialogs import help_selection, help_shortcuts
from elements import condition_action, state, state_action, state_comment, transition
from project_manager import project_manager
from widgets import custom_text

from . import compile_handling


class MenuBar:
    """This object creates the menu bar of the tool and manages its functionality."""

    def __init__(self, row, column) -> None:
        menue_frame = ttk.Frame(project_manager.root, borderwidth=2, relief=tk.RAISED, style="My.TFrame")
        menue_frame.grid(column=column, row=row, sticky="nsew")
        file_menu_button = ttk.Menubutton(menue_frame, text="File", style="My.TMenubutton")
        hdl_menu_button = ttk.Menubutton(menue_frame, text="HDL", style="My.TMenubutton")
        prefs_menu_button = ttk.Menubutton(menue_frame, text="Prefs", style="My.TMenubutton")
        tool_title = ttk.Label(menue_frame, text="HDL-FSM-Editor", font=("Arial", 15), style="My.TLabel")
        search_frame = ttk.Frame(menue_frame, borderwidth=2, style="My.TFrame")
        info_menu_button = ttk.Menubutton(menue_frame, text="Info", style="My.TMenubutton")
        file_menu_button.grid(row=0, column=0)
        hdl_menu_button.grid(row=0, column=1)
        prefs_menu_button.grid(row=0, column=2, sticky="w")
        tool_title.grid(row=0, column=3)
        search_frame.grid(row=0, column=4)
        info_menu_button.grid(row=0, column=5)
        menue_frame.columnconfigure(3, weight=1)  # The column with the title expands.

        self.file_menu = tk.Menu(file_menu_button)  # , activeborderwidth=0, borderwidth=0)
        file_menu_button.configure(menu=self.file_menu)
        self.file_menu.add_command(
            label="New", accelerator="Ctrl+n", command=file_handling.new_design, font=("Arial", 10)
        )
        self.file_menu.add_command(
            label="Open ...", accelerator="Ctrl+o", command=file_handling.open_file, font=("Arial", 10)
        )
        self.file_menu.add_command(label="Save", accelerator="Ctrl+s", command=file_handling.save, font=("Arial", 10))
        self.file_menu.add_command(label="Save as ...", command=file_handling.save_as, font=("Arial", 10))
        self.file_menu.add_command(label="Exit", command=self._close_tool, font=("Arial", 10))
        project_manager.root.protocol("WM_DELETE_WINDOW", self._close_tool)

        self.hdl_menu = tk.Menu(hdl_menu_button)
        hdl_menu_button.configure(menu=self.hdl_menu)
        self.hdl_menu.add_command(
            label="Generate",
            accelerator="Ctrl+g",
            command=lambda: hdl_generation.HdlGeneration(write_to_file=True),
            font=("Arial", 10),
        )
        self.hdl_menu.add_command(
            label="Compile", accelerator="Ctrl+p", command=compile_handling.compile_hdl, font=("Arial", 10)
        )

        self.prefs_menu = tk.Menu(prefs_menu_button, tearoff=0)
        prefs_menu_button.configure(menu=self.prefs_menu)
        self.prefs_menu.add_command(
            label="Dark Mode",
            command=self.switch_mode,
            font=("Arial", 10),
        )

        search_string = tk.StringVar()
        search_string.set("")
        replace_string = tk.StringVar()
        replace_string.set("")
        search_string_entry = ttk.Entry(search_frame, width=23, textvariable=search_string, style="My.TEntry")
        replace_string_entry = ttk.Entry(search_frame, width=23, textvariable=replace_string, style="My.TEntry")
        search_button = ttk.Button(
            search_frame,
            text="Find",
            command=lambda: find_replace.FindReplace(search_string, replace_string, replace=False),
            style="My.TButton",
        )
        search_button2 = ttk.Button(
            search_frame,
            text="Find in HDL",
            command=lambda: find_replace.FindReplace(search_string, replace_string, replace=False, in_hdl=True),
            style="My.TButton",
        )
        distance_label = ttk.Label(search_frame, text=" ", width=2, style="My.TLabel")
        replace_button = ttk.Button(
            search_frame,
            text="Find & Replace",
            command=lambda: find_replace.FindReplace(search_string, replace_string, replace=True),
            style="My.TButton",
        )
        search_string_entry.bind(
            "<Return>", lambda event: find_replace.FindReplace(search_string, replace_string, replace=False)
        )
        search_button.bind(
            "<Return>", lambda event: find_replace.FindReplace(search_string, replace_string, replace=False)
        )
        search_button2.bind(
            "<Return>",
            lambda event: find_replace.FindReplace(search_string, replace_string, replace=False, in_hdl=True),
        )
        replace_string_entry.bind(
            "<Return>", lambda event: find_replace.FindReplace(search_string, replace_string, replace=True)
        )
        replace_button.bind(
            "<Return>", lambda event: find_replace.FindReplace(search_string, replace_string, replace=True)
        )
        search_string_entry.grid(row=0, column=0)
        search_button.grid(row=0, column=1)
        search_button2.grid(row=0, column=2)
        distance_label.grid(row=0, column=3)
        replace_string_entry.grid(row=0, column=4)
        replace_button.grid(row=0, column=5)

        self.info_menu = tk.Menu(info_menu_button)
        info_menu_button.configure(menu=self.info_menu)
        self.help_menu = tk.Menu(self.info_menu, tearoff=0)
        self.info_menu.add_cascade(
            label="Help",
            menu=self.help_menu,
            font=("Arial", 10),
        )
        self.info_menu.add_command(
            label="About", command=lambda: messagebox.showinfo("About:", constants.HEADER_STRING), font=("Arial", 10)
        )
        self.help_menu.add_command(
            label="Editing Shortcuts",
            command=help_shortcuts.ShortCutsDialog,
            font=("Arial", 10),
        )
        self.help_menu.add_command(
            label="Text Selection",
            command=help_selection.SelectionDialog,
            font=("Arial", 10),
        )

        # Bindings of the menus:
        project_manager.root.bind_all("<Control-o>", lambda event: file_handling.open_file())
        project_manager.root.bind_all("<Control-s>", lambda event: file_handling.save())
        project_manager.root.bind_all("<Control-g>", lambda event: hdl_generation.HdlGeneration(write_to_file=True))
        project_manager.root.bind_all("<Control-n>", lambda event: file_handling.new_design())
        project_manager.root.bind_all("<Control-p>", lambda event: compile_handling.compile_hdl())
        project_manager.root.bind_all("<Control-f>", lambda event: search_string_entry.focus_set())
        project_manager.root.bind_all("<Control-O>", lambda event: self._capslock_warning("O"))
        project_manager.root.bind_all("<Control-S>", lambda event: self._capslock_warning("S"))
        project_manager.root.bind_all("<Control-G>", lambda event: self._capslock_warning("G"))
        project_manager.root.bind_all("<Control-N>", lambda event: self._capslock_warning("N"))
        project_manager.root.bind_all("<Control-P>", lambda event: self._capslock_warning("P"))
        project_manager.root.bind_all("<Control-F>", lambda event: self._capslock_warning("F"))

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
        self._write_rc_file()
        sys.exit()

    def _write_rc_file(self):
        config_dictionary = {}
        config_dictionary["graphical_mode"] = (
            "Normal Mode" if self.prefs_menu.entrycget(0, "label") == "Dark Mode" else "Dark Mode"
        )
        config_dictionary["working_directory"] = project_manager.tab_control_ref.working_directory_value.get()
        try:
            with open(Path.home() / ".hdl-fsm-editor.rc", "w", encoding="utf-8") as fileobject:
                fileobject.write(json.dumps(config_dictionary, indent=4, default=str))
                print("Created configuration file " + str(Path.home()) + "/.hdl-fsm-editor.rc")
        except Exception as e:  # pylint: disable=broad-except
            print("HDL-FSM-Editor-Warning: Could not write to file " + str(Path.home()) + "/.hdl-fsm-editor.rc.", e)

    def switch_mode(self) -> None:
        """Switch between "Dark Mode" and "Normal Mode"."""
        mode = self.prefs_menu.entrycget(0, "label")
        project_manager.style_admin_ref.activate_mode(mode)
        # Configure all widgets which do not support the ttk.style feature:
        self._configure_menus(mode)
        self._configure_listboxes(mode)
        for text_widget in custom_text.CustomText.declaration_text_widgets() + [
            project_manager.tab_hdl_ref.hdl_frame_text,
            project_manager.tab_log_ref.log_frame_text,
        ]:
            text_widget.configure_mode(mode)
        # Configure all elements already inserted into the diagram:
        for canvas_window in project_manager.canvas_windows_ref_dict.values():
            for text_widget in canvas_window.text_ids:
                text_widget.configure_mode(mode)
        for state_ref in state.States.ref_dict.values():
            state_ref.configure_mode(mode)
        for state_action_ref in state_action.StateAction.ref_dict.values():
            state_action_ref.configure_mode(mode)
        for state_comment_ref in state_comment.StateComment.ref_dict.values():
            state_comment_ref.configure_mode(mode)
        for transition_line in transition.TransitionLine.ref_dict.values():
            transition_line.configure_mode(mode)
        for condition_action_ref in condition_action.ConditionAction.ref_dict.values():
            condition_action_ref.configure_mode(mode)
        self._configure_diagram_tab_background(mode)
        # The new background color must be stored for sure in the design file, as at any read from file
        # the background color is determined by the value found in design file,
        if not project_manager.root.title().startswith("unnamed*"):
            file_handling.save()
        if mode == "Dark Mode":
            self.prefs_menu.entryconfig(0, label="Normal Mode")
        else:
            self.prefs_menu.entryconfig(0, label="Dark Mode")

    def _configure_menus(self, mode):
        menu_list = [self.file_menu, self.hdl_menu, self.prefs_menu, self.info_menu, self.help_menu]
        for menu in menu_list:
            if mode == "Dark Mode":
                menu.configure(background="black", foreground="white", activebackground="gray")
            else:
                menu.configure(background="SystemMenu", foreground="SystemMenuText", activebackground="SystemHighlight")

    def _configure_listboxes(self, mode):
        project_manager.root.option_clear()
        if mode == "Normal Mode":
            project_manager.root.option_clear()
            project_manager.root.option_add("*TCombobox*Listbox.background", "white")
            project_manager.root.option_add("*TCombobox*Listbox.foreground", "black")
            project_manager.root.option_add("*TCombobox*Listbox.selectBackground", "#0078D7")
            project_manager.root.option_add("*TCombobox*Listbox.selectForeground", "white")
            project_manager.root.option_add("*TCombobox*Listbox.highlightThickness", "1")
        else:
            project_manager.root.option_add("*TCombobox*Listbox.background", "black")
            project_manager.root.option_add("*TCombobox*Listbox.foreground", "white")
            project_manager.root.option_add("*TCombobox*Listbox.selectBackground", "#0078D7")
            project_manager.root.option_add("*TCombobox*Listbox.selectForeground", "white")
            project_manager.root.option_add("*TCombobox*Listbox.highlightThickness", "1")

    def _configure_diagram_tab_background(self, mode):
        if mode == "Dark Mode":
            diagram_background = "black"
            grid_color = "gray40"
        else:
            diagram_background = "white"
            grid_color = "gray85"
        project_manager.grid_drawer.remove_grid()
        project_manager.canvas.configure(bg=diagram_background)
        project_manager.diagram_background_color.set(diagram_background)
        project_manager.grid_drawer.color = grid_color
        project_manager.grid_drawer.draw_grid()

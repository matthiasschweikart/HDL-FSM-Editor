"""Control-panel tab for project configuration (module name, language, paths, etc.)."""

import copy
import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

import constants
import custom_text
import undo_handling
from constants import GuiTab
from dialogs.color_changer import ColorChanger
from project_manager import project_manager


class TabControl:
    """Control panel for project configuration (module name, language, paths, etc.)."""

    def __init__(self) -> None:
        control_frame = ttk.Frame(project_manager.notebook, takefocus=False)
        control_frame.grid(sticky=(tk.W, tk.E))
        control_frame.columnconfigure(0, weight=0)  # column contains the labels.
        control_frame.columnconfigure(1, weight=1)  # column contains the entry boxes.
        control_frame.columnconfigure(2, weight=0)  # column contains the buttons.

        module_name = tk.StringVar()
        project_manager.module_name = module_name
        module_name.set("")
        module_name_label = ttk.Label(control_frame, text="Module-Name:", padding=5)
        _module_name_entry = ttk.Entry(control_frame, textvariable=module_name)
        module_name_label.grid(row=0, column=0, sticky=tk.W)
        _module_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        _module_name_entry.select_clear()

        language = tk.StringVar()
        project_manager.language = language
        language.set("VHDL")
        language_label = ttk.Label(control_frame, text="Language:", padding=5)
        language_combobox = ttk.Combobox(
            control_frame, textvariable=language, values=("VHDL", "Verilog", "SystemVerilog"), state="readonly"
        )
        language_combobox.bind("<<ComboboxSelected>>", lambda event: self.switch_language_mode())
        language_label.grid(row=1, column=0, sticky=tk.W)
        language_combobox.grid(row=1, column=1, sticky=tk.W)

        generate_path_value = tk.StringVar(value="")
        project_manager.generate_path_value = generate_path_value
        generate_path_value.trace_add("write", lambda *args: self._show_path_has_changed())
        generate_path_label = ttk.Label(control_frame, text="Directory for generated HDL:", padding=5)
        _generate_path_entry = ttk.Entry(control_frame, textvariable=generate_path_value, width=80)
        generate_path_button = ttk.Button(control_frame, text="Select...", command=self._set_path, style="Path.TButton")
        generate_path_label.grid(row=2, column=0, sticky=tk.W)
        _generate_path_entry.grid(row=2, column=1, sticky="ew")
        generate_path_button.grid(row=2, column=2, sticky="ew")

        _select_file_number_label = ttk.Label(control_frame, text="Generation attributes:", padding=5)
        _select_file_number_frame = ttk.Frame(control_frame)
        _select_file_number_label.grid(row=3, column=0, sticky=tk.W)
        _select_file_number_frame.grid(row=3, column=1, sticky=(tk.W, tk.E))

        select_file_number_text = tk.IntVar()
        project_manager.select_file_number_text = select_file_number_text
        select_file_number_text.set(2)
        self._select_file_number_radio_button1 = ttk.Radiobutton(
            _select_file_number_frame, takefocus=False, variable=select_file_number_text, text="1 file", value=1
        )
        self._select_file_number_radio_button2 = ttk.Radiobutton(
            _select_file_number_frame, takefocus=False, variable=select_file_number_text, text="2 files", value=2
        )
        include_timestamp_in_output = tk.BooleanVar(value=True)
        project_manager.include_timestamp_in_output = include_timestamp_in_output
        include_timestamp_in_output.trace_add("write", lambda *args: undo_handling.update_window_title())
        include_timestamp_checkbox = ttk.Checkbutton(_select_file_number_frame, variable=include_timestamp_in_output)
        include_timestamp_label = ttk.Label(
            _select_file_number_frame, text="Include timestamp in generated HDL files", width=40
        )
        include_timestamp_checkbox.grid(row=0, column=0, sticky=tk.W)
        include_timestamp_label.grid(row=0, column=1, sticky=tk.W)
        self._select_file_number_radio_button1.grid(row=0, column=2, sticky=tk.W)
        self._select_file_number_radio_button2.grid(row=0, column=3, sticky=tk.W)

        reset_signal_name = tk.StringVar()
        project_manager.reset_signal_name = reset_signal_name
        reset_signal_name.set("")
        reset_signal_name_label = ttk.Label(control_frame, text="Name of asynchronous reset input port:", padding=5)
        _reset_signal_name_entry = ttk.Entry(control_frame, width=23, textvariable=reset_signal_name)
        _reset_signal_name_entry.bind("<Key>", lambda event: undo_handling.update_window_title())
        reset_signal_name_label.grid(row=4, column=0, sticky=tk.W)
        _reset_signal_name_entry.grid(row=4, column=1, sticky=tk.W)

        clock_signal_name = tk.StringVar()
        project_manager.clock_signal_name = clock_signal_name
        clock_signal_name.set("")
        clock_signal_name_label = ttk.Label(control_frame, text="Name of clock input port:", padding=5)
        _clock_signal_name_entry = ttk.Entry(control_frame, width=23, textvariable=clock_signal_name)
        _clock_signal_name_entry.bind("<Key>", lambda event: undo_handling.update_window_title())
        clock_signal_name_label.grid(row=5, column=0, sticky=tk.W)
        _clock_signal_name_entry.grid(row=5, column=1, sticky=tk.W)

        compile_cmd = tk.StringVar()
        project_manager.compile_cmd = compile_cmd
        compile_cmd.set("ghdl -a $file1 $file2; ghdl -e $name; ghdl -r $name")
        compile_cmd_label = ttk.Label(control_frame, text="Compile command:", padding=5)
        _compile_cmd_entry = ttk.Entry(control_frame, width=23, textvariable=compile_cmd)
        compile_cmd_label.grid(row=6, column=0, sticky=tk.W)
        _compile_cmd_entry.grid(row=6, column=1, sticky="ew")

        _compile_cmd_docu = ttk.Label(
            control_frame,
            text="Variables for compile command:\n$file1\t= Entity-File\n$file2\t= Architecture-File\n$file\t\
= File with Entity and Architecture\n$name\t= Module Name",
            padding=5,
        )
        project_manager.compile_cmd_docu = _compile_cmd_docu
        project_manager.compile_cmd_docu.grid(row=7, column=1, sticky=tk.W)

        edit_cmd = tk.StringVar()
        project_manager.edit_cmd = edit_cmd
        edit_cmd.set("C:/Program Files/Notepad++/notepad++.exe -nosession -multiInst")
        edit_cmd_label = ttk.Label(control_frame, text="Edit command (executed by Ctrl+e):", padding=5)
        _edit_cmd_entry = ttk.Entry(control_frame, width=23, textvariable=edit_cmd)
        edit_cmd_label.grid(row=8, column=0, sticky=tk.W)
        _edit_cmd_entry.grid(row=8, column=1, sticky="ew")

        additional_sources_value = tk.StringVar(value="")
        project_manager.additional_sources_value = additional_sources_value
        additional_sources_value.trace_add("write", lambda *args: self._show_path_has_changed())
        additional_sources_label = ttk.Label(
            control_frame,
            text="Additional sources:\n(used only by HDL-SCHEM-Editor, must\nbe added manually to compile command)",
            padding=5,
        )
        _additional_sources_entry = ttk.Entry(control_frame, textvariable=additional_sources_value, width=80)
        additional_sources_button = ttk.Button(
            control_frame, text="Select...", command=self._add_path, style="Path.TButton"
        )
        additional_sources_label.grid(row=9, column=0, sticky=tk.W)
        _additional_sources_entry.grid(row=9, column=1, sticky=(tk.W, tk.E))
        additional_sources_button.grid(row=9, column=2, sticky=(tk.W, tk.E))

        working_directory_value = tk.StringVar(value="")
        project_manager.working_directory_value = working_directory_value
        working_directory_value.trace_add("write", lambda *args: self._show_path_has_changed())
        working_directory_label = ttk.Label(control_frame, text="Working directory:", padding=5)
        _working_directory_entry = ttk.Entry(control_frame, textvariable=working_directory_value, width=80)
        working_directory_button = ttk.Button(
            control_frame, text="Select...", command=self._set_working_directory, style="Path.TButton"
        )
        working_directory_label.grid(row=10, column=0, sticky=tk.W)
        _working_directory_entry.grid(row=10, column=1, sticky="ew")
        working_directory_button.grid(row=10, column=2, sticky="ew")

        diagram_background_color = tk.StringVar(value="white")
        project_manager.diagram_background_color = diagram_background_color
        diagram_background_color.trace_add("write", lambda *args: self._change_color_of_diagram_background())
        diagram_background_color_label = ttk.Label(control_frame, text="Diagram background color:", padding=5)
        diagram_background_color_entry = ttk.Entry(control_frame, textvariable=diagram_background_color, width=80)
        diagram_background_color_button = ttk.Button(
            control_frame, text="Choose color...", command=self.choose_bg_color, style="Path.TButton"
        )
        diagram_background_color_label.grid(row=11, column=0, sticky=tk.W)
        diagram_background_color_entry.grid(row=11, column=1, sticky="ew")
        diagram_background_color_button.grid(row=11, column=2, sticky="ew")
        _diagram_background_color_error = ttk.Label(control_frame, text="", padding=5)
        project_manager.diagram_background_color_error = _diagram_background_color_error
        _diagram_background_color_error.grid(row=12, column=1, sticky=tk.W)

        project_manager.notebook.add(control_frame, sticky="nsew", text=GuiTab.CONTROL.value)

        project_manager.entry_widgets = [
            {"stringvar": module_name, "entry": _module_name_entry},
            {"stringvar": generate_path_value, "entry": _generate_path_entry},
            {"stringvar": reset_signal_name, "entry": _reset_signal_name_entry},
            {"stringvar": clock_signal_name, "entry": _clock_signal_name_entry},
            {"stringvar": compile_cmd, "entry": _compile_cmd_entry},
            {"stringvar": edit_cmd, "entry": _edit_cmd_entry},
            {"stringvar": additional_sources_value, "entry": _additional_sources_entry},
            {"stringvar": working_directory_value, "entry": _working_directory_entry},
        ]

    def switch_language_mode(self) -> None:  # also called from file_handling.py
        new_language = project_manager.language.get()
        if new_language == "VHDL":
            project_manager.highlight_dict_ref.highlight_pattern_dict = copy.deepcopy(
                constants.VHDL_HIGHLIGHT_PATTERN_DICT
            )
            project_manager.highlight_dict_ref.highlight_pattern_dict["not_read"].clear()
            project_manager.highlight_dict_ref.highlight_pattern_dict["not_written"].clear()
            # enable 2 files mode
            project_manager.select_file_number_text.set(2)
            self._select_file_number_radio_button1.grid(row=0, column=2, sticky=tk.E)
            self._select_file_number_radio_button2.grid(row=0, column=3, sticky=tk.E)
            # Interface: Adapt documentation for generics and ports
            project_manager.tab_interface_ref.paned_window_interface.insert(
                0, project_manager.tab_interface_ref.interface_package_frame, weight=1
            )
            project_manager.interface_generics_label.config(text="Generics:")
            project_manager.interface_ports_label.config(text="Ports:")
            # Internals: Enable VHDL-package text field
            project_manager.tab_internals_ref.paned_window_internals.insert(
                0, project_manager.tab_internals_ref.internals_package_frame, weight=1
            )
            # Internals: Architecture-Declarations, 2*Variable Declarations umbenennen
            project_manager.internals_architecture_label.config(text="Architecture Declarations:")
            project_manager.internals_process_clocked_label.config(text="Variable Declarations for clocked process:")
            project_manager.internals_process_combinatorial_label.config(
                text="Variable Declarations for combinatorial process:"
            )
            # Modify compile command:
            project_manager.compile_cmd.set("ghdl -a $file1 $file2; ghdl -e $name; ghdl -r $name")
            project_manager.compile_cmd_docu.config(
                text="Variables for compile command:\n$file1\t= Entity-File\n$file2\t= Architecture-File\n$file\t\
    = File with Entity and Architecture\n$name\t= Entity Name"
            )
        else:  # "Verilog" or "SystemVerilog"
            project_manager.highlight_dict_ref.highlight_pattern_dict = copy.deepcopy(
                constants.VERILOG_HIGHLIGHT_PATTERN_DICT
            )
            project_manager.highlight_dict_ref.highlight_pattern_dict["not_read"].clear()
            project_manager.highlight_dict_ref.highlight_pattern_dict["not_written"].clear()
            # Control: disable 2 files mode
            project_manager.select_file_number_text.set(1)
            self._select_file_number_radio_button1.grid_forget()
            self._select_file_number_radio_button2.grid_forget()
            # Interface: Remove VHDL-package text field
            project_manager.tab_interface_ref.paned_window_interface.forget(
                project_manager.tab_interface_ref.interface_package_frame
            )
            # Interface: Adapt documentation for generics and ports
            project_manager.interface_generics_label.config(text="Parameters:")
            project_manager.interface_ports_label.config(text="Ports:")
            # Internals: Remove VHDL-package text field
            project_manager.tab_internals_ref.paned_window_internals.forget(
                project_manager.tab_internals_ref.internals_package_frame
            )
            # Internals: Architecture-Declarations umbenennen, 2*Variable Declarations umbenennen
            project_manager.internals_architecture_label.config(text="Internal Declarations:")
            project_manager.internals_process_clocked_label.config(
                text="Local Variable Declarations for clocked always process (not supported by all Verilog compilers):"
            )
            project_manager.internals_process_combinatorial_label.config(
                text=(
                    "Local Variable Declarations for combinatorial always process "
                    "(not supported by all Verilog compilers):"
                )
            )
            # Modify compile command:
            if new_language == "Verilog":
                project_manager.compile_cmd.set("iverilog -o $name $file; vvp $name")
            else:
                project_manager.compile_cmd.set("iverilog -g2012 -o $name $file; vvp $name")
            project_manager.compile_cmd_docu.config(
                text="Variables for compile command:\n$file\t= Module-File\n$name\t= Module Name"
            )

        custom_text.refresh_highlighting_in_all_declaration_widgets()

    def _show_path_has_changed(self) -> None:
        undo_handling.design_has_changed()

    def _set_path(self) -> None:
        path = askdirectory(title="Select directory for generated HDL")
        if path != "" and not path.isspace():
            project_manager.generate_path_value.set(path)

    def _add_path(self):
        old_entry = project_manager.additional_sources_value.get()
        if old_entry != "":
            old_entries = old_entry.split(",")
            path = askopenfilename(
                title="Select directory of additional sources", initialdir=os.path.dirname(old_entries[0])
            )
        else:
            path = askopenfilename(title="Select directory of additional sources")
        if path != "":
            if old_entry == "":
                project_manager.additional_sources_value.set(path)
            else:
                project_manager.additional_sources_value.set(old_entry + ", " + path)

    def _set_working_directory(self) -> None:
        path = askdirectory(title="Select working directory")
        if path != "" and not path.isspace():
            project_manager.working_directory_value.set(path)

    def _change_color_of_diagram_background(self) -> None:
        try:
            project_manager.canvas.configure(bg=project_manager.diagram_background_color.get())
            project_manager.diagram_background_color_error.configure(text="")
        except tk.TclError:
            project_manager.canvas.configure(bg="white")
            project_manager.diagram_background_color_error.configure(
                text="The string '"
                + project_manager.diagram_background_color.get()
                + "' is not a valid color definition, using 'white' instead."
            )

    def choose_bg_color(self) -> None:  # also called from canvas_editing.py
        new_color = ColorChanger(project_manager.canvas.cget("bg")).ask_color()
        if new_color is not None:
            project_manager.canvas.configure(bg=new_color)
            project_manager.diagram_background_color.set(new_color)

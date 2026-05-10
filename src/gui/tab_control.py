"""Control-panel tab for project configuration (module name, language, paths, etc.)."""

import copy
import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

import constants
from constants import GuiTab
from dialogs.color_changer import ColorChanger
from project_manager import project_manager
from widgets import custom_text


class TabControl:
    """Control panel for project configuration (module name, language, paths, etc.)."""

    def __init__(self) -> None:
        control_frame = ttk.Frame(project_manager.notebook, takefocus=False)
        control_frame.grid(sticky=(tk.W, tk.E))
        control_frame.columnconfigure(0, weight=0)  # column contains the labels.
        control_frame.columnconfigure(1, weight=1)  # column contains the entry boxes.
        control_frame.columnconfigure(2, weight=0)  # column contains the buttons.

        self.module_name = tk.StringVar()
        project_manager.module_name = self.module_name
        self.module_name.set("")
        module_name_label = ttk.Label(control_frame, text="Module-Name:", padding=5)
        self.module_name_entry = ttk.Entry(control_frame, textvariable=self.module_name)
        module_name_label.grid(row=0, column=0, sticky=tk.W)
        self.module_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.module_name_entry.select_clear()

        self.language = tk.StringVar()
        project_manager.language = self.language
        self.language.set("VHDL")
        self.last_language = "VHDL"
        language_label = ttk.Label(control_frame, text="Language:", padding=5)
        language_combobox = ttk.Combobox(
            control_frame, textvariable=self.language, values=("VHDL", "Verilog", "SystemVerilog"), state="readonly"
        )
        language_combobox.bind("<<ComboboxSelected>>", lambda event: self.switch_language_mode())
        language_label.grid(row=1, column=0, sticky=tk.W)
        language_combobox.grid(row=1, column=1, sticky=tk.W)

        self.generate_path_value = tk.StringVar(value="")
        project_manager.generate_path_value = self.generate_path_value
        generate_path_label = ttk.Label(control_frame, text="Directory for generated HDL:", padding=5)
        generate_path_entry = ttk.Entry(control_frame, textvariable=self.generate_path_value, width=80)
        generate_path_button = ttk.Button(control_frame, text="Select...", command=self._set_path, style="Path.TButton")
        generate_path_label.grid(row=2, column=0, sticky=tk.W)
        generate_path_entry.grid(row=2, column=1, sticky="ew")
        generate_path_button.grid(row=2, column=2, sticky="ew")

        select_file_number_label = ttk.Label(control_frame, text="Generation attributes:", padding=5)
        select_file_number_frame = ttk.Frame(control_frame)
        select_file_number_label.grid(row=3, column=0, sticky=tk.W)
        select_file_number_frame.grid(row=3, column=1, sticky=(tk.W, tk.E))

        self.select_file_number_text = tk.IntVar()
        project_manager.select_file_number_text = self.select_file_number_text
        self.select_file_number_text.set(2)
        self.select_file_number_radio_button1 = ttk.Radiobutton(
            select_file_number_frame, takefocus=False, variable=self.select_file_number_text, text="1 file", value=1
        )
        self.select_file_number_radio_button2 = ttk.Radiobutton(
            select_file_number_frame, takefocus=False, variable=self.select_file_number_text, text="2 files", value=2
        )
        self.include_timestamp_in_output = tk.BooleanVar(value=True)
        project_manager.include_timestamp_in_output = self.include_timestamp_in_output
        include_timestamp_checkbox = ttk.Checkbutton(
            select_file_number_frame, variable=self.include_timestamp_in_output
        )
        include_timestamp_label = ttk.Label(
            select_file_number_frame, text="Include timestamp in generated HDL files", width=40
        )
        include_timestamp_checkbox.grid(row=0, column=0, sticky=tk.W)
        include_timestamp_label.grid(row=0, column=1, sticky=tk.W)
        self.select_file_number_radio_button1.grid(row=0, column=2, sticky=tk.W)
        self.select_file_number_radio_button2.grid(row=0, column=3, sticky=tk.W)

        self.reset_signal_name = tk.StringVar()
        project_manager.reset_signal_name = self.reset_signal_name
        self.reset_signal_name.set("")
        reset_signal_name_label = ttk.Label(control_frame, text="Name of asynchronous reset input port:", padding=5)
        reset_signal_name_entry = ttk.Entry(control_frame, width=23, textvariable=self.reset_signal_name)
        reset_signal_name_label.grid(row=4, column=0, sticky=tk.W)
        reset_signal_name_entry.grid(row=4, column=1, sticky=tk.W)

        self.clock_signal_name = tk.StringVar()
        project_manager.clock_signal_name = self.clock_signal_name
        self.clock_signal_name.set("")
        clock_signal_name_label = ttk.Label(control_frame, text="Name of clock input port:", padding=5)
        self.clock_signal_name_entry = ttk.Entry(control_frame, width=23, textvariable=self.clock_signal_name)
        clock_signal_name_label.grid(row=5, column=0, sticky=tk.W)
        self.clock_signal_name_entry.grid(row=5, column=1, sticky=tk.W)

        self.compile_cmd = tk.StringVar()
        project_manager.compile_cmd = self.compile_cmd
        self.compile_cmd.set("ghdl -a $file1 $file2; ghdl -e $name; ghdl -r $name")
        compile_cmd_label = ttk.Label(control_frame, text="Compile command:", padding=5)
        compile_cmd_entry = ttk.Entry(control_frame, width=23, textvariable=self.compile_cmd)
        compile_cmd_label.grid(row=6, column=0, sticky=tk.W)
        compile_cmd_entry.grid(row=6, column=1, sticky="ew")

        self.compile_cmd_docu = ttk.Label(
            control_frame,
            text="Variables for compile command:\n$file1\t= Entity-File\n$file2\t= Architecture-File\n"
            "$file\t= File with Entity and Architecture\n$name\t= Module Name",
            padding=5,
        )
        self.compile_cmd_docu.grid(row=7, column=1, sticky=tk.W)

        self.edit_cmd = tk.StringVar()
        project_manager.edit_cmd = self.edit_cmd
        self.edit_cmd.set("C:/Program Files/Notepad++/notepad++.exe -nosession -multiInst")
        edit_cmd_label = ttk.Label(control_frame, text="Edit command (executed by Ctrl+e):", padding=5)
        edit_cmd_entry = ttk.Entry(control_frame, width=23, textvariable=self.edit_cmd)
        edit_cmd_label.grid(row=8, column=0, sticky=tk.W)
        edit_cmd_entry.grid(row=8, column=1, sticky="ew")

        self.additional_sources_value = tk.StringVar(value="")
        project_manager.additional_sources_value = self.additional_sources_value
        additional_sources_label = ttk.Label(
            control_frame,
            text="Additional sources:\n(used only by HDL-SCHEM-Editor, must\nbe added manually to compile command)",
            padding=5,
        )
        additional_sources_entry = ttk.Entry(control_frame, textvariable=self.additional_sources_value, width=80)
        additional_sources_button = ttk.Button(
            control_frame, text="Select...", command=self._add_path, style="Path.TButton"
        )
        additional_sources_label.grid(row=9, column=0, sticky=tk.W)
        additional_sources_entry.grid(row=9, column=1, sticky=(tk.W, tk.E))
        additional_sources_button.grid(row=9, column=2, sticky=(tk.W, tk.E))

        self.working_directory_value = tk.StringVar(value="")
        project_manager.working_directory_value = self.working_directory_value
        working_directory_label = ttk.Label(control_frame, text="Working directory:", padding=5)
        working_directory_entry = ttk.Entry(control_frame, textvariable=self.working_directory_value, width=80)
        working_directory_button = ttk.Button(
            control_frame, text="Select...", command=self._set_working_directory, style="Path.TButton"
        )
        working_directory_label.grid(row=10, column=0, sticky=tk.W)
        working_directory_entry.grid(row=10, column=1, sticky="ew")
        working_directory_button.grid(row=10, column=2, sticky="ew")

        self.diagram_background_color = tk.StringVar(value="white")
        project_manager.diagram_background_color = self.diagram_background_color
        self.diagram_background_color.trace_add("write", lambda *args: self._change_color_of_diagram_background())
        diagram_background_color_label = ttk.Label(control_frame, text="Diagram background color:", padding=5)
        diagram_background_color_entry = ttk.Entry(control_frame, textvariable=self.diagram_background_color, width=80)
        diagram_background_color_button = ttk.Button(
            control_frame, text="Choose color...", command=self.choose_bg_color, style="Path.TButton"
        )
        diagram_background_color_label.grid(row=11, column=0, sticky=tk.W)
        diagram_background_color_entry.grid(row=11, column=1, sticky="ew")
        diagram_background_color_button.grid(row=11, column=2, sticky="ew")
        diagram_background_color_error = ttk.Label(control_frame, text="", padding=5)
        project_manager.diagram_background_color_error = diagram_background_color_error
        diagram_background_color_error.grid(row=12, column=1, sticky=tk.W)

        self._module_name_trace_id = None
        self._language_trace_id = None
        self._generate_path_trace_id = None
        self._select_file_number_trace_id = None
        self._include_timestamp_trace_id = None
        self._reset_signal_name_trace_id = None
        self._clock_signal_name_trace_id = None
        self._compile_cmd_trace_id = None
        self._edit_cmd_trace_id = None
        self._additional_sources_trace_id = None
        self._working_directory_trace_id = None
        self._diagram_background_color_trace_id = None
        self.activate_traces()

        project_manager.notebook.add(control_frame, sticky="nsew", text=GuiTab.CONTROL.value)

        # The key "stringvar" is used for searching in variables, the key "entry" is used for selecting a hit.
        project_manager.entry_widgets = [
            {"stringvar": self.module_name, "entry": self.module_name_entry},
            {"stringvar": self.generate_path_value, "entry": generate_path_entry},
            {"stringvar": self.reset_signal_name, "entry": reset_signal_name_entry},
            {"stringvar": self.clock_signal_name, "entry": self.clock_signal_name_entry},
            {"stringvar": self.compile_cmd, "entry": compile_cmd_entry},
            {"stringvar": self.edit_cmd, "entry": edit_cmd_entry},
            {"stringvar": self.additional_sources_value, "entry": additional_sources_entry},
            {"stringvar": self.working_directory_value, "entry": working_directory_entry},
        ]

    def switch_language_mode(self) -> None:  # also called from file_handling.py
        """Apply current language (VHDL/Verilog): update highlight dict, file count, labels, and layout."""
        new_language = project_manager.language.get()
        if new_language == "VHDL" and self.last_language != "VHDL":
            self.last_language = "VHDL"
            project_manager.highlight_dict_ref.highlight_pattern_dict = copy.deepcopy(
                constants.VHDL_HIGHLIGHT_PATTERN_DICT
            )
            project_manager.highlight_dict_ref.highlight_pattern_dict["not_read"].clear()
            project_manager.highlight_dict_ref.highlight_pattern_dict["not_written"].clear()
            # enable 2 files mode
            project_manager.select_file_number_text.set(2)
            self.select_file_number_radio_button1.grid(row=0, column=2, sticky=tk.E)
            self.select_file_number_radio_button2.grid(row=0, column=3, sticky=tk.E)
            # Interface: Adapt documentation for generics and ports
            project_manager.tab_interface_ref.paned_window.insert(
                0, project_manager.tab_interface_ref.interface_package_frame, weight=1
            )
            project_manager.tab_interface_ref.interface_generics_label.config(text="Generics:")
            # Internals: Enable VHDL-package text field
            project_manager.tab_internals_ref.paned_window.insert(
                0, project_manager.tab_internals_ref.internals_package_frame, weight=1
            )
            # Internals: Architecture-Declarations (adapt labels to VHDL)
            project_manager.tab_internals_ref.internals_architecture_label.config(text="Architecture Declarations:")
            project_manager.tab_internals_ref.internals_process_clocked_label.config(
                text="Variable Declarations for clocked process:"
            )
            project_manager.tab_internals_ref.internals_process_combinatorial_label.config(
                text="Variable Declarations for combinatorial process:"
            )
            # Modify compile command:
            project_manager.compile_cmd.set("ghdl -a $file1 $file2; ghdl -e $name; ghdl -r $name")
            self.compile_cmd_docu.config(
                text="Variables for compile command:\n$file1\t= Entity-File\n$file2\t= Architecture-File\n$file\t"
                "= File with Entity and Architecture\n$name\t= Entity Name"
            )
        elif new_language != "VHDL" and self.last_language == "VHDL":
            self.last_language = new_language  # "Verilog" or "SystemVerilog"
            project_manager.highlight_dict_ref.highlight_pattern_dict = copy.deepcopy(
                constants.VERILOG_HIGHLIGHT_PATTERN_DICT
            )
            project_manager.highlight_dict_ref.highlight_pattern_dict["not_read"].clear()
            project_manager.highlight_dict_ref.highlight_pattern_dict["not_written"].clear()
            # Control: disable 2 files mode
            project_manager.select_file_number_text.set(1)
            self.select_file_number_radio_button1.grid_forget()
            self.select_file_number_radio_button2.grid_forget()
            # Interface: Remove VHDL-package text field
            project_manager.tab_interface_ref.paned_window.forget(
                project_manager.tab_interface_ref.interface_package_frame
            )
            # Interface: Adapt documentation for generics and ports
            project_manager.tab_interface_ref.interface_generics_label.config(text="Parameters:")
            # Internals: Remove VHDL-package text field
            project_manager.tab_internals_ref.paned_window.forget(
                project_manager.tab_internals_ref.internals_package_frame
            )
            # Internals: Architecture-Declarations (adapt labels to Verilog)
            project_manager.tab_internals_ref.internals_architecture_label.config(text="Internal Declarations:")
            project_manager.tab_internals_ref.internals_process_clocked_label.config(
                text="Local Variable Declarations for clocked always process (not supported by all Verilog compilers):"
            )
            project_manager.tab_internals_ref.internals_process_combinatorial_label.config(
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
            self.compile_cmd_docu.config(
                text="Variables for compile command:\n$file\t= Module-File\n$name\t= Module Name"
            )

        custom_text.CustomText.refresh_highlighting_in_all_declaration_widgets()

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
        """Open color picker and set canvas background to the chosen color."""
        new_color = ColorChanger(project_manager.canvas.cget("bg")).ask_color()
        if new_color is not None:
            project_manager.canvas.configure(bg=new_color)
            project_manager.diagram_background_color.set(new_color)

    def highlight_item(self, hdl_item_type, *_):
        """
        This method must have the same name as the method custom_text.CustomText.highlight_item.
        It is called, when in the "generated HDL"-tab module-name, the p_states line or
        the rising_edge-line are clicked per mouse to jump to its declaration.
        If hdl_item_type == "reset_and_clock_signal_name" then always the clock signal entry is selected.
        """
        if hdl_item_type == "module_name":
            self.module_name_entry.select_range(0, tk.END)
        elif hdl_item_type == "reset_and_clock_signal_name":
            self.clock_signal_name_entry.select_range(0, tk.END)

    def activate_traces(self) -> None:
        """Activate the traces for the given StringVars to mark the design as changed when they are modified."""
        self._module_name_trace_id = self.module_name.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._language_trace_id = self.language.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._generate_path_trace_id = self.generate_path_value.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._include_timestamp_trace_id = self.include_timestamp_in_output.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._select_file_number_trace_id = self.select_file_number_text.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._reset_signal_name_trace_id = self.reset_signal_name.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._clock_signal_name_trace_id = self.clock_signal_name.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._compile_cmd_trace_id = self.compile_cmd.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._edit_cmd_trace_id = self.edit_cmd.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._additional_sources_trace_id = self.additional_sources_value.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._working_directory_trace_id = self.working_directory_value.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )
        self._diagram_background_color_trace_id = self.diagram_background_color.trace_add(
            "write", lambda *args: project_manager.undo_handling_ref.design_has_changed()
        )

    def deactivate_traces(self) -> None:
        """Deactivate the traces for the given StringVars."""
        self.module_name.trace_remove("write", self._module_name_trace_id)
        self.language.trace_remove("write", self._language_trace_id)
        self.generate_path_value.trace_remove("write", self._generate_path_trace_id)
        self.select_file_number_text.trace_remove("write", self._select_file_number_trace_id)
        self.include_timestamp_in_output.trace_remove("write", self._include_timestamp_trace_id)
        self.reset_signal_name.trace_remove("write", self._reset_signal_name_trace_id)
        self.clock_signal_name.trace_remove("write", self._clock_signal_name_trace_id)
        self.compile_cmd.trace_remove("write", self._compile_cmd_trace_id)
        self.edit_cmd.trace_remove("write", self._edit_cmd_trace_id)
        self.additional_sources_value.trace_remove("write", self._additional_sources_trace_id)
        self.working_directory_value.trace_remove("write", self._working_directory_trace_id)
        self.diagram_background_color.trace_remove("write", self._diagram_background_color_trace_id)

"""
State manager for HDL-FSM-Editor.
This module provides a simple way to access application state throughout the application.
"""

import tkinter as tk
from tkinter import ttk


class ProjectManager:
    """Simple project manager - just holds the state and provides access."""

    def __init__(self) -> None:
        # Graphical elements of the GUI:
        self._root: tk.Tk = None
        self._notebook: ttk.Notebook = None
        self._canvas: tk.Canvas = None
        self._entry_widgets: list = []  # List of entry widgets of control-tab
        self._state_action_default_button: ttk.Button = None
        self._global_action_clocked_button: ttk.Button = None
        self._global_action_combinatorial_button: ttk.Button = None
        self._reset_entry_button: ttk.Button = None
        self._undo_button: ttk.Button = None
        self._redo_button: ttk.Button = None
        self._tab_control_ref = None  #: tab_control.TabControl
        self._tab_interface_ref = None  #: tab_interface.TabInterface
        self._tab_internals_ref = None  #: tab_internals.TabInternals
        self._tab_diagram_ref = None  #: tab_diagram.TabDiagram
        self._tab_hdl_ref = None  #: tab_hdl.TabHDL
        self._tab_log_ref = None  #: tab_log.TabLog
        self._menu_bar_ref = None  #: menu_bar.MenuBar
        self._diagram_background_color: tk.StringVar = None
        self._diagram_background_color_error: ttk.Label = None

        # Service objects of the GUI:
        self._link_dict_ref = None  #: link_dictionary.LinkDictionary
        self._grid_drawer = None  # : grid_drawing.GridDraw
        self._highlight_dict_ref = None  #: linting.HighLightDict
        self._write_data_creator_ref = None  #: write_data_creator.WriteDataCreator
        self._undo_handling_ref = None  #: undo_handling.UndoHandling

        # Parameters of the GUI:
        self._state_radius = 20.0
        self._priority_distance = 30
        self._reset_entry_size = 40
        self._fontsize = 10
        self._label_fontsize = 8
        self._state_name_font = None
        self._abs_zoom_factor = 5.0
        self._regex_message_find_for_vhdl: str = "(.*?):([0-9]+):[0-9]+:.*"
        self._regex_message_find_for_verilog: str = (
            "(.*?):([0-9]+): .*"  # Added ' ' after the second ':', to get no hit at time stamps (i.e. 16:58:36).
        )
        self._regex_file_name_quote: str = "\\1"
        self._regex_file_line_number_quote: str = "\\2"
        self._size_of_file1_line_number: int = 0
        self._size_of_file2_line_number: int = 0

        # Parameters of the design
        self._language: tk.StringVar = None
        self._module_name: tk.Entry = None
        self._reset_signal_name: tk.StringVar = None
        self._clock_signal_name: tk.StringVar = None

        # Parameters of the project:
        self._current_file: str = ""
        self._previous_file: str = ""
        self._generate_path_value: tk.StringVar = None
        self._working_directory_value: tk.StringVar = None
        self._additional_sources_value: tk.StringVar = None
        self._select_file_number_text: tk.IntVar = None
        self._compile_cmd: tk.Entry = None
        self._edit_cmd: tk.Entry = None
        self._include_timestamp_in_output: tk.BooleanVar = None
        self._date_of_hdl_file_shown_in_hdl_tab: float = 0.0
        self._date_of_hdl_file2_shown_in_hdl_tab: float = 0.0

    @property
    def highlight_dict_ref(self):  # -> linting.HighLightDict:
        """Get the highlight dictionary."""
        return self._highlight_dict_ref

    @highlight_dict_ref.setter
    def highlight_dict_ref(self, value):  # value : linting.HighLightDict) -> None:
        """Set the highlight dictionary."""
        self._highlight_dict_ref = value

    @property
    def state_radius(self) -> float:
        """Get the state radius."""
        return self._state_radius

    @state_radius.setter
    def state_radius(self, value: float) -> None:
        """Set the state radius."""
        self._state_radius = value

    @property
    def priority_distance(self) -> float:
        """Get the priority distance."""
        return self._priority_distance

    @priority_distance.setter
    def priority_distance(self, value: float) -> None:
        """Set the priority distance."""
        self._priority_distance = value

    @property
    def reset_entry_size(self) -> float:
        """Get the reset entry size."""
        return self._reset_entry_size

    @reset_entry_size.setter
    def reset_entry_size(self, value: float) -> None:
        """Set the reset entry size."""
        self._reset_entry_size = value

    @property
    def fontsize(self) -> int:
        """Get the font size."""
        return self._fontsize

    @fontsize.setter
    def fontsize(self, value: int) -> None:
        """Set the font size."""
        self._fontsize = value

    @property
    def state_name_font(self):
        """Get the state name font."""
        return self._state_name_font

    @state_name_font.setter
    def state_name_font(self, value) -> None:
        """Set the state name font."""
        self._state_name_font = value

    @property
    def label_fontsize(self) -> int:
        """Get the label font size."""
        return self._label_fontsize

    @label_fontsize.setter
    def label_fontsize(self, value: int) -> None:
        """Set the label font size."""
        self._label_fontsize = value

    @property
    def menu_bar_ref(self):  # -> menu_bar.MenuBar:
        """Get the menu bar reference."""
        return self._menu_bar_ref

    @menu_bar_ref.setter
    def menu_bar_ref(self, value):  # value : menu_bar.MenuBar) -> None:
        """Set the menu bar reference."""
        self._menu_bar_ref = value

    @property
    def tab_log_ref(self):  # -> tab_log.TabLog:
        """Get the tab log reference."""
        return self._tab_log_ref

    @tab_log_ref.setter
    def tab_log_ref(self, value):  # value : tab_log.TabLog) -> None:
        """Set the tab log reference."""
        self._tab_log_ref = value

    @property
    def tab_hdl_ref(self):  # -> tab_hdl.TabHDL:
        """Get the tab HDL reference."""
        return self._tab_hdl_ref

    @tab_hdl_ref.setter
    def tab_hdl_ref(self, value):  # value : tab_hdl.TabHDL) -> None:
        """Set the tab HDL reference."""
        self._tab_hdl_ref = value

    @property
    def tab_diagram_ref(self):  # -> tab_diagram.TabDiagram:
        """Get the tab diagram reference."""
        return self._tab_diagram_ref

    @tab_diagram_ref.setter
    def tab_diagram_ref(self, value):  # value : tab_diagram.TabDiagram) -> None:
        """Set the tab diagram reference."""
        self._tab_diagram_ref = value

    @property
    def tab_internals_ref(self):  # -> tab_internals.TabInternals:
        """Get the tab internals reference."""
        return self._tab_internals_ref

    @tab_internals_ref.setter
    def tab_internals_ref(self, value):  # value : tab_internals.TabInternals) -> None:
        """Set the tab internals reference."""
        self._tab_internals_ref = value

    @property
    def tab_interface_ref(self):  # -> tab_interface.TabInterface:
        """Get the tab interface reference."""
        return self._tab_interface_ref

    @tab_interface_ref.setter
    def tab_interface_ref(self, value):  # value : tab_interface.TabInterface) -> None:
        """Set the tab interface reference."""
        self._tab_interface_ref = value

    @property
    def tab_control_ref(self):  # -> tab_control.TabControl:
        """Get the tab control reference."""
        return self._tab_control_ref

    @tab_control_ref.setter
    def tab_control_ref(self, value):  # value : tab_control.TabControl) -> None:
        """Set the tab control reference."""
        self._tab_control_ref = value

    @property
    def link_dict_ref(self):  # -> link_dictionary.LinkDictionary:
        """Get the link dictionary."""
        return self._link_dict_ref

    @link_dict_ref.setter
    def link_dict_ref(self, value):  # value : link_dictionary.LinkDictionary) -> None:
        """Set the link dictionary."""
        self._link_dict_ref = value

    @property
    def date_of_hdl_file_shown_in_hdl_tab(self) -> float:
        """Get the date of HDL file shown in HDL tab."""
        return self._date_of_hdl_file_shown_in_hdl_tab

    @date_of_hdl_file_shown_in_hdl_tab.setter
    def date_of_hdl_file_shown_in_hdl_tab(self, value: float) -> None:
        """Set the date of HDL file shown in HDL tab."""
        self._date_of_hdl_file_shown_in_hdl_tab = value

    @property
    def date_of_hdl_file2_shown_in_hdl_tab(self) -> float:
        """Get the date of HDL file 2 shown in HDL tab."""
        return self._date_of_hdl_file2_shown_in_hdl_tab

    @date_of_hdl_file2_shown_in_hdl_tab.setter
    def date_of_hdl_file2_shown_in_hdl_tab(self, value: float) -> None:
        """Set the date of HDL file 2 shown in HDL tab."""
        self._date_of_hdl_file2_shown_in_hdl_tab = value

    @property
    def size_of_file1_line_number(self) -> int:
        """Get the size of file 1 line number."""
        return self._size_of_file1_line_number

    @size_of_file1_line_number.setter
    def size_of_file1_line_number(self, value: int) -> None:
        """Set the size of file 1 line number."""
        self._size_of_file1_line_number = value

    @property
    def size_of_file2_line_number(self) -> int:
        """Get the size of file 2 line number."""
        return self._size_of_file2_line_number

    @size_of_file2_line_number.setter
    def size_of_file2_line_number(self, value: int) -> None:
        """Set the size of file 2 line number."""
        self._size_of_file2_line_number = value

    @property
    def regex_file_name_quote(self) -> str:
        """Get the regex file name quote pattern."""
        return self._regex_file_name_quote

    @regex_file_name_quote.setter
    def regex_file_name_quote(self, value: str) -> None:
        """Set the regex file name quote pattern."""
        self._regex_file_name_quote = value

    @property
    def regex_file_line_number_quote(self) -> str:
        """Get the regex file line number quote pattern."""
        return self._regex_file_line_number_quote

    @regex_file_line_number_quote.setter
    def regex_file_line_number_quote(self, value: str) -> None:
        """Set the regex file line number quote pattern."""
        self._regex_file_line_number_quote = value

    @property
    def regex_message_find_for_vhdl(self) -> str:
        """Get the regex message find pattern for VHDL."""
        return self._regex_message_find_for_vhdl

    @regex_message_find_for_vhdl.setter
    def regex_message_find_for_vhdl(self, value: str) -> None:
        """Set the regex message find pattern for VHDL."""
        self._regex_message_find_for_vhdl = value

    @property
    def regex_message_find_for_verilog(self) -> str:
        """Get the regex message find pattern for Verilog."""
        return self._regex_message_find_for_verilog

    @regex_message_find_for_verilog.setter
    def regex_message_find_for_verilog(self, value: str) -> None:
        """Set the regex message find pattern for Verilog."""
        self._regex_message_find_for_verilog = value

    @property
    def undo_button(self) -> ttk.Button:
        """Get the undo button."""
        return self._undo_button

    @undo_button.setter
    def undo_button(self, value: ttk.Button) -> None:
        """Set the undo button."""
        self._undo_button = value

    @property
    def redo_button(self) -> ttk.Button:
        """Get the redo button."""
        return self._redo_button

    @redo_button.setter
    def redo_button(self, value: ttk.Button) -> None:
        """Set the redo button."""
        self._redo_button = value

    @property
    def grid_drawer(self):  # -> grid_drawing.GridDraw:
        """Get the grid drawer."""
        return self._grid_drawer

    @grid_drawer.setter
    def grid_drawer(self, value):  # -> None:
        """Set the grid drawer."""
        self._grid_drawer = value

    @property
    def reset_entry_button(self) -> ttk.Button:
        """Get the reset entry button."""
        return self._reset_entry_button

    @reset_entry_button.setter
    def reset_entry_button(self, value: ttk.Button) -> None:
        """Set the reset entry button."""
        self._reset_entry_button = value

    @property
    def global_action_clocked_button(self) -> ttk.Button:
        """Get the global action clocked button."""
        return self._global_action_clocked_button

    @global_action_clocked_button.setter
    def global_action_clocked_button(self, value: ttk.Button) -> None:
        """Set the global action clocked button."""
        self._global_action_clocked_button = value

    @property
    def global_action_combinatorial_button(self) -> ttk.Button:
        """Get the global action combinatorial button."""
        return self._global_action_combinatorial_button

    @global_action_combinatorial_button.setter
    def global_action_combinatorial_button(self, value: ttk.Button) -> None:
        """Set the global action combinatorial button."""
        self._global_action_combinatorial_button = value

    @property
    def state_action_default_button(self) -> ttk.Button:
        """Get the state action default button."""
        return self._state_action_default_button

    @state_action_default_button.setter
    def state_action_default_button(self, value: ttk.Button) -> None:
        """Set the state action default button."""
        self._state_action_default_button = value

    @property
    def include_timestamp_in_output(self) -> tk.BooleanVar:
        """Get the include timestamp in output BooleanVar."""
        return self._include_timestamp_in_output

    @include_timestamp_in_output.setter
    def include_timestamp_in_output(self, value: tk.BooleanVar) -> None:
        """Set the include timestamp in output BooleanVar."""
        self._include_timestamp_in_output = value

    @property
    def diagram_background_color_error(self) -> tk.Label:
        """Get the diagram background color error Label."""
        return self._diagram_background_color_error

    @diagram_background_color_error.setter
    def diagram_background_color_error(self, value: tk.Label) -> None:
        """Set the diagram background color error Label."""
        self._diagram_background_color_error = value

    @property
    def diagram_background_color(self) -> tk.StringVar:
        """Get the diagram background color StringVar."""
        return self._diagram_background_color

    @diagram_background_color.setter
    def diagram_background_color(self, value: tk.StringVar) -> None:
        """Set the diagram background color StringVar."""
        self._diagram_background_color = value

    @property
    def canvas(self) -> tk.Canvas:
        """Get the canvas widget."""
        return self._canvas

    @canvas.setter
    def canvas(self, value: tk.Canvas) -> None:
        """Set the canvas widget."""
        self._canvas = value

    @property
    def notebook(self) -> tk.ttk.Notebook:
        """Get the notebook widget."""
        return self._notebook

    @notebook.setter
    def notebook(self, value: tk.ttk.Notebook) -> None:
        """Set the notebook widget."""
        self._notebook = value

    @property
    def root(self) -> tk.Tk:
        """Get the root Tk widget."""
        return self._root

    @root.setter
    def root(self, value: tk.Tk) -> None:
        """Set the root Tk widget."""
        self._root = value

    @property
    def language(self) -> tk.StringVar:
        """Get the language StringVar."""
        return self._language

    @language.setter
    def language(self, value: tk.StringVar) -> None:
        """Set the language StringVar."""
        self._language = value

    @property
    def module_name(self) -> tk.Entry:
        """Get the module name Entry widget."""
        return self._module_name

    @module_name.setter
    def module_name(self, value: tk.Entry) -> None:
        """Set the module name Entry widget."""
        self._module_name = value

    @property
    def edit_cmd(self) -> tk.Entry:
        """Get the edit command Entry widget."""
        return self._edit_cmd

    @edit_cmd.setter
    def edit_cmd(self, value: tk.Entry) -> None:
        """Set the edit command Entry widget."""
        self._edit_cmd = value

    @property
    def compile_cmd(self) -> tk.Entry:
        """Get the compile command Entry widget."""
        return self._compile_cmd

    @compile_cmd.setter
    def compile_cmd(self, value: tk.Entry) -> None:
        """Set the compile command Entry widget."""
        self._compile_cmd = value

    @property
    def select_file_number_text(self) -> tk.IntVar:
        """Get the select file number IntVar."""
        return self._select_file_number_text

    @select_file_number_text.setter
    def select_file_number_text(self, value: tk.IntVar) -> None:
        """Set the select file number IntVar."""
        self._select_file_number_text = value

    @property
    def working_directory_value(self) -> tk.StringVar:
        """Get the reset signal name StringVar."""
        return self._working_directory_value

    @working_directory_value.setter
    def working_directory_value(self, value: tk.StringVar) -> None:
        """Set the reset signal name StringVar."""
        self._working_directory_value = value

    @property
    def additional_sources_value(self) -> tk.StringVar:
        """Get the additional sources StringVar."""
        return self._additional_sources_value

    @additional_sources_value.setter
    def additional_sources_value(self, value: tk.StringVar) -> None:
        """Set the additional sources StringVar."""
        self._additional_sources_value = value

    @property
    def generate_path_value(self) -> tk.StringVar:
        """Get the reset signal name StringVar."""
        return self._generate_path_value

    @generate_path_value.setter
    def generate_path_value(self, value: tk.StringVar) -> None:
        """Set the reset signal name StringVar."""
        self._generate_path_value = value

    @property
    def reset_signal_name(self) -> tk.StringVar:
        """Get the reset signal name StringVar."""
        return self._reset_signal_name

    @reset_signal_name.setter
    def reset_signal_name(self, value: tk.StringVar) -> None:
        """Set the reset signal name StringVar."""
        self._reset_signal_name = value

    @property
    def clock_signal_name(self) -> tk.StringVar:
        """Get the clock signal name StringVar."""
        return self._clock_signal_name

    @clock_signal_name.setter
    def clock_signal_name(self, value: tk.StringVar) -> None:
        """Set the clock signal name StringVar."""
        self._clock_signal_name = value

    @property
    def entry_widgets(self) -> list:
        """Get the list of entry widgets."""
        return self._entry_widgets

    @entry_widgets.setter
    def entry_widgets(self, value: list) -> None:
        """Set the list of entry widgets."""
        self._entry_widgets = value

    # @property
    # def project(self) -> Project:
    #     """Direct access to the project state."""
    #     return self._project

    @property
    def current_file(self) -> str:
        """Get the current file path."""
        return self._current_file

    @current_file.setter
    def current_file(self, value: str) -> str:
        """Set the current file path."""
        self._current_file = value

    @property
    def previous_file(self) -> str:
        """Get the previous file path."""
        return self._previous_file

    @previous_file.setter
    def previous_file(self, value: str) -> str:
        """Set the previous file path."""
        self._previous_file = value

    @property
    def abs_zoom_factor(self) -> float:
        """Get the absolute zoom factor."""
        return self._abs_zoom_factor

    @abs_zoom_factor.setter
    def abs_zoom_factor(self, value: float) -> None:
        """Set the absolute zoom factor."""
        self._abs_zoom_factor = value

    @property
    def write_data_creator_ref(self) -> float:
        """Get the write_data_creator reference."""
        return self._write_data_creator_ref

    @write_data_creator_ref.setter
    def write_data_creator_ref(self, value: float) -> None:
        """Set the write_data_creator reference."""
        self._write_data_creator_ref = value

    @property
    def undo_handling_ref(self) -> float:
        """Get the undo_handling reference."""
        return self._undo_handling_ref

    @undo_handling_ref.setter
    def undo_handling_ref(self, value: float) -> None:
        """Set the undo_handling reference."""
        self._undo_handling_ref = value

    # def update(self, **kwargs) -> None:
    #     """Update multiple state attributes."""
    #     for key, value in kwargs.items():
    #         self.set(key, value)

    # def reset(self) -> None:
    #     """Reset state to initial values."""
    #     self._project = Project()
    #     self._current_file = ""
    #     self._previous_file = ""


project_manager = ProjectManager()

"""
This module handling contains all needed methods for the notebook widget.
"""

import os
from tkinter import messagebox, ttk

import update_hdl_tab
from constants import GuiTab
from project_manager import project_manager
from utils.hdl_paths import get_architecture_output_path, get_primary_output_path
from utils.var_expansion import expand_generate_path

from . import tab_control, tab_diagram, tab_hdl, tab_interface, tab_internals, tab_log


class NotebookTop(ttk.Notebook):
    """
    For the top-level notebook widget a NotebookTop object is created.
    """

    def __init__(self, row, column) -> None:
        super().__init__(padding=5)
        self.grid(column=column, row=row, sticky="nsew")
        project_manager.notebook = self
        project_manager.tab_control_ref = tab_control.TabControl()
        project_manager.tab_interface_ref = tab_interface.TabInterface()
        project_manager.tab_internals_ref = tab_internals.TabInternals()
        project_manager.tab_diagram_ref = tab_diagram.TabDiagram()
        project_manager.tab_hdl_ref = tab_hdl.TabHDL()
        project_manager.tab_log_ref = tab_log.TabLog()
        self.bind("<<NotebookTabChanged>>", lambda event: self._handle_notebook_tab_changed_event())

    def _handle_notebook_tab_changed_event(self) -> None:
        self._enable_undo_redo_if_diagram_tab_is_active_else_disable()
        self._update_hdl_tab_if_necessary()
        self._if_hdl_tab_set_focus()

    def _enable_undo_redo_if_diagram_tab_is_active_else_disable(self) -> None:
        if self.index(self.select()) == 3:  # diagram-tab is active
            project_manager.canvas.bind_all("<Control-z>", lambda event: project_manager.undo_handling_ref.undo())
            project_manager.canvas.bind_all("<Control-Z>", lambda event: project_manager.undo_handling_ref.redo())
        else:
            # necessary, because if you type Control-z when another tab is active,
            # then in the diagram tab an undo would take place.
            project_manager.canvas.unbind_all("<Control-z>")
            project_manager.canvas.unbind_all("<Control-Z>")

    def _update_hdl_tab_if_necessary(self) -> None:
        if self.index(self.select()) == 4:  # HDL-tab is active
            raw_path = project_manager.generate_path_value.get()
            generate_path = expand_generate_path(raw_path, project_manager.current_file)
            module_name = project_manager.module_name.get()
            language = project_manager.language.get()
            file_count = project_manager.select_file_number_text.get()
            hdlfilename = get_primary_output_path(generate_path, module_name, language, file_count) or ""
            hdlfilename2 = get_architecture_output_path(generate_path, module_name, language, file_count) or ""
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
                        generate_path,
                        project_manager.module_name.get(),
                    )
                    project_manager.date_of_hdl_file_shown_in_hdl_tab = update_ref.get_date_of_hdl_file()
                    project_manager.date_of_hdl_file2_shown_in_hdl_tab = update_ref.get_date_of_hdl_file2()

    def _if_hdl_tab_set_focus(self) -> None:
        selected_tab_index = self.index(self.select())
        if selected_tab_index == 4:  # Index of HDL tab
            project_manager.tab_hdl_ref.hdl_frame_text.focus_set()

    def show_tab(self, tab: GuiTab) -> None:
        """Select the notebook tab whose text equals the given GuiTab value."""
        notebook_ids = self.tabs()
        for tab_id in notebook_ids:
            if self.tab(tab_id, option="text") == tab.value:
                self.select(tab_id)

"""
This module handling contains all needed methods for the notebook widget.
"""

from tkinter import ttk

import tab_control
import tab_diagram
import tab_hdl
import tab_interface
import tab_internals
import tab_log
from constants import GuiTab
from project_manager import project_manager


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

    def show_tab(self, tab: GuiTab) -> None:
        """Select the notebook tab whose text equals the given GuiTab value."""
        notebook_ids = self.tabs()
        for tab_id in notebook_ids:
            if self.tab(tab_id, option="text") == tab.value:
                self.select(tab_id)

"""Internals tab: editing of internal packages and architecture declarations."""

import tkinter as tk
from tkinter import ttk

from constants import GuiTab
from project_manager import project_manager
from widgets import custom_text

from . import sash_moving


class TabInternals:
    """Tab for editing internal packages and signals."""

    def __init__(self):

        self.paned_window = ttk.PanedWindow(project_manager.notebook, orient=tk.VERTICAL, takefocus=True)
        self.paned_window_height = 1

        self.internals_package_frame = ttk.Frame(self.paned_window)
        self.internals_package_frame.columnconfigure(0, weight=1)
        self.internals_package_frame.columnconfigure(1, weight=0)
        self.internals_package_frame.rowconfigure(0, weight=0)
        self.internals_package_frame.rowconfigure(1, weight=1)
        internals_package_label = ttk.Label(self.internals_package_frame, text="Packages:", padding=5)
        interface_package_linfo = ttk.Label(
            self.internals_package_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        self.internals_package_text = custom_text.CustomText(
            self.internals_package_frame,
            text_type="package",
            height=3,
            width=10,
            undo=True,
            font=("Courier", 10),
            wrap=tk.WORD,
        )
        internals_package_scroll = ttk.Scrollbar(
            self.internals_package_frame, orient=tk.VERTICAL, cursor="arrow", command=self.internals_package_text.yview
        )
        self.internals_package_text.config(yscrollcommand=internals_package_scroll.set)
        internals_package_label.grid(row=0, column=0, sticky=tk.W)
        interface_package_linfo.grid(row=0, column=0, sticky=tk.E)
        self.internals_package_text.grid(row=1, column=0, sticky="nsew")
        internals_package_scroll.grid(row=1, column=1, sticky="nsew")

        internals_architecture_frame = ttk.Frame(self.paned_window)
        internals_architecture_frame.columnconfigure(0, weight=1)
        internals_architecture_frame.columnconfigure(1, weight=0)
        internals_architecture_frame.rowconfigure(0, weight=0)
        internals_architecture_frame.rowconfigure(1, weight=1)
        self.internals_architecture_label = ttk.Label(
            internals_architecture_frame, text="Architecture Declarations:", padding=5
        )
        interface_architecture_info = ttk.Label(
            internals_architecture_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        self.internals_architecture_text = custom_text.CustomText(
            internals_architecture_frame,
            text_type="declarations",
            height=3,
            width=10,
            undo=True,
            font=("Courier", 10),
            wrap=tk.WORD,
        )
        internals_architecture_scroll = ttk.Scrollbar(
            internals_architecture_frame,
            orient=tk.VERTICAL,
            cursor="arrow",
            command=self.internals_architecture_text.yview,
        )
        self.internals_architecture_text.config(yscrollcommand=internals_architecture_scroll.set)
        self.internals_architecture_label.grid(row=0, column=0, sticky=tk.W)
        interface_architecture_info.grid(row=0, column=0, sticky=tk.E)
        self.internals_architecture_text.grid(row=1, column=0, sticky="nsew")
        internals_architecture_scroll.grid(row=1, column=1, sticky="nsew")

        internals_process_clocked_frame = ttk.Frame(self.paned_window)
        internals_process_clocked_frame.columnconfigure(0, weight=1)
        internals_process_clocked_frame.columnconfigure(1, weight=0)
        internals_process_clocked_frame.rowconfigure(0, weight=0)
        internals_process_clocked_frame.rowconfigure(1, weight=1)
        self.internals_process_clocked_label = ttk.Label(
            internals_process_clocked_frame, text="Variable Declarations for clocked process:", padding=5
        )
        interface_process_clocked_info = ttk.Label(
            internals_process_clocked_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        self.internals_process_clocked_text = custom_text.CustomText(
            internals_process_clocked_frame,
            text_type="variable",
            height=3,
            width=10,
            undo=True,
            font=("Courier", 10),
            wrap=tk.WORD,
        )
        internals_process_clocked_scroll = ttk.Scrollbar(
            internals_process_clocked_frame,
            orient=tk.VERTICAL,
            cursor="arrow",
            command=self.internals_process_clocked_text.yview,
        )
        self.internals_process_clocked_text.config(yscrollcommand=internals_process_clocked_scroll.set)
        self.internals_process_clocked_label.grid(row=0, column=0, sticky=tk.W)
        interface_process_clocked_info.grid(row=0, column=0, sticky=tk.E)
        self.internals_process_clocked_text.grid(row=1, column=0, sticky="nsew")
        internals_process_clocked_scroll.grid(row=1, column=1, sticky="nsew")

        internals_process_combinatorial_frame = ttk.Frame(self.paned_window)
        internals_process_combinatorial_frame.columnconfigure(0, weight=1)
        internals_process_combinatorial_frame.columnconfigure(1, weight=0)
        internals_process_combinatorial_frame.rowconfigure(0, weight=0)
        internals_process_combinatorial_frame.rowconfigure(1, weight=1)
        self.internals_process_combinatorial_label = ttk.Label(
            internals_process_combinatorial_frame, text="Variable Declarations for combinatorial process:", padding=5
        )
        interface_process_combinatorial_info = ttk.Label(
            internals_process_combinatorial_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        self.internals_process_combinatorial_text = custom_text.CustomText(
            internals_process_combinatorial_frame,
            text_type="variable",
            height=3,
            width=10,
            undo=True,
            font=("Courier", 10),
            wrap=tk.WORD,
        )
        internals_process_combinatorial_scroll = ttk.Scrollbar(
            internals_process_combinatorial_frame,
            orient=tk.VERTICAL,
            cursor="arrow",
            command=self.internals_process_combinatorial_text.yview,
        )
        self.internals_process_combinatorial_text.config(yscrollcommand=internals_process_combinatorial_scroll.set)
        self.internals_process_combinatorial_label.grid(row=0, column=0, sticky=tk.W)
        interface_process_combinatorial_info.grid(row=0, column=0, sticky=tk.E)
        self.internals_process_combinatorial_text.grid(row=1, column=0, sticky="nsew")
        internals_process_combinatorial_scroll.grid(row=1, column=1, sticky="nsew")

        self.paned_window.add(self.internals_package_frame, weight=1)
        self.paned_window.add(internals_architecture_frame, weight=1)
        self.paned_window.add(internals_process_clocked_frame, weight=1)
        self.paned_window.add(internals_process_combinatorial_frame, weight=1)
        project_manager.notebook.add(self.paned_window, sticky="nsew", text=GuiTab.INTERNALS.value)

        self.internals_package_text.bind("<Control-z>", lambda event: self.internals_package_text.undo())
        self.internals_package_text.bind("<Control-Z>", lambda event: self.internals_package_text.redo())
        self.internals_package_text.bind(
            "<Control-e>", lambda event: self.internals_package_text.edit_in_external_editor()
        )
        self.internals_package_text.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )

        self.internals_architecture_text.bind("<Control-z>", lambda event: self.internals_architecture_text.undo())
        self.internals_architecture_text.bind("<Control-Z>", lambda event: self.internals_architecture_text.redo())
        self.internals_architecture_text.bind(
            "<Control-e>", lambda event: self.internals_architecture_text.edit_in_external_editor()
        )
        self.internals_architecture_text.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )

        self.internals_process_clocked_text.bind(
            "<Control-z>", lambda event: self.internals_process_clocked_text.undo()
        )
        self.internals_process_clocked_text.bind(
            "<Control-Z>", lambda event: self.internals_process_clocked_text.redo()
        )
        self.internals_process_clocked_text.bind(
            "<Control-e>", lambda event: self.internals_process_clocked_text.edit_in_external_editor()
        )
        self.internals_process_clocked_text.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )

        self.internals_process_combinatorial_text.bind(
            "<Control-z>", lambda event: self.internals_process_combinatorial_text.undo()
        )
        self.internals_process_combinatorial_text.bind(
            "<Control-Z>", lambda event: self.internals_process_combinatorial_text.redo()
        )
        self.internals_process_combinatorial_text.bind(
            "<Control-e>", lambda event: self.internals_process_combinatorial_text.edit_in_external_editor()
        )
        self.internals_process_combinatorial_text.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )

    def adjust_sash_positions(self) -> None:
        """Adjust sash positions of paned window if the window is increased."""
        if self._abort_after_storing_new_height():
            return
        if project_manager.language.get() == "VHDL":
            text_list = [
                self.internals_package_text,
                self.internals_architecture_text,
                self.internals_process_clocked_text,
                self.internals_process_combinatorial_text,
            ]
        else:
            text_list = [
                self.internals_architecture_text,
                self.internals_process_clocked_text,
                self.internals_process_combinatorial_text,
            ]
        sash_moving.SashMover(self.paned_window, text_list)

    def _abort_after_storing_new_height(self) -> bool:
        new_height = self.paned_window.winfo_height()
        if new_height == 1:  # not yet initialized
            return True
        old_height = self.paned_window_height
        self.paned_window_height = new_height
        return self.paned_window_height < old_height

"""Internals tab: editing of internal packages and architecture declarations."""

import tkinter as tk
from tkinter import ttk

import custom_text
import undo_handling
from constants import GuiTab
from project_manager import project_manager


class TabInternals:
    """Tab for editing internal packages and signals."""

    def __init__(self):
        # global self.paned_window_internals, self.internals_package_frame

        self.paned_window_internals = ttk.PanedWindow(project_manager.notebook, orient=tk.VERTICAL, takefocus=True)

        self.internals_package_frame = ttk.Frame(self.paned_window_internals)
        self.internals_package_frame.columnconfigure(0, weight=1)
        self.internals_package_frame.columnconfigure(1, weight=0)
        self.internals_package_frame.rowconfigure(0, weight=0)
        self.internals_package_frame.rowconfigure(1, weight=1)
        _internals_package_label = ttk.Label(self.internals_package_frame, text="Packages:", padding=5)
        interface_package_info = ttk.Label(
            self.internals_package_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        internals_package_text = custom_text.CustomText(
            self.internals_package_frame, text_type="package", height=3, width=10, undo=True, font=("Courier", 10)
        )
        project_manager.internals_package_text = internals_package_text
        internals_package_text.bind("<Control-Z>", lambda event: internals_package_text.edit_redo())
        internals_package_text.bind("<Control-e>", lambda event: internals_package_text.edit_in_external_editor())
        internals_package_text.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        _internals_package_scroll = ttk.Scrollbar(
            self.internals_package_frame, orient=tk.VERTICAL, cursor="arrow", command=internals_package_text.yview
        )
        internals_package_text.config(yscrollcommand=_internals_package_scroll.set)
        _internals_package_label.grid(row=0, column=0, sticky=tk.W)
        interface_package_info.grid(row=0, column=0, sticky=tk.E)
        internals_package_text.grid(row=1, column=0, sticky="nsew")
        _internals_package_scroll.grid(row=1, column=1, sticky="nsew")
        self.paned_window_internals.add(self.internals_package_frame, weight=1)

        internals_architecture_frame = ttk.Frame(self.paned_window_internals)
        internals_architecture_frame.columnconfigure(0, weight=1)
        internals_architecture_frame.columnconfigure(1, weight=0)
        internals_architecture_frame.rowconfigure(0, weight=0)
        internals_architecture_frame.rowconfigure(1, weight=1)
        _internals_architecture_label = ttk.Label(
            internals_architecture_frame, text="Architecture Declarations:", padding=5
        )
        project_manager.internals_architecture_label = _internals_architecture_label
        interface_architecture_info = ttk.Label(
            internals_architecture_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        internals_architecture_text = custom_text.CustomText(
            internals_architecture_frame, text_type="declarations", height=3, width=10, undo=True, font=("Courier", 10)
        )
        project_manager.internals_architecture_text = internals_architecture_text
        internals_architecture_text.bind("<Control-z>", lambda event: internals_architecture_text.undo())
        internals_architecture_text.bind("<Control-Z>", lambda event: internals_architecture_text.redo())
        internals_architecture_text.bind(
            "<Control-e>", lambda event: internals_architecture_text.edit_in_external_editor()
        )
        internals_architecture_text.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        internals_architecture_scroll = ttk.Scrollbar(
            internals_architecture_frame, orient=tk.VERTICAL, cursor="arrow", command=internals_architecture_text.yview
        )
        internals_architecture_text.config(yscrollcommand=internals_architecture_scroll.set)
        _internals_architecture_label.grid(row=0, column=0, sticky=tk.W)
        interface_architecture_info.grid(row=0, column=0, sticky=tk.E)
        internals_architecture_text.grid(row=1, column=0, sticky="nsew")
        internals_architecture_scroll.grid(row=1, column=1, sticky="nsew")
        self.paned_window_internals.add(internals_architecture_frame, weight=1)

        internals_process_clocked_frame = ttk.Frame(self.paned_window_internals)
        internals_process_clocked_frame.columnconfigure(0, weight=1)
        internals_process_clocked_frame.columnconfigure(1, weight=0)
        internals_process_clocked_frame.rowconfigure(0, weight=0)
        internals_process_clocked_frame.rowconfigure(1, weight=1)
        _internals_process_clocked_label = ttk.Label(
            internals_process_clocked_frame, text="Variable Declarations for clocked process:", padding=5
        )
        project_manager.internals_process_clocked_label = _internals_process_clocked_label
        interface_process_clocked_info = ttk.Label(
            internals_process_clocked_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        internals_process_clocked_text = custom_text.CustomText(
            internals_process_clocked_frame, text_type="variable", height=3, width=10, undo=True, font=("Courier", 10)
        )
        project_manager.internals_process_clocked_text = internals_process_clocked_text
        internals_process_clocked_text.bind("<Control-z>", lambda event: internals_process_clocked_text.undo())
        internals_process_clocked_text.bind("<Control-Z>", lambda event: internals_process_clocked_text.redo())
        internals_process_clocked_text.bind(
            "<Control-e>", lambda event: internals_process_clocked_text.edit_in_external_editor()
        )
        internals_process_clocked_text.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        internals_process_clocked_scroll = ttk.Scrollbar(
            internals_process_clocked_frame,
            orient=tk.VERTICAL,
            cursor="arrow",
            command=internals_process_clocked_text.yview,
        )
        internals_process_clocked_text.config(yscrollcommand=internals_process_clocked_scroll.set)
        _internals_process_clocked_label.grid(row=0, column=0, sticky=tk.W)
        interface_process_clocked_info.grid(row=0, column=0, sticky=tk.E)
        internals_process_clocked_text.grid(row=1, column=0, sticky="nsew")
        internals_process_clocked_scroll.grid(row=1, column=1, sticky="nsew")
        self.paned_window_internals.add(internals_process_clocked_frame, weight=1)

        internals_process_combinatorial_frame = ttk.Frame(self.paned_window_internals)
        internals_process_combinatorial_frame.columnconfigure(0, weight=1)
        internals_process_combinatorial_frame.columnconfigure(1, weight=0)
        internals_process_combinatorial_frame.rowconfigure(0, weight=0)
        internals_process_combinatorial_frame.rowconfigure(1, weight=1)
        _internals_process_combinatorial_label = ttk.Label(
            internals_process_combinatorial_frame, text="Variable Declarations for combinatorial process:", padding=5
        )
        project_manager.internals_process_combinatorial_label = _internals_process_combinatorial_label
        interface_process_combinatorial_info = ttk.Label(
            internals_process_combinatorial_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        internals_process_combinatorial_text = custom_text.CustomText(
            internals_process_combinatorial_frame,
            text_type="variable",
            height=3,
            width=10,
            undo=True,
            font=("Courier", 10),
        )
        project_manager.internals_process_combinatorial_text = internals_process_combinatorial_text
        internals_process_combinatorial_text.bind(
            "<Control-z>", lambda event: internals_process_combinatorial_text.undo()
        )
        internals_process_combinatorial_text.bind(
            "<Control-Z>", lambda event: internals_process_combinatorial_text.redo()
        )
        internals_process_combinatorial_text.bind(
            "<Control-e>", lambda event: internals_process_combinatorial_text.edit_in_external_editor()
        )
        internals_process_combinatorial_text.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        internals_process_combinatorial_scroll = ttk.Scrollbar(
            internals_process_combinatorial_frame,
            orient=tk.VERTICAL,
            cursor="arrow",
            command=internals_process_combinatorial_text.yview,
        )
        internals_process_combinatorial_text.config(yscrollcommand=internals_process_combinatorial_scroll.set)
        _internals_process_combinatorial_label.grid(row=0, column=0, sticky=tk.W)
        interface_process_combinatorial_info.grid(row=0, column=0, sticky=tk.E)
        internals_process_combinatorial_text.grid(row=1, column=0, sticky="nsew")
        internals_process_combinatorial_scroll.grid(row=1, column=1, sticky="nsew")
        self.paned_window_internals.add(internals_process_combinatorial_frame, weight=1)

        project_manager.notebook.add(self.paned_window_internals, sticky="nsew", text=GuiTab.INTERNALS.value)

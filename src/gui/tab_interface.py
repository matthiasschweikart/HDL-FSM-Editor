"""Interface tab: editing of packages, generics, and signals (entity/port view)."""

import tkinter as tk
from tkinter import ttk

from constants import GuiTab
from project_manager import project_manager
from widgets import custom_text

from . import sash_moving


class TabInterface:
    """Tab for editing interface packages and signals."""

    def __init__(self) -> None:
        self.paned_window_interface = ttk.PanedWindow(project_manager.notebook, orient=tk.VERTICAL, takefocus=True)
        self.paned_window_interface_height = None

        self.interface_package_frame = ttk.Frame(self.paned_window_interface)
        self.interface_package_frame.columnconfigure(0, weight=1)
        self.interface_package_frame.columnconfigure(1, weight=0)
        self.interface_package_frame.rowconfigure(0, weight=0)
        self.interface_package_frame.rowconfigure(1, weight=1)
        self.interface_package_label = ttk.Label(self.interface_package_frame, text="Packages:", padding=5)
        interface_package_info = ttk.Label(
            self.interface_package_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        self.interface_package_text = custom_text.CustomText(
            self.interface_package_frame,
            text_type="package",
            height=3,
            width=10,
            undo=True,
            font=("Courier", 10),
            wrap=tk.WORD,
        )
        project_manager.interface_package_text = self.interface_package_text
        self.interface_package_text.insert("1.0", "library ieee;\nuse ieee.std_logic_1164.all;")
        self.interface_package_text.update_highlight_tags(
            10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
        )
        self.interface_package_text.bind("<Control-Z>", lambda event: self.interface_package_text.edit_redo())
        self.interface_package_text.bind(
            "<Control-e>", lambda event: self.interface_package_text.edit_in_external_editor()
        )
        self.interface_package_text.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )
        _interface_package_scroll = ttk.Scrollbar(
            self.interface_package_frame, orient=tk.VERTICAL, cursor="arrow", command=self.interface_package_text.yview
        )
        self.interface_package_text.config(yscrollcommand=_interface_package_scroll.set)
        self.interface_package_label.grid(row=0, column=0, sticky="wns")
        interface_package_info.grid(row=0, column=0, sticky=tk.E)
        self.interface_package_text.grid(row=1, column=0, sticky="nsew")
        _interface_package_scroll.grid(row=1, column=1, sticky="nsew")

        self.interface_generics_frame = ttk.Frame(self.paned_window_interface)
        self.interface_generics_frame.columnconfigure(0, weight=1)
        self.interface_generics_frame.columnconfigure(1, weight=0)
        self.interface_generics_frame.rowconfigure(0, weight=0)
        self.interface_generics_frame.rowconfigure(1, weight=1)
        self.interface_generics_label = ttk.Label(self.interface_generics_frame, text="Generics:", padding=5)
        project_manager.interface_generics_label = self.interface_generics_label
        interface_generics_info = ttk.Label(
            self.interface_generics_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        self.interface_generics_text = custom_text.CustomText(
            self.interface_generics_frame,
            text_type="generics",
            height=3,
            width=10,
            undo=True,
            font=("Courier", 10),
            wrap=tk.WORD,
        )
        project_manager.interface_generics_text = self.interface_generics_text
        self.interface_generics_text.bind("<Control-Z>", lambda event: self.interface_generics_text.edit_redo())
        self.interface_generics_text.bind(
            "<Control-e>", lambda event: self.interface_generics_text.edit_in_external_editor()
        )
        self.interface_generics_text.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )
        interface_generics_scroll = ttk.Scrollbar(
            self.interface_generics_frame,
            orient=tk.VERTICAL,
            cursor="arrow",
            command=self.interface_generics_text.yview,
        )
        self.interface_generics_text.config(yscrollcommand=interface_generics_scroll.set)
        self.interface_generics_label.grid(row=0, column=0, sticky="wns")
        interface_generics_info.grid(row=0, column=0, sticky=tk.E)
        self.interface_generics_text.grid(row=1, column=0, sticky="nsew")
        interface_generics_scroll.grid(row=1, column=1, sticky="nsew")

        interface_ports_frame = ttk.Frame(self.paned_window_interface)
        interface_ports_frame.columnconfigure(0, weight=1)
        interface_ports_frame.columnconfigure(1, weight=0)
        interface_ports_frame.rowconfigure(0, weight=0)
        interface_ports_frame.rowconfigure(1, weight=1)
        self.interface_ports_label = ttk.Label(interface_ports_frame, text="Ports:", padding=5)
        project_manager.interface_ports_label = self.interface_ports_label
        interface_ports_info = ttk.Label(interface_ports_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5)
        self.interface_ports_text = custom_text.CustomText(
            interface_ports_frame, text_type="ports", height=3, width=10, undo=True, font=("Courier", 10), wrap=tk.WORD
        )
        project_manager.interface_ports_text = self.interface_ports_text
        self.interface_ports_text.bind("<Control-z>", lambda event: self.interface_ports_text.undo())
        self.interface_ports_text.bind("<Control-Z>", lambda event: self.interface_ports_text.redo())
        self.interface_ports_text.bind("<Control-e>", lambda event: self.interface_ports_text.edit_in_external_editor())
        self.interface_ports_text.bind(
            "<<TextModified>>", lambda event: project_manager.undo_handling_ref.update_window_title()
        )
        interface_ports_scroll = ttk.Scrollbar(
            interface_ports_frame, orient=tk.VERTICAL, cursor="arrow", command=self.interface_ports_text.yview
        )
        self.interface_ports_text.config(yscrollcommand=interface_ports_scroll.set)
        self.interface_ports_label.grid(row=0, column=0, sticky=tk.W)
        interface_ports_info.grid(row=0, column=0, sticky=tk.E)
        self.interface_ports_text.grid(row=1, column=0, sticky="nsew")
        interface_ports_scroll.grid(row=1, column=1, sticky="nsew")

        self.paned_window_interface.add(self.interface_package_frame, weight=1)
        self.paned_window_interface.add(interface_ports_frame, weight=1)
        self.paned_window_interface.add(self.interface_generics_frame, weight=1)
        project_manager.notebook.add(self.paned_window_interface, sticky="nsew", text=GuiTab.INTERFACE.value)

    def adjust_sash_positions(self) -> None:
        """Adjust sash positions of paned window if the window is increased."""
        if self._abort_after_storing_new_height():
            return
        if project_manager.language.get() == "VHDL":
            text_list = [self.interface_package_text, self.interface_ports_text, self.interface_generics_text]
        else:
            text_list = [self.interface_ports_text, self.interface_generics_text]
        sash_moving.SashMover(self.paned_window_interface, text_list)

    def _abort_after_storing_new_height(self) -> bool:
        new_height = self.paned_window_interface.winfo_height()
        if new_height == 1:  # not yet initialized
            return True
        old_height = self.paned_window_interface_height
        self.paned_window_interface_height = new_height
        return (
            old_height is None or self.paned_window_interface_height < old_height
        )  # not initialized or height reduced

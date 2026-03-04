"""Interface tab: editing of packages, generics, and signals (entity/port view)."""

import tkinter as tk
from tkinter import ttk

import custom_text
import undo_handling
from constants import GuiTab
from project_manager import project_manager


class TabInterface:
    """Tab for editing interface packages and signals."""

    def __init__(self) -> None:
        self.paned_window_interface = ttk.PanedWindow(project_manager.notebook, orient=tk.VERTICAL, takefocus=True)

        self.interface_package_frame = ttk.Frame(self.paned_window_interface)
        self.interface_package_frame.columnconfigure(0, weight=1)
        self.interface_package_frame.columnconfigure(1, weight=0)
        self.interface_package_frame.rowconfigure(0, weight=0)
        self.interface_package_frame.rowconfigure(1, weight=1)
        _interface_package_label = ttk.Label(self.interface_package_frame, text="Packages:", padding=5)
        interface_package_info = ttk.Label(
            self.interface_package_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5
        )
        interface_package_text = custom_text.CustomText(
            self.interface_package_frame, text_type="package", height=3, width=10, undo=True, font=("Courier", 10)
        )
        project_manager.interface_package_text = interface_package_text
        interface_package_text.insert("1.0", "library ieee;\nuse ieee.std_logic_1164.all;")
        interface_package_text.update_highlight_tags(
            10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
        )
        interface_package_text.bind("<Control-Z>", lambda event: interface_package_text.edit_redo())
        interface_package_text.bind("<Control-e>", lambda event: interface_package_text.edit_in_external_editor())
        interface_package_text.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        _interface_package_scroll = ttk.Scrollbar(
            self.interface_package_frame, orient=tk.VERTICAL, cursor="arrow", command=interface_package_text.yview
        )
        interface_package_text.config(yscrollcommand=_interface_package_scroll.set)
        _interface_package_label.grid(row=0, column=0, sticky="wns")
        interface_package_info.grid(row=0, column=0, sticky=tk.E)
        interface_package_text.grid(row=1, column=0, sticky="nsew")
        _interface_package_scroll.grid(row=1, column=1, sticky="nsew")
        self.paned_window_interface.add(self.interface_package_frame, weight=1)

        interface_generics_frame = ttk.Frame(self.paned_window_interface)
        interface_generics_frame.columnconfigure(0, weight=1)
        interface_generics_frame.columnconfigure(1, weight=0)
        interface_generics_frame.rowconfigure(0, weight=0)
        interface_generics_frame.rowconfigure(1, weight=1)
        _interface_generics_label = ttk.Label(interface_generics_frame, text="Generics:", padding=5)
        project_manager.interface_generics_label = _interface_generics_label
        interface_generics_info = ttk.Label(interface_generics_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5)
        interface_generics_text = custom_text.CustomText(
            interface_generics_frame, text_type="generics", height=3, width=10, undo=True, font=("Courier", 10)
        )
        project_manager.interface_generics_text = interface_generics_text
        interface_generics_text.bind("<Control-Z>", lambda event: interface_generics_text.edit_redo())
        interface_generics_text.bind("<Control-e>", lambda event: interface_generics_text.edit_in_external_editor())
        interface_generics_text.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        interface_generics_scroll = ttk.Scrollbar(
            interface_generics_frame, orient=tk.VERTICAL, cursor="arrow", command=interface_generics_text.yview
        )
        interface_generics_text.config(yscrollcommand=interface_generics_scroll.set)
        _interface_generics_label.grid(row=0, column=0, sticky="wns")
        interface_generics_info.grid(row=0, column=0, sticky=tk.E)
        interface_generics_text.grid(row=1, column=0, sticky="nsew")
        interface_generics_scroll.grid(row=1, column=1, sticky="nsew")
        self.paned_window_interface.add(interface_generics_frame, weight=1)

        interface_ports_frame = ttk.Frame(self.paned_window_interface)
        interface_ports_frame.columnconfigure(0, weight=1)
        interface_ports_frame.columnconfigure(1, weight=0)
        interface_ports_frame.rowconfigure(0, weight=0)
        interface_ports_frame.rowconfigure(1, weight=1)
        _interface_ports_label = ttk.Label(interface_ports_frame, text="Ports:", padding=5)
        project_manager.interface_ports_label = _interface_ports_label
        interface_ports_info = ttk.Label(interface_ports_frame, text="Undo/Redo: Ctrl-z/Ctrl-Z,Ctrl-y", padding=5)
        interface_ports_text = custom_text.CustomText(
            interface_ports_frame, text_type="ports", height=3, width=10, undo=True, font=("Courier", 10)
        )
        project_manager.interface_ports_text = interface_ports_text
        interface_ports_text.bind("<Control-z>", lambda event: interface_ports_text.undo())
        interface_ports_text.bind("<Control-Z>", lambda event: interface_ports_text.redo())
        interface_ports_text.bind("<Control-e>", lambda event: interface_ports_text.edit_in_external_editor())
        interface_ports_text.bind("<<TextModified>>", lambda event: undo_handling.update_window_title())
        interface_ports_scroll = ttk.Scrollbar(
            interface_ports_frame, orient=tk.VERTICAL, cursor="arrow", command=interface_ports_text.yview
        )
        interface_ports_text.config(yscrollcommand=interface_ports_scroll.set)
        _interface_ports_label.grid(row=0, column=0, sticky=tk.W)
        interface_ports_info.grid(row=0, column=0, sticky=tk.E)
        interface_ports_text.grid(row=1, column=0, sticky="nsew")
        interface_ports_scroll.grid(row=1, column=1, sticky="nsew")
        self.paned_window_interface.add(interface_ports_frame, weight=1)

        project_manager.notebook.add(self.paned_window_interface, sticky="nsew", text=GuiTab.INTERFACE.value)

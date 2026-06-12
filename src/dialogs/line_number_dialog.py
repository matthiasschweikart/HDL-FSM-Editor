"""
This class lets the user define a line number to jump to.
"""

import tkinter as tk
from tkinter import ttk

from codegen import hdl_generation
from project_manager import project_manager


class LineNumberDialog:
    """This class lets the user define a line number to jump to."""

    def __init__(self):
        self.window = tk.Toplevel(project_manager.root)
        self.window.title("HFE:")

        header = ttk.Label(self.window, text="Enter line number to jump to:", width=35, anchor="center")
        frame1 = ttk.Frame(self.window)
        frame2 = ttk.Frame(self.window)
        header.grid(row=0, column=0, sticky="we")
        frame1.grid(row=1, column=0, sticky="we")
        frame2.grid(row=2, column=0, sticky="we")

        line_number = tk.IntVar()
        self.line_number_entry = ttk.Entry(frame1, textvariable=line_number, width=10)
        self.line_number_entry.focus_set()
        self.line_number_entry.grid(row=0, column=1, pady=5)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(2, weight=1)

        self.file_var = tk.IntVar()
        if project_manager.language.get() == "VHDL" and project_manager.select_file_number_text.get() == 2:
            self.file_var.set(2)
            radio1 = ttk.Radiobutton(frame2, takefocus=False, variable=self.file_var, text="in Architecture", value=2)
            radio2 = ttk.Radiobutton(frame2, takefocus=False, variable=self.file_var, text="in Entity", value=1)
            radio1.grid(row=0, column=0)
            radio2.grid(row=0, column=1)
        else:
            self.file_var.set(1)
        button1 = ttk.Button(frame2, text="OK", command=self._jump, padding=5)
        button2 = ttk.Button(frame2, text="Cancel", command=self.window.destroy, padding=5)
        button1.grid(row=1, column=0)
        button2.grid(row=1, column=1)
        frame2.columnconfigure(0, weight=1)
        frame2.columnconfigure(1, weight=1)
        self.line_number_entry.bind("<Return>", lambda e: self._jump())

    def _jump(self):
        project_manager.tab_hdl_ref.hdl_frame_text.tag_delete("goto-line")
        line_number = self.line_number_entry.get().strip()
        if not line_number.isdigit():
            return
        if self.file_var.get() == 1:
            project_manager.tab_hdl_ref.hdl_frame_text.see(f"{line_number}.0")
            project_manager.tab_hdl_ref.hdl_frame_text.tag_add(
                "goto-line", f"{line_number}.0", f"{int(line_number) + 1}.0"
            )
        else:
            project_manager.tab_hdl_ref.hdl_frame_text.see(
                f"{int(line_number) + hdl_generation.HdlGeneration.last_line_number_of_file1}.0"
            )
            project_manager.tab_hdl_ref.hdl_frame_text.tag_add(
                "goto-line",
                f"{int(line_number) + hdl_generation.HdlGeneration.last_line_number_of_file1}.0",
                f"{int(line_number) + 1 + hdl_generation.HdlGeneration.last_line_number_of_file1}.0",
            )
        project_manager.tab_hdl_ref.hdl_frame_text.tag_configure("goto-line", background="yellow")
        self.window.destroy()

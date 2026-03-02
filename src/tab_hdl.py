"""HDL tab: displays and manages the generated HDL code in the notebook."""

import re
import tkinter as tk
from tkinter import ttk

import custom_text
from codegen import hdl_generation
from codegen.hdl_generation_config import GenerationConfig
from constants import GuiTab
from project_manager import project_manager


class TabHDL:
    """Module for creating and managing the HDL Notebook Tab."""

    def __init__(self) -> None:
        self._line_number_under_pointer_hdl_tab: int = 0
        self._func_id_jump: str | None = None

        hdl_frame = ttk.Frame(project_manager.notebook)
        hdl_frame.grid()
        hdl_frame.columnconfigure(0, weight=1)
        hdl_frame.rowconfigure(0, weight=1)

        hdl_frame_text = custom_text.CustomText(hdl_frame, text_type="generated", undo=False, font=("Courier", 10))
        project_manager.hdl_frame_text = hdl_frame_text
        hdl_frame_text.grid(row=0, column=0, sticky="nsew")
        hdl_frame_text.columnconfigure((0, 0), weight=1)
        hdl_frame_text.config(state=tk.DISABLED)

        hdl_frame_text_scroll = ttk.Scrollbar(
            hdl_frame, orient=tk.VERTICAL, cursor="arrow", command=hdl_frame_text.yview
        )
        hdl_frame_text.config(yscrollcommand=hdl_frame_text_scroll.set)
        hdl_frame_text_scroll.grid(row=0, column=1, sticky="nsew")

        hdl_frame_text.bind("<Motion>", self._cursor_move_hdl_tab)

        project_manager.notebook.add(hdl_frame, sticky="nsew", text=GuiTab.GENERATED_HDL.value)

    def _cursor_move_hdl_tab(self, *_) -> None:
        if project_manager.hdl_frame_text.get("1.0", tk.END + "- 1 char") == "":
            return
        # Determine current cursor position:
        delta_x = project_manager.hdl_frame_text.winfo_pointerx() - project_manager.hdl_frame_text.winfo_rootx()
        delta_y = project_manager.hdl_frame_text.winfo_pointery() - project_manager.hdl_frame_text.winfo_rooty()
        index_string = project_manager.hdl_frame_text.index(
            f"@{delta_x},{delta_y}"
        )  # index_string has the format "1.34"
        # Determine current line number:
        line_number = int(re.sub(r"\..*", "", index_string))  # Remove everything after '.'
        # Check if cursor is on a different line than before:
        if line_number != self._line_number_under_pointer_hdl_tab:
            project_manager.hdl_frame_text.tag_delete("underline")  # remove previous underline
            config = GenerationConfig.from_main_window()
            if line_number > hdl_generation.last_line_number_of_file1:
                # Cursor is in file 2 (architecture file)
                line_number_in_file = line_number - hdl_generation.last_line_number_of_file1
                selected_file = config.get_architecture_file()
                start_index = project_manager.size_of_file2_line_number
            else:
                line_number_in_file = line_number
                selected_file = config.get_primary_file()
                start_index = project_manager.size_of_file1_line_number
            while project_manager.hdl_frame_text.get(f"{line_number}.{start_index - 1}") == " ":
                start_index += 1  # leading blanks shall not be underlined
            if project_manager.link_dict_ref.has_link(selected_file, line_number_in_file):
                project_manager.hdl_frame_text.tag_add(  # add tag for all characters until end of line
                    "underline", f"{line_number}.{start_index - 1}", f"{line_number + 1}.0"
                )
                project_manager.hdl_frame_text.tag_config("underline", underline=1)  # activate underline
                self._func_id_jump = project_manager.hdl_frame_text.bind(  # Bind to text widget
                    "<Control-Button-1>",
                    lambda event: project_manager.link_dict_ref.jump_to_source(selected_file, line_number_in_file),
                )
            else:
                # For this line no link exists:
                project_manager.hdl_frame_text.unbind("<Button-1>", self._func_id_jump)
                self._func_id_jump = None
            self._line_number_under_pointer_hdl_tab = line_number

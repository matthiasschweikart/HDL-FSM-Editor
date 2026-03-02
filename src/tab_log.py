"""Log tab: build/output log display with clear and regex-hyperlink options."""

import re
import tkinter as tk
from tkinter import messagebox, ttk

import custom_text
import undo_handling
from constants import GuiTab
from dialogs.regex_dialog import RegexDialog
from project_manager import project_manager


class TabLog:
    """Module for creating and managing the Log Notebook Tab."""

    def __init__(self) -> None:
        self._debug_active = False
        self._regex_error_happened = False
        self._line_number_under_pointer_log_tab: int = 0
        self._func_id_jump1 = None
        self._func_id_jump2 = None
        log_frame = ttk.Frame(project_manager.notebook)
        log_frame.grid()
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)

        log_frame_button_frame = ttk.Frame(log_frame)
        log_frame_text = custom_text.CustomText(log_frame, text_type="log", undo=False)
        project_manager.log_frame_text = log_frame_text
        log_frame_button_frame.grid(row=0, column=0, sticky="ew")
        log_frame_text.grid(row=1, column=0, sticky="nsew")
        log_frame_text.columnconfigure((0, 0), weight=1)
        log_frame_text.config(state=tk.DISABLED)

        log_frame_clear_button = ttk.Button(log_frame_button_frame, takefocus=False, text="Clear", style="Find.TButton")
        log_frame_clear_button.grid(row=0, column=0, sticky=tk.W)
        log_frame_clear_button.configure(command=self._clear_log_tab)

        log_frame_regex_button = ttk.Button(
            log_frame_button_frame, takefocus=False, text="Define Regex for Hyperlinks", style="Find.TButton"
        )
        log_frame_regex_button.grid(row=0, column=1, sticky=tk.W)
        log_frame_regex_button.config(command=self._edit_regex)

        log_frame_text_scroll = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, cursor="arrow", command=log_frame_text.yview
        )
        log_frame_text.config(yscrollcommand=log_frame_text_scroll.set)
        log_frame_text_scroll.grid(row=1, column=1, sticky="nsew")

        log_frame_text.bind("<Motion>", self._cursor_move_log_tab)

        project_manager.notebook.add(log_frame, sticky="nsew", text=GuiTab.COMPILE_MSG.value)
        self._debug_active = tk.IntVar()
        self._debug_active.set(1)  # 1: inactive, 2: active

    def _clear_log_tab(self) -> None:
        project_manager.log_frame_text.config(state=tk.NORMAL)
        project_manager.log_frame_text.delete("1.0", tk.END)
        project_manager.log_frame_text.config(state=tk.DISABLED)

    def _edit_regex(self, *_) -> None:
        """Open the regex configuration dialog and update settings if confirmed."""

        # Determine current pattern based on language
        current_pattern = (
            project_manager.regex_message_find_for_vhdl
            if project_manager.language.get() == "VHDL"
            else project_manager.regex_message_find_for_verilog
        )

        # Create and show dialog
        result = RegexDialog.ask_regex(
            parent=project_manager.root,
            language=project_manager.language.get(),
            current_pattern=current_pattern,
            current_filename_group=project_manager.regex_file_name_quote,
            current_line_number_group=project_manager.regex_file_line_number_quote,
            current_debug_active=self._debug_active.get() == 2,
        )

        if result is not None:
            # Update global variables based on language
            if project_manager.language.get() == "VHDL":
                project_manager.regex_message_find_for_vhdl = result.pattern
            else:
                project_manager.regex_message_find_for_verilog = result.pattern

            project_manager.regex_file_name_quote = result.filename_group
            project_manager.regex_file_line_number_quote = result.line_number_group
            self._debug_active.set(2 if result.debug_active else 1)

            undo_handling.design_has_changed()
            self._regex_error_happened = False

    def _cursor_move_log_tab(self, *_) -> None:
        if project_manager.log_frame_text.get("1.0", tk.END + "- 1 char") == "":
            return
        debug = self._debug_active.get() == 2
        # Determine current cursor position:
        delta_x = project_manager.log_frame_text.winfo_pointerx() - project_manager.log_frame_text.winfo_rootx()
        delta_y = project_manager.log_frame_text.winfo_pointery() - project_manager.log_frame_text.winfo_rooty()
        index_string = project_manager.log_frame_text.index(f"@{delta_x},{delta_y}")
        # Determine current line number:
        line_number = int(re.sub(r"\..*", "", index_string))
        if line_number != self._line_number_under_pointer_log_tab and self._regex_error_happened is False:
            project_manager.log_frame_text.tag_delete("underline")

            regex_message_find = (
                project_manager.regex_message_find_for_vhdl
                if project_manager.language.get() == "VHDL"
                else project_manager.regex_message_find_for_verilog
            )
            if debug:
                print("\nUsed Regex                         : ", regex_message_find)
            try:
                message_rgx = re.compile(regex_message_find)
            except re.error as e:
                self._regex_error_happened = True
                messagebox.showerror("Error in HDL-FSM-Editor by regular expression", repr(e))
                return

            content_of_line = project_manager.log_frame_text.get(str(line_number) + ".0", str(line_number + 1) + ".0")
            content_of_line = content_of_line[:-1]  # Remove return
            if message_rgx.match(content_of_line):
                file_name = message_rgx.sub(project_manager.regex_file_name_quote, content_of_line)
                if debug:
                    print("Regex found line                   : ", content_of_line)
                    print("Regex found filename (group 1)     :", '"' + file_name + '"')

                file_line_number_string = message_rgx.sub(project_manager.regex_file_line_number_quote, content_of_line)
                if file_line_number_string != content_of_line:
                    try:
                        file_line_number = int(file_line_number_string)
                    except ValueError:
                        messagebox.showerror("Error converting line number to integer:", file_line_number_string)
                        return
                    if debug:
                        print("Regex found line-number (group 2)  :", '"' + file_line_number_string + '"')
                else:
                    if debug:
                        print("Regex found no line-number         : Getting line-number by group 2 did not work.")
                    return

                if project_manager.link_dict_ref.has_link(
                    file_name, file_line_number
                ):  # For example ieee source files are not a key in link_dict.
                    if debug:
                        print("Filename and line-number are found in Link-Dictionary.")
                    project_manager.log_frame_text.tag_add(
                        "underline", str(line_number) + ".0", str(line_number + 1) + ".0"
                    )
                    project_manager.log_frame_text.tag_config("underline", underline=1, foreground="red")
                    self._func_id_jump1 = project_manager.log_frame_text.bind(
                        "<Control-Button-1>",
                        lambda event: project_manager.link_dict_ref.jump_to_source(file_name, file_line_number),
                    )
                    self._func_id_jump2 = project_manager.log_frame_text.bind(
                        "<Alt-Button-1>",
                        lambda event: project_manager.link_dict_ref.jump_to_hdl(file_name, file_line_number),
                    )
                else:
                    if debug:
                        print("Filename or line-number not found in Link-Dictionary.")
                    # Add only tag (for coloring in red), but don't underline as no link exists.
                    project_manager.log_frame_text.tag_add(
                        "underline", str(line_number) + ".0", str(line_number + 1) + ".0"
                    )

            else:
                if debug:
                    print("Regex did not match line           : ", content_of_line)
                if self._func_id_jump1 is not None:
                    project_manager.log_frame_text.unbind("<Button-1>", self._func_id_jump1)
                if self._func_id_jump2 is not None:
                    project_manager.log_frame_text.unbind("<Button-1>", self._func_id_jump2)
                self._func_id_jump1 = None
                self._func_id_jump2 = None
            self._line_number_under_pointer_log_tab = line_number

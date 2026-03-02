"""
The code was copied and extended from https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
"""

import os
import platform
import re
import subprocess
import tempfile
import tkinter as tk

import config
import constants
import file_handling
from codegen import hdl_generation_architecture_state_actions, hdl_generation_library
from elements import global_actions_combinatorial
from project_manager import project_manager
from widgets.code_editor import CodeEditor

FUNCTION_DECL_RE = re.compile(r"function\s+(\w+)", re.IGNORECASE)
VHDL_ATTRIBUTE_RE = re.compile(r"\w+\s+'\s+\w+", re.IGNORECASE)
LOOP_INDEX_RE = re.compile(r"\sfor\s+(.+?)\s+in\s", re.IGNORECASE | re.DOTALL)
PROCESS_RE = re.compile(r"process(\s|\().*?\sbegin\s.*?\send\s+process(\s*;|\s.*?;)", re.IGNORECASE | re.DOTALL)
VARIABLE_DECL_RE = re.compile(r"\svariable\s+(.*?):.*?;", re.IGNORECASE | re.DOTALL)
ASSIGN_RHS_RE = re.compile(r"=.*?;", re.IGNORECASE | re.DOTALL)
ALWAYS_RE = re.compile(r"always\s*@.*?begin", re.IGNORECASE | re.DOTALL)
WITH_SELECT_RE = re.compile(r"with\s+.*?\s+select", re.IGNORECASE | re.DOTALL)
NOT_ASSIGNMENTS_RE = re.compile(r"^[^=]*?;", re.IGNORECASE | re.MULTILINE)
WHEN_RE = re.compile(r"\swhen\s+([^\s\"\']+?)\s+=>", re.IGNORECASE | re.DOTALL)

VHDL_KEYWORD_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in constants.VHDL_KEYWORDS_FOR_SIGNAL_HANDLING
    + (
        r" process[^;]*?begin ",
        r" end\s+?process\s*?;",
        # Wrong: r" process .*?$",
        r" end\s+?case\s*?;",
        r" end\s+?if\s*?;",
        r" end\s*?;",
        r" end\s+",
        r"\(",
        r"\)",
        r"\+",
        r"\*",
        r"true",
        r"false",
        r"-",
        r"/",
        r"%",
        r"&",
        r"=>",
        r"' . '",
        r" [0-9]+ ",
        r'[^\\s]"[0-9,a-f,A-F]+"',
        r'"[0,1]+"',
        r"report\s*'.*?'",
        r'report\s*".*?"',
    )
]
DATATYPE_PATTERNS = [
    re.compile(r" " + re.escape(k) + r" ", re.IGNORECASE) for k in constants.VHDL_HIGHLIGHT_PATTERN_DICT["datatype"]
]


class CustomText(CodeEditor):
    """
    This code was copied and extended from:
    https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
    The Tk-Text-widget supports bindings described here:
    https://www.tcl-lang.org/man/tcl8.4/TkCmd/text.htm#M152
    """

    read_variables_of_all_windows = {}
    written_variables_of_all_windows = {}

    def __init__(self, *args, text_type, **kwargs) -> None:
        """A text widget that report on internal widget commands"""
        super().__init__(*args, wrap=tk.NONE, **kwargs)
        self.text_type = text_type
        # text_type is in:
        # ["package","generics","ports","variable","condition","generated","action","declarations","log","comment"]
        self.format_after_id = None
        self.update_highlight_after_id = None
        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.bind("<Tab>", lambda event: self.indent_selection())
        if platform.system() == "Windows":
            self.bind("<Shift-Tab>", lambda event: self.unindent_selection())
        else:
            self.bind("<ISO_Left_Tab>", lambda event: self.unindent_selection())
        # Overwrites the default control-o = "insert a new line", needed for opening a new file:
        self.bind("<Control-o>", lambda event: self._open())
        # After pressing a key 2 things happen:
        # 1. The new character is inserted in the text.
        # 2. format() is started
        # But as inserting the character takes a while, format() will still find the old text,
        # so it must be delayed until the character was inserted:
        self.bind(
            "<Key>", lambda event: self.format_after_idle()
        )  # This binding will be overwritten for the CustomText objects in Interface/Internals tab.
        self.bind("<Button-1>", lambda event: self.tag_delete("highlight"))
        self.signals_list = []  # Will be updated at file-read, key-event, undo/redo if text_type is a declaration.
        self.constants_list = []
        self.readable_ports_list = []
        self.writable_ports_list = []
        self.generics_list = []
        self.port_types_list = []  # Used by interface_ports_text, needed for removing port types at linting.
        self.function_names_list = []
        CustomText.read_variables_of_all_windows[self] = []
        CustomText.written_variables_of_all_windows[self] = []
        self.tag_config("message_red", foreground="red")
        self.tag_config("message_green", foreground="green")

    def _open(self) -> str:
        file_handling.open_file()
        # Prevent a second call of open_file() by bind_all binding (which is located in entry 4 of the bind-list):
        return "break"

    def _proxy(self, command, *args) -> None:
        cmd = (self._orig, command) + args
        try:
            result = self.tk.call(cmd)
            if command in ("insert", "delete", "replace"):
                self.event_generate("<<TextModified>>")
            return result
        except Exception:  # pylint: disable=broad-except
            return None

    def edit_in_external_editor(self) -> None:
        """
        Loads the text into an external editor, and after closing the editor, the text in the CustomText
        is replaced by the (possibly) modified text.
        """
        with tempfile.NamedTemporaryFile(
            suffix=".vhd" if project_manager.language.get() == "VHDL" else ".v",
            delete=False,
            mode="w",
            encoding="utf-8",
        ) as tf:
            tf.write(self.get("1.0", "end-1c"))
            tmpname = tf.name
        try:
            cmd = project_manager.edit_cmd.get().split() + [tmpname]
            subprocess.run(cmd, check=False)  # blocks efficiently
            with open(tmpname, encoding="utf-8") as f:
                new_text = f.read()
        finally:
            os.unlink(tmpname)
        self.delete("1.0", tk.END)
        self.insert("1.0", new_text)
        self.format()

    def format_after_idle(self) -> None:
        if self.text_type != "log":
            if self.format_after_id is not None:
                self.after_cancel(self.format_after_id)
            self.format_after_id = self.after(200, self.format)

    def format(self) -> None:
        """Resizes the text box, updates several lists of signals/variables, and updates the highlighting."""
        text = self.get("1.0", tk.END)
        self._update_size_of_text_box(text)
        if self.text_type in ("declarations", "variable", "action"):
            self.update_custom_text_class_signals_list()
        elif self.text_type == "ports":
            self.update_custom_text_class_ports_list()
        elif self.text_type == "generics":
            self.update_custom_text_class_generics_list()
        self._update_entry_of_this_window_in_list_of_read_and_written_variables_of_all_windows()
        self._update_highlighting_in_all_texts()

    def _update_size_of_text_box(self, text) -> None:
        nr_of_lines = 0
        nr_of_characters_in_line = 0
        max_line_length = 0
        if self not in [
            project_manager.interface_generics_text,
            project_manager.interface_package_text,
            project_manager.interface_ports_text,
            project_manager.internals_architecture_text,
            project_manager.internals_process_clocked_text,
            project_manager.internals_process_combinatorial_text,
            project_manager.internals_package_text,
        ]:
            for c in text:
                if c != "\n":
                    nr_of_characters_in_line += 1
                    max_line_length = max(nr_of_characters_in_line, max_line_length)
                else:
                    nr_of_lines += 1
                    nr_of_characters_in_line = 0
            self.config(width=max_line_length)
            self.config(height=nr_of_lines)

    def _update_highlighting_in_all_texts(self) -> None:
        # The tags "control", "datatype", "function" must only be updated in this CustomText object:
        self.update_highlight_tags(project_manager.fontsize, ["control", "datatype", "function"])
        project_manager.highlight_dict_ref.recreate_keyword_list_of_unused_signals()
        # The tags "not_read", "not_written", and "comment" must be updated in all CustomText objects:
        self._update_highlight_tags_in_all_windows_for_not_read_not_written_and_comment()

    def update_highlight_tags(self, fontsize, highlight_tag_name_list) -> None:
        """
        Updates only in this text. Called when text is changed by:
        - format()
        - starting the tool (only for highlighting the predefined VHDL library statements in Interface/Packages)
        - after opening a file
        - after undo/redo
        - after editing in external editor
        - after loading HDL into HDL-Tab
        - after HDL generation
        """
        # highlight_tag_name is in ["control", "datatype", "function", "not_read", "not_written", "comment"]
        for highlight_tag_name in highlight_tag_name_list:
            self.tag_delete(highlight_tag_name)
            self._tag_add_highlight_tag(highlight_tag_name)
            self._tag_configure_highlight_tag(highlight_tag_name, fontsize)

    def _tag_add_highlight_tag(self, highlight_tag_name) -> None:
        for highlight_search_pattern in project_manager.highlight_dict_ref.highlight_pattern_dict[highlight_tag_name]:
            if self.text_type != "comment":  # State comment text
                self._add_highlight_tag_for_single_pattern(highlight_tag_name, highlight_search_pattern)

    def _tag_configure_highlight_tag(self, highlight_tag_name, fontsize) -> None:
        if self.text_type not in ("condition", "action", "comment"):
            fontsize = 10  # Fixed fontsize for declaration text boxes.
        self.tag_configure(
            highlight_tag_name,
            foreground=config.HIGHLIGHT_COLORS[highlight_tag_name],
            font=("Courier", int(fontsize), "normal"),
        )  # int() is necessary, because fontsize can be a "real" number.

    def _add_highlight_tag_for_single_pattern(self, highlight_tag_name, highlight_search_pattern) -> None:
        copy_of_text = self.get("1.0", tk.END + "- 1 chars")
        if copy_of_text == "":
            return
        copy_of_text = self._replace_strings_and_attributes_by_blanks(copy_of_text)
        while True:
            if highlight_tag_name == "comment":
                match_object = re.search(
                    highlight_search_pattern, copy_of_text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
                )
                if not match_object:
                    break
                if match_object.start() == match_object.end():
                    break
                replace_string = " " * (match_object.end() - match_object.start())
                copy_of_text = (
                    copy_of_text[: match_object.start()] + replace_string + copy_of_text[match_object.end() :]
                )
                self.tag_add(
                    "comment",
                    "1.0 + " + str(match_object.start()) + " chars",
                    "1.0 + " + str(match_object.end()) + " chars",
                )
            else:
                # The keyword might be some strange character, when the user stumbles of the keyboard.
                # Normally this does not cause any problems, because no match_object will be created.
                # If a match object is created, it is important that the match is removed from the text.
                # For example for the keyword '.' the match is not removed.
                # So a check was inserted which checks if the text has been modified here.
                search_string = (
                    "([^a-zA-Z0-9_]|^)" + highlight_search_pattern + "([^a-zA-Z0-9_]|$)"
                )  # Prevent a hit, when the keyword is part of another word.
                try:
                    match_object = re.search(search_string, copy_of_text, flags=re.IGNORECASE)
                except re.error:
                    # Happens i.e. if search_string contains "**".
                    match_object = None
                if not match_object:
                    break
                match_start, match_end = self._remove_surrounding_characters_from_the_match(
                    match_object, highlight_search_pattern
                )
                old_text = copy_of_text
                copy_of_text = (
                    copy_of_text[:match_start] + " " * len(highlight_search_pattern) + copy_of_text[match_end:]
                )
                if copy_of_text == old_text:
                    break
                self.tag_add(
                    highlight_tag_name, "1.0 + " + str(match_start) + " chars", "1.0 + " + str(match_end) + " chars"
                )

    def _replace_strings_and_attributes_by_blanks(self, copy_of_text):
        for search_string in ["'image", "'length", '".*?"', "'.*?'"]:
            while True:
                match_object = re.search(search_string, copy_of_text, flags=re.IGNORECASE)
                if match_object:
                    if match_object.start() == match_object.end():
                        break
                    replace_string = " " * (match_object.end() - match_object.start())
                    copy_of_text = (
                        copy_of_text[: match_object.start()] + replace_string + copy_of_text[match_object.end() :]
                    )
                else:
                    break
        return copy_of_text

    def _remove_surrounding_characters_from_the_match(self, match_object, keyword) -> tuple:
        if match_object.end() - match_object.start() == len(keyword) + 2:
            return match_object.start() + 1, match_object.end() - 1
        if match_object.end() - match_object.start() == len(keyword) + 1:
            if match_object.group().endswith(keyword):
                return match_object.start() + 1, match_object.end()
            return match_object.start(), match_object.end() - 1
        return match_object.start(), match_object.end()

    def undo(self) -> None:
        """Undoes the last action and formats the text."""
        # self.edit_undo() # causes a second "undo", as Ctrl-z automatically starts edit_undo()
        self.format_after_idle()

    def redo(self) -> None:
        """Redoes the last undone action and formats the text."""
        self.edit_redo()
        self.format_after_idle()

    def update_custom_text_class_signals_list(self) -> None:
        """Updates the signals_list and constants_list of this CustomText object."""
        # ["package","generics","ports","variable","condition","generated","action","declarations","log","comment"]
        all_signal_declarations = self.get("1.0", tk.END).lower()
        all_signal_declarations = hdl_generation_library.remove_comments_and_returns(all_signal_declarations)
        all_signal_declarations = hdl_generation_library.remove_functions(all_signal_declarations)
        all_signal_declarations = hdl_generation_library.remove_type_declarations(all_signal_declarations)
        all_signal_declarations = hdl_generation_library.surround_character_by_blanks(":", all_signal_declarations)
        # For VHDL processes in "global actions combinatorial":
        all_signal_declarations = re.sub(r"process\s*\(.*?\)", "", all_signal_declarations)

        self.signals_list = hdl_generation_library.get_all_declared_signal_and_variable_names(all_signal_declarations)
        self.constants_list = hdl_generation_library.get_all_declared_constant_names(all_signal_declarations)

    def update_custom_text_class_ports_list(self) -> None:  # Needed at self==project_manager.interface_ports_text
        """Updates the port_types_list of this CustomText object, if it is the interface_ports_text"""
        all_port_declarations = self.get("1.0", tk.END).lower()
        self.readable_ports_list = hdl_generation_architecture_state_actions.get_all_readable_ports(
            all_port_declarations, check=False
        )
        self.writable_ports_list = hdl_generation_architecture_state_actions.get_all_writable_ports(
            all_port_declarations
        )
        self.port_types_list = hdl_generation_architecture_state_actions.get_all_port_types(all_port_declarations)

    def update_custom_text_class_generics_list(self) -> None:
        """Updates the generics_list of this CustomText object, if it is the interface_generics_text"""
        all_generic_declarations = project_manager.interface_generics_text.get("1.0", tk.END).lower()
        self.generics_list = hdl_generation_architecture_state_actions.get_all_generic_names(all_generic_declarations)

    def _update_entry_of_this_window_in_list_of_read_and_written_variables_of_all_windows(self) -> None:
        CustomText.read_variables_of_all_windows[self] = []
        CustomText.written_variables_of_all_windows[self] = []
        text = self.get("1.0", tk.END + "- 1 chars")
        text = hdl_generation_library.convert_hdl_lines_into_a_searchable_string(text)
        if text.isspace():
            return
        if project_manager.language.get() == "VHDL" and self == project_manager.internals_architecture_text:
            self._fill_function_names_list()
        if project_manager.language.get() == "VHDL":
            text = self._remove_loop_indices(text)
        if project_manager.language.get() == "VHDL" and self._text_is_global_actions_combinatorial():
            # "processes" are possible in this text, which might contain "uncomplete" variable usage:
            text = self._add_uncomplete_vhdl_variables_to_read_or_written_variables_of_all_windows(text)
        text = self._add_read_constants_from_case_when_to_read_variables_of_all_windows(text)  # Keywords are used here.
        text = self._remove_keywords(text)
        text = self._remove_vhdl_attributes(text)
        if project_manager.language.get() == "VHDL":
            text = re.sub(r"\..*?\s", " ", text)  # remove all record-element-names from their signal/variable names
        if self.text_type == "condition":
            text = self._remove_condition_keywords(text)
            CustomText.read_variables_of_all_windows[self] = text.split()
        elif self.text_type == "action":
            self._process_action_read_and_written_variables(text)

    def _process_action_read_and_written_variables(self, text: str) -> None:
        text = self._add_read_variables_from_procedure_calls_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_with_select_blocks_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_conditions_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_case_constructs_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_assignments_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_always_statements_to_read_variables_of_all_windows(text)
        CustomText.read_variables_of_all_windows[self] = list(set(CustomText.read_variables_of_all_windows[self]))
        # remove remaining "when" of a "case"-statement (left hand side)
        text = re.sub(" when | when$|^when |^when$", "", text, flags=re.I)
        # remove remaining "|" of a "case"-statement
        text = re.sub(r"\|", "", text, flags=re.I)
        # remove remaining "else" of an if-clause (left hand side)
        text = re.sub(" else | else$|^else |^else$", "", text, flags=re.I)

        # Store the remaining variable names and remove duplicates from the list:
        CustomText.written_variables_of_all_windows[self] = list(set(text.split()))
        # When the ";" is missing, then the right hand side with "<=" could not be found and erased.
        # So remove "<=" and ":=" from these lists:
        _remove_items_from_list(CustomText.read_variables_of_all_windows[self], ["<=", ":="])
        _remove_items_from_list(
            CustomText.read_variables_of_all_windows[self],
            project_manager.internals_architecture_text.function_names_list,
        )
        _remove_items_from_list(CustomText.read_variables_of_all_windows[self], [";", ","])
        # ';' appears at VHDL-"null" assignments.
        _remove_items_from_list(CustomText.written_variables_of_all_windows[self], [";", "<=", ":="])

    def _text_is_global_actions_combinatorial(self):
        list_of_canvas_id = project_manager.canvas.find_withtag("global_actions_combinatorial1")
        if list_of_canvas_id:
            canvas_id = list_of_canvas_id[0]
            if global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict[canvas_id].text_id == self:
                return True
        return False

    def _fill_function_names_list(self):
        self.function_names_list = []
        copy_of_text = self.get("1.0", tk.END + "- 1 chars")
        while True:
            match = FUNCTION_DECL_RE.search(copy_of_text)
            if match:
                if match.start() == match.end():
                    break
                function_name = match.group(0).split()[1]
                if function_name not in self.function_names_list:
                    self.function_names_list.append(function_name)
                copy_of_text = re.sub(match.group(0), "", copy_of_text)
            else:
                break

    def _remove_vhdl_attributes(self, text):
        search_for_attributes = r"\w+\s+'\s+\w+"  # remove signal-name and attribute; example: "paddr ' range"
        while True:
            match = re.search(search_for_attributes, text, flags=re.IGNORECASE)
            if match:
                if match.start() == match.end():
                    break
                # print("match found =", match.group(0) + "|")
                # print("index found =", match.group(1) + "|")
                text = text[: match.start()] + text[match.end() :]
            else:
                break
        return text

    def _remove_loop_indices(self, text):
        # Suchen nach "for   in"
        while True:
            match = LOOP_INDEX_RE.search(text)
            if match:
                if match.start() == match.end():
                    break
                # print("match found =", match.group(0) + "|")
                # print("index found =", match.group(1) + "|")
                text = text[: match.start()] + text[match.end() :]
                search_for_index = " " + match.group(1) + " "
                text = re.sub(search_for_index, " ", text)
            else:
                break
        return text

    def _add_uncomplete_vhdl_variables_to_read_or_written_variables_of_all_windows(self, text):
        text_list, proc_list, remaining_text = self._split_in_lists_of_text_and_processes(text)
        for p_number, process in enumerate(proc_list):
            process, all_variable_names = self._remove_variable_declarations(process)
            process, written_variables = self._remove_written_variables(process, all_variable_names)
            process, read_variables = self._remove_read_variables(process, all_variable_names)
            proc_list[p_number] = process
            self._add_to_read_or_written_variables_of_all_windows(all_variable_names, written_variables, read_variables)
        new_text = ""
        # Reconstruct the text from text_list and the modified processes from proc_list:
        for i, text_before in enumerate(text_list):
            new_text += text_before + proc_list[i]
        return new_text + remaining_text

    def _split_in_lists_of_text_and_processes(self, text):
        proc_list = []
        text_list = []
        while True:
            match = PROCESS_RE.search(text)
            if match:
                if match.start() == match.end():
                    break
                text_list.append(text[: match.start()])
                proc_list.append(text[match.start() : match.end()])
                text = text[match.end() :]  # remove before-match and match from text
            else:
                break
        return text_list, proc_list, text

    def _remove_variable_declarations(self, process):
        all_variable_names = []
        while True:
            match = VARIABLE_DECL_RE.search(process)
            if match:
                if match.start() == match.end():
                    break
                all_variable_names.append(match.group(1).strip())
                process = process[: match.start()] + " " + process[match.end() :]  # remove declaration from process
            else:
                break
        return process, all_variable_names

    def _remove_written_variables(self, process, all_variable_names):
        written_variables = []
        for variable_name in all_variable_names:
            search_for_assignment_to_variable = rf"\s{variable_name}\s*:="
            while True:
                match = re.search(search_for_assignment_to_variable, process, flags=re.IGNORECASE)
                if match:
                    if match.start() == match.end():
                        break
                    process = (
                        process[: match.start()] + " " + process[match.end() - 2 :]
                    )  # remove assigned variable-name from process (without ":=")
                    written_variables.append(variable_name)
                else:
                    break
        written_variables = list(set(written_variables))  # remove duplicates
        return process, written_variables

    def _remove_read_variables(self, process, all_variable_names):
        read_variables = []
        for variable_name in all_variable_names:
            search_for_reading_of_variable = rf"\s{variable_name}\s*"
            while True:
                match = re.search(search_for_reading_of_variable, process, flags=re.IGNORECASE)
                if match:
                    if match.start() == match.end():
                        break
                    process = (  # Insert $dummy$ to keep "case <variable> is" as a complete statement.
                        process[: match.start()] + " $dummy$ " + process[match.end() :]
                    )  # remove assigned variable-name from process
                    read_variables.append(variable_name)
                else:
                    break
        read_variables = list(set(read_variables))  # remove duplicates
        return process, read_variables

    def _add_to_read_or_written_variables_of_all_windows(self, all_variable_names, written_variables, read_variables):
        for process_variable_name in all_variable_names:
            # if process_variable_name not in written_variables:
            #     CustomText.read_variables_of_all_windows[self] += [process_variable_name]  # may be be colored red
            # elif process_variable_name not in read_variables:
            #     CustomText.written_variables_of_all_windows[self] += [process_variable_name]  # may be colored yellow
            if process_variable_name in read_variables:
                CustomText.read_variables_of_all_windows[self] += [process_variable_name]  # may be be colored red
            if process_variable_name in written_variables:
                CustomText.written_variables_of_all_windows[self] += [process_variable_name]  # may be colored yellow
        for used_variable_name in written_variables + read_variables:
            if used_variable_name not in all_variable_names:
                CustomText.read_variables_of_all_windows[self] += [used_variable_name]  # may be colored red

    def _remove_keywords(self, text):
        if project_manager.language.get() == "VHDL":
            text = self._remove_keywords_from_vhdl(text)
        else:
            text = self._remove_keywords_from_verilog(text)
        return text

    def _remove_keywords_from_vhdl(self, text):
        for pattern in VHDL_KEYWORD_PATTERNS:
            text = pattern.sub("  ", text)  # Keep the blanks the keyword is surrounded by.
        for pattern in DATATYPE_PATTERNS:
            text = pattern.sub("  ", text)  # Keep the blanks the keyword is surrounded by.
        return text

    def _remove_keywords_from_verilog(self, text):
        for keyword in constants.VERILOG_KEYWORDS_FOR_SIGNAL_HANDLING + (
            " end ",
            " endcase\\s*?;",
            "\\(",
            "\\)",
            "{",
            "}",
            "\\+",
            "-",
            "/",
            "%",
            " [0-9]+ ",  # something like 123
            " [0-9]+'[^0-9][0-9]+ ",  # something like 3'b000
        ):
            text = re.sub(keyword, "  ", text, flags=re.I)  # Keep the blanks the keyword is surrounded by.
        return text

    def _remove_condition_keywords(self, text):
        if project_manager.language.get() == "VHDL":
            for keyword in (" = ", " /= ", " < ", " <= ", " > ", " >= "):
                text = re.sub(keyword, "  ", text, flags=re.I)  # Keep the blanks the keyword is surrounded by.
        else:
            for keyword in (
                " === ",
                " == ",
                " != ",
                " < ",
                " <= ",
                " > ",
                " >= ",
                " = ",  # This is an uncomplete comparison, which shall not be identified as signal by highlighting.
                " ! ",  # This is an uncomplete comparison, which shall not be identified as signal by highlighting.
            ):
                text = re.sub(keyword, "  ", text, flags=re.I)  # Keep the blanks the keyword is surrounded by.
        return text

    def _add_read_variables_from_procedure_calls_to_read_variables_of_all_windows(self, text):
        if project_manager.language.get() != "VHDL":
            return text
        all_procedure_calls = []
        while True:
            match = NOT_ASSIGNMENTS_RE.search(text)
            if match:
                if match.start() == match.end():
                    break
                all_procedure_calls.append(match.group(0)[:-1])  # append without semicolon
                text = text[: match.start()] + text[match.end() :]  # remove match from text
            else:
                break
        for procedure_call in all_procedure_calls:
            procedure_parameters = self._remove_procedure_name(procedure_call)
            procedure_parameter_list = procedure_parameters.split(",")
            for procedure_parameter in procedure_parameter_list:
                procedure_parameter = procedure_parameter.strip()
                if (
                    procedure_parameter != ""
                    and procedure_parameter not in ["x", "X"]
                    and not procedure_parameter.isdigit()
                ):
                    # As the procedure definition may not be part of this VHDL file,
                    # it can not for sure be determined, which parameter is read and which parameter is written.
                    if procedure_parameter in project_manager.interface_ports_text.readable_ports_list:
                        # If a parameter is an input port, then it is read.
                        CustomText.read_variables_of_all_windows[self] += [procedure_parameter]
                    elif procedure_parameter in project_manager.interface_ports_text.writable_ports_list:
                        # If a parameter is an output port, then it is written and
                        # must be added to the variable text with a pseudo assignment:
                        text += procedure_parameter + " <= ;"
                    else:
                        # If a parameter is neither an input nor an output, then the parameter is probably a signal.
                        # But it is not clear if it is written or read and
                        # to avoid false alarms it is added to both lists:
                        CustomText.read_variables_of_all_windows[self] += [procedure_parameter]
                        text += procedure_parameter + " <= ;"
        return text

    def _remove_procedure_name(self, procedure_call):
        return re.sub(r"^.*?\s", "", procedure_call.lstrip())

    def _add_read_variables_from_with_select_blocks_to_read_variables_of_all_windows(self, text):
        if project_manager.language.get() == "VHDL":
            all_with_selects = []
            while True:  # Collect all with_selects and remove them from text.
                match = WITH_SELECT_RE.search(text)
                if match:
                    if match.start() == match.end():
                        break
                    all_with_selects.append(match.group(0))
                    text = text[: match.start()] + text[match.end() :]  # remove match from text
                else:
                    break
            for with_select in all_with_selects:
                with_select = re.sub("^with ", " ", with_select, flags=re.I)
                with_select = re.sub(" select$", " ", with_select, flags=re.I)
                CustomText.read_variables_of_all_windows[self] += (
                    with_select.split()
                )  # split() removes only blanks here.
        return text

    def _add_read_variables_from_conditions_to_read_variables_of_all_windows(self, text):
        if project_manager.language.get() == "VHDL":
            condition_search_pattern = (
                "^if\\s+[^;]*?\\s+then| if\\s+[^;]*?\\s+then|elsif\\s+[^;]*?\\s+then|"
                + "^when\\s+[^;]*?\\s+else| when\\s+[^;]*?\\s+else"
            )
        else:
            condition_search_pattern = "^if\\s+[^;]*?\\s+begin| if\\s+[^;]*?\\s+begin"  # Verilog
        all_conditions = []
        while True:  # Collect all conditions and remove them from text.
            # print("text for search =", text)
            match = re.search(condition_search_pattern, text, flags=re.IGNORECASE)
            if match:
                if match.start() == match.end():
                    break
                # print("match.group(0)", match.group(0))
                all_conditions.append(match.group(0))
                text = text[: match.start()] + text[match.end() :]  # remove match from text
                # print(text)
            else:
                break
        for condition in all_conditions:
            if project_manager.language.get() == "VHDL":
                condition = re.sub("^if| if", " ", condition, flags=re.I)
                condition = re.sub("^elsif| elsif", " ", condition, flags=re.I)
                condition = re.sub(" then$", " ", condition, flags=re.I)
                condition = re.sub("^when| when", " ", condition, flags=re.I)
                condition = re.sub(" else$", " ", condition, flags=re.I)
                for keyword in (" = ", " /= ", " < ", " <= ", " > ", " >= "):
                    condition = re.sub(keyword, "  ", condition)  # Keep the blanks the keyword is surrounded by.
            else:
                condition = re.sub("^if| if ", " ", condition, flags=re.I)
                condition = re.sub(" begin$", " ", condition, flags=re.I)
                for keyword in (
                    " === ",
                    " == ",
                    " != ",
                    " < ",
                    " <= ",
                    " > ",
                    " >= ",
                    " = ",  # This is an uncomplete comparison, which shall not be identified as signal by highlighting.
                    " ! ",
                ):  # This is an uncomplete comparison, which shall not be identified as signal by highlighting.
                    condition = re.sub(keyword, "  ", condition)  # Keep the blanks the keyword is surrounded by.
            CustomText.read_variables_of_all_windows[self] += condition.split()
        return text

    def _add_read_constants_from_case_when_to_read_variables_of_all_windows(self, text):
        if project_manager.language.get() == "VHDL":
            while True:
                match = WHEN_RE.search(text)
                if match:
                    if match.start() == match.end():
                        break
                    if match.group(1) != "others":
                        CustomText.read_variables_of_all_windows[self] += [match.group(1)]
                    text = text[: match.start()] + text[match.end() :]  # remove match from text
                else:
                    break
        return text

    def _add_read_variables_from_case_constructs_to_read_variables_of_all_windows(self, text):
        if project_manager.language.get() == "VHDL":
            case_search_pattern = "^case\\s+.+?\\s+is| case\\s+.+?\\s+is"
        else:
            case_search_pattern = "^case\\s*?\\(.*?\\)| case\\s*?\\(.*?\\)"  # Verilog
        all_cases = []
        while True:  # Collect all case-statements and remove them from text.
            match = re.search(case_search_pattern, text, flags=re.IGNORECASE)
            if match:
                if match.start() == match.end():
                    break
                all_cases.append(match.group(0))
                text = text[: match.start()] + text[match.end() :]  # remove match from text
            else:
                break
        for case in all_cases:
            if project_manager.language.get() == "VHDL":
                case = re.sub("^case | case ", "", case, flags=re.I)
                case = re.sub(" is$", "", case, flags=re.I)
            else:
                case = re.sub("^case\\s*?\\(| case\\s*?\\(", "", case, flags=re.I)
                case = re.sub("\\)", "", case, flags=re.I)
                case = re.sub(",", " ", case, flags=re.I)
            CustomText.read_variables_of_all_windows[self] += case.split()
        return text

    def _add_read_variables_from_assignments_to_read_variables_of_all_windows(self, text):
        while True:  # Collect all right hand sides and remove them from text.
            match = ASSIGN_RHS_RE.search(text)
            if match:
                # remove not only the match but also complete ":=" or "<=":
                if match.start() - 1 == match.end():
                    break
                text = text[: match.start() - 1] + text[match.end() :]
                hit = match.group(0)[+1:-1]
                hit = re.sub(",", "", hit)  # Remove "," of a "with .. select" statement.
                # remove remaining "when" of a "with .. select"-statement (right hand side):
                hit = re.sub(" when | when$|^when |^when$", "", hit, flags=re.I)
                # remove remaining "else" of an "when .. else"-clause (right hand side).
                hit = re.sub(" else | else$|^else |^else$", "", hit, flags=re.I)
                hit = re.sub(" ' ", "", hit, flags=re.I)  # remove remaining "ticks" of VHDL attributes
                CustomText.read_variables_of_all_windows[self] += list(set(hit.split()))  # remove duplicates from list
            else:
                break
        return text

    def _add_read_variables_from_always_statements_to_read_variables_of_all_windows(self, text):
        while True:
            match = ALWAYS_RE.search(text)
            if match:
                if match.start() == match.end():
                    break
                text = text[: match.start()] + text[match.end() :]
                hit = match.group(0)
                hit = re.sub(r"always\s*@", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"begin", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"\(", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"\)", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r" or ", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r" and ", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"posedge ", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"negedge ", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"\*", "", hit, flags=re.IGNORECASE)
                CustomText.read_variables_of_all_windows[self] += hit.split()
            else:
                break
        return text

    def highlight_item(self, _, __, number_of_line) -> None:
        """Highlights a line. Used when a line is clicked in the "Generated HDL" or "Compile Messages" text box."""
        self.tag_add("highlight", str(number_of_line) + ".0", str(number_of_line + 1) + ".0")
        self.tag_config("highlight", background="orange")
        self.see(str(number_of_line) + ".0")
        self.focus_set()

    def _update_highlight_tags_in_all_windows_for_not_read_not_written_and_comment(self) -> None:
        if self.update_highlight_after_id is not None:
            project_manager.root.after_cancel(self.update_highlight_after_id)
        self.update_highlight_after_id = project_manager.root.after(
            300, self._update_highlight_tags_in_all_windows_for_not_read_not_written_and_comment_after_idle
        )

    def _update_highlight_tags_in_all_windows_for_not_read_not_written_and_comment_after_idle(self) -> None:
        # Comment must be the last, because in the range of a comment all other tags are deleted:
        for text_ref in CustomText.read_variables_of_all_windows:
            text_ref.update_highlight_tags(project_manager.fontsize, ["not_read", "not_written", "comment"])
        for text_ref in _declaration_text_widgets():
            text_ref.update_highlight_tags(10, ["not_read", "not_written", "comment"])


def _declaration_text_widgets():
    """Text widgets that show HDL declarations (interface/internals). Used for language-aware highlighting."""
    return [
        project_manager.interface_generics_text,
        project_manager.interface_package_text,
        project_manager.interface_ports_text,
        project_manager.internals_architecture_text,
        project_manager.internals_process_clocked_text,
        project_manager.internals_process_combinatorial_text,
        project_manager.internals_package_text,
    ]


def refresh_highlighting_in_all_declaration_widgets() -> None:
    """Reapply syntax highlighting in all declaration widgets (e.g. after language change)."""
    tag_list = ["not_read", "not_written", "control", "datatype", "function", "comment"]
    for text_ref in _declaration_text_widgets():
        text_ref.update_highlight_tags(10, tag_list)
    project_manager.highlight_dict_ref.recreate_keyword_list_of_unused_signals()


def _remove_items_from_list(lst: list, items) -> None:
    for item in items:
        if item in lst:
            lst.remove(item)

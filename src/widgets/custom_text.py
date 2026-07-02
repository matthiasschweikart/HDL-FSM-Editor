"""
The code was copied and extended from https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
"""

import os
import re
import shlex
import subprocess
import tempfile
import tkinter as tk

import constants
import file_handling
from actions import canvas_editing
from codegen import hdl_generation_architecture_state_actions, hdl_generation_library
from elements import (
    condition_action,
    global_actions_clocked,
    global_actions_combinatorial,
    state_action,
    state_actions_default,
    state_comment,
)
from project_manager import project_manager
from widgets import custom_text_linting

from . import config
from .code_editor import CodeEditor


class CustomText(CodeEditor):
    """
    This code was copied and extended from:
    https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
    The Tk-Text-widget supports bindings described here:
    https://www.tcl-lang.org/man/tcl8.4/TkCmd/text.htm#M152
    """

    read_variables_of_all_windows = {}
    written_variables_of_all_windows = {}

    def __init__(self, *args, text_type, wrap=tk.NONE, **kwargs) -> None:
        """A text widget that report on internal widget commands"""
        super().__init__(*args, wrap=wrap, **kwargs)
        self.text_type = text_type
        # text_type is in:
        # ["package","generics","ports","variable","condition","generated","action","declarations","log","comment"]
        self.update_highlight_after_id = None
        self.overwrite = None
        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        # Overwrites the default control-o = "insert a new line", needed for opening a new file:
        self.bind("<Control-o>", lambda event: self._open())
        self.bind("<Key>", self.format_after_idle)
        self.bind("<Button-1>", lambda event: self.tag_delete("highlight"))  # Tag is created by links in HDL/log-tab
        self.bind("<Insert>", lambda event: self._toggle_overwrite())  # Switch between insert/overwrite mode.
        self.signals_list = []  # Will be updated at file-read, key-event, undo/redo if text_type is a declaration.
        self.constants_list = []
        self.readable_ports_list = []
        self.writable_ports_list = []
        self.generics_list = []
        self.port_types_list = []  # Used by interface_ports_text, needed for removing port types at linting.
        self.function_names_list = []
        CustomText.read_variables_of_all_windows[self] = []
        CustomText.written_variables_of_all_windows[self] = []
        self._define_text_tags(kwargs.get("font"))
        self.format_after_id = None

    def _proxy(self, command, *args) -> None:
        cmd = (self._orig, command) + args
        try:
            result = self.tk.call(cmd)
            if command in ("insert", "delete", "replace"):
                self.event_generate("<<TextModified>>")
            return result
        except Exception:  # pylint: disable=broad-except
            return None

    def _open(self) -> str:
        file_handling.open_file()
        # Prevent a second call of open_file() by bind_all binding (which is located in entry 4 of the bind-list):
        return "break"

    def _toggle_overwrite(self):
        self.overwrite = not self.overwrite
        return "break"

    def _define_text_tags(self, font):
        self.tag_configure("message_red", foreground="red")
        self.tag_configure("message_green", foreground="green")
        self.tag_configure("highlight", background="orange")
        self._provide_hdl_text_tags_for_this_font(*font)

    def _provide_hdl_text_tags_for_this_font(self, fontname, fontsize):
        """Prepare syntax highlighting format tags for custom_text."""
        for highlight_tag_name in constants.VHDL_HIGHLIGHT_PATTERN_DICT:
            self.tag_configure(
                highlight_tag_name,
                foreground=config.HIGHLIGHT_COLORS[highlight_tag_name],
                font=(
                    fontname,
                    fontsize,
                    "normal",
                ),
            )

    def edit_in_external_editor(self) -> None:
        """Open current text in external editor (blocking), then replace content with edited result."""
        with tempfile.NamedTemporaryFile(
            suffix=".vhd" if project_manager.language.get() == "VHDL" else ".v",
            delete=False,
            mode="w",
            encoding="utf-8",
        ) as tf:
            tf.write(self.get("1.0", "end-1c"))
            tmp_name = tf.name
        try:
            cmd = shlex.split(project_manager.edit_cmd.get()) + [tmp_name]
            subprocess.run(cmd, check=False)  # blocks efficiently
            with open(tmp_name, encoding="utf-8") as f:
                new_text = f.read()
        finally:
            os.unlink(tmp_name)
        self.delete("1.0", tk.END)
        self.insert("1.0", new_text)
        self.format(None)

    def format_after_idle(self, event) -> None:
        """Schedule format() after 200 ms idle (except for log text)."""
        if event is not None and event.keysym in ("Control_L", "Control_R"):  # code_editor.py uses event=None
            return  # No formatting as long as Ctrl is pressed alone.
        # Prevent the formatting of log text, which can be very long and may contain keywords by accident (which
        # shall not be highlighted) and can not be changed by key-presses:
        if self.text_type not in ("generated", "log"):
            self._delete_character_if_overwrite_mode(event)
            if self.format_after_id is not None:
                self.after_cancel(self.format_after_id)
            self.format_after_id = self.after_idle(self.format, event)

    def _delete_character_if_overwrite_mode(self, event):
        if (
            self.overwrite
            and event is not None
            and event.keysym not in ("BackSpace", "Delete", "Control_L", "Control_R")
        ):
            cursor_index = self.index(tk.INSERT)
            if self.get(cursor_index) != "\n" and self.compare(cursor_index, "<", tk.END):
                self.delete(cursor_index)

    def format(self, event) -> None:
        """Update text box size and highlighting."""
        text = self.get("1.0", tk.END)
        self._update_size_of_text_box(text)
        if self.text_type in ("declarations", "variable", "action"):
            self.update_custom_text_class_signals_list()
        elif self.text_type == "ports":
            self.update_custom_text_class_ports_list()
        elif self.text_type == "generics":
            self.update_custom_text_class_generics_list()
        custom_text_linting.CustomTextLinting(
            text,
            self.text_type,
            CustomText.read_variables_of_all_windows[self],
            CustomText.written_variables_of_all_windows[self],
        )
        if event is not None:
            # event is None when format() is called from __init__, which happens when the design is load from a file.
            # In this case update_highlight_tags_in_all_texts() is called from file_handling_load.py and must not
            # be called here from each text widget.
            self.update_highlight_tags_in_all_texts()
            if event.keysym == "BackSpace":
                # In order to keep the mouse-pointer inside the shrinking window:
                self._move_mouse_to_insert_cursor()

    def _move_mouse_to_insert_cursor(self) -> None:
        bbox_char = self.bbox("insert")
        if bbox_char is None:
            return
        x, y, _, height = bbox_char
        self.event_generate(
            "<Motion>",
            warp=True,
            x=x,
            y=y + height // 2,
        )

    def _update_size_of_text_box(self, text) -> None:
        nr_of_lines = 0
        nr_of_characters_in_line = 0
        max_line_length = 0
        if self not in [
            project_manager.tab_interface_ref.interface_generics_text,
            project_manager.tab_interface_ref.interface_package_text,
            project_manager.tab_interface_ref.interface_ports_text,
            project_manager.tab_internals_ref.internals_architecture_text,
            project_manager.tab_internals_ref.internals_process_clocked_text,
            project_manager.tab_internals_ref.internals_process_combinatorial_text,
            project_manager.tab_internals_ref.internals_package_text,
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

    def update_highlight_tags(self) -> None:
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
        # highlight_tag_name: "control", "datatype", "function", "not_read", "not_written", "comment"]
        for highlight_tag_name in constants.VHDL_HIGHLIGHT_PATTERN_DICT:
            self.tag_remove(highlight_tag_name, "1.0", tk.END)  # Remove all previous tags of this type.
            for highlight_search_pattern in project_manager.highlight_dict_ref.highlight_pattern_dict[
                highlight_tag_name
            ]:
                if self.text_type != "comment":  # State comment text
                    self._add_highlight_tag_for_single_pattern(highlight_tag_name, highlight_search_pattern)

    def _add_highlight_tag_for_single_pattern(self, highlight_tag_name, highlight_search_pattern) -> None:
        copy_of_text = self.get("1.0", tk.END + "- 1 chars")
        if copy_of_text == "":
            return
        copy_of_text = self._replace_strings_and_attributes_by_blanks(copy_of_text)
        if highlight_tag_name == "comment":
            pattern = highlight_search_pattern
            group_index = 0
        else:
            # Prevent a hit, when the keyword is part of another word:
            pattern = r"([^a-zA-Z0-9_]|^)(" + highlight_search_pattern + r")([^a-zA-Z0-9_]|$)"
            group_index = 2
        match_objects = re.finditer(pattern, copy_of_text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        for match_object in match_objects:
            self.tag_add(
                highlight_tag_name,
                "1.0 + " + str(match_object.start(group_index)) + " chars",
                "1.0 + " + str(match_object.end(group_index)) + " chars",
            )

    def _replace_strings_and_attributes_by_blanks(self, copy_of_text):
        """Replace string literals and VHDL attributes in text with spaces for safe regex search."""

        for search_string in [
            '".*?"',
            "'.*?'",
            "'image",
            "'length",
            "'left",
            "'right",
            "'high",
            "'low",
            "'range",
            "'reverse_range",
            "'pos",
            "'val",
        ]:
            copy_of_text = re.sub(search_string, lambda match_object: " " * len(match_object.group(0)), copy_of_text)
        return copy_of_text

    def undo(self) -> None:
        """Undoes the last action and formats the text."""
        # self.edit_undo() # causes a second "undo", as Ctrl-z automatically starts edit_undo()
        self.format_after_idle(None)

    def redo(self) -> None:
        """Redoes the last undone action and formats the text."""
        self.edit_redo()
        self.format_after_idle(None)

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

    def update_custom_text_class_ports_list(
        self,
    ) -> None:  # Needed at self==project_manager.tab_interface_ref.interface_ports_text
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
        all_generic_declarations = project_manager.tab_interface_ref.interface_generics_text.get("1.0", tk.END).lower()
        self.generics_list = hdl_generation_architecture_state_actions.get_all_generic_names(all_generic_declarations)

    def highlight_item(self, _, __, number_of_line) -> None:
        """Highlights a line. Used when a line is clicked in the "Generated HDL" or "Compile Messages" text box."""
        self.tag_add("highlight", str(number_of_line) + ".0", str(number_of_line + 1) + ".0")
        self.tag_config("highlight", background="orange")
        self.see(str(number_of_line) + ".0")
        self.focus_set()
        canvas_id_of_window = self._get_canvas_id_of_window()
        if canvas_id_of_window is not None:
            coords = project_manager.canvas.coords(canvas_id_of_window)
            zoom_center = coords[0], coords[1]
            zoom_factor = 0.75 * project_manager.state_radius_default / project_manager.state_radius
            canvas_editing.canvas_zoom(zoom_center, zoom_factor)

    def _get_canvas_id_of_window(self) -> int | None:
        for canvas_id, text_ref in state_actions_default.StateActionsDefault.ref_dict.items():
            if text_ref.text_id == self:
                return canvas_id
        for canvas_id, text_ref in global_actions_clocked.GlobalActionsClocked.ref_dict.items():
            if self in (text_ref.text_before_id, text_ref.text_after_id):
                return canvas_id
        for canvas_id, text_ref in global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict.items():
            if text_ref.text_id == self:
                return canvas_id
        for canvas_id, text_ref in state_action.StateAction.ref_dict.items():
            if text_ref.text_id == self:
                return canvas_id
        for canvas_id, text_ref in state_comment.StateComment.ref_dict.items():
            if text_ref.text_id == self:
                return canvas_id
        for canvas_id, text_ref in condition_action.ConditionAction.ref_dict.items():
            if self in (text_ref.condition_id, text_ref.action_id):
                return canvas_id
        return None

    @classmethod
    def update_highlight_tags_in_all_texts(cls) -> None:
        """Update the highlight tags for not_read, not_written, control, datatype, function, and comment."""
        project_manager.highlight_dict_ref.recreate_keyword_list_of_unused_signals()
        for text_ref in CustomText.read_variables_of_all_windows:
            text_ref.update_highlight_tags()
        for text_ref in cls.declaration_text_widgets():
            text_ref.update_highlight_tags()

    @classmethod
    def refresh_highlighting_in_all_declaration_widgets(cls) -> None:
        """Reapply syntax highlighting in all declaration widgets (e.g. after language change)."""
        project_manager.highlight_dict_ref.recreate_keyword_list_of_unused_signals()
        for text_ref in cls.declaration_text_widgets():
            text_ref.update_highlight_tags()

    @classmethod
    def declaration_text_widgets(cls) -> list:
        """Text widgets that show HDL declarations (interface/internals). Used for language-aware highlighting."""
        return [
            project_manager.tab_interface_ref.interface_generics_text,
            project_manager.tab_interface_ref.interface_package_text,
            project_manager.tab_interface_ref.interface_ports_text,
            project_manager.tab_internals_ref.internals_architecture_text,
            project_manager.tab_internals_ref.internals_process_clocked_text,
            project_manager.tab_internals_ref.internals_process_combinatorial_text,
            project_manager.tab_internals_ref.internals_package_text,
        ]

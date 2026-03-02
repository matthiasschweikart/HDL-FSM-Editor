"""
This module contains all method to support "undo" and "redo".
"""

import os
import re
import tkinter as tk

import constants
import file_handling
from elements import (
    condition_action,
    connector,
    global_actions_clocked,
    global_actions_combinatorial,
    reset_entry,
    state,
    state_action,
    state_actions_default,
    state_comment,
    transition,
)
from project_manager import project_manager

stack = []
# Pylint expects this to be a constant with uppercase naming.
stack_write_pointer = 0  # pylint: disable=invalid-name # module-level mutable pointer


def update_window_title() -> None:
    """Set window title to 'unnamed' or append '*' if the design is modified."""
    title = project_manager.root.title()
    if title == "tk":
        project_manager.root.title("unnamed")
    elif not title.endswith("*"):
        title += "*"
        project_manager.root.title(title)


def design_has_changed() -> None:
    """Push current design to undo stack, update title, and save to .tmp if file is set."""
    _add_changes_to_design_stack()
    update_window_title()
    if project_manager.current_file != "" and not project_manager.root.title().startswith("unnamed"):
        # print("design_has_changed: tmp is created by =", inspect.stack()[1][3])
        file_handling.save_in_file(project_manager.current_file + ".tmp")


def undo() -> None:
    """Restore diagram to previous version from stack (ignored when focus is on custom text)."""
    global stack_write_pointer
    # As <Control-z> is bound with the bind_all-command to the diagram, this binding must be ignored, when
    # the focus is on a customtext-widget: Then a Control-z must change the text and must not change the diagram.
    focus = str(project_manager.canvas.focus_get())
    if "customtext" not in focus and stack_write_pointer > 1:
        # stack_write_pointer points at an empty place in stack.
        # stack_write_pointer-1 points at the version which contains the last change
        # stack_write_pointer-2 points at the version before the last change:
        stack_write_pointer -= 2
        _set_diagram_to_version_selected_by_stack_pointer()
        stack_write_pointer += 1
        if stack_write_pointer == 1:
            title = project_manager.root.title()
            if title.endswith("*"):
                project_manager.root.title(title[:-1])
        if (
            stack_write_pointer == 1
        ):  # 1 is the next free place in the stack, 0 is the empty design, so nothing to undo is left
            project_manager.undo_button.config(state="disabled")
            if os.path.isfile(project_manager.current_file + ".tmp"):
                os.remove(project_manager.current_file + ".tmp")
        project_manager.redo_button.config(state="enabled")


def redo() -> None:
    """Restore diagram to next version from stack (ignored when focus is on custom text)."""
    global stack_write_pointer
    # As <Control-Z> is bound with the bind_all-command to the diagram, this binding must be ignored, when
    # the focus is on the customtext-widget: Then a Control-Z must change the text and must not change the diagram.
    focus = str(project_manager.canvas.focus_get())
    if "customtext" not in focus and stack_write_pointer < len(stack):
        _set_diagram_to_version_selected_by_stack_pointer()
        stack_write_pointer += 1
        project_manager.undo_button.config(state="enabled")
    if stack_write_pointer == len(stack):
        project_manager.redo_button.config(state="disabled")


def _add_changes_to_design_stack() -> None:
    global stack_write_pointer
    _remove_stack_entries_from_write_pointer_to_the_end_of_the_stack()
    new_design = _get_complete_design_as_text_object()
    stack.append(new_design)
    stack_write_pointer += 1
    if stack_write_pointer > 1:
        project_manager.undo_button.config(state="enabled")
    project_manager.redo_button.config(state="disabled")


def _remove_stack_entries_from_write_pointer_to_the_end_of_the_stack() -> None:
    if len(stack) > stack_write_pointer:
        del stack[stack_write_pointer:]


# TODO: This should be the same as saving to a file.
# Maybe including some extra information as the zoom level.
def _get_complete_design_as_text_object():
    design = ""
    design += "modulename|" + project_manager.module_name.get() + "\n"
    design += "language|" + project_manager.language.get() + "\n"
    design += "generate_path|" + project_manager.generate_path_value.get() + "\n"
    design += "additional_sources|" + project_manager.additional_sources_value.get() + "\n"
    design += "working_directory|" + project_manager.working_directory_value.get() + "\n"
    design += "number_of_files|" + str(project_manager.select_file_number_text.get()) + "\n"
    design += "reset_signal_name|" + project_manager.reset_signal_name.get() + "\n"
    design += "clock_signal_name|" + project_manager.clock_signal_name.get() + "\n"
    design += "state_number|" + str(state.States.state_number) + "\n"
    design += "transition_number|" + str(transition.TransitionLine.transition_number) + "\n"
    design += "connector_number|" + str(connector.ConnectorInstance.connector_number) + "\n"
    design += "conditionaction_id|" + str(condition_action.ConditionAction.conditionaction_id) + "\n"
    design += "mytext_id|" + str(state_action.StateAction.state_action_id) + "\n"
    design += "reset_entry_size|" + str(project_manager.reset_entry_size) + "\n"
    design += "state_radius|" + str(project_manager.state_radius) + "\n"
    design += "priority_distance|" + str(project_manager.priority_distance) + "\n"
    design += "fontsize|" + str(project_manager.fontsize) + "\n"
    design += "label_fontsize|" + str(project_manager.label_fontsize) + "\n"
    design += "visible_center|" + file_handling.get_visible_center_as_string() + "\n"
    design += "include_timestamp_in_output|" + str(project_manager.include_timestamp_in_output.get()) + "\n"
    design += (
        "interface_package|"
        + str(len(project_manager.interface_package_text.get("1.0", tk.END)) - 1)
        + "|"
        + project_manager.interface_package_text.get("1.0", tk.END)
    )
    design += (
        "interface_generics|"
        + str(len(project_manager.interface_generics_text.get("1.0", tk.END)) - 1)
        + "|"
        + project_manager.interface_generics_text.get("1.0", tk.END)
    )
    design += (
        "interface_ports|"
        + str(len(project_manager.interface_ports_text.get("1.0", tk.END)) - 1)
        + "|"
        + project_manager.interface_ports_text.get("1.0", tk.END)
    )
    design += (
        "internals_package|"
        + str(len(project_manager.internals_package_text.get("1.0", tk.END)) - 1)
        + "|"
        + project_manager.internals_package_text.get("1.0", tk.END)
    )
    design += (
        "internals_architecture|"
        + str(len(project_manager.internals_architecture_text.get("1.0", tk.END)) - 1)
        + "|"
        + project_manager.internals_architecture_text.get("1.0", tk.END)
    )
    design += (
        "internals_process|"
        + str(len(project_manager.internals_process_clocked_text.get("1.0", tk.END)) - 1)
        + "|"
        + project_manager.internals_process_clocked_text.get("1.0", tk.END)
    )
    design += (
        "internals_process_combinatorial|"
        + str(len(project_manager.internals_process_combinatorial_text.get("1.0", tk.END)) - 1)
        + "|"
        + project_manager.internals_process_combinatorial_text.get("1.0", tk.END)
    )
    items = project_manager.canvas.find_all()
    print_tags = False
    for i in items:
        if project_manager.canvas.type(i) == "oval":
            design += "state|"
            design += _get_coords(i)
            design += _get_tags(i)
            design += _get_fill_color(i)
            design += "\n"
        elif project_manager.canvas.type(i) == "text":
            design += "text|"
            design += _get_coords(i)
            design += project_manager.canvas.itemcget(i, "text") + " "
            design += _get_tags(i)
            design += "\n"
        elif project_manager.canvas.type(i) == "line" and "grid_line" not in project_manager.canvas.gettags(i):
            design += "line|"
            design += _get_coords(i)
            design += _get_tags(i)
            design += "\n"
        elif project_manager.canvas.type(i) == "polygon":
            design += "polygon|"
            design += _get_coords(i)
            design += _get_tags(i)
            design += "\n"
        elif project_manager.canvas.type(i) == "rectangle":
            design += "rectangle|"
            design += _get_coords(i)
            design += _get_tags(i)
            design += "\n"
        elif project_manager.canvas.type(i) == "window":
            if i in state_action.StateAction.ref_dict:
                design += "window_state_action_block|"
                text = state_action.StateAction.ref_dict[i].text_id.get("1.0", tk.END)
                design += str(len(text)) + "|"
                design += text
                design += _get_coords(i)
            elif i in state_comment.StateComment.ref_dict:
                design += "window_state_comment|"
                text = state_comment.StateComment.ref_dict[i].text_id.get("1.0", tk.END)
                design += str(len(text)) + "|"
                design += text
                design += _get_coords(i)
            elif i in condition_action.ConditionAction.ref_dict:
                design += "window_condition_action_block|"
                text = condition_action.ConditionAction.ref_dict[i].condition_id.get("1.0", tk.END)
                design += str(len(text)) + "|"
                design += text
                text = condition_action.ConditionAction.ref_dict[i].action_id.get("1.0", tk.END)
                design += str(len(text)) + "|"
                design += text
                design += _get_coords(i)
                print_tags = True
            elif i in global_actions_clocked.GlobalActionsClocked.ref_dict:
                design += "window_global_actions|"
                text_before = global_actions_clocked.GlobalActionsClocked.ref_dict[i].text_before_id.get("1.0", tk.END)
                design += str(len(text_before)) + "|"
                design += text_before
                text_after = global_actions_clocked.GlobalActionsClocked.ref_dict[i].text_after_id.get("1.0", tk.END)
                design += str(len(text_after)) + "|"
                design += text_after
                design += _get_coords(i)
            elif i in global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict:
                design += "window_global_actions_combinatorial|"
                text = global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict[i].text_id.get("1.0", tk.END)
                design += str(len(text)) + "|"
                design += text
                design += _get_coords(i)
            elif i in state_actions_default.StateActionsDefault.ref_dict:
                design += "window_state_actions_default|"
                text = state_actions_default.StateActionsDefault.ref_dict[i].text_id.get("1.0", tk.END)
                design += str(len(text)) + "|"
                design += text
                design += _get_coords(i)
            else:
                print(
                    "get_complete_design_as_text_object: Fatal, unknown dictionary key ",
                    i,
                    project_manager.canvas.type(i),
                )
            design += _get_tags(i)
            if print_tags is True:
                print_tags = False
            design += " \n"

    return design


def _get_coords(canvas_id) -> str:
    coords = project_manager.canvas.coords(canvas_id)
    coords_string = ""
    for c in coords:
        coords_string += str(c) + " "
    return coords_string


def _get_tags(canvas_id) -> str:
    tags = project_manager.canvas.gettags(canvas_id)
    tags_string = ""
    for t in tags:
        if t != "current":
            tags_string += str(t) + " "
    return tags_string


def _get_fill_color(canvas_id):
    color = project_manager.canvas.itemcget(canvas_id, "fill")
    return "fill=" + color + " "


# Pylint expects this to be a constant with uppercase naming.
_line_index = 0  # pylint: disable=invalid-name # mutable loop index in parser


def _set_diagram_to_version_selected_by_stack_pointer() -> None:
    global _line_index
    # Remove the old design:
    state_action.StateAction.ref_dict = {}
    condition_action.ConditionAction.ref_dict = {}
    state_comment.StateComment.ref_dict = {}
    project_manager.canvas.delete("all")
    project_manager.grid_drawer.draw_grid()  # must be available when transitions are raised above.
    # Bring the notebook tab with the diagram into the foreground:
    notebook_ids = project_manager.notebook.tabs()
    for notebook_id in notebook_ids:
        if project_manager.notebook.tab(notebook_id, option="text") == "Graph":
            project_manager.notebook.select(notebook_id)
    # Read the design from the stack:
    design = stack[stack_write_pointer]
    # Convert the string stored in "design" into a list (but provide a return at each line end,
    # to have the same format as when reading from a file):
    lines_without_return = design.split("\n")
    lines = []
    for line in lines_without_return:
        lines.append(line + "\n")
    # Build the new design:
    _line_index = 0
    list_of_states = []
    transition_dict = {}
    state_comment_dictionary = {}
    state_action_dictionary = {}
    condition_action_dictionary = {}
    while _line_index < len(lines):
        if lines[_line_index].startswith("state_number|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "state_number|")
            state.States.state_number = int(rest_of_line)
        elif lines[_line_index].startswith("transition_number|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "transition_number|")
            transition.TransitionLine.transition_number = int(rest_of_line)
        elif lines[_line_index].startswith("connector_number|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "connector_number|")
            connector.ConnectorInstance.connector_number = int(rest_of_line)
        elif lines[_line_index].startswith("conditionaction_id|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "conditionaction_id|")
            condition_action.ConditionAction.conditionaction_id = int(rest_of_line)
        elif lines[_line_index].startswith("mytext_id|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "mytext_id|")
            state_action.StateAction.state_action_id = int(rest_of_line)
        elif lines[_line_index].startswith("state_radius|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "state_radius|")
            project_manager.state_radius = float(rest_of_line)
        elif lines[_line_index].startswith("reset_entry_size|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "reset_entry_size|")
            project_manager.reset_entry_size = int(float(rest_of_line))
        elif lines[_line_index].startswith("priority_distance|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "priority_distance|")
            project_manager.priority_distance = int(float(rest_of_line))
        elif lines[_line_index].startswith("fontsize|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "fontsize|")
            fontsize = float(rest_of_line)
            project_manager.fontsize = fontsize
            project_manager.state_name_font.configure(size=int(fontsize))
        elif lines[_line_index].startswith("label_fontsize|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "label_fontsize|")
            project_manager.label_fontsize = float(rest_of_line)
        elif lines[_line_index].startswith("visible_center|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "visible_center|")
            file_handling.shift_visible_center_to_window_center(rest_of_line)
        elif lines[_line_index].startswith("state|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "state|")
            coords = []
            tags = ()
            fill_color = constants.STATE_COLOR
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    if "fill=" in e:
                        fill_color = e.replace("fill=", "")
                    else:
                        tags = tags + (e,)
            ref = state.States(coords, tags, "dummy", fill_color)
            list_of_states.append(ref.state_id)
        elif lines[_line_index].startswith("polygon|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "polygon|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            reset_entry.ResetEntry(coords, tags)
        elif lines[_line_index].startswith("text|"):  # This is a state-name or a priority-number.
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "text|")
            tags = ()
            entries = rest_of_line.split()
            coords = []
            coords.append(float(entries[0]))
            coords.append(float(entries[1]))
            text = entries[2]
            for e in entries[3:]:
                tags = tags + (e,)
            text_is_state_name = False
            text_is_reset_text = False
            for t in tags:
                if t.startswith("state"):  # state<nr>_name
                    text_is_state_name = True
                    state_tag = t[:-5]
                    project_manager.canvas.itemconfigure(state_tag + "_name", text=text, tags=tags)
                elif t.startswith("reset_text"):
                    text_is_reset_text = True
            if not text_is_state_name and not text_is_reset_text:  # priority number
                for t in tags:
                    if t.startswith("transition"):
                        transition_tag = t[:-8]
                        if transition_tag not in transition_dict:
                            transition_dict[transition_tag] = {}
                        transition_dict[transition_tag]["prio-item"] = {"text": text}
                        break
        elif lines[_line_index].startswith("line|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "line|")
            coords = []
            tags = ()
            trans_id = None
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            for t in tags:
                if t.startswith("ca_connection"):  # line to condition&action block
                    if t not in condition_action_dictionary:
                        condition_action_dictionary[t] = {}
                    condition_action_dictionary[t]["line_coords"] = coords
                    condition_action_dictionary[t]["line_tags"] = tags
                    break
                if t.startswith("connection"):  # line to state action
                    if t not in state_action_dictionary:
                        state_action_dictionary[t] = {}
                    state_action_dictionary[t]["line_coords"] = coords
                    state_action_dictionary[t]["line_tags"] = tags
                    break
                if t.endswith("_comment_line"):  # line to comment
                    if t[:-5] not in state_comment_dictionary:
                        state_comment_dictionary[t[:-5]] = {}
                    state_comment_dictionary[t[:-5]]["line_coords"] = coords
                if t.startswith("transition"):
                    if t not in transition_dict:
                        transition_dict[t] = {}
                    transition_dict[t]["line-item"] = {"coords": coords, "tags": tags}
                    break
            if trans_id is not None:
                project_manager.canvas.tag_lower(trans_id)  # lines are always in "background"
        elif lines[_line_index].startswith("rectangle|"):  # Used as connector or as priority entry.
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "rectangle|")
            coords = []
            tags = ()
            entries = rest_of_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            is_priority_rectangle = True
            for t in tags:
                if t.startswith("connector"):
                    is_priority_rectangle = False
            if not is_priority_rectangle:
                rectangle_id = connector.ConnectorInstance(coords, tags)
                project_manager.canvas.tag_raise(rectangle_id)  # priority rectangles are always in "foreground"
        elif lines[_line_index].startswith("window_state_action_block|"):  # state_action
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "window_state_action_block|")
            text = _get_data(rest_of_line, lines)
            coords = []
            tags = ()
            _line_index += 1
            last_line = lines[_line_index]
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            for t in tags:
                if t.startswith("connection"):  # line to state action
                    connection_tag = t[:-6]
                    if connection_tag not in state_action_dictionary:
                        state_action_dictionary[connection_tag] = {}
                    state_action_dictionary[connection_tag]["state_coords"] = coords
                    state_action_dictionary[connection_tag]["state_tags"] = tags
                    state_action_dictionary[connection_tag]["text"] = text
                    break
        elif lines[_line_index].startswith("window_state_comment|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "window_state_comment|")
            text = _get_data(rest_of_line, lines)
            coords = []
            tags = ()
            _line_index += 1
            last_line = lines[_line_index]
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            if tags[0] not in state_comment_dictionary:
                state_comment_dictionary[tags[0]] = {}
            state_comment_dictionary[tags[0]]["window_coords"] = coords
            state_comment_dictionary[tags[0]]["window_tags"] = tags
            state_comment_dictionary[tags[0]]["text"] = text
        elif lines[_line_index].startswith("window_condition_action_block|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "window_condition_action_block|")
            condition = _get_data(rest_of_line, lines)
            _line_index += 1
            next_line = lines[_line_index]
            action = _get_data(next_line, lines)
            coords = []
            tags = ()
            _line_index += 1
            last_line = lines[_line_index]
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            connected_to_reset_entry = False
            for t in tags:
                if t == "connected_to_reset_transition":
                    connected_to_reset_entry = True
                if t.startswith("ca_connection"):  # "ca_connection<n>_anchor"
                    if t[:-7] not in condition_action_dictionary:
                        condition_action_dictionary[t[:-7]] = {}
                    condition_action_dictionary[t[:-7]]["window_coords"] = coords
                    condition_action_dictionary[t[:-7]]["window_tags"] = tags
                    condition_action_dictionary[t[:-7]]["condition"] = condition
                    condition_action_dictionary[t[:-7]]["action"] = action
                    condition_action_dictionary[t[:-7]]["connected_to_reset_entry"] = connected_to_reset_entry
        elif lines[_line_index].startswith("window_global_actions|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "window_global_actions|")
            text_before = _get_data(rest_of_line, lines)
            _line_index += 1
            next_line = lines[_line_index]
            text_after = _get_data(next_line, lines)
            coords = []
            tags = ()
            _line_index += 1
            last_line = lines[_line_index]
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            global_actions_ref = global_actions_clocked.GlobalActionsClocked(
                coords[0], coords[1], height=1, width=8, padding=1, tags=tags
            )
            global_actions_ref.text_before_id.insert("1.0", text_before)
            global_actions_ref.text_before_id.format()
            global_actions_ref.text_after_id.insert("1.0", text_after)
            global_actions_ref.text_after_id.format()
        elif lines[_line_index].startswith("window_global_actions_combinatorial|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "window_global_actions_combinatorial|")
            text = _get_data(rest_of_line, lines)
            coords = []
            tags = ()
            _line_index += 1
            last_line = lines[_line_index]
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            action_ref = global_actions_combinatorial.GlobalActionsCombinatorial(
                coords[0], coords[1], height=1, width=8, padding=1, tags=tags
            )
            action_ref.text_id.insert("1.0", text)
            action_ref.text_id.format()
        elif lines[_line_index].startswith("window_state_actions_default|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "window_state_actions_default|")
            text = _get_data(rest_of_line, lines)
            coords = []
            tags = ()
            _line_index += 1
            last_line = lines[_line_index]
            entries = last_line.split()
            for e in entries:
                try:
                    v = float(e)
                    coords.append(v)
                except ValueError:
                    tags = tags + (e,)
            action_ref = state_actions_default.StateActionsDefault(
                coords[0], coords[1], height=1, width=8, padding=1, tags=tags
            )
            action_ref.text_id.insert("1.0", text)
            action_ref.text_id.format()

        elif lines[_line_index].startswith("interface_package|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "interface_package|")
            data = _get_data(rest_of_line, lines)
            project_manager.interface_package_text.delete("1.0", tk.END)
            project_manager.interface_package_text.insert("1.0", data)
            project_manager.interface_package_text.update_highlight_tags(
                10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
            )
        elif lines[_line_index].startswith("interface_generics|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "interface_generics|")
            data = _get_data(rest_of_line, lines)
            project_manager.interface_generics_text.delete("1.0", tk.END)
            project_manager.interface_generics_text.insert("1.0", data)
            project_manager.interface_generics_text.update_highlight_tags(
                10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
            )
            project_manager.interface_generics_text.update_custom_text_class_generics_list()
        elif lines[_line_index].startswith("interface_ports|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "interface_ports|")
            data = _get_data(rest_of_line, lines)
            project_manager.interface_ports_text.delete("1.0", tk.END)
            project_manager.interface_ports_text.insert("1.0", data)
            project_manager.interface_ports_text.update_highlight_tags(
                10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
            )
            project_manager.interface_ports_text.update_custom_text_class_ports_list()
        elif lines[_line_index].startswith("internals_package|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "internals_package|")
            data = _get_data(rest_of_line, lines)
            project_manager.internals_package_text.delete("1.0", tk.END)
            project_manager.internals_package_text.insert("1.0", data)
            project_manager.internals_package_text.update_highlight_tags(
                10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
            )
        elif lines[_line_index].startswith("internals_architecture|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "internals_architecture|")
            data = _get_data(rest_of_line, lines)
            project_manager.internals_architecture_text.delete("1.0", tk.END)
            project_manager.internals_architecture_text.insert("1.0", data)
            project_manager.internals_architecture_text.update_highlight_tags(
                10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
            )
            project_manager.internals_architecture_text.update_custom_text_class_signals_list()
        elif lines[_line_index].startswith("internals_process|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "internals_process|")
            data = _get_data(rest_of_line, lines)
            project_manager.internals_process_clocked_text.delete("1.0", tk.END)
            project_manager.internals_process_clocked_text.insert("1.0", data)
            project_manager.internals_process_clocked_text.update_highlight_tags(
                10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
            )
            project_manager.internals_process_clocked_text.update_custom_text_class_signals_list()
        elif lines[_line_index].startswith("internals_process_combinatorial|"):
            rest_of_line = _remove_keyword_from_line(lines[_line_index], "internals_process_combinatorial|")
            data = _get_data(rest_of_line, lines)
            project_manager.internals_process_combinatorial_text.delete("1.0", tk.END)
            project_manager.internals_process_combinatorial_text.insert("1.0", data)
            project_manager.internals_process_combinatorial_text.update_highlight_tags(
                10, ["not_read", "not_written", "control", "datatype", "function", "comment"]
            )
            project_manager.internals_process_combinatorial_text.update_custom_text_class_signals_list()
        _line_index += 1
    for state_canvas_id in list_of_states:
        transition.TransitionLine.adapt_visibility_of_priority_rectangles_at_state(state_canvas_id)
    if project_manager.canvas.find_withtag("global_actions1") == ():
        project_manager.global_action_clocked_button.config(state=tk.NORMAL)
    else:
        project_manager.global_action_clocked_button.config(state=tk.DISABLED)
    if project_manager.canvas.find_withtag("global_actions_combinatorial1") == ():
        project_manager.global_action_combinatorial_button.config(state=tk.NORMAL)
    else:
        project_manager.global_action_combinatorial_button.config(state=tk.DISABLED)
    if project_manager.canvas.find_withtag("state_actions_default") == ():
        project_manager.state_action_default_button.config(state=tk.NORMAL)
    else:
        project_manager.state_action_default_button.config(state=tk.DISABLED)
    if project_manager.canvas.find_withtag("reset_entry") == ():
        project_manager.reset_entry_button.config(state=tk.NORMAL)
    else:
        project_manager.reset_entry_button.config(state=tk.DISABLED)
    for _, single_transition_dict in transition_dict.items():
        transition_coords = single_transition_dict["line-item"]["coords"]
        tags = single_transition_dict["line-item"]["tags"]
        priority = single_transition_dict["prio-item"]["text"]
        transition.TransitionLine(transition_coords, tags, priority, new_transition=False)
    for _, state_action_info in state_action_dictionary.items():
        action_ref = state_action.StateAction(
            state_action_info["state_coords"][0],
            state_action_info["state_coords"][1],
            height=1,
            width=8,
            padding=1,
            tags=state_action_info["state_tags"],
            line_coords=state_action_info["line_coords"],
            line_tags=state_action_info["line_tags"],
            increment=False,
        )
        action_ref.text_id.insert("1.0", state_action_info["text"])
        action_ref.text_id.format()
    for _, state_comment_info in state_comment_dictionary.items():
        comment_ref = state_comment.StateComment(
            state_comment_info["window_coords"][0] - 100,
            state_comment_info["window_coords"][1],
            height=1,
            width=8,
            padding=1,
            tags=state_comment_info["window_tags"],
            line_coords=state_comment_info["line_coords"],
        )
        comment_ref.text_id.insert("1.0", state_comment_info["text"])
        comment_ref.text_id.format()

    for _, condition_action_info in condition_action_dictionary.items():
        condition_action_ref = condition_action.ConditionAction(
            condition_action_info["window_coords"][0],
            condition_action_info["window_coords"][1],
            condition_action_info["connected_to_reset_entry"],
            height=1,
            width=8,
            padding=1,
            tags=condition_action_info["window_tags"],
            condition=condition_action_info["condition"],
            action=condition_action_info["action"],
            line_coords=condition_action_info["line_coords"],
            line_tags=condition_action_info["line_tags"],
            increment=False,
        )
        if (
            condition_action_ref.condition_id.get("1.0", tk.END) == "\n"
            and condition_action_ref.action_id.get("1.0", tk.END) != "\n"
        ):
            condition_action_ref.condition_label.grid_forget()
            condition_action_ref.condition_id.grid_forget()
        if (
            condition_action_ref.condition_id.get("1.0", tk.END) != "\n"
            and condition_action_ref.action_id.get("1.0", tk.END) == "\n"
        ):
            condition_action_ref.action_label.grid_forget()
            condition_action_ref.action_id.grid_forget()

    transition.TransitionLine.hide_priority_of_single_outgoing_transitions()


def _remove_keyword_from_line(line, keyword):
    return line[len(keyword) :]


def _get_data(rest_of_line, lines):
    length_of_data = _get_length_info_from_line(rest_of_line)
    first_data = _remove_length_info(rest_of_line)
    data = _get_remaining_data(lines, length_of_data, first_data)
    return data


def _get_length_info_from_line(rest_of_line) -> int:
    return int(re.sub(r"\|.*", "", rest_of_line))


def _remove_length_info(rest_of_line):
    return re.sub(r".*\|", "", rest_of_line)


def _get_remaining_data(lines, length_of_data, first_data):
    global _line_index
    data = first_data
    while len(data) < length_of_data:
        _line_index += 1
        data = data + lines[_line_index]
    return data[:-1]

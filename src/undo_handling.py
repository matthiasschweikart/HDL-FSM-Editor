"""
This module contains all method to support "undo" and "redo".
"""

import os

import file_handling
import file_handling_load
import file_handling_save
from constants import GuiTab
from project_manager import project_manager

stack = []
# Pylint expects this to be a constant with uppercase naming.
stack_write_pointer = 0  # pylint: disable=invalid-name # module-level mutable pointer


def design_has_changed() -> None:
    """Push current design to undo stack, update title, and save to .tmp if file is set."""
    _add_changes_to_design_stack()
    update_window_title()
    if project_manager.current_file != "" and not project_manager.root.title().startswith("unnamed"):
        # print("design_has_changed: tmp is created by =", inspect.stack()[1][3])
        file_handling.save_in_file(project_manager.current_file + ".tmp")


def _add_changes_to_design_stack() -> None:
    global stack_write_pointer
    _remove_stack_entries_from_write_pointer_to_the_end_of_the_stack()
    new_design = file_handling_save.save_design_to_dict()
    visible_center = _get_visible_center()
    stack.append([new_design, visible_center])
    stack_write_pointer += 1
    if stack_write_pointer > 1:
        project_manager.undo_button.config(state="enabled")
    project_manager.redo_button.config(state="disabled")


def _remove_stack_entries_from_write_pointer_to_the_end_of_the_stack() -> None:
    if len(stack) > stack_write_pointer:
        del stack[stack_write_pointer:]


def _get_visible_center() -> list[float, float]:
    """Return the canvas visible center coordinates as a space-separated string."""
    visible_rectangle = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    visible_center = [
        (visible_rectangle[0] + visible_rectangle[2]) / 2,
        (visible_rectangle[1] + visible_rectangle[3]) / 2,
    ]
    return visible_center


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


def _set_diagram_to_version_selected_by_stack_pointer() -> None:
    # Remove the old design:
    file_handling.clear_design()
    project_manager.notebook.show_tab(GuiTab.DIAGRAM)
    design, visible_center = stack[stack_write_pointer]
    project_manager.tab_control_ref.deactivate_traces()  # Loading the design shall not create a new stack entry.
    file_handling_load.load_design_from_dict(design)
    project_manager.tab_control_ref.activate_traces()
    # project_manager.canvas.after(1000, _shift_visible_center_to_window_center, visible_center)
    _shift_visible_center_to_window_center(visible_center)
    project_manager.grid_drawer.draw_grid()


def _shift_visible_center_to_window_center(visible_center) -> None:
    """Pan canvas so the given center string becomes the current window center."""
    actual_visible_rectangle = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    actual_visible_center = [
        (actual_visible_rectangle[0] + actual_visible_rectangle[2]) / 2,
        (actual_visible_rectangle[1] + actual_visible_rectangle[3]) / 2,
    ]
    project_manager.canvas.scan_mark(int(visible_center[0]), int(visible_center[1]))
    project_manager.canvas.scan_dragto(int(actual_visible_center[0]), int(actual_visible_center[1]), gain=1)


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


def update_window_title() -> None:
    """Set window title to 'unnamed' or append '*' if the design is already named."""
    title = project_manager.root.title()
    if title == "tk":
        project_manager.root.title("unnamed")
    elif not title.endswith("*"):
        title += "*"
        project_manager.root.title(title)

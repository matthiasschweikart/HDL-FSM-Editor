"""
This module contains method used when the user edits the diagram.
"""

from tkinter import messagebox

from project_manager import project_manager

from . import canvas_font_sizes

# import inspect


def view_all() -> None:
    """Fit all canvas content in view and optionally adjust font size."""
    project_manager.grid_drawer.remove_grid()
    project_manager.canvas.update_idletasks()  # to get correct results from bbox
    complete_rectangle = project_manager.canvas.bbox("all")
    if complete_rectangle is not None:
        view_rectangle(complete_rectangle, check_fit=True)
    project_manager.grid_drawer.draw_grid()


def view_rectangle(complete_rectangle, check_fit) -> None:
    """Zoom and pan so the given rectangle is visible; optionally adjust font size."""
    if complete_rectangle[2] - complete_rectangle[0] != 0 and complete_rectangle[3] - complete_rectangle[1] != 0:
        visible_rectangle = [
            project_manager.canvas.canvasx(0),
            project_manager.canvas.canvasy(0),
            project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
            project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
        ]
        factor = _calculate_zoom_factor(complete_rectangle, visible_rectangle)
        too_big = False
        project_manager.canvas.update_idletasks()  # to get correct results from bbox
        actual_rectangle = project_manager.canvas.bbox("all")
        for coord in actual_rectangle:
            # The Canvas which is used, has a scrollregion +/-100000, so here this limit
            # is checked (unclear if really necessary):
            if abs(coord) * factor > 100000:
                too_big = True
        if too_big is False:
            complete_center = _determine_center_of_rectangle(complete_rectangle)
            visible_center = _determine_center_of_rectangle(visible_rectangle)
            _move_canvas_point_from_to(complete_center, visible_center)
            canvas_zoom(complete_center, factor)
            if check_fit:
                _decrement_font_size_if_window_is_too_wide()
        else:
            messagebox.showerror("Fatal", "Zoom factor is too big.")
    # canvas_modify_bindings.switch_to_move_mode()


def _calculate_zoom_factor(complete_rectangle, visible_rectangle):
    complete_width = complete_rectangle[2] - complete_rectangle[0]
    complete_height = complete_rectangle[3] - complete_rectangle[1]
    visible_width = visible_rectangle[2] - visible_rectangle[0]
    visible_height = visible_rectangle[3] - visible_rectangle[1]
    scale_x = visible_width / complete_width
    scale_y = visible_height / complete_height
    factor = min(scale_x, scale_y)
    return factor


def _determine_center_of_rectangle(rectangle_coords) -> list:
    return [(rectangle_coords[0] + rectangle_coords[2]) / 2, (rectangle_coords[1] + rectangle_coords[3]) / 2]


def _move_canvas_point_from_to(complete_center, visible_center) -> None:
    project_manager.canvas.scan_mark(int(complete_center[0]), int(complete_center[1]))
    project_manager.canvas.scan_dragto(int(visible_center[0]), int(visible_center[1]), gain=1)


def canvas_zoom(zoom_center, zoom_factor) -> None:
    """Apply zoom factor around the given center; update scroll and font size."""
    # Modify factor, so that fontsize is always an integer:
    fontsize_rounded_down = int(project_manager.fontsize * zoom_factor)
    if zoom_factor > 1 and fontsize_rounded_down == project_manager.fontsize:
        fontsize_rounded_down += 1
    if fontsize_rounded_down != 0:
        zoom_factor = fontsize_rounded_down / project_manager.fontsize
        project_manager.abs_zoom_factor *= zoom_factor
        project_manager.canvas.scale(
            "all", 0, 0, zoom_factor, zoom_factor
        )  # Scaling must use xoffset=0 and yoffset=0 to preserve the gridspacing of state_radius.
        _scroll_canvas_to_show_the_zoom_center(zoom_center, zoom_factor)
        _adapt_scroll_bars(zoom_factor)
        canvas_font_sizes.adapt_global_size_variables(zoom_factor)


def _scroll_canvas_to_show_the_zoom_center(zoom_center, zoom_factor) -> None:
    new_position_of_zoom_center = [coord * zoom_factor for coord in zoom_center]
    project_manager.canvas.scan_mark(
        int(new_position_of_zoom_center[0]), int(new_position_of_zoom_center[1])
    )  # Mark the point of the canvas, which serves as anchor for the shift.
    project_manager.canvas.scan_dragto(int(zoom_center[0]), int(zoom_center[1]), gain=1)


def _adapt_scroll_bars(factor) -> None:
    scrollregion_strings = project_manager.canvas.cget("scrollregion").split()
    scrollregion_scaled = [int(float(x) * factor) for x in scrollregion_strings]
    project_manager.canvas.configure(scrollregion=scrollregion_scaled)


def _decrement_font_size_if_window_is_too_wide() -> None:
    visible_rectangle = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    project_manager.canvas.update_idletasks()  # to get correct results from bbox
    complete_rectangle = project_manager.canvas.bbox("all")
    if (
        (
            complete_rectangle[0] < visible_rectangle[0]
            or complete_rectangle[1] < visible_rectangle[1]
            or complete_rectangle[2] > visible_rectangle[2]
            or complete_rectangle[3] > visible_rectangle[3]
        )
        and project_manager.fontsize != 1  # When fontsize==1 then zoom_factor calculates to 0, which makes no sense.
    ):
        complete_center = _determine_center_of_rectangle(complete_rectangle)
        visible_center = _determine_center_of_rectangle(visible_rectangle)
        _move_canvas_point_from_to(complete_center, visible_center)
        zoom_factor = (project_manager.fontsize - 1) / project_manager.fontsize
        canvas_zoom(complete_center, zoom_factor)
        _decrement_font_size_if_window_is_too_wide()


def translate_window_event_coordinates_in_rounded_canvas_coordinates(event) -> list:
    """Return canvas coordinates [x, y] for the event, rounded to the state radius grid."""
    canvas_grid_x_coordinate = project_manager.canvas.canvasx(event.x, gridspacing=project_manager.state_radius)
    canvas_grid_y_coordinate = project_manager.canvas.canvasy(event.y, gridspacing=project_manager.state_radius)
    return [canvas_grid_x_coordinate, canvas_grid_y_coordinate]


def translate_window_event_coordinates_in_exact_canvas_coordinates(event) -> list:
    """Return exact canvas coordinates [x, y] for the event."""
    canvas_grid_x_coordinate, canvas_grid_y_coordinate = (
        project_manager.canvas.canvasx(event.x),
        project_manager.canvas.canvasy(event.y),
    )
    return [canvas_grid_x_coordinate, canvas_grid_y_coordinate]


def zoom_plus() -> None:
    """Zoom in by 10% around the visible center."""
    project_manager.canvas.grid_remove()  # Make the canvas invisible.
    project_manager.grid_drawer.remove_grid()
    factor = 1.1
    visible_rectangle = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    visible_center = _determine_center_of_rectangle(visible_rectangle)
    canvas_zoom(visible_center, factor)
    project_manager.grid_drawer.draw_grid()
    project_manager.canvas.grid()


def zoom_minus() -> None:
    """Zoom out by 10% around the visible center."""
    project_manager.canvas.grid_remove()  # Make the canvas invisible.
    project_manager.grid_drawer.remove_grid()
    factor = 1 / 1.1
    visible_rectangle = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    visible_center = _determine_center_of_rectangle(visible_rectangle)
    canvas_zoom(visible_center, factor)
    project_manager.grid_drawer.draw_grid()
    project_manager.canvas.grid()


def zoom_wheel(event) -> None:
    """Handle mouse wheel: zoom in/out at cursor position."""
    project_manager.grid_drawer.remove_grid()
    # event.delta: attribute of the mouse wheel under Windows and MacOs.
    # One "felt step" at the mouse wheel gives this value:
    # Windows: delta=+/-120 ; MacOS: delta=+/-1 ; Linux: delta=0
    # num: attribute of the the mouse wheel under Linux  ("scroll-up=5" and "scroll-down=4").
    factor = 1
    if event.num == 5 or event.delta < 0:  # scroll down
        factor = 1 / 1.1
    elif event.num == 4 or event.delta >= 0:  # scroll up
        factor = 1.1
    zoom_center = translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    canvas_zoom(zoom_center, factor)
    project_manager.grid_drawer.draw_grid()
    # canvas_modify_bindings.switch_to_move_mode()


def zoom_wheel_window_item(event, canvas_id) -> None:
    """Zoom in/out at cursor position of the given window item."""
    project_manager.grid_drawer.remove_grid()
    # event.delta: attribute of the mouse wheel under Windows and MacOs.
    # One "felt step" at the mouse wheel gives this value:
    # Windows: delta=+/-120 ; MacOS: delta=+/-1 ; Linux: delta=0
    # num: attribute of the the mouse wheel under Linux  ("scroll-up=5" and "scroll-down=4").
    factor = 1
    if event.num == 5 or event.delta < 0:  # scroll down
        factor = 1 / 1.1
    elif event.num == 4 or event.delta >= 0:  # scroll up
        factor = 1.1
    window_coor = project_manager.canvas.coords(canvas_id)
    project_manager.canvas.update_idletasks()  # to get correct results from bbox
    window_bbox = project_manager.canvas.bbox(canvas_id)
    zoom_center_x = window_coor[0] + event.x
    zoom_center_y = window_coor[1] - (window_bbox[3] - window_bbox[1]) / 2 + event.y
    zoom_center = (zoom_center_x, zoom_center_y)
    canvas_zoom(zoom_center, factor)
    project_manager.grid_drawer.draw_grid()
    # canvas_modify_bindings.switch_to_move_mode()

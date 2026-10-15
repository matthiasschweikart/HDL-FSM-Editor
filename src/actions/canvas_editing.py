"""
This module contains method used when the user edits the diagram.
"""

from project_manager import project_manager

from . import canvas_font_sizes

# import inspect


def view_all() -> None:
    """Fit all canvas content in view and optionally adjust font size."""
    complete_rectangle = project_manager.canvas.bbox("diagram-element")
    if complete_rectangle is not None:
        project_manager.grid_drawer.remove_grid()
        project_manager.canvas.grid_remove()
        view_rectangle(complete_rectangle, check_fit=True)
        set_scroll_region_if_needed()


def set_scroll_region_if_needed() -> None:
    # The scroll region must be set at tool start and file read:
    scroll_region = project_manager.canvas.cget("scrollregion")
    if not scroll_region:
        scroll_region = "0.0 0.0 0.0 0.0"
    scroll_region = [float(value) for value in scroll_region.split()]
    if scroll_region[2] - scroll_region[0] < 10:
        # scroll region was not initialized yet.
        scroll_region = [
            project_manager.canvas.canvasx(0) - project_manager.canvas.winfo_width(),
            project_manager.canvas.canvasy(0) - project_manager.canvas.winfo_height(),
            project_manager.canvas.canvasx(project_manager.canvas.winfo_width()) + project_manager.canvas.winfo_width(),
            project_manager.canvas.canvasy(
                project_manager.canvas.winfo_height() + project_manager.canvas.winfo_height()
            ),
        ]
        project_manager.canvas.configure(scrollregion=scroll_region)


def view_rectangle(rectangle_to_view, check_fit: bool = False) -> None:
    """Zoom and pan so the given rectangle is visible; optionally fix zooming if anything extends beyond the view."""
    if rectangle_to_view[2] - rectangle_to_view[0] == 0 or rectangle_to_view[3] - rectangle_to_view[1] == 0:
        project_manager.canvas.grid()
        project_manager.grid_drawer.draw_grid()
        return
    project_manager.grid_drawer.remove_grid()
    factor = _calculate_zoom_factor(rectangle_to_view)
    center_of_rectangle_to_view = _determine_center_of_rectangle(rectangle_to_view)
    _shift_canvas_to_make_point_visible_in_the_middle(center_of_rectangle_to_view)
    canvas_zoom(center_of_rectangle_to_view, factor, check_fit)


def zoom_plus_minus(factor) -> None:
    """Zoom in by 10% around the visible center."""
    project_manager.grid_drawer.remove_grid()
    project_manager.canvas.grid_remove()
    visible_canvas_area = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    visible_center = _determine_center_of_rectangle(visible_canvas_area)
    canvas_zoom(visible_center, factor)


def zoom_wheel(event, event_x, event_y) -> None:
    """Zoom in/out at cursor position of the given window item."""
    project_manager.grid_drawer.remove_grid()
    project_manager.canvas.grid_remove()
    # event.delta: attribute of the mouse wheel under Windows and MacOs.
    # One "felt step" at the mouse wheel gives this value:
    # Windows: delta=+/-120 ; MacOS: delta=+/-1 ; Linux: delta=0
    # num: attribute of the the mouse wheel under Linux  ("scroll-up=5" and "scroll-down=4").
    factor = 1
    if event.num == 5 or event.delta < 0:  # scroll down
        factor = 1 / 1.1
    elif event.num == 4 or event.delta >= 0:  # scroll up
        factor = 1.1
    # Adapt the zoom factor here, so that the new center of the zoomed window can be predicted correctly here.
    # Otherwise canvas_zoom() would adapt the zoom factor, which would change the position of the zoom center.
    factor = _modify_zoom_factor_to_achieve_reproducable_zoom_results(factor)
    if factor == 0 or project_manager.fontsize * factor > 300:  # do not accept fontsize above 300
        project_manager.canvas.grid()
        return
    visible_canvas_area = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    visible_center = _determine_center_of_rectangle(visible_canvas_area)
    zoom_center = [  # Place new center between event and visible center, so that it will become the new visible center.
        event_x + (visible_center[0] - event_x) / factor,
        event_y + (visible_center[1] - event_y) / factor,
    ]
    canvas_zoom(zoom_center, factor)


def canvas_zoom(zoom_center, zoom_factor, check_fit: bool = False) -> None:
    """Apply zoom factor around the given center; update scroll and font size."""
    zoom_factor = _modify_zoom_factor_to_achieve_reproducable_zoom_results(zoom_factor)
    if zoom_factor == 0 or project_manager.fontsize * zoom_factor > 300:  # do not accept fontsize above 300
        project_manager.canvas.grid()
        return
    project_manager.abs_zoom_factor *= zoom_factor
    # Scaling must use xoffset=0 and yoffset=0 to preserve the gridspacing of state_radius:
    project_manager.canvas.scale("all", 0, 0, zoom_factor, zoom_factor)
    new_position_of_zoom_center = [coord * zoom_factor for coord in zoom_center]
    _shift_canvas_to_make_point_visible_in_the_middle(new_position_of_zoom_center)
    _adapt_scroll_region_after_zoom(zoom_factor)
    canvas_font_sizes.adapt_fontsizes_and_store_global_size_variables(zoom_factor)
    if check_fit:
        # Wait until the canvas is rendered before checking the new size:
        project_manager.canvas.after_idle(_decrement_font_size_if_window_is_too_wide)
    else:
        project_manager.canvas.grid()
        project_manager.grid_drawer.draw_grid()


def _calculate_zoom_factor(rectangle_to_view):
    visible_canvas_area = [
        project_manager.canvas.canvasx(0),  # 0 = event.x of a mouse-movement at the top-left corner of the canvas
        project_manager.canvas.canvasy(0),  # 0 = event.y of a mouse-movement at the top-left corner of the canvas
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    rectangle_to_view_width = rectangle_to_view[2] - rectangle_to_view[0]
    rectangle_to_view_height = rectangle_to_view[3] - rectangle_to_view[1]
    visible_width = visible_canvas_area[2] - visible_canvas_area[0]
    visible_height = visible_canvas_area[3] - visible_canvas_area[1]
    scale_x = visible_width / rectangle_to_view_width
    scale_y = visible_height / rectangle_to_view_height
    factor = min(scale_x, scale_y)
    return factor


def _determine_center_of_rectangle(rectangle_coords) -> list:
    return [(rectangle_coords[0] + rectangle_coords[2]) / 2, (rectangle_coords[1] + rectangle_coords[3]) / 2]


def _shift_canvas_to_make_point_visible_in_the_middle(center_of_rectangle_to_view) -> None:
    visible_canvas_area = [
        project_manager.canvas.canvasx(0),  # 0 = event.x of a mouse-movement at the top-left corner of the canvas
        project_manager.canvas.canvasy(0),  # 0 = event.y of a mouse-movement at the top-left corner of the canvas
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    visible_center = _determine_center_of_rectangle(visible_canvas_area)
    project_manager.canvas.scan_mark(int(center_of_rectangle_to_view[0]), int(center_of_rectangle_to_view[1]))
    project_manager.canvas.scan_dragto(int(visible_center[0]), int(visible_center[1]), gain=1)


def adapt_scroll_region_after_window_resize() -> None:
    scroll_region = project_manager.canvas.cget("scrollregion").split()
    if not scroll_region:  # Possible after tool start.
        return
    scroll_region = [float(coord) for coord in scroll_region]
    visible_area = (
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    )
    # When the tool window is enlarged by the user, the scroll region must be adapted accordingly:
    # When the window-size is increased to the right side, the canvas is not moved,
    # but more of its area gets visible until the right scroll region limit is reached.
    # When the window-size is further increased to the right side, then the canvas is moved to the right
    # until the left scroll region limit is reached. At this point the horizontal scroll bar has its
    # maximum size. If the window is increased further, the visible area the first time exceeds
    # the scroll region and the scroll region will be adapted in horizontal direction.
    # When the window-size is increased to the left side, first the canvas is moved, until on the
    # right side the scroll region limit is reached. If the window is increased further to the left side,
    # the canvas is not moved anymore, but more of its left area gets visible until the left
    # scroll region limit is reached. At this point the horizontal scroll bar has its maximum size.
    # If the window is increased further, the visible area exceeds the scroll region and the scroll
    # region will be adapted in horizontal direction.
    # When the window-size is increased to the top or bottom side, the behavior is equivalent to the horizontal case.
    margin = 10
    if (  # Both condition should get true at the same time:
        visible_area[0] < scroll_region[0] - margin  # left limit exceeded
        or visible_area[2] > scroll_region[2] + margin  # right limit exceeded
    ):
        project_manager.canvas.configure(
            scrollregion=[visible_area[0], scroll_region[1], visible_area[2], scroll_region[3]]
        )
    scroll_region = [float(coord) for coord in project_manager.canvas.cget("scrollregion").split()]
    if (  # Both condition should get true at the same time:
        visible_area[1] < scroll_region[1] - margin  # top limit exceeded
        or visible_area[3] > scroll_region[3] + margin  # bottom limit exceeded
    ):
        project_manager.canvas.configure(
            scrollregion=[scroll_region[0], visible_area[1], scroll_region[2], visible_area[3]]
        )


def _adapt_scroll_region_after_zoom(factor) -> None:
    scroll_region_old = [float(x) for x in project_manager.canvas.cget("scrollregion").split()]
    scroll_region_scaled = [x * factor for x in scroll_region_old]  # shift and scale the scroll region values.
    if factor > 1:
        # The elements in the diagram are now bigger visible within the visible area.
        # The size of the visible area has not changed, so when the expanded scroll region is
        # applied, the scrollbar-shifters will get smaller, what is the expected behavior.
        project_manager.canvas.configure(scrollregion=scroll_region_scaled)
        return
    # factor < 1:
    # The elements in the diagram are now smaller visible within the visible area.
    # The size of the visible area has not changed, so when the shrunk scroll region is
    # applied, the scrollbar-shifters will get bigger, what is the expected behavior.
    # When one of scrollbar-shifters has reached its maximum value, then the visible area
    # in that direction is as big as or bigger than the scroll-region. In that case the
    # scroll-region must be made bigger, which will shrink the shifters, so that they later
    # can grow again.
    visible_area = (
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    )
    if (
        visible_area[0] < scroll_region_scaled[0]  # left limit exceeded
        or visible_area[2] > scroll_region_scaled[2]  # right limit exceeded
        or visible_area[1] < scroll_region_scaled[1]  # top limit exceeded
        or visible_area[3] > scroll_region_scaled[3]  # bottom limit exceeded
    ):
        # The shrunk scroll region is at the correct position.
        # Resize it to its previous size, because it is smaller than the visible area:
        delta_x = (scroll_region_scaled[2] - scroll_region_scaled[0]) / factor / 2
        delta_y = (scroll_region_scaled[3] - scroll_region_scaled[1]) / factor / 2
        scroll_region_scaled = [
            scroll_region_scaled[0] - delta_x,
            scroll_region_scaled[1] - delta_y,
            scroll_region_scaled[2] + delta_x,
            scroll_region_scaled[3] + delta_y,
        ]
    project_manager.canvas.configure(scrollregion=scroll_region_scaled)


def _modify_zoom_factor_to_achieve_reproducable_zoom_results(zoom_factor):
    # If the zoom_factor is allowed to create a non-integer font size, the following use of
    # the integer fontsize causes view-all results, which alternate between different sizes.
    fontsize_rounded = round(project_manager.fontsize * zoom_factor)
    if zoom_factor > 1 and fontsize_rounded == project_manager.fontsize:
        fontsize_rounded += 1
    elif zoom_factor < 1 and fontsize_rounded == project_manager.fontsize:  # new factor would be 1
        fontsize_rounded = int(project_manager.fontsize * zoom_factor)
    return fontsize_rounded / project_manager.fontsize


def _decrement_font_size_if_window_is_too_wide() -> None:
    visible_canvas_area = [
        project_manager.canvas.canvasx(0),
        project_manager.canvas.canvasy(0),
        project_manager.canvas.canvasx(project_manager.canvas.winfo_width()),
        project_manager.canvas.canvasy(project_manager.canvas.winfo_height()),
    ]
    complete_rectangle = project_manager.canvas.bbox("diagram-element")
    if (
        complete_rectangle  # is None if the diagram is empty
        and _complete_rectangle_extends_visible_area(complete_rectangle, visible_canvas_area)
        and project_manager.fontsize != 1  # When fontsize==1 then zoom_factor calculates to 0, which makes no sense.
    ):
        complete_center = _determine_center_of_rectangle(complete_rectangle)
        _shift_canvas_to_make_point_visible_in_the_middle(complete_center)
        zoom_factor = (project_manager.fontsize - 1) / project_manager.fontsize
        canvas_zoom(complete_center, zoom_factor, check_fit=True)
    else:
        project_manager.canvas.grid()
        project_manager.grid_drawer.draw_grid()


def _complete_rectangle_extends_visible_area(complete_rectangle, visible_canvas_area) -> bool:
    """Return True if the complete rectangle extends beyond the visible rectangle."""
    return (
        complete_rectangle[0] < visible_canvas_area[0]
        or complete_rectangle[1] < visible_canvas_area[1]
        or complete_rectangle[2] > visible_canvas_area[2]
        or complete_rectangle[3] > visible_canvas_area[3]
    )


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

"""
This module contains method used when the user edits the diagram.
"""

from actions import move_handling_initialization
from project_manager import project_manager

from . import canvas_editing


def start_view_rectangle(event) -> None:
    """Begin drawing a view rectangle from the current event position."""
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    rectangle_id = project_manager.canvas.create_rectangle(event_x, event_y, event_x, event_y, dash=(3, 5))
    project_manager.canvas.tag_raise(rectangle_id, "all")
    # The binding for 'Motion' must be added with '+', as 'store_mouse_position' is also bound to 'Motion':
    funcid_canvas_draw_view_rectangle = project_manager.canvas.bind(
        "<Motion>", lambda event: _draw_view_rectangle(event, rectangle_id), "+"
    )
    project_manager.canvas.bind(
        "<ButtonRelease-1>",
        lambda event: _view_area(rectangle_id, funcid_canvas_draw_view_rectangle),
    )
    project_manager.canvas.bind(
        "<ButtonRelease-3>",
        lambda event: _view_area_or_show_context_menu(rectangle_id, funcid_canvas_draw_view_rectangle),
    )


def _draw_view_rectangle(event, rectangle_id) -> None:  # Called by Motion-event.
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    rectangle_coords = project_manager.canvas.coords(rectangle_id)
    if event_x > rectangle_coords[0] and event_y > rectangle_coords[1]:
        project_manager.canvas.coords(rectangle_id, rectangle_coords[0], rectangle_coords[1], event_x, event_y)


def _view_area(rectangle_id, funcid_canvas_draw_view_rectangle) -> None:
    # Called when "view area" was started by the button "view area".
    project_manager.grid_drawer.remove_grid()
    complete_rectangle = project_manager.canvas.coords(rectangle_id)
    canvas_editing.view_rectangle(complete_rectangle, check_fit=False)
    project_manager.canvas.delete(rectangle_id)
    _restore_binding(funcid_canvas_draw_view_rectangle)
    project_manager.grid_drawer.draw_grid()


def _view_area_or_show_context_menu(rectangle_id, funcid_canvas_draw_view_rectangle) -> None:
    # Called when "view area" was started by the right mouse button or when the context menu is opened.
    rectangle_coords = project_manager.canvas.coords(rectangle_id)
    if rectangle_coords[0] != rectangle_coords[2] and rectangle_coords[1] != rectangle_coords[3]:
        _view_area(rectangle_id, funcid_canvas_draw_view_rectangle)
    else:
        project_manager.canvas.delete(rectangle_id)
        overlapping_canvas_ids = project_manager.canvas.find_overlapping(
            rectangle_coords[0] - 5, rectangle_coords[1] - 5, rectangle_coords[0] + 5, rectangle_coords[1] + 5
        )
        item_found = False
        for canvas_id in overlapping_canvas_ids:
            tags = project_manager.canvas.gettags(canvas_id)
            if "grid_line" not in tags:
                item_found = True
        if not item_found:
            project_manager.grid_drawer.show_context_menu()
        _restore_binding(funcid_canvas_draw_view_rectangle)


def _restore_binding(funcid_canvas_draw_view_rectangle):
    project_manager.canvas.unbind("<Motion>", funcid_canvas_draw_view_rectangle)
    project_manager.canvas.unbind("<ButtonRelease-1>")
    project_manager.canvas.unbind("<ButtonRelease-3>")
    # Restore the original binding (Button-1 is bound to start_view_rectangle(), when "view area"-Button was used):
    project_manager.canvas.bind("<Button-1>", move_handling_initialization.move_initialization)

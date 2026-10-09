"""
The method move_initialization is bound to to "Button-1" (left mouse button).
It is only used for moving a transition.
"""

from actions import (
    canvas_editing,
    move_handling,
    move_handling_canvas_item,
    move_handling_finish,
    move_handling_transition_movelist,
)
from elements import transition
from project_manager import project_manager


def move_initialization(event) -> None:
    """Start move on Button-1: find transition under cursor, build move list, bind Motion and ButtonRelease-1."""
    if move_handling_canvas_item.MoveHandlingCanvasItem.move_handling_canvas_item_is_active:
        return
    event_x, event_y = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    line_id, transition_tag = _look_for_transition(event_x, event_y)
    if line_id is None:
        return
    # The move_list which is created here has an entry for each item, which must be moved.
    # In case of a transition the move_list has only 1 entry.
    # Each entry is a list containing the canvas-item-id of the object to be moved,
    # the point to move (or an empty string for non-transition items),
    # and optionally a third entry which is not needed for moving transitions.
    move_list, coords_before_move = move_handling_transition_movelist.create_move_list_for_transition(
        line_id, event_x, event_y
    )
    transition.TransitionLine.extend_transition_to_state_middle_points(transition_tag)
    point_to_move = move_list[0][1]
    _prepare_for_disconnecting_the_transition(transition_tag, point_to_move)
    # Only create bindings for <Motion> and <ButtonRelease-1> (move_finish accesses always move_list[0]),
    #  if there is something to move:
    if move_list:
        # When the user ends moving at an illegal place, the moving continues until he clicks Button-1 again.
        # This second Button-1 click shall not start a new moving, so the binding for Button-1 is removed here:
        project_manager.canvas.unbind("<Button-1>")
        # The second Button-1 shall also not start a moving of canvas-items:
        move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = True

        # With first=True the position of the cursor relativly to the anchor point of the object to move is
        # determined and stored. This distance is afterwards at each cursor movement added to the event coordinates
        # in order to get the new coordinates of the object to move.
        # This prevents the object from jumping to the cursor at the first movement.
        move_handling.move_to_coordinates(event.x, event.y, move_list, first=True, move_to_grid=False)

        # Create a binding for the now following movements of the mouse and for finishing the moving:
        move_do_funcid = project_manager.canvas.bind(
            "<Motion>",
            lambda motion_event: move_handling.move_to_coordinates(
                motion_event.x, motion_event.y, move_list, first=False, move_to_grid=False
            ),
            add="+",
        )  # Must be "added", as store_mouse_position is already bound to "Motion".
        project_manager.canvas.bind(
            "<ButtonRelease-1>",
            lambda release_event: move_handling_finish.move_finish(
                release_event, move_list, move_do_funcid, coords_before_move
            ),
        )


def _look_for_transition(event_x, event_y) -> int | None:
    overlapping_items = project_manager.canvas.find_overlapping(event_x, event_y, event_x, event_y)
    for overlapping_item in overlapping_items:
        # Check if the cursor is inside of a item for which moving is done by MoveHandlingCanvasItem.
        # Check for canvas-window items is not needed: move_initialization is not called for them.
        if project_manager.canvas.type(overlapping_item) in ("oval", "rectangle", "polygon"):
            # Cursor is inside a state, a connector, a priority-rectangle or the reset entry.
            # Return without the second find_overlapping() for these items, because otherwise moving by
            # MoveHandlingCanvasItem and moving by overlapping items would run at the same time, causing conflicts:
            return None
    # Only transitions are left and are found in this way:
    overlapping_items = project_manager.canvas.find_overlapping(
        event_x - project_manager.state_radius / 4,
        event_y - project_manager.state_radius / 4,
        event_x + project_manager.state_radius / 4,
        event_y + project_manager.state_radius / 4,
    )
    for overlapping_canvas_id in overlapping_items:
        tags = project_manager.canvas.gettags(overlapping_canvas_id)
        for tag in tags:
            if tag.startswith("transition"):
                transition_tag = tag
        for tag in tags:
            if tag.startswith("coming_from") or tag.startswith("going_to"):  # transition
                return overlapping_canvas_id, transition_tag
    return None, None


def _prepare_for_disconnecting_the_transition(transition_tag, point_to_move) -> None:
    transition_tags = project_manager.canvas.gettags(transition_tag)
    for tag in transition_tags:
        if point_to_move == "start" and tag.startswith("coming_from_"):
            project_manager.canvas.dtag(transition_tag, tag)  # delete the "coming_from_" tag from the line
            start_state_tag = tag[12:]
            # delete the transition<n>_start-tag from the connected state:
            project_manager.canvas.dtag(start_state_tag, transition_tag + "_start")
            if tag == "coming_from_reset_entry":
                for t in transition_tags:
                    if t.startswith("ca_connection"):
                        project_manager.canvas.dtag("connected_to_reset_transition", "connected_to_reset_transition")
            priority_dict = transition.TransitionLine.determine_priorities_of_outgoing_transitions(start_state_tag)
            if len(priority_dict) == 1:
                for outgoing_transition in priority_dict:
                    project_manager.canvas.itemconfigure(outgoing_transition + "priority", state=tk.HIDDEN)
                    project_manager.canvas.itemconfigure(outgoing_transition + "rectangle", state=tk.HIDDEN)
        elif point_to_move == "end" and tag.startswith("going_to_"):
            end_state_tag = tag[9:]
            # delete the transition<n>_end-tag from the connected state:
            project_manager.canvas.dtag(end_state_tag, transition_tag + "_end")
            project_manager.canvas.dtag(transition_tag, tag)  # delete the "going_to_" tag from the line

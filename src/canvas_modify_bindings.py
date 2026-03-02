"""
This module contains all methods to change the binding of the left mouse-button for
inserting the different graphical objects.
"""

import canvas_editing
import move_handling_canvas_item
import move_handling_initialization
from elements import (
    connector,
    global_actions_clocked,
    global_actions_combinatorial,
    reset_entry,
    state,
    state_actions_default,
    transition,
)
from project_manager import project_manager


def switch_to_state_insertion() -> None:
    """Bind left click to state insertion; cursor to circle."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = False
    # From now on states can be inserted by left mouse button (this ends with the escape key):
    project_manager.root.config(cursor="circle")
    project_manager.canvas.bind("<Button-1>", state.States.insert_state)


def switch_to_transition_insertion() -> None:
    """Bind left click to transition insertion; cursor to cross."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = True
    # From now on transitions can be inserted by left mouse button (this ends with the escape key):
    project_manager.root.config(cursor="cross")
    project_manager.canvas.bind("<Button-1>", transition.TransitionLine.transition_start)


def switch_to_connector_insertion() -> None:
    """Bind left click to connector insertion; cursor to dot."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = False
    #    print("switch_to_connector_insertion")
    project_manager.root.config(cursor="dot")
    project_manager.canvas.bind("<Button-1>", connector.ConnectorInstance.create_connector)


def switch_to_reset_entry_insertion() -> None:
    """Bind left click to reset entry insertion if none exists; cursor to center_ptr."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = False
    #    print("switch_to_reset_entry_insertion")
    if project_manager.canvas.find_withtag("reset_entry") == ():  # Only 1 reset entry is allowed.
        project_manager.root.config(cursor="center_ptr")
        project_manager.canvas.bind("<Button-1>", reset_entry.ResetEntry.insert_reset_entry)


def switch_to_state_action_default_insertion() -> None:
    """Bind left click to state-actions-default insertion if none exists."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = False
    #    print("switch_to_state_action_default_insertion")
    if project_manager.canvas.find_withtag("state_actions_default") == ():  # Only 1 global action is allowed.
        project_manager.root.config(cursor="bogosity")
        project_manager.canvas.bind(
            "<Button-1>", state_actions_default.StateActionsDefault.insert_state_actions_default
        )


def switch_to_global_action_clocked_insertion() -> None:
    """Bind left click to global clocked action insertion if none exists."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = False
    #    print("switch_to_global_action_clocked_insertion")
    if project_manager.canvas.find_withtag("global_actions1") == ():  # Only 1 global action is allowed.
        project_manager.root.config(cursor="bogosity")
        project_manager.canvas.bind(
            "<Button-1>", global_actions_clocked.GlobalActionsClocked.insert_global_actions_clocked
        )


def switch_to_global_action_combinatorial_insertion() -> None:
    """Bind left click to global combinatorial action insertion if none exists."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = False
    #    print("switch_to_global_action_combinatorial_insertion")
    if project_manager.canvas.find_withtag("global_actions_combinatorial1") == ():  # Only 1 global action is allowed.
        project_manager.root.config(cursor="bogosity")
        project_manager.canvas.bind(
            "<Button-1>", global_actions_combinatorial.GlobalActionsCombinatorial.insert_global_actions_combinatorial
        )


def switch_to_move_mode() -> None:
    """Bind left click to move/selection; cursor to arrow."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = False
    #    print("switch_to_move_mode")
    project_manager.root.config(cursor="arrow")
    project_manager.canvas.focus_set()  # Removes the focus from the last used button.
    project_manager.canvas.bind("<Button-1>", move_handling_initialization.move_initialization)


def switch_to_view_area() -> None:
    """Bind left click to draw view rectangle; cursor to plus."""
    move_handling_canvas_item.MoveHandlingCanvasItem.transition_insertion_runs = False
    #    print("switch_to_view_area")
    project_manager.root.config(cursor="plus")
    project_manager.canvas.bind("<Button-1>", canvas_editing.start_view_rectangle)

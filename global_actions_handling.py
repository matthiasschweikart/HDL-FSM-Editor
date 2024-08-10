from tkinter import *
import canvas_editing
import global_actions
import global_actions_combinatorial
import state_actions_default
import undo_handling
import main_window

global_actions_clocked_number = 0
global_actions_combinatorial_number = 0
state_actions_default_number = 0

def insert_global_actions_clocked(event):
    global global_actions_clocked_number
    if global_actions_clocked_number==0: # Only 1 global action is allowed.
        main_window.global_action_clocked_button.config(state=DISABLED)
        global_actions_clocked_number += 1
        insert_global_actions_clocked_in_canvas(event)
        undo_handling.design_has_changed()

def insert_global_actions_clocked_in_canvas(event):
    canvas_grid_coordinates_of_the_event = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
    create_global_actions_clocked(canvas_grid_coordinates_of_the_event)

def create_global_actions_clocked(canvas_grid_coordinates_of_the_event):
    ref = global_actions.GlobalActions(canvas_grid_coordinates_of_the_event[0], canvas_grid_coordinates_of_the_event[1], height=1, width=8, padding=3)
    ref.tag()

def insert_global_actions_combinatorial(event):
    global global_actions_combinatorial_number
    if global_actions_combinatorial_number==0: # Only 1 global action is allowed.
        main_window.global_action_combinatorial_button.config(state=DISABLED)
        global_actions_combinatorial_number += 1
        insert_global_actions_combinatorial_in_canvas(event)
        undo_handling.design_has_changed()

def insert_global_actions_combinatorial_in_canvas(event):
    canvas_grid_coordinates_of_the_event = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
    create_global_actions_combinatorial(canvas_grid_coordinates_of_the_event)

def create_global_actions_combinatorial(canvas_grid_coordinates_of_the_event):
    ref = global_actions_combinatorial.GlobalActionsCombinatorial(canvas_grid_coordinates_of_the_event[0], canvas_grid_coordinates_of_the_event[1], height=1, width=8, padding=3)
    ref.tag()

def insert_state_actions_default(event):
    global state_actions_default_number
    if state_actions_default_number==0: # Only 1 global action is allowed.
        main_window.state_action_default_button.config(state=DISABLED)
        state_actions_default_number += 1
        insert_state_actions_default_in_canvas(event)
        undo_handling.design_has_changed()

def insert_state_actions_default_in_canvas(event):
    canvas_grid_coordinates_of_the_event = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
    create_state_actions_default(canvas_grid_coordinates_of_the_event)

def create_state_actions_default(canvas_grid_coordinates_of_the_event):
    ref = state_actions_default.StateActionsDefault(canvas_grid_coordinates_of_the_event[0], canvas_grid_coordinates_of_the_event[1], height=1, width=8, padding=3)
    ref.tag()

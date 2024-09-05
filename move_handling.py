"""
This module contains a method to decide which graphical object must be moved.
"""
import state_handling
import state_actions_default
import state_action_handling
import transition_handling
import condition_action_handling
import connector_handling
import reset_entry_handling
import global_actions
import global_actions_combinatorial
import canvas_editing
import main_window
import state_comment

def move_do(event, move_list, first):
    if event.type=="5": # ButtonRelease
        last = True
    else: # Motion
        last = False
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    for entry in move_list:
        item_id            = entry[0]
        item_point_to_move = entry[1]
        item_type = main_window.canvas.type(item_id)
        if item_type=='oval':
            state_handling.move_to(event_x, event_y, item_id, first, last)
        elif item_type=='polygon':
            reset_entry_handling.move_to(event_x, event_y, item_id, first, last)
        elif item_type=='line':
            transition_handling.move_to (event_x, event_y, item_id, item_point_to_move, first, move_list, last)
        elif item_type=='rectangle':
            connector_handling.move_to  (event_x, event_y, item_id, first, last)
        elif item_type=='window':
            if item_id in state_action_handling.MyText.mytext_dict:
                ref = state_action_handling.MyText.mytext_dict[item_id]
            elif item_id in state_comment.StateComment.dictionary:
                ref = state_comment.StateComment.dictionary[item_id]
            elif item_id in state_actions_default.StateActionsDefault.dictionary:
                ref = state_actions_default.StateActionsDefault.dictionary[item_id]
            elif item_id in global_actions.GlobalActions.dictionary:
                ref = global_actions.GlobalActions.dictionary[item_id]
            elif item_id in global_actions_combinatorial.GlobalActionsCombinatorial.dictionary:
                ref = global_actions_combinatorial.GlobalActionsCombinatorial.dictionary[item_id]
            else:
                ref = condition_action_handling.ConditionAction.dictionary[item_id]
            ref.move_to(event_x, event_y, first, last)
        else:
            print("move: Fatal, unknown canvas type", "|"+item_type+"|")

def get_exact_or_rounded_canvas_coordinates(event):
    if event.type=="5": # ButtonRelease
        return canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
    else: # Motion
        return canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)

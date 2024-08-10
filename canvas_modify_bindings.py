import canvas_editing
import transition_handling
import move_handling_initialization
import connector_handling
import reset_entry_handling
import global_actions_handling
import state_handling
import main_window

def switch_to_state_insertion():
    # From now on states can be inserted by left mouse button (this ends with the escape key):
    main_window.root.config(cursor="circle")
    main_window.canvas.bind('<Button-1>', lambda event : state_handling.insert_state(event))
   
def switch_to_transition_insertion():
    # From now on transitions can be inserted by left mouse button (this ends with the escape key):
    main_window.root.config(cursor="cross")
    main_window.canvas.bind('<Button-1>', lambda event : transition_handling.transition_start(event)) 

def switch_to_connector_insertion():
    main_window.root.config(cursor="dot")
    main_window.canvas.bind('<Button-1>', lambda event : connector_handling.insert_connector(event)) 

def switch_to_reset_entry_insertion():
    main_window.root.config(cursor="center_ptr")
    main_window.canvas.bind('<Button-1>', lambda event : reset_entry_handling.insert_reset_entry(event)) 

def switch_to_state_action_default_insertion():
    main_window.root.config(cursor="bogosity")
    main_window.canvas.bind('<Button-1>', lambda event : global_actions_handling.insert_state_actions_default(event)) 

def switch_to_global_action_clocked_insertion():
    main_window.root.config(cursor="bogosity")
    main_window.canvas.bind('<Button-1>', lambda event : global_actions_handling.insert_global_actions_clocked(event)) 

def switch_to_global_action_combinatorial_insertion():
    main_window.root.config(cursor="bogosity")
    main_window.canvas.bind('<Button-1>', lambda event : global_actions_handling.insert_global_actions_combinatorial(event)) 

def switch_to_move_mode():
    main_window.root.config(cursor="arrow")
    main_window.canvas.focus_set() # Removes the focus from the last used button.
    main_window.canvas.bind('<Button-1>', lambda event : move_handling_initialization.move_initialization(event))

def switch_to_view_area():
    main_window.root.config(cursor="plus")
    main_window.canvas.bind('<Button-1>', lambda event : canvas_editing.start_view_rectangle(event))

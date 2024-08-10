"""
The method move_initialization is bound to to "Button-1" (click at left mouse button).
When the mouse hovers over one of the text boxes, this binding is not active,
as the text boxes are Canvas-Windows, for which the Canvas binding is not valid.
"""
import move_handling
import move_handling_finish
import transition_handling
import canvas_editing
import main_window

# works bad, not used:
# def move_initialization_window(event, canvas_id_window):
#     window_canvas_x, window_canvas_y = main_window.canvas.coords(canvas_id_window)
#     # Calculate the event-coordinates from the sub-window event coordinates:
#     x0 = main_window.canvas.canvasx(0)
#     y0 = main_window.canvas.canvasy(0)
#     event.x = window_canvas_x - x0
#     event.y = window_canvas_y - y0
#     main_window.canvas.coords(canvas_id_window, window_canvas_x + 5, window_canvas_y )
#     move_initialization_overlapping(event, window_canvas_x, window_canvas_y)

def move_initialization(event):
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    move_initialization_overlapping(event, event_x, event_y)

def move_initialization_overlapping(event, event_x, event_y):
    items_near_mouse_click_location = create_a_list_of_overlapping_items_near_the_mouse_click_location(event_x, event_y)
    if items_near_mouse_click_location==(): return
    if mouse_click_happened_in_state_name     (items_near_mouse_click_location) : return # The state name shall be changed and no moving is required.
    if mouse_click_happened_in_priority_number(items_near_mouse_click_location) : return # The priority shall be changed and no moving is required.
    if mouse_click_happened_in_connection_line(items_near_mouse_click_location) : return # No connection-line can be moved.
    move_list = create_move_list(items_near_mouse_click_location, event_x, event_y)
    # The move_list has an entry for each item, which must be moved.
    # The first entry contains always the object, the user wants to move.
    # All following entries are objects, which are "connected" to the object of the first entry and must also be moved.
    # These items can be moved:
    # reset_entry, state, transition, connector, state_action_window, condition_action_window, global_action windows.
    # When a transitions is moved, then its connection-line to a condition_action_window is adapted after the moving (as the line is not visible during moving).
    # For each item a "move_to" function exists, which moves all elements of the item (for example at a transition: line, priority-rectangle,
    # priority-text, but not the connection-line to a condition_action_window).
    # Each entry consists out of 2 or 3 values (stored in a list):
    # The first value is always the canvas-item-id.
    # The second value is only different from "" at transitions:
    # There the point of the line which has to bemoved is stored as a string: 'start', 'next_to_start', 'next_to_end', 'end'.
    # The third value is the tag of the transition to which the moved condition_action belongs.
    
    # Give the user a feedback, that an object was picked up for moving, by moving the objects of the moving list immediately to the actual position of the mouse:
    move_handling.move_do(event, move_list, first=True)
    
    # Create a binding for the now following movements of the mouse and for finishing the moving:
    move_do_funcid = main_window.canvas.bind('<Motion>', lambda event, move_list=move_list:
                                  move_handling.move_do(event, move_list, first=False), add='+') # Must be "added", as store_mouse_position is already bound to "Motion".
    main_window.canvas.bind('<ButtonRelease-1>', lambda event, move_list=move_list, move_do_funcid=move_do_funcid:
                 move_handling_finish.move_finish(event, move_list, move_do_funcid)) # move_finish must unbind move_do from "Motion", so it needs the function id.

    # From Button-1 the callback "move_initialization()" must be removed, because the user will use Button-1 a second time,
    # when move_finish() did not accept the location of the ButtonRelease-1 and this second time shall not start a new moving:
    main_window.canvas.unbind('<Button-1>')

def create_a_list_of_overlapping_items_near_the_mouse_click_location(event_x, event_y):
    # As soon as a mouse click happens inside a canvas-window item, this click does not call move_initialization,
    # as there is no binding inside the canvas-window for this event. If there would be a binding,
    # it would return event coordinates from inside the window, which cannot be easily converted into canvas coordinates,
    # as the window does not know its own location. So here a bigger overlapping area must be used,
    # so that the user can click beneath the window and catch it.
    return main_window.canvas.find_overlapping(event_x-6, event_y-6, event_x+6, event_y+6) # Find which Canvas-Items are near to the mouse-click.
def mouse_click_happened_in_state_name(items_near_mouse_click_location):
    if len(items_near_mouse_click_location)==2:
        list_item_types = []
        for item_id in items_near_mouse_click_location:
            list_item_types.append(main_window.canvas.type(item_id))
        if "oval" in list_item_types and "text" in list_item_types:
            return True
        else:
            return False
    else:
        return False
def mouse_click_happened_in_priority_number(items_near_mouse_click_location):
    list_item_types = []
    for item_id in items_near_mouse_click_location:
        list_item_types.append(main_window.canvas.type(item_id))
    if "rectangle" in list_item_types and "text" in list_item_types:
        return True
    else:
        return False
def mouse_click_happened_in_connection_line(items_near_mouse_click_location):
    for item_id in items_near_mouse_click_location:
        if main_window.canvas.type(item_id)=="line": 
            tags = main_window.canvas.gettags(item_id)
            for t in tags:
                if t.startswith("connected_to"):
                    return True
    return False
   
def create_move_list(items_near_mouse_click_location, event_x, event_y):
    move_list = []
    move_list_entry_for_diagram_object = create_move_list_entry_if_a_diagram_object_is_moved(items_near_mouse_click_location)
    if move_list_entry_for_diagram_object!=None:
        move_list.append(move_list_entry_for_diagram_object)
        add_lines_connected_to_the_diagram_object_to_the_list(move_list)
    else: # A Canvas line point is moved.
        add_items_for_moving_a_single_line_point_to_the_list(move_list, items_near_mouse_click_location, event_x, event_y)
    return move_list
def create_move_list_entry_if_a_diagram_object_is_moved(items_near_mouse_click_location):
    move_list_entry = None
    for item_id in items_near_mouse_click_location:
        if (main_window.canvas.gettags(item_id)[0].startswith("state")                        or
            main_window.canvas.gettags(item_id)[0].startswith("state_action")                 or
            main_window.canvas.gettags(item_id)[0].startswith("condition_action")             or
            main_window.canvas.gettags(item_id)[0].startswith("reset_entry")                  or
            main_window.canvas.gettags(item_id)[0].startswith("global_actions")               or
            main_window.canvas.gettags(item_id)[0].startswith("global_actions_combinatorial") or
            main_window.canvas.gettags(item_id)[0].startswith("connector")
           ):
            # The move_list_entry must contain item_ids (and not tags), as only the item_id can later be used as a key for a dictionary.
            move_list_entry = [item_id, ""] # The empty second entry must be generated, as later on it will be accessed in move_handling.move_do without checking if its exists.
            return move_list_entry
    return move_list_entry
def add_lines_connected_to_the_diagram_object_to_the_list(move_list):
    tag_list_of_object_to_move = main_window.canvas.gettags(move_list[0][0])
    for tag in tag_list_of_object_to_move: # Check which Canvas lines are "connected" and must be moved together with the diagram object.
        to_be_moved_point_of_connected_line = ""
        if tag.endswith("_start"):
            tag_of_connected_line = tag[:-6]
            to_be_moved_point_of_connected_line = "start"
        elif tag.endswith("_end"):
            tag_of_connected_line = tag[:-4]
            to_be_moved_point_of_connected_line = "end"
        if to_be_moved_point_of_connected_line!="":
            id_of_connected_line = main_window.canvas.find_withtag(tag_of_connected_line)[0]
            move_list.append([id_of_connected_line, to_be_moved_point_of_connected_line])
            transition_handling.extend_to_middle_points(tag_of_connected_line)
    return
def get_move_list_entry_for_line_of_condition_action_block(transition_tag):
    transition_tags = main_window.canvas.gettags(transition_tag)
    for t in transition_tags:
        if t.startswith("ca_connection"): # To this transition, a condition_action block is connected.
            ca_connection_tag = t[0:-4]
            id_of_ca_connection = main_window.canvas.find_withtag(ca_connection_tag)[0]
            return [id_of_ca_connection, "end", transition_tag] # The transition_tag is needed in move_finish.
    return []
def add_items_for_moving_a_single_line_point_to_the_list( move_list, items_near_mouse_click_location, event_x, event_y):
    line_id = find_the_item_id_of_the_line(items_near_mouse_click_location)
    transition_tags = search_for_the_tags_of_a_transition(line_id) # A line can represent a "transition" or a "connection" (connections are ignored here).
    if transition_tags!=():
        moving_point = transition_handling.get_point_to_move(line_id, event_x, event_y)
        for tag in transition_tags:
            if tag.startswith("transition"):
                id_of_transition = main_window.canvas.find_withtag(tag)[0]
                move_list.append([id_of_transition, moving_point]) # moving point is one of: "start", "next_to_start", "next_to_end", "end" as at maximum 4 points in a line are supported.
                transition_handling.extend_to_middle_points(tag)
                transition_tag = tag
        # Remove tags, which are not valid anymore:
        remove_tags_which_will_get_obsolete_by_moving(line_id, transition_tag, transition_tags, moving_point)
        return
    else:
        return # move_list is emtpy in this case.
def find_the_item_id_of_the_line(items_near_mouse_click_location):
    for item_id in items_near_mouse_click_location:
        if main_window.canvas.type(item_id)=='line':
            return item_id
def search_for_the_tags_of_a_transition(line_id):
    line_tags = main_window.canvas.gettags(line_id)
    for tag in line_tags:
        if tag.startswith("transition"):
            return line_tags
        else:
            return ()
def remove_tags_which_will_get_obsolete_by_moving(line_id, transition_tag, transition_tags, moving_point):
    for tag in transition_tags:
        if moving_point=='start' and tag.startswith("coming_from_"):
            main_window.canvas.dtag(line_id, tag) # delete the "coming_from_" tag from the line
            start_state_tag = tag[12:]
            main_window.canvas.dtag(start_state_tag, transition_tag + "_start") # delete the transition<n>_start-tag from the connected state.
            if tag=="coming_from_reset_entry":
                for t in transition_tags:
                    if t.startswith("ca_connection"):
                        main_window.canvas.dtag("connected_to_reset_transition", "connected_to_reset_transition")
        elif moving_point=='end' and tag.startswith("going_to_"):
            end_state_tag = tag[9:]
            main_window.canvas.dtag(end_state_tag, transition_tag + "_end") # delete the transition<n>_end-tag from the connected state.
            main_window.canvas.dtag(line_id, tag) # delete the "going_to_" tag from the line
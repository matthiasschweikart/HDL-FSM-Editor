import undo_handling
import canvas_editing
import main_window

connector_number = 0
difference_x = 0
difference_y = 0

def insert_connector(event):
    global connector_number
    connector_number += 1
    # Translate the window coordinate into the canvas coordinate (the Canvas is bigger than the window):
    event_x, event_y = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
    #connector_id = main_window.canvas.create_rectangle(event_x-5, event_y-5, event_x+5, event_y+5, fill='violet', tag="connector" + str(connector_number))
    connector_id = main_window.canvas.create_rectangle(event_x-canvas_editing.state_radius/4, event_y-canvas_editing.state_radius/4,
                                                       event_x+canvas_editing.state_radius/4, event_y+canvas_editing.state_radius/4,
                                                       fill='violet', tag="connector" + str(connector_number))
    main_window.canvas.tag_bind(connector_id,"<Enter>", lambda event, id=connector_id : main_window.canvas.itemconfig(id, width=2))
    main_window.canvas.tag_bind(connector_id,"<Leave>", lambda event, id=connector_id : main_window.canvas.itemconfig(id, width=1))
    undo_handling.design_has_changed()

def move_to(event_x, event_y, rectangle_id, first, last):
    global difference_x, difference_y
    if first==True:
        # Calculate the difference between the "anchor" point and the event:
        coords = main_window.canvas.coords(rectangle_id)
        middle_point = calculate_middle_point(coords)
        difference_x, difference_y = - event_x + middle_point[0], - event_y + middle_point[1]
    # Keep the distance between event and anchor point constant:
    event_x, event_y = event_x + difference_x, event_y + difference_y
    if last==True:
        event_x = canvas_editing.state_radius * round(event_x/canvas_editing.state_radius)
        event_y = canvas_editing.state_radius * round(event_y/canvas_editing.state_radius)
    edge_length            = determine_edge_length_of_the_rectangle(rectangle_id)
    new_upper_left_corner  = calculate_new_upper_left_corner_of_the_rectangle (event_x, event_y, edge_length)
    new_lower_right_corner = calculate_new_lower_right_corner_of_the_rectangle(event_x, event_y, edge_length)
    move_rectangle_in_canvas(rectangle_id, new_upper_left_corner, new_lower_right_corner)

def calculate_middle_point(coords):
    middle_x = (coords[0] + coords[2])/2
    middle_y = (coords[1] + coords[3])/2
    return [middle_x, middle_y]

def determine_edge_length_of_the_rectangle(rectangle_id):
    rectangle_coords = main_window.canvas.coords(rectangle_id)
    edge_length = rectangle_coords[2] - rectangle_coords[0]
    return edge_length

def calculate_new_upper_left_corner_of_the_rectangle (event_x, event_y, edge_length):
    return [event_x-edge_length/2, event_y-edge_length/2]

def calculate_new_lower_right_corner_of_the_rectangle(event_x, event_y, edge_length):
    return [event_x+edge_length/2, event_y+edge_length/2]

def move_rectangle_in_canvas(rectangle_id, new_upper_left_corner, new_lower_right_corner):
      main_window.canvas.coords(rectangle_id, *new_upper_left_corner, *new_lower_right_corner)

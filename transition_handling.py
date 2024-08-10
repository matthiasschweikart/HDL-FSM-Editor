from tkinter import *   # Because of "*", all tkinter-functions can be called directly with their names.
import vector_handling
import canvas_editing
import canvas_modify_bindings
import OptionMenu
import condition_action_handling
import math
import undo_handling
import move_handling_initialization
import main_window

transition_number = 0
difference_x = 0
difference_y = 0

def move_to(event_x, event_y, transition_id, point, first, move_list, last):
    global difference_x, difference_y
    if (main_window.canvas.type(move_list[0][0])=="line" and (move_list[0][1] in ("start", "end"))):
        middle_of_line_is_moved = False
    else:
        middle_of_line_is_moved = True
    if middle_of_line_is_moved==True:
        if first==True:
            # Calculate the difference between the "anchor" point and the event:
            coords = main_window.canvas.coords(transition_id)
            if   point=='start':
                point_to_move = [coords[0], coords[1]]
            elif point=='next_to_start':
                point_to_move = [coords[2], coords[3]]
            elif point=='next_to_end':
                point_to_move = [coords[-4], coords[-3]]
            elif point=='end':
                point_to_move = [coords[-2], coords[-1]]
            else:
                print("transition_handling: Fatal, unknown point =", point)
            difference_x, difference_y = - event_x + point_to_move[0], - event_y + point_to_move[1]
    else:
        difference_x = 0
        difference_y = 0
    # Keep the distance between event and anchor point constant:
    event_x, event_y = event_x + difference_x, event_y + difference_y
    if last is True:
        event_x = canvas_editing.state_radius * round(event_x/canvas_editing.state_radius)
        event_y = canvas_editing.state_radius * round(event_y/canvas_editing.state_radius)
    transition_tag = main_window.canvas.gettags(transition_id)[0]
    main_window.canvas.tag_lower(transition_tag)
    # Move transition:
    transition_coords = main_window.canvas.coords(transition_tag)
    if   point=='start':
        main_window.canvas.coords(transition_tag, event_x, event_y, *transition_coords[2:])
    elif point=='next_to_start':
        main_window.canvas.coords(transition_tag, *transition_coords[0:2], event_x, event_y, *transition_coords[4:])
    elif point=='next_to_end':
        main_window.canvas.coords(transition_tag, *transition_coords[-8:-4], event_x, event_y, *transition_coords[-2:])
    elif point=='end':
        main_window.canvas.coords(transition_tag, *transition_coords[-8:-2], event_x, event_y)
    else:
        print("transition_handling: Fatal, unknown point =", point)
    # Move priority rectangle:
    if transition_tag.startswith("transition"): # There is no priority rectangle at a "connection".
        # The tag "transition_tag + '_start'" is already removed from the old start state when the transition start-point is moved.
        # In all other cases the tag exists.
        # So try to get the coordinates of the start state (there the priority rectangle is positioned):
        start_state_coords = main_window.canvas.coords(transition_tag + "_start")
        if point=='start':
            if start_state_coords==[] or main_window.canvas.type(transition_tag + "_start")=="polygon": # Transition start point is disconnected from its start state and moved alone.
                start_state_radius = 0
            else:                      #  State with connected transition is moved.
                start_state_radius = abs(start_state_coords[2] - start_state_coords[0])/2
            # Calculates the position of the priority rectangle by shortening the vector from the event (= first point of transition) to the second point of the transition.
            [priority_middle_x,priority_middle_y,dummy_x,dummy_y] = vector_handling.shorten_vector(start_state_radius+canvas_editing.priority_distance,event_x,event_y,0,transition_coords[2] ,transition_coords[3] ,1,0)
        else:
            # Calculates the position of the priority rectangle by shortening the first point of transition to the second point of the transition.
            start_state_radius = abs(start_state_coords[2] - start_state_coords[0])/2
            # Because the transition is already extended to the start-state middle, the length of the vector must be shortened additionally by the start state radius, to keep the priority outside of the start-state.
            [priority_middle_x,priority_middle_y,dummy_x,dummy_y] = vector_handling.shorten_vector(start_state_radius+canvas_editing.priority_distance,transition_coords[0],transition_coords[1],0,transition_coords[2] ,transition_coords[3] ,1,0)
        [rectangle_width_half, rectangle_height_half] = get_rectangle_dimensions(transition_tag+'rectangle')
        main_window.canvas.coords(transition_tag+'rectangle',priority_middle_x-rectangle_width_half, priority_middle_y-rectangle_height_half,
                                                             priority_middle_x+rectangle_width_half, priority_middle_y+rectangle_height_half)
        main_window.canvas.coords(transition_tag+'priority',priority_middle_x, priority_middle_y)
        main_window.canvas.tag_raise(transition_tag+'rectangle', transition_tag)
        main_window.canvas.tag_raise(transition_tag+'priority', transition_tag+'rectangle')

def get_rectangle_dimensions(id):
    rectangle_coords = main_window.canvas.coords(id)
    rectangle_width_half  = (rectangle_coords[2] - rectangle_coords[0])/2
    rectangle_height_half = (rectangle_coords[3] - rectangle_coords[1])/2
    return [rectangle_width_half, rectangle_height_half]

def extend_to_middle_points(transition_tag):
    transition_coords  = main_window.canvas.coords(transition_tag)
    #print("extend_to_middle_points: transition_tag, transition_coords =", transition_tag, transition_coords)
    if transition_tag.startswith("transition"):
        #print("extend_to_middle_points: transition_tag =", transition_tag, transition_coords)
        start_coords = main_window.canvas.coords(transition_tag + "_start") # The coordinates are from a circle (state) or from a connector (rectangle) or from the reset entry (polygon).
        end_coords   = main_window.canvas.coords(transition_tag + "_end")
        if main_window.canvas.type(transition_tag + "_start")!="polygon": # At the reset entry the transition start point is not modified for moving.
            transition_coords[0]  = (start_coords[0] + start_coords[2])//2
            transition_coords[1]  = (start_coords[1] + start_coords[3])//2
        transition_coords[-2] = (end_coords[0] + end_coords[2])//2
        transition_coords[-1] = (end_coords[1] + end_coords[3])//2
    elif transition_tag.startswith("connection"):
        #print("extend_to_middle_points: connection_tag =", transition_tag + "_end")
        end_state_coords = main_window.canvas.coords(transition_tag + "_end")
        #print("extend_to_middle_points: transition_tag, end_state_coords, transition_coords =", transition_tag, end_state_coords,transition_coords)
        transition_coords[-2] = (end_state_coords[0] + end_state_coords[2])//2
        transition_coords[-1] = (end_state_coords[1] + end_state_coords[3])//2
    else:
        #print ("extend_to_middle-points: Fatal: transition_tag =", transition_tag, "cannot be handled.")
        pass
    main_window.canvas.coords(transition_tag, *transition_coords) # No move, but the transition is only lengthened.
    # Move the line "under" the states to get more beauty:
    main_window.canvas.tag_lower(transition_tag, transition_tag + "_start")
    main_window.canvas.tag_lower(transition_tag, transition_tag + "_end")

def get_point_to_move(item_id, event_x, event_y):
    # Determine which point of the transition is nearest to the event:
    transition_coords = main_window.canvas.coords(item_id)
    number_of_points  = len(transition_coords)//2
    distance_to_event     = []
    distance_to_neighbour = []
    for i in range(number_of_points):
        distance_to_event.append(math.sqrt((event_x-transition_coords[2*i])**2+(event_y-transition_coords[2*i+1])**2))
        if i<number_of_points-1:
            distance_to_neighbour.append(math.sqrt((transition_coords[2*i]-transition_coords[2*i+2])**2+(transition_coords[2*i+1]-transition_coords[2*i+3])**2))
    min = 0
    for i in range(number_of_points):
        if (distance_to_event[i]<distance_to_event[min]):
            min = i
    #print ("get_point_to_move: min =", min)
    if number_of_points==4:
        if   min==0:
            return 'start'
        elif min==1:
            return 'next_to_start'
        elif min==2:
            return 'next_to_end'
        else:
            return 'end'
    elif number_of_points==3:
        if   distance_to_event[0]<distance_to_neighbour[0]/4:
            return 'start'
        elif distance_to_event[0]<distance_to_neighbour[0]*3/4:
            main_window.canvas.coords(item_id, *transition_coords[0:2], event_x, event_y, *transition_coords[2:6]) # insert new point into transition
            return 'next_to_start'
        elif distance_to_event[0]<distance_to_neighbour[0]:
            return 'next_to_start'
        elif distance_to_event[1]<distance_to_neighbour[1]/4:
            return 'next_to_start'
        elif distance_to_event[1]<distance_to_neighbour[1]*3/4:
            main_window.canvas.coords(item_id, *transition_coords[0:4], event_x, event_y, *transition_coords[4:6]) # insert new point into transition
            return 'next_to_end'
        else:
            return 'end'
    else:
        if   distance_to_event[0]<distance_to_neighbour[0]/3:
            return 'start'
        elif distance_to_event[0]<distance_to_neighbour[0]*2/3:
            main_window.canvas.coords(item_id, *transition_coords[0:2], event_x, event_y, *transition_coords[2:4])
            return 'next_to_start'
        else:
            return 'end'

def shorten_to_state_border(transition_tag):
    transition_coords = main_window.canvas.coords(transition_tag)
    tag_list = main_window.canvas.gettags(transition_tag)
    connection = False
    for tag in tag_list:
        if   tag.startswith("coming_from_"):
            start_state_tag = tag[12:]
        elif tag.startswith("going_to_"):
            end_state_tag = tag[9:]
        elif tag.startswith("connected_to_"):
            connection = True
            end_state_tag = tag[13:]
    if connection==False:
        #print ("shorten_to_state_border: start_state_tag, end_state_tag =", start_state_tag, end_state_tag)
        start_state_coords = main_window.canvas.coords(start_state_tag)
        end_state_coords   = main_window.canvas.coords(end_state_tag)
        if start_state_tag=="reset_entry":
            start_state_radius = 0
        else:
            start_state_radius = (start_state_coords[2] - start_state_coords[0])/2
        end_state_radius   = (end_state_coords[2] - end_state_coords [0])/2
        #print("shorten_to_state_border: start_state_radius, end_state_radius", start_state_radius, end_state_radius)
        transition_start_coords = vector_handling.shorten_vector(start_state_radius,transition_coords[0],transition_coords[1],0,transition_coords[2],transition_coords[3],1,0)
        #print("shorten_to_state_border: transition_start_coords", transition_start_coords)
        transition_end_coords   = vector_handling.shorten_vector(0,transition_coords[-4],transition_coords[-3],end_state_radius,transition_coords[-2],transition_coords[-1],0,1)
        transition_coords[ 0] = transition_start_coords[ 0]
        transition_coords[ 1] = transition_start_coords[ 1]
        transition_coords[-2] = transition_end_coords  [-2]
        transition_coords[-1] = transition_end_coords  [-1]
        main_window.canvas.coords(transition_tag,transition_coords)
        main_window.canvas.tag_lower(transition_tag)
        # Move priority rectangle:
        start_state_radius = abs(start_state_coords[2] - start_state_coords[0])/2
        [priority_middle_x,priority_middle_y,dummy_x,dummy_y] = vector_handling.shorten_vector(0+canvas_editing.priority_distance,transition_coords[0],transition_coords[1],0,transition_coords[2] ,transition_coords[3] ,1,0)
        [rectangle_width_half, rectangle_height_half] = get_rectangle_dimensions(transition_tag+'rectangle')
        main_window.canvas.coords(transition_tag+'rectangle',priority_middle_x-rectangle_width_half, priority_middle_y-rectangle_height_half,
                                                             priority_middle_x+rectangle_width_half, priority_middle_y+rectangle_height_half)
        main_window.canvas.coords(transition_tag+'priority',priority_middle_x, priority_middle_y)
    else:
        #print ("shorten_to_state_border: end_state_tag =", end_state_tag)
        end_state_coords   = main_window.canvas.coords(end_state_tag)
        end_state_radius   = (end_state_coords  [2] - end_state_coords  [0])/2
        #print("shorten_to_state_border: end_state_radius", end_state_radius)
        transition_end_coords   = vector_handling.shorten_vector(0,transition_coords[-4],transition_coords[-3],end_state_radius,transition_coords[-2],transition_coords[-1],0,1)
        transition_coords[-2] = transition_end_coords  [-2]
        transition_coords[-1] = transition_end_coords  [-1]
        main_window.canvas.coords(transition_tag,transition_coords)
        main_window.canvas.tag_lower(transition_tag)

def transition_start(event):
    global transition_number
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    ids = main_window.canvas.find_overlapping(event_x,event_y,event_x,event_y)
    if ids!=():
        for id in ids:
            type = main_window.canvas.type(id)
            if ( type=='oval' or
                 type=='polygon' or
                (type=='rectangle' and main_window.canvas.gettags(id)[0].startswith("connector"))
               ):
                main_window.root.unbind_all('<Escape>') # No switch to "move mode" shall happen during transition insertion, as after the first mouse click a second one is needed eventually.
                for tag in main_window.canvas.gettags(id):
                    if tag.startswith("state") or tag.startswith("connector") or tag.startswith("reset_entry"):
                        tag_of_object_where_transition_starts = tag
                main_window.canvas.addtag_withtag("transition"+str(transition_number)+'_start',tag_of_object_where_transition_starts)
                start_object_coords = main_window.canvas.coords(tag_of_object_where_transition_starts)
                if type=="oval" or type=="rectangle":
                    line_start_x = start_object_coords[0]/2 + start_object_coords[2]/2
                    line_start_y = start_object_coords[1]/2 + start_object_coords[3]/2
                else: # polygon, this means reset-entry
                    line_start_x = start_object_coords[4]
                    line_start_y = start_object_coords[5]
                # Create first a line with length 0:
                transition_id = main_window.canvas.create_line(line_start_x,line_start_y,line_start_x,line_start_y, arrow='last', fill="blue", smooth=True, tags=('transition'+str(transition_number),'coming_from_' + tag_of_object_where_transition_starts))
                main_window.canvas.tag_bind(transition_id,"<Enter>"   , lambda event, transition_id=transition_id : main_window.canvas.itemconfig(transition_id, width=3))
                main_window.canvas.tag_bind(transition_id,"<Leave>"   , lambda event, transition_id=transition_id : main_window.canvas.itemconfig(transition_id, width=1))
                main_window.canvas.tag_bind(transition_id,"<Button-3>", lambda event, transition_id=transition_id : show_menu(event, transition_id))
                transition_draw_funcid = main_window.canvas.bind('<Motion>'  , lambda event, id=transition_id : transition_draw (event, id), add='+')  # Afterwards a mouse motion modifies the line.
                main_window.canvas.bind('<Button-1>', lambda event, id=transition_id, start_state=id, transition_draw_funcid=transition_draw_funcid: transition_end  (event, id, start_state, transition_draw_funcid))  # The next click with the left mouse button ends the modification of the line.
    else:
        #print('Transition must start in a state')
        pass

def transition_draw(event, id):
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    coords_new = main_window.canvas.coords(id)
    coords_new[-2] = event_x
    coords_new[-1] = event_y
    main_window.canvas.coords(id,coords_new)

def transition_end (event, transition_id, start_state, transition_draw_funcid):
    global transition_number
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    #print('Transition End: transition_id =', transition_id)
    # Check if the mouse is over a state:
    ids = main_window.canvas.find_overlapping(event_x,event_y,event_x,event_y)
    end_state_id = -1
    for i in ids:
        type = main_window.canvas.type(i)
        #print("Transition End: canvas.type(i) =", canvas.type(i), canvas.gettags(i)[0])
        if (type=='oval') or (type=='rectangle' and main_window.canvas.gettags(i)[0].startswith("connector")):
            end_state_id = i
    # Check if the transition must be ended or continued:
    if (end_state_id==-1):
        #print ('Transition End: Continue transition, because no state is under the mouse')
        coords_new = main_window.canvas.coords(transition_id)
        if (len(coords_new)<8): # add an additional point to the transition
            coords_new.append(event_x)
            coords_new.append(event_y)
            main_window.canvas.coords(transition_id,coords_new)
        else:
            return # pass # the mouse click is not accepted, because already 3 points are defined and the next must be over a state.
    elif (end_state_id==start_state and len(main_window.canvas.coords(transition_id))<8):
        #print("Transition End: The transition points back to the start state and needs additional points to be added.")
        return # pass # the mouse click is not accepted.
    else:
        #print("Transition End: End transition at state or connector with id =", end_state_id)
        main_window.canvas.addtag_withtag("transition"+str(transition_number)+'_end',end_state_id)
        state_tags = main_window.canvas.gettags(end_state_id)
        for tag in state_tags:
            if tag.startswith("state") or tag.startswith("connector"):
                end_state_tag = tag
        main_window.canvas.addtag_withtag("going_to_" + end_state_tag ,"transition"+str(transition_number))
        # Restore bindings:
        #print ("transition_end: canvas.bind() vor unbind", canvas.bind(), transition_draw_funcid)
        main_window.canvas.unbind('<Motion>', transition_draw_funcid)
        #print ("transition_end: canvas.bind() nach unbind", canvas.bind())
        main_window.canvas.bind('<Motion>'  , lambda event : canvas_editing.store_mouse_position(event))
        #print ("transition_end: canvas.bind() nach bind", canvas.bind())
        main_window.canvas.bind('<Button-1>', lambda event : transition_start(event)) # From now on transitions can be inserted again by left mouse button (this ends with the escape key).
        main_window.root.bind_all('<Escape>', lambda event : canvas_modify_bindings.switch_to_move_mode())

        # Determine the middle of the state, as the transition shall touch it (later the transition will be shorted):
        end_state_coords = main_window.canvas.coords(end_state_id)
        state_middle_x = end_state_coords[0]/2 + end_state_coords[2]/2
        state_middle_y = end_state_coords[1]/2 + end_state_coords[3]/2
        coords_new = main_window.canvas.coords(transition_id)
        coords_new[-2] = state_middle_x
        coords_new[-1] = state_middle_y
        main_window.canvas.coords(transition_id, coords_new)

        # Shorten the start and the end of the transition, as they both shall only point to the "middle" of the state but shall exactly touch it.
        # Transitions connect states and connectors and once also the reset entry.
        # States and connectors have the same coordinate handling with an upper left and a lower right point.
        # So they can be handled without any difference.
        # But the reset entry has 5 coordinates and the transition is connected to the third point.
        # So here a different handling has to be implemented:
        end_state_radius = abs(end_state_coords[2]-end_state_coords[0])//2
        #if canvas.type(start_state)!="polygon":
        start_object_coords = main_window.canvas.coords(start_state)
        start_state_radius = abs(start_object_coords[2]-start_object_coords[0])//2
        if (len(coords_new)==4):
            if len(start_object_coords)==10:
                #print("transition_end: reset_entry found")
                vector1 = vector_handling.shorten_vector(start_state_radius,coords_new[0],coords_new[1],end_state_radius,state_middle_x,state_middle_y,1,1)
                vector1[0] = start_object_coords[4]
                vector1[1] = start_object_coords[5]
                vector2 = vector1
            else:
                vector1 = vector_handling.shorten_vector(start_state_radius,coords_new[0],coords_new[1],end_state_radius,state_middle_x,state_middle_y,1,1)
                vector2 = vector1
        elif (len(coords_new)==6):
            if len(start_object_coords)==10:
                vector1 = []
                vector1.append(start_object_coords[4])
                vector1.append(start_object_coords[5])
                vector2 = vector_handling.shorten_vector(start_state_radius,coords_new[2],coords_new[3],end_state_radius,state_middle_x,state_middle_y,0,1)
            else:
                vector1 = vector_handling.shorten_vector(start_state_radius,coords_new[0],coords_new[1],end_state_radius,coords_new[2] ,coords_new[3] ,1,0)
                vector2 = vector_handling.shorten_vector(start_state_radius,coords_new[2],coords_new[3],end_state_radius,state_middle_x,state_middle_y,0,1)
        else: # len(coords_new)==8
            if len(start_object_coords)==10:
                vector1 = []
                vector1.append(start_object_coords[4])
                vector1.append(start_object_coords[5])
                vector2 = vector_handling.shorten_vector(start_state_radius,coords_new[4],coords_new[5],end_state_radius,state_middle_x,state_middle_y,0,1)
            else:
                vector1 = vector_handling.shorten_vector(start_state_radius,coords_new[0],coords_new[1],end_state_radius,coords_new[2] ,coords_new[3] ,1,0)
                vector2 = vector_handling.shorten_vector(start_state_radius,coords_new[4],coords_new[5],end_state_radius,state_middle_x,state_middle_y,0,1)
        coords_new[0]  = vector1[0]
        coords_new[1]  = vector1[1]
        coords_new[-2] = vector2[2]
        coords_new[-1] = vector2[3]
        main_window.canvas.coords(transition_id,coords_new)

        # Determine middle of the priority rectangle position by shortening the transition vector:
        [priority_middle_x,priority_middle_y,dummy_x,dummy_y] = vector_handling.shorten_vector(canvas_editing.priority_distance,coords_new[0],coords_new[1],0,coords_new[2] ,coords_new[3] ,1,0)
        transition_tag = 'transition' + str(transition_number)
        main_window.canvas.create_text(priority_middle_x, priority_middle_y, text='1', tag=(transition_tag + 'priority'), font=canvas_editing.state_name_font)
        text_rectangle = main_window.canvas.bbox(transition_tag + 'priority')
        main_window.canvas.create_rectangle(text_rectangle, tag=(transition_tag + 'rectangle'), fill='cyan')
        main_window.canvas.tag_raise(transition_tag + 'priority')
        main_window.canvas.tag_bind(transition_tag + 'priority' ,"<Double-Button-1>",
                         lambda event,transition_tag=transition_tag  : edit_priority(event, transition_tag))
        transition_number += 1
        undo_handling.design_has_changed()

def edit_priority(event, transition_tag):
    main_window.canvas.unbind('<Button-1>')
    main_window.canvas.unbind_all('<Delete>')
    priority_tag = transition_tag + "priority"
    old_text = main_window.canvas.itemcget(priority_tag,'text')
    text_box = Entry(main_window.canvas, width=10, justify=CENTER)
    text_box.insert(END, old_text)
    text_box.select_range(0, END)
    text_box.bind('<Return>', lambda event, transition_tag=transition_tag, text_box=text_box: update_priority(transition_tag, text_box))
    text_box.bind('<Escape>', lambda event, transition_tag=transition_tag, text_box=text_box, old_text=old_text: abort_edit_text(transition_tag, text_box, old_text))
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    main_window.canvas.create_window(event_x, event_y, window=text_box, tag='entry-window')
    text_box.focus_set()

def update_priority(transition_tag,text_box):
    main_window.canvas.delete('entry-window')
    main_window.canvas.itemconfig(transition_tag + "priority", text=text_box.get())
    text_rectangle = main_window.canvas.bbox(transition_tag + 'priority')
    main_window.canvas.coords(transition_tag + 'rectangle', text_rectangle)
    text_box.destroy()
    main_window.canvas.tag_raise(transition_tag + "rectangle", transition_tag)
    main_window.canvas.tag_raise(transition_tag + "priority", transition_tag + "rectangle")
    undo_handling.design_has_changed()
    main_window.canvas.bind    ('<Button-1>', lambda event : move_handling_initialization.move_initialization(event))
    main_window.canvas.bind_all('<Delete>'  , lambda event : canvas_editing.delete())

def abort_edit_text(transition_tag, text_box, old_text):
    main_window.canvas.delete('entry-window')
    main_window.canvas.itemconfig(transition_tag + "priority", text=old_text)
    text_box.destroy()
    main_window.canvas.tag_raise(transition_tag + "rectangle", transition_tag)
    main_window.canvas.tag_raise(transition_tag + "priority", transition_tag + "rectangle")
    main_window.canvas.bind    ('<Button-1>', lambda event : move_handling_initialization.move_initialization(event))
    main_window.canvas.bind_all('<Delete>'  , lambda event : canvas_editing.delete())

def show_menu(event, transition_id):
    list = OptionMenu.MyListbox(main_window.canvas, ['add condition&action'], height=1, bg='lightgrey', width=21, activestyle='dotbox',relief=RAISED)
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    window = main_window.canvas.create_window(event_x+40,event_y,window=list)
    list.bind("<Button-1>", lambda event, window=window, list=list, menu_x=event_x, menu_y=event_y, transition_id=transition_id :
                                   evaluate_menu(event, window, list, menu_x, menu_y, transition_id))
    list.bind("<Leave>"   , lambda event, window=window, list=list : close_menu(event, window, list))

def evaluate_menu(event, window, list, menu_x, menu_y, transition_id):
    selected_entry = list.get(list.curselection())
    if (selected_entry=='add condition&action'):
        transition_tags = main_window.canvas.gettags(transition_id)
        has_condition_action = False
        connected_to_reset_entry = False
        for tag in transition_tags:
            if tag.startswith("ca_connection"):
                has_condition_action = True
            elif tag=="coming_from_reset_entry":
                connected_to_reset_entry = True
        if has_condition_action==False:
            condition_action_ref = condition_action_handling.ConditionAction(menu_x, menu_y, connected_to_reset_entry, height=1, width=8, padding=3, increment=True)
            condition_action_ref.tag(connected_to_reset_entry)
            condition_action_ref.draw_line(transition_id, menu_x, menu_y)
            condition_action_ref.condition_id.focus() # Puts the text input cursor into the text box.
    list.destroy()
    main_window.canvas.delete(window)
    if has_condition_action==False:
        undo_handling.design_has_changed() # It must be waited until the window for the menu is deleted.

def close_menu(event, window, list):
    list.destroy()
    main_window.canvas.delete(window)

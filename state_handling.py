from tkinter import *   # Because of "*", all tkinter-functions can be called directly with their names.
import OptionMenu
import state_action_handling
import move_handling_initialization
import canvas_editing
import transition_handling
import undo_handling
import main_window

state_number = 0 # Defaultvalue, will be increased with every new state.
difference_x = 0
difference_y = 0

def move_to(event_x, event_y, state_id, first, last):
    global difference_x, difference_y
    if first==True:
        # Calculate the difference between the "anchor" point and the event:
        coords = main_window.canvas.coords(state_id)
        middle_point = calculate_middle_point(coords)
        difference_x, difference_y = - event_x + middle_point[0], - event_y + middle_point[1]
    # Keep the distance between event and anchor point constant:
    event_x, event_y = event_x + difference_x, event_y + difference_y
    if last==True:
        event_x = canvas_editing.state_radius * round(event_x/canvas_editing.state_radius)
        event_y = canvas_editing.state_radius * round(event_y/canvas_editing.state_radius)
    text_tag = determine_the_tag_of_the_state_name(state_id)
    state_radius = determine_the_radius_of_the_state(state_id)
    main_window.canvas.coords(state_id, event_x-state_radius, event_y-state_radius,
                                        event_x+state_radius, event_y+state_radius)
    main_window.canvas.coords(text_tag, event_x, event_y)
    main_window.canvas.tag_raise(state_id, 'all')
    main_window.canvas.tag_raise(text_tag, state_id)

def calculate_middle_point(coords):
    middle_x = (coords[0] + coords[2])/2
    middle_y = (coords[1] + coords[3])/2
    return [middle_x, middle_y]

def determine_the_tag_of_the_state_name(state_id):
    tags = main_window.canvas.gettags(state_id)
    for tag in tags:
        if tag.startswith("state"):
            return tag + "_name"
def determine_the_radius_of_the_state(state_id):
    state_coords = main_window.canvas.coords(state_id)
    return (state_coords[2] - state_coords[0])//2

def get_canvas_id_of_state_name(state_id):
    tags = main_window.canvas.gettags(state_id)
    return main_window.canvas.find_withtag(tags[0] + "_name")[0]
  
def insert_state(event):
    global state_number
    state_number += 1
    event_x, event_y = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
    state_id = main_window.canvas.create_oval(event_x-canvas_editing.state_radius, event_y-canvas_editing.state_radius,
                                              event_x+canvas_editing.state_radius, event_y+canvas_editing.state_radius,
                                              fill='cyan', width=2, outline='blue', tags='state' + str(state_number))
    main_window.canvas.tag_lower(state_id,'all')
    text_id  = main_window.canvas.create_text(event_x, event_y, text='S' + str(state_number), tags='state' + str(state_number) + "_name", font=canvas_editing.state_name_font)
    main_window.canvas.tag_bind(text_id ,"<Double-Button-1>", lambda event, text_id=text_id : edit_state_name(event, text_id))
    main_window.canvas.tag_bind(state_id,"<Enter>"          , lambda event, id=state_id     : main_window.canvas.itemconfig(id, width=4))
    main_window.canvas.tag_bind(state_id,"<Leave>"          , lambda event, id=state_id     : main_window.canvas.itemconfig(id, width=2))
    main_window.canvas.tag_bind(state_id,"<Button-3>"       , lambda event, id=state_id     : show_menu(event, id))
    undo_handling.design_has_changed()
    #print ("New State"    , state_id, main_window.canvas.coords(state_id))
    #print ("New Statename", text_id , main_window.canvas.coords(text_id))

def show_menu(event, id):
    list = OptionMenu.MyListbox(main_window.canvas, ['add action'], height=1, bg='grey', width=12, activestyle='dotbox', relief=RAISED)
    [event_x, event_y] = canvas_editing.translate_window_event_coordinates_in_exact_canvas_coordinates(event)
    window = main_window.canvas.create_window(event_x+40,event_y,window=list)
    list.bind("<Button-1>", lambda event, window=window, list=list, menu_x=event_x, menu_y=event_y, state_id=id : evaluate_menu(event, window, list, menu_x, menu_y, state_id))
    list.bind("<Leave>"   , lambda event, window=window, list=list : close_menu(window, list))

def evaluate_menu(event, window, list, menu_x, menu_y, state_id):
    selected_entry = list.get(list.curselection())
    if (selected_entry=='add action'):
        tags = main_window.canvas.gettags(state_id)
        action_block_exists = False
        for tag in tags:
            if tag.startswith("connection"):
                action_block_exists = True
        if action_block_exists==False:
            action_ref = state_action_handling.MyText(menu_x,menu_y, height=1, width=8, padding=3, increment=True)
            action_ref.connect_to_state        (menu_x,menu_y, state_id)
            action_ref.tag()
    list.destroy()
    main_window.canvas.delete(window)
    if action_block_exists==False:
        undo_handling.design_has_changed()

def close_menu(window, list):
    list.destroy()
    main_window.canvas.delete(window)

def edit_state_name(event, text_id):
    main_window.canvas.unbind('<Button-1>')
    main_window.canvas.unbind_all('<Delete>')
    old_text = main_window.canvas.itemcget(text_id,'text')
    text_box = Entry(main_window.canvas, width=10, justify=CENTER)
    #text_box = Entry(None, width=10, justify=CENTER) funktioniert auch, unklar, was richtig/besser ist.
    text_box.insert(END, old_text)
    text_box.select_range(0, END)
    text_box.bind('<Return>', lambda event, text_id=text_id, text_box=text_box: update_state_name(text_id, text_box))
    text_box.bind('<Escape>', lambda event, text_id=text_id, text_box=text_box, old_text=old_text: abort_edit_text(text_id,text_box,old_text))
    event_x, event_y = canvas_editing.translate_window_event_coordinates_in_rounded_canvas_coordinates(event)
    main_window.canvas.create_window(event_x, event_y, window=text_box, tag='entry-window')
    text_box.focus_set()

def update_state_name(text_id, text_box):
    tags = main_window.canvas.gettags(text_id)
    for t in tags:
        if t.startswith("state"): # Format of text_id tag: 'state' + str(state_number) + "_name"
            state_tag = t[:-5]
    # Analyze the old situation:
    state_coords_old = main_window.canvas.coords(state_tag)
    # Update the text:
    main_window.canvas.delete('entry-window')
    new_text = text_box.get()
    if new_text!="":
        main_window.canvas.itemconfig(text_id, text=new_text)
    # Resize the state:
    size = main_window.canvas.bbox(text_id)
    text_width = size[2] - size[0] + 5 # Make the text a little bit bigger, so that it does not touch the state circle.
    state_width = state_coords_old[2] - state_coords_old[0]
    difference = text_width - state_width
    state_size_new = state_coords_old[2] - state_coords_old[0] + difference
    if (state_size_new<2*canvas_editing.state_radius):
        increase = 2*canvas_editing.state_radius - state_size_new
        difference = difference + increase
    coords_new = []
    coords_new.append(state_coords_old[0] - difference//2)
    coords_new.append(state_coords_old[1] - difference//2)
    coords_new.append(state_coords_old[2] + difference//2)
    coords_new.append(state_coords_old[3] + difference//2)
    main_window.canvas.coords(state_tag,coords_new)
    undo_handling.design_has_changed()
    text_box.destroy()
    main_window.canvas.bind    ('<Button-1>', lambda event : move_handling_initialization.move_initialization(event))
    main_window.canvas.bind_all('<Delete>'  , lambda event : canvas_editing.delete())
    tags = main_window.canvas.gettags(state_tag)
    for t in tags:
        if t.endswith("_start"):
            transition_handling.extend_to_middle_points(t[:-6])
            transition_handling.shorten_to_state_border(t[:-6])
        elif t.endswith("_end"):
            transition_handling.extend_to_middle_points(t[:-4])
            transition_handling.shorten_to_state_border(t[:-4])

def abort_edit_text(text_id, text_box, old_text):
    main_window.canvas.delete('entry-window')
    main_window.canvas.itemconfig(text_id, text=old_text)
    text_box.destroy()
    main_window.canvas.bind    ('<Button-1>', lambda event : move_handling_initialization.move_initialization(event))
    main_window.canvas.bind_all('<Delete>'  , lambda event : canvas_editing.delete())

from tkinter import *
from tkinter import ttk

import canvas_editing
import undo_handling
import custom_text
import main_window
import move_handling
import move_handling_finish

class MyText():
    mytext_id = 0
    mytext_dict = {}
    def __init__(self, menu_x, menu_y, height, width, padding, increment):
        if increment is True:
            MyText.mytext_id += 1
        self.difference_x = 0
        self.difference_y = 0
        self.first_call_of_move_item = True
        # Create frame:
        self.frame_id = ttk.Frame(main_window.canvas, relief=FLAT, padding=padding, style="StateActionsWindow.TFrame")
        self.frame_id.bind("<Enter>", lambda event, self=self : self.activate  ())
        self.frame_id.bind("<Leave>", lambda event, self=self : self.deactivate())
        # Create label object inside frame:
        self.label_id = ttk.Label(self.frame_id, text="State actions (combinatorial): ",
                        font=("Arial",int(canvas_editing.label_fontsize)),
                        style='StateActionsWindow.TLabel')
        # Create text object inside frame:
        self.text_id = custom_text.CustomText(self.frame_id, type="action", height=height, width=width, undo=True, maxundo=-1 , font=("Courier",int(canvas_editing.fontsize)))
        self.text = ""
        self.text_id .bind("<Control-z>"     , lambda event : self.text_id.undo())
        self.text_id .bind("<Control-Z>"     , lambda event : self.text_id.redo())
        self.text_id .bind("<<TextModified>>", lambda event : undo_handling.modify_window_title())
        self.text_id .bind("<FocusIn>"       , lambda event : main_window.canvas.unbind_all("<Delete>"))
        self.text_id .bind("<FocusOut>"      , lambda event : main_window.canvas.bind_all('<Delete>', lambda event: canvas_editing.delete()))
        # Create bindings for moving:
        self.frame_id.bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        self.label_id.bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        self.text_id .bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        # Create canvas window for frame and text:
        self.window_id = main_window.canvas.create_window(menu_x+100,menu_y,window=self.frame_id, anchor=W)
        MyText.mytext_dict[self.window_id] = self
        self.label_id.grid(column=0, row=0, sticky=(N, W, E)) 
        self.text_id.grid (column=0, row=1, sticky=(S, W, E))

    def move_item(self, event):
        bbox_canvas_x1, bbox_canvas_y1, _, _, = main_window.canvas.bbox(self.window_id)
        canvas_x0 = main_window.canvas.canvasx(0)
        canvas_y0 = main_window.canvas.canvasy(0)
        bbox_window_x1 = bbox_canvas_x1 - canvas_x0
        bbox_window_y1 = bbox_canvas_y1 - canvas_y0
        event.x = bbox_window_x1 + event.x
        event.y = bbox_window_y1 + event.y
        if self.first_call_of_move_item:
            self.first_call_of_move_item = False
            self.frame_id.bind("<ButtonRelease-1>", self.move_item_end)
            self.label_id.bind("<ButtonRelease-1>", self.move_item_end)
            self.text_id .bind("<ButtonRelease-1>", self.move_item_end)
            canvas_event_x = main_window.canvas.canvasx(event.x)
            canvas_event_y = main_window.canvas.canvasy(event.y)
            coords = main_window.canvas.coords(self.window_id)
            self.difference_x, self.difference_y = - canvas_event_x + coords[0], - canvas_event_y + coords[1]
        move_list = [[self.window_id, ""]]
        move_handling.move_do(event, move_list, first=False)

    def move_item_end(self, event):
        self.first_call_of_move_item = True
        self.frame_id.unbind("<ButtonRelease-1>")
        self.label_id.unbind("<ButtonRelease-1>")
        self.text_id .unbind("<ButtonRelease-1>")
        move_handling_finish.hide_the_connection_line_of_moved_condition_action_window([[self.window_id, ""]])
        undo_handling.design_has_changed()

    def tag(self):
        main_window.canvas.itemconfigure(self.window_id, tag=('state_action'+str(MyText.mytext_id), "connection" + str(MyText.mytext_id) + "_start"))

    def connect_to_state(self, menu_x, menu_y, state_id):
        # Draw a line from the state to the action block which is added to the state:
        state_coords = main_window.canvas.coords (state_id)
        main_window.canvas.addtag_withtag("connection" + str(MyText.mytext_id) + "_end", state_id)
        state_tags   = main_window.canvas.gettags(state_id)
        self.line_id = main_window.canvas.create_line(menu_x+100, menu_y, (state_coords[2] + state_coords[0])/2, (state_coords[3] + state_coords[1])/2, dash=(2,2),
                                          tag=('connection'+str(MyText.mytext_id),'connected_to_' + state_tags[0]))
        main_window.canvas.tag_bind(self.line_id, "<Enter>", lambda event, self=self : self.activate_line  ())
        main_window.canvas.tag_bind(self.line_id, "<Leave>", lambda event, self=self : self.deactivate_line())
        main_window.canvas.tag_lower(self.line_id, state_id)

    def activate(self):
        self.frame_id.configure(style='Window.TFrame',padding=3) # increase the width of the line around the box
        self.text = self.text_id.get("1.0", END)

    def deactivate(self):
        self.frame_id.configure(style='Window.TFrame',padding=1) # decrease the width of the line around the box
        self.frame_id.focus() # "unfocus" the Text, when the mouse leaves the text.
        if self.text_id.get("1.0", END)!= self.text:
            undo_handling.design_has_changed()

    def activate_line(self):
        main_window.canvas.itemconfigure(self.line_id, width=3) # increase the width of the line around the box

    def deactivate_line(self):
        main_window.canvas.itemconfigure(self.line_id, width=1) # decrease the width of the line around the box

    def move_to(self, event_x, event_y, first, last):
        self.frame_id.configure(padding=1) # decrease the width of the line around the box
        if first==True:
            self.frame_id.configure(padding=4) # increase the width of the line around the box
            # Calculate the difference between the "anchor" point and the event:
            coords = main_window.canvas.coords(self.window_id)
            self.difference_x, self.difference_y = - event_x + coords[0], - event_y + coords[1]
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + self.difference_x, event_y + self.difference_y
        # if last==True:
        #     event_x = canvas_editing.state_radius * round(event_x/canvas_editing.state_radius)
        #     event_y = canvas_editing.state_radius * round(event_y/canvas_editing.state_radius)
        main_window.canvas.coords(self.window_id, event_x, event_y)
        # Move the connection line:
        window_tags = main_window.canvas.gettags(self.window_id)
        for t in window_tags:
            if t.startswith("connection"):
                line_tag = t[:-6]
        self.line_coords = main_window.canvas.coords(line_tag)
        self.line_coords[0] = event_x
        self.line_coords[1] = event_y
        main_window.canvas.coords(line_tag, self.line_coords)

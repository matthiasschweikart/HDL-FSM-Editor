from tkinter import *
from tkinter import ttk

import canvas_editing
import canvas_modify_bindings
import undo_handling
import custom_text
import main_window
import move_handling

class GlobalActionsCombinatorial():
    dictionary = {}
    def __init__(self, menu_x, menu_y, height, width, padding):
        self.frame_id = ttk.Frame(main_window.canvas, relief=FLAT, padding=padding, style='GlobalActionsWindow.TFrame')
        self.frame_id.bind("<Enter>", lambda event, self=self : self.activate())
        self.frame_id.bind("<Leave>", lambda event, self=self : self.deactivate())
        # Create label object inside frame:
        self.label    = ttk.Label(self.frame_id, text="Global actions combinatorial: " ,
                                  font=("Arial",int(canvas_editing.label_fontsize)),
                                  style="GlobalActionsWindow.TLabel")
        self.text_id  = custom_text.CustomText(self.frame_id, type="action", height=height, width=width, undo=True, maxundo=-1, font=("Courier",int(canvas_editing.fontsize)))
        self.text_id .bind("<Control-z>"     , lambda event : self.text_id.undo())
        self.text_id .bind("<Control-Z>"     , lambda event : self.text_id.redo())
        self.text_id .bind("<<TextModified>>", lambda event : undo_handling.modify_window_title())
        self.text_id .bind("<FocusIn>"       , lambda event : main_window.canvas.unbind_all("<Delete>"))
        self.text_id .bind("<FocusOut>"      , lambda event : main_window.canvas.bind_all('<Delete>', lambda event: canvas_editing.delete()))
        # Create bindings for moving:
        self.frame_id.bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        self.label   .bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        self.text_id .bind("<B1-Motion>"     , self.move_item) # Touching inside the window.

        self.label.grid   (row=0, column=0, sticky=(N, W, E))
        self.text_id.grid (row=1, column=0, sticky=(E,W))

        self.difference_x = 0
        self.difference_y = 0
        self.first_call_of_move_item = True

        # Create canvas window for frame and text:
        self.window_id = main_window.canvas.create_window(menu_x, menu_y, window=self.frame_id, anchor=W)
        self.frame_id.lower()
        GlobalActionsCombinatorial.dictionary[self.window_id] = self
        canvas_modify_bindings.switch_to_move_mode()

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
            self.label   .bind("<ButtonRelease-1>", self.move_item_end)
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
        self.label   .unbind("<ButtonRelease-1>")
        self.text_id .unbind("<ButtonRelease-1>")
        undo_handling.design_has_changed()

    def tag(self):
        main_window.canvas.itemconfigure(self.window_id, tag='global_actions_combinatorial1')

    def activate(self):
        self.frame_id.configure(padding=3) # increase the width of the line around the box
        self.text = self.text_id.get("1.0", END)

    def deactivate(self):
        self.frame_id.configure(padding=1) # decrease the width of the line around the box
        self.frame_id.focus() # "unfocus" the Text, when the mouse leaves the text.
        #self.text_id.format()
        if self.text_id.get("1.0", END)!=self.text:
            undo_handling.design_has_changed()

    def move_to(self, event_x, event_y, first, last):
        self.frame_id.configure(padding=1) # decrease the width of the line around the box
        if first==True:
            self.frame_id.configure(padding=4) # increase the width of the line around the box
            # Calculate the difference between the "anchor" point and the event:
            coords = main_window.canvas.coords(self.window_id)
            self.difference_x, self.difference_y = - event_x + coords[0], - event_y + coords[1]
        # Keep the distance between event and anchor point constant:
        event_x, event_y = event_x + self.difference_x, event_y + self.difference_y
        main_window.canvas.coords(self.window_id, event_x, event_y)

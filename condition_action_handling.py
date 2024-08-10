"""
    This class handles the condition&action box which can be activated for each transition.
"""
import tkinter as tk
from tkinter import ttk

import canvas_editing
import undo_handling
import custom_text
import main_window
import move_handling_initialization
import move_handling
import move_handling_finish

class ConditionAction():
    conditionaction_id = 0
    dictionary = {}
    def __init__(self, menu_x, menu_y, connected_to_reset_entry, height, width, padding, increment):
        if increment is True:
            ConditionAction.conditionaction_id += 1
        self.difference_x = 0
        self.difference_y = 0
        self.line_id      = None
        self.line_coords  = None
        self.first_call_of_move_item = True
        # Create frame:
        self.frame_id = ttk.Frame(main_window.canvas, relief=tk.FLAT, padding=padding, style='Window.TFrame')
        self.frame_id.bind("<Enter>", lambda event : self.activate())
        self.frame_id.bind("<Leave>", lambda event : self.deactivate())
        # Create objects inside frame:
        if connected_to_reset_entry:
            label_action_text = "Transition actions (asynchronous):"
        else:
            label_action_text = "Transition actions (clocked):"
        self.condition_label = ttk.Label             (self.frame_id, text="Transition condition: ", font=("Arial",int(canvas_editing.label_fontsize)))
        self.action_label    = ttk.Label             (self.frame_id, text=label_action_text       , font=("Arial",int(canvas_editing.label_fontsize)))
        self.action_id       = custom_text.CustomText(self.frame_id, type="action"   , takefocus=0, height=height, width=width, undo=True, maxundo=-1,
                                                      font=("Courier",int(canvas_editing.fontsize)))
        self.condition_id    = custom_text.CustomText(self.frame_id, type="condition", takefocus=0, height=height, width=width, undo=True, maxundo=-1,
                                                      font=("Courier",int(canvas_editing.fontsize)))
        # Create bindings for Undo/Redo:
        self.action_id      .bind("<Control-z>"     , lambda event : self.action_id.undo())
        self.action_id      .bind("<Control-Z>"     , lambda event : self.action_id.redo())
        self.condition_id   .bind("<Control-z>"     , lambda event : self.condition_id.undo())
        self.condition_id   .bind("<Control-Z>"     , lambda event : self.condition_id.redo())
        self.action_id      .bind("<<TextModified>>", lambda event : undo_handling.modify_window_title())
        self.condition_id   .bind("<<TextModified>>", lambda event : undo_handling.modify_window_title())
        self.action_id      .bind("<FocusIn>"       , lambda event : main_window.canvas.unbind_all("<Delete>"))
        self.action_id      .bind("<FocusOut>"      , lambda event : main_window.canvas.bind_all  ('<Delete>', lambda event: canvas_editing.delete()))
        self.condition_id   .bind("<FocusIn>"       , lambda event : main_window.canvas.unbind_all("<Delete>"))
        self.condition_id   .bind("<FocusOut>"      , lambda event : main_window.canvas.bind_all  ('<Delete>', lambda event: canvas_editing.delete()))
        # Create bindings for moving:
        self.frame_id       .bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        self.condition_label.bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        self.condition_id   .bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        self.action_label   .bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        self.action_id      .bind("<B1-Motion>"     , self.move_item) # Touching inside the window.
        # Define layout:
        self.register_all_widgets_at_grid()
        # Create canvas window for the frame:
        self.window_id = main_window.canvas.create_window(menu_x, menu_y, window=self.frame_id, anchor=tk.W)
        # Create dictionary for translating the canvas-id of the canvas-window into a reference to this object:
        ConditionAction.dictionary[self.window_id] = self

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
            self.frame_id       .bind("<ButtonRelease-1>", self.move_item_end)
            self.condition_label.bind("<ButtonRelease-1>", self.move_item_end)
            self.condition_id   .bind("<ButtonRelease-1>", self.move_item_end)
            self.action_label   .bind("<ButtonRelease-1>", self.move_item_end)
            self.action_id      .bind("<ButtonRelease-1>", self.move_item_end)
            canvas_event_x = main_window.canvas.canvasx(event.x)
            canvas_event_y = main_window.canvas.canvasy(event.y)
            coords = main_window.canvas.coords(self.window_id)
            self.difference_x, self.difference_y = - canvas_event_x + coords[0], - canvas_event_y + coords[1]
        move_list = [[self.window_id, ""]]
        move_handling.move_do(event, move_list, first=False)

    def move_item_end(self, event):
        self.first_call_of_move_item = True
        self.frame_id       .unbind("<ButtonRelease-1>")
        self.condition_label.unbind("<ButtonRelease-1>")
        self.condition_id   .unbind("<ButtonRelease-1>")
        self.action_label   .unbind("<ButtonRelease-1>")
        self.action_id      .unbind("<ButtonRelease-1>")
        move_handling_finish.hide_the_connection_line_of_moved_condition_action_window([[self.window_id, ""]])
        undo_handling.design_has_changed()

    def register_all_widgets_at_grid(self):
        self.condition_label.grid (row=0, column=0, sticky=(tk.W,tk.E))
        self.condition_id.grid    (row=1, column=0, sticky=(tk.W,tk.E))
        self.action_label.grid    (row=2, column=0, sticky=(tk.W,tk.E))
        self.action_id.grid       (row=3, column=0, sticky=(tk.W,tk.E))

    def tag(self, connected_to_reset_entry):
        if connected_to_reset_entry is True:
            tag=('condition_action'+str(ConditionAction.conditionaction_id), "ca_connection"+str(ConditionAction.conditionaction_id) + "_anchor", "connected_to_reset_transition")
        else:
            tag=('condition_action'+str(ConditionAction.conditionaction_id), "ca_connection"+str(ConditionAction.conditionaction_id) + "_anchor")
        main_window.canvas.itemconfigure(self.window_id, tag=tag)

    def change_descriptor_to(self, text):
        self.action_label.config(text=text) # Used for switching between "asynchronous" and "synchron" (clocked) transition.

    def draw_line(self, transition_id, menu_x, menu_y):
        # Draw a line from the transition start point to the condition_action block which is added to the transition:
        transition_coords = main_window.canvas.coords (transition_id)
        transition_tags   = main_window.canvas.gettags(transition_id)
        self.line_id = main_window.canvas.create_line(menu_x, menu_y, transition_coords[0], transition_coords[1], dash=(2,2), state=tk.HIDDEN,
                       tag=('ca_connection'+str(ConditionAction.conditionaction_id),'connected_to_' + transition_tags[0]))
        main_window.canvas.addtag_withtag("ca_connection"+str(ConditionAction.conditionaction_id)+"_end", transition_id)
        main_window.canvas.tag_lower(self.line_id,transition_id)

    def activate(self):
        self.frame_id.configure(padding=3) # increase the width of the line around the box
        self.action    = self.action_id.get   ("1.0", tk.END)
        self.condition = self.condition_id.get("1.0", tk.END)
        self.register_all_widgets_at_grid()

    def deactivate(self):
        self.frame_id.configure(padding=1) # decrease the width of the line around the box
        self.frame_id.focus() # "unfocus" the Text, when the mouse leaves the text.
        if (self.condition_id.get("1.0", tk.END)!= self.condition or
            self.action_id.get   ("1.0", tk.END)!= self.action):
            undo_handling.design_has_changed()
        if self.condition_id.get("1.0", tk.END)=="\n" and self.action_id.get("1.0", tk.END)!="\n":
            self.condition_label.grid_forget()
            self.condition_id.grid_forget()
        if self.condition_id.get("1.0", tk.END)!="\n" and self.action_id.get("1.0", tk.END)=="\n":
            self.action_label.grid_forget()
            self.action_id.grid_forget()

    def move_to(self, event_x, event_y, first, last):
        self.frame_id.configure(padding=1) # decrease the width of the line around the box
        if first is True:
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
        # Move the line which connects the window to the transition:
        window_tags = main_window.canvas.gettags(self.window_id)
        for tag in window_tags:
            if tag.startswith("ca_connection"):
                line_tag = tag[:-7]
        self.line_coords = main_window.canvas.coords(line_tag)
        self.line_coords[0] = event_x
        self.line_coords[1] = event_y
        main_window.canvas.coords(line_tag, self.line_coords)
        main_window.canvas.itemconfig(line_tag, state=tk.NORMAL)

    def hide_line(self):
        window_tags = main_window.canvas.gettags(self.window_id)
        for t in window_tags:
            if t.startswith("ca_connection"):
                line_tag = t[:-7]
        main_window.canvas.itemconfig(line_tag, state=tk.HIDDEN)

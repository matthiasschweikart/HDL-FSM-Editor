from tkinter import *

class MyListbox(Listbox):

    def __init__(self, master, items, *args, **kwargs):
        Listbox.__init__(self, master, exportselection = False, background = 'grey', *args, **kwargs)

        for item in items:
            self.insert(END, item)

        self.bind('<Enter>',  self.snapHighlightToMouse)
        self.bind('<Motion>', self.snapHighlightToMouse)

    def snapHighlightToMouse(self, event):
        self.selection_clear(0, END)
        self.selection_set(self.nearest(event.y))

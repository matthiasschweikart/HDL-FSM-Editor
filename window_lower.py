import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root, bg="bisque")
canvas.pack(fill="both", expand=True)

def focus_win(event):
    event.widget.lift()

for n, color in enumerate(("black", "red", "orange", "green", "blue", "white")):
    win = tk.Frame(canvas, background=color, width=100, height=100)
    x = 50 + n*20
    y = 50 + n*20
    canvas.create_window(x, y, window=win)
    win.bind("<1>", focus_win)
rec = canvas.create_rectangle(x, y, x+100, y+100)
canvas.tag_raise(rec, "all")


root.mainloop()
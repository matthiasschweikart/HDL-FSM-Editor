import tkinter as tk
from tkinter import ttk


def toggle_state():
    if button3.instate(["disabled"]):
        button3.state(["!disabled"])
        button4.state(["!disabled"])
        button2.configure(text="Disable Button 3")
    else:
        button3.state(["disabled"])
        button4.state(["disabled"])
        button2.configure(text="Enable Button 3")


def switch_to_normal_mode():
    style.configure("Button2.TButton", foreground="black", background="cyan2")
    style.map(
        "Button2.TButton",
        font=[],
        foreground=[("active", "black"), ("disabled", "grey65")],
        background=[("active", "cyan"), ("disabled", "grey85")],
    )


def switch_to_dark_mode():
    style.configure("Button2.TButton", foreground="cyan2", background="black")
    style.map(
        "Button2.TButton",
        font=[("disabled", ("TkDefaultFont", 10, "italic"))],
        foreground=[("active", "cyan"), ("disabled", "cyan2")],
        background=[("active", "black"), ("disabled", "black")],
    )


def toggle_mode():
    if button1.cget("text").startswith("Switch button3 to dark mode"):
        switch_to_dark_mode()
        button1.configure(text="Switch button3 to normal mode")
    else:
        switch_to_normal_mode()
        button1.configure(text="Switch button3 to dark mode")


root = tk.Tk()

style = ttk.Style()
style.theme_use("default")
# style.theme_use("clam")
switch_to_normal_mode()

button1 = ttk.Button(root, text="Switch button3 to dark mode", command=toggle_mode)
button2 = ttk.Button(root, text="Disable Button 3", command=toggle_state)
button3 = ttk.Button(root, text="Button3: my-style", style="Button2.TButton")
button4 = ttk.Button(root, text="Button4: default")
button1.grid()
button2.grid()
button3.grid()
button4.grid()
# 2. Basis-Konfiguration für das Entry-Widget (Standard-Zustand)
style.configure(
    "TEntry",
    padding=6,
    relief="flat",  # Flaches, modernes Design
    borderwidth=1,
    bordercolor="#CCCCCC",  # Grauer Rahmen im inaktiven Zustand
    lightcolor="#CCCCCC",  # Verhindert 3D-Effekte des Themes
    fieldbackground="white",
)

# 3. Dynamische Fokus-Steuerung per 'style.map'
style.map(
    "TEntry",
    # Wenn 'focus' aktiv ist -> Blau, sonst -> Grau
    bordercolor=[("focus", "red"), ("!focus", "#CCCCCC")],
    lightcolor=[("focus", "cyan"), ("!focus", "#CCCCCC")],
    # Hintergrund wechselt bei Fokus zu einem sanften Hellblau
    fieldbackground=[("focus", "#F0F7FF"), ("!focus", "white")],
)

# Test-Widgets hinzufügen (zwei Stück, um den Fokus-Wechsel mit 'Tab' zu sehen)
entry1 = ttk.Entry(root)
entry1.grid()

root.mainloop()

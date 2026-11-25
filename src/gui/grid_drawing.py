"""
This class draws a grid into the canvas.
Das Menu soll der Zustansspeicher sein.
Beim Toolstart wird erst immer das Grid sichtbar gemacht.
Falls im .rc-File grid_invisible gespeichert ist, wird danach das Grid ausgeblendet.
Das Menu muss immer entsprechend umgeschaltet werden.
Die Methoden remove_grid und draw_grid werden verwendet, wenn z.B. beim Zoomen das Grid angepasst werden muss.
Während remove_grid nicht prüfen muss, ob das Grid sichtbar ist,
prüft draw_grid dies und zeichnet das Grid nur, wenn es sichtbar sein soll.
Da das Menu der Zustandsspeicher ist und das Menu in der Klasse GridDraw nicht sichtbar ist,
müsste der Zustand, wenn benötigt, eigentlich als Parameter mitgegeben werden.
Besser wäre es aber, wenn die Klasse GridDraw solche Parameter nicht sehen würde,
d.h. wenn grid_draw() aufgerufen wird, immer auch ein Grid zu zeichnen wäre.
grid_draw wird aufgerufen:

"""

import tkinter as tk

from project_manager import project_manager


class GridDraw:
    """
    This class draws a grid into the canvas.
    """

    grid_color_normal_mode = "gray85"
    grid_color_dark_mode = "gray50"

    def __init__(self, canvas) -> None:
        self.canvas = canvas
        self.color = GridDraw.grid_color_normal_mode
        self.grid_is_visible = True
        self.draw_grid()

    def remove_grid(self) -> None:
        """Remove all grid lines from the canvas."""
        self.canvas.delete("grid_line")

    def draw_grid(self) -> None:
        """Draw grid lines in the visible window; lower grid below content."""
        if self.grid_is_visible:
            self.remove_grid()  # prevent grid to exist multiple times
            visible_window = [
                self.canvas.canvasx(0),
                self.canvas.canvasy(0),
                self.canvas.canvasx(self.canvas.winfo_width()),
                self.canvas.canvasy(self.canvas.winfo_height()),
            ]
            grid_size = project_manager.state_radius
            if grid_size > 8:
                self._draw_horizontal_grid(grid_size, visible_window)
                self._draw_vertical_grid(grid_size, visible_window)
            self.canvas.tag_lower("grid_line")

    def _draw_horizontal_grid(self, grid_size, visible_window) -> None:
        # An extra margin of 3*grid_size is used because otherwise there are sometimes too few grid-lines:
        x_min = visible_window[0] - visible_window[0] % grid_size - 3 * grid_size
        x_max = visible_window[2] + visible_window[2] % grid_size + 3 * grid_size
        y = visible_window[1] - visible_window[1] % grid_size - 3 * grid_size
        y_max = visible_window[3] + visible_window[3] % grid_size + 3 * grid_size
        while y < y_max:
            self.canvas.create_line(x_min, y, x_max, y, dash=(1, 1), fill=self.color, tags="grid_line")
            y += grid_size

    def _draw_vertical_grid(self, grid_size, visible_window) -> None:
        x = visible_window[0] - visible_window[0] % grid_size
        x_max = visible_window[2] + visible_window[2] % grid_size
        y_min = visible_window[1] - visible_window[1] % grid_size
        y_max = visible_window[3] + visible_window[3] % grid_size
        while x < x_max:
            self.canvas.create_line(x, y_min, x, y_max, dash=(1, 1), fill=self.color, tags="grid_line")
            x += grid_size

    def show_context_menu(self) -> None:
        """Show context menu at zoom_coords for background color and grid visibility."""
        if project_manager.menu_bar_ref.prefs_menu.entrycget(0, "label") == "Dark Mode":
            background = "gray92"
            forgeround = "black"
            activebackground = "royal blue"
        else:
            background = "black"
            forgeround = "white"
            activebackground = "gray"
        menu = tk.Menu(
            project_manager.canvas,
            tearoff=0,
            background=background,
            foreground=forgeround,
            activebackground=activebackground,
        )
        menu.add_command(label="Change background color", command=project_manager.tab_control_ref.choose_bg_color)
        if self.grid_is_visible is True:
            menu.add_command(label="Hide grid", command=self.toggle_grid)
        else:
            menu.add_command(label="Show grid", command=self.toggle_grid)
        menu.tk_popup(project_manager.root.winfo_pointerx(), project_manager.root.winfo_pointery())

    def toggle_grid(self) -> None:
        if self.grid_is_visible:
            self.grid_is_visible = False
            self.remove_grid()
        else:
            self.grid_is_visible = True
            self.draw_grid()

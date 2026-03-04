"""
This class draws a grid into the canvas.
"""

from project_manager import project_manager


class GridDraw:
    """
    This class draws a grid into the canvas.
    """

    def __init__(self, canvas) -> None:
        self.canvas = canvas
        self.show_grid = True

    def remove_grid(self) -> None:
        """Remove all grid lines from the canvas."""
        self.canvas.delete("grid_line")

    def draw_grid(self) -> None:
        """Draw grid lines in the visible window if show_grid is True; lower grid below content."""
        if self.show_grid is True:
            visible_window = [
                self.canvas.canvasx(0),
                self.canvas.canvasy(0),
                self.canvas.canvasx(self.canvas.winfo_width()),
                self.canvas.canvasy(self.canvas.winfo_height()),
            ]
            grid_size = project_manager.state_radius
            if grid_size > 8:
                self.__draw_horizontal_grid(grid_size, visible_window)
                self.__draw_vertical_grid(grid_size, visible_window)
        self.canvas.tag_lower("grid_line")

    def __draw_horizontal_grid(self, grid_size, visible_window) -> None:
        # An extra margin of 3*grid_size is used because otherwise there are sometimes too few grid-lines:
        x_min = visible_window[0] - visible_window[0] % grid_size - 3 * grid_size
        x_max = visible_window[2] + visible_window[2] % grid_size + 3 * grid_size
        y = visible_window[1] - visible_window[1] % grid_size - 3 * grid_size
        y_max = visible_window[3] + visible_window[3] % grid_size + 3 * grid_size
        while y < y_max:
            self.canvas.create_line(x_min, y, x_max, y, dash=(1, 1), fill="gray85", tags="grid_line")
            y += grid_size

    def __draw_vertical_grid(self, grid_size, visible_window) -> None:
        x = visible_window[0] - visible_window[0] % grid_size
        x_max = visible_window[2] + visible_window[2] % grid_size
        y_min = visible_window[1] - visible_window[1] % grid_size
        y_max = visible_window[3] + visible_window[3] % grid_size
        while x < x_max:
            self.canvas.create_line(x, y_min, x, y_max, dash=(1, 1), fill="gray85", tags="grid_line")
            x += grid_size

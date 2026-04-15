"""Class for moving the sashes of an increasing window:
First the sashes are moved into sight, if they are outside of the window.
Then it is checked how much free space is in each each text widget.
If there is free space in one widget and another widget needs space,
then each sash (from top to down) is moved up as far as possible.
This is done until the last widget is reached and then the process is
repeated in reverse direction until the first widget is reached.
During this second phase the sashes are moved down.
"""


class SashMover:
    """Class for moving the sashes of an increasing window"""

    def __init__(self, paned_window, text_list):
        self.paned_window = paned_window
        self.text_list = text_list
        self._move_sashes_into_sight()
        oversize_list = self._create_oversize_list()
        if not oversize_list:
            return
        self._move_sashes(oversize_list)

    def _move_sashes_into_sight(self) -> None:
        number_of_texts = len(self.text_list)
        if self.paned_window.sashpos(number_of_texts - 2) + 10 > self.paned_window.winfo_height():
            for index in range(number_of_texts - 1):
                self.paned_window.sashpos(index, int(self.paned_window.winfo_height() * (index + 1) / number_of_texts))

    def _create_oversize_list(self) -> list:
        oversize_list = []
        character_height = self._get_character_height()
        if character_height != 0:
            for text in self.text_list:
                text_height = text.get("1.0", "end").count("\n") * character_height + 4  # +4 for padding
                oversize = text.winfo_height() - text_height
                oversize_list.append(oversize)
        if oversize_list and (
            all(oversize >= 0 for oversize in oversize_list)  # no space needed
            or all(oversize <= 0 for oversize in oversize_list)  # no space available
        ):
            return []
        return oversize_list

    def _move_sashes(self, oversize_list) -> None:
        for index in range(len(oversize_list) - 1):
            if oversize_list[index] > 0 and not all(os > 0 for os in oversize_list[index + 1 :]):
                self.paned_window.sashpos(
                    index,
                    self.paned_window.sashpos(index) - oversize_list[index],  # shift up
                )
                oversize_list[index + 1] = oversize_list[index + 1] + oversize_list[index]
                oversize_list[index] = 0
        for index in range(len(oversize_list) - 1, 0, -1):
            if oversize_list[index] > 0 and not all(os >= 0 for os in oversize_list[:index]):
                self.paned_window.sashpos(
                    index - 1,
                    self.paned_window.sashpos(index - 1) + oversize_list[index],  # shift down
                )
                oversize_list[index - 1] = oversize_list[index - 1] + oversize_list[index]
                oversize_list[index] = 0

    def _get_character_height(self) -> int:
        character_height = 0
        for text in self.text_list:
            character_bbox = text.bbox("1.0")
            if character_bbox != (0, 0, 0, 0) and character_bbox[3] is not None:
                character_height = character_bbox[3]
        return character_height

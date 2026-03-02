"""
This class modifies the data at file-write in a way
that the resulting file will only differ from the read file
if the user added/removed/moved any schematic-element or
changed any text/name/contol-information. Any scrolling, zooming
will not create a different file content.
"""

import canvas_editing


class WriteDataCreator:
    """
    Only one WriteDataCreator object is used.
    It is created at a file-operation.
    """

    def __init__(self, standard_size) -> None:
        """Store standard_size for normalized write; last_design_dictionary used for change detection."""
        self.standard_size = standard_size
        self.last_design_dictionary = None

    def store_as_compare_object(self, design_dictionary) -> None:
        """Store design_dictionary as baseline for later diff (e.g. to avoid unnecessary file writes)."""
        self.last_design_dictionary = design_dictionary

    def zoom_graphic_to_standard_size(self, actual_size) -> float:
        """Zoom canvas to standard_size/actual_size at origin; return the zoom factor."""
        zoom_factor = self.standard_size / actual_size
        canvas_editing.canvas_zoom([0, 0], zoom_factor)
        return zoom_factor

    def zoom_graphic_back_to_actual_size(self, zoom_factor) -> None:
        """Restore canvas zoom by applying 1/zoom_factor at origin."""
        canvas_editing.canvas_zoom([0, 0], 1 / zoom_factor)

    def round_and_sort_data(self, design_dictionary, allowed_element_names_in_design_dictionary) -> dict[str, list]:
        """Sort and round coordinates/parameters in design_dictionary; store as compare object; return updated dict."""
        used_element_names = self._get_used_element_names(design_dictionary, allowed_element_names_in_design_dictionary)
        design_dictionary = self._sort_graphic_elements(design_dictionary, used_element_names)
        design_dictionary = self._round_coordinates(design_dictionary, used_element_names)
        design_dictionary = self._round_parameters(design_dictionary)
        self.store_as_compare_object(design_dictionary)
        return design_dictionary

    def _get_used_element_names(self, design_dictionary, allowed_element_names_in_design_dictionary) -> list:
        used_element_names = []
        for element_name in allowed_element_names_in_design_dictionary:
            if element_name in design_dictionary:
                used_element_names.append(element_name)
        return used_element_names

    def _round_coordinates(self, design_dictionary, used_element_names) -> dict[str, list]:
        for element_name in used_element_names:
            if element_name in ("window_condition_action_block", "window_global_actions"):
                index_of_tags = 3
            elif element_name.startswith("window_"):
                index_of_tags = 2
            else:
                index_of_tags = 1
            for graphic_instance_index, graphical_instance_property_list in enumerate(design_dictionary[element_name]):
                identifier_at_write = graphical_instance_property_list[index_of_tags][0]
                coordinates_at_write = graphical_instance_property_list[0]
                identifier_from_last, coordinates_from_last = self._get_info_from_last_data_by_index(
                    element_name, graphic_instance_index, index_of_tags
                )
                for coordinate_index, coordinate_at_write in enumerate(coordinates_at_write):
                    coordinate_at_write = round(coordinate_at_write, 0)  # round to integer
                    if (
                        # In the last data there is a corresponding graphical instance:
                        identifier_from_last != ""
                        # The graphic instance is not a wire or a wire whose number of points did not change:
                        and len(coordinates_at_write) == len(coordinates_from_last)
                        # The graphic instance exists in last data at same position in the list:
                        and identifier_at_write == identifier_from_last
                        # The last coordinate is already a (rounded) integer value:
                        and coordinates_from_last[coordinate_index] % 1 == 0
                        # And differs from the new value:
                        and coordinates_from_last[coordinate_index] != coordinate_at_write
                        # And differs only by a small amount:
                        and abs(coordinates_from_last[coordinate_index] - coordinate_at_write)
                        < 0.2 * self.standard_size
                    ):
                        coordinate_at_write = coordinates_from_last[coordinate_index]
                    graphical_instance_property_list[0][coordinate_index] = coordinate_at_write
        return design_dictionary

    def _get_info_from_last_data_by_index(self, element_name, graphic_instance_index, index_of_tags) -> list:
        if (
            self.last_design_dictionary is not None
            and element_name in self.last_design_dictionary
            and graphic_instance_index < len(self.last_design_dictionary[element_name])
        ):
            identifier_from_last = self.last_design_dictionary[element_name][graphic_instance_index][index_of_tags][0]
            coordinates_from_last = self.last_design_dictionary[element_name][graphic_instance_index][0]
        else:
            identifier_from_last = ""
            coordinates_from_last = []
        return identifier_from_last, coordinates_from_last

    def _round_parameters(self, design_dictionary) -> dict[str, list]:
        design_dictionary["label_fontsize"] = round(design_dictionary["label_fontsize"], 0)
        design_dictionary["priority_distance"] = round(design_dictionary["priority_distance"], 0)
        return design_dictionary

    def _sort_graphic_elements(self, design_dictionary, used_element_names) -> dict[str, list]:
        # At all sorts the key is the first tag which the graphical element has (identifier tag).
        # The sorting will always give the same result if the order of tags is not changed by tkinter.
        for element_name in used_element_names:
            if element_name in ("window_condition_action_block", "window_global_actions"):
                index_of_tags = 3
            elif element_name.startswith("window_"):
                index_of_tags = 2
            else:
                index_of_tags = 1
            design_dictionary[element_name] = sorted(
                design_dictionary[element_name], key=lambda x, idx=index_of_tags: x[idx][0]
            )
        return design_dictionary

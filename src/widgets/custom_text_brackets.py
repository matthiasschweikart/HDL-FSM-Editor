"""Bracket highlighting helper for CustomText widgets."""

import re
import tkinter as tk


class BracketHighlighter:
    """Encapsulates bracket matching and highlighting logic for a tkinter Text widget."""

    def __init__(
        self,
        text_widget,
        normal_tag_names,
        normal_colors,
    ):
        self.text_widget = text_widget
        self.normal_tag_names = normal_tag_names
        self.normal_colors = normal_colors

    def highlight_brackets(self, language) -> None:
        """Highlight matching brackets in the text."""
        self._unhighlight_all_bracket_pairs()
        bracket_dicts = []  # Resets the bracket-dictionary used for show_corresponding_brackets().
        bracket_search_strings = [r"[\(\)]"] if language == "VHDL" else [r"[\(\)]", r"[\[\]]", r"[\{\}]"]
        for bracket_search_string in bracket_search_strings:
            # Create a bracket dictionary:
            # Keys = indices of all opening and closing brackets in the text.
            # Value = A dictionary for each index, which has "bracket_char" as key and the bracket-character as value.
            bracket_dict = self._create_bracket_dict(bracket_search_string)
            bracket_dicts.append(bracket_dict.copy())  # Save before bracket_dict is modified in the while-loop.
            color_number = 0
            continue_loop = True
            while continue_loop:
                # Remove all most "inner" closed brackets.
                continue_loop = False
                last_index = None
                last_char = None
                for index, char_dict in list(bracket_dict.items()):
                    self.text_widget.tag_add("bracket_color_wrong", index)  # Default color.
                    bracket_dicts[-1][index]["corresponding_bracket_index"] = None  # Default value.
                    opening_bracket_to_search = self._determine_opening_bracket_to_search(char_dict)
                    if opening_bracket_to_search is not None and last_char == opening_bracket_to_search:
                        self._highlight_bracket_pair(last_index, index, color_number)
                        bracket_dicts[-1][last_index]["corresponding_bracket_index"] = index
                        bracket_dicts[-1][index]["corresponding_bracket_index"] = last_index
                        self._remove_found_bracket_pair(bracket_dict, last_index, index)  # For next while-loop step.
                        continue_loop = True
                    last_index = index
                    last_char = char_dict["bracket_char"]
                color_number = (color_number + 1) % len(self.normal_colors)
        self._show_corresponding_brackets(bracket_dicts)

    def _show_corresponding_brackets(self, bracket_dicts) -> None:
        for bracket_dict in bracket_dicts:
            insert_index = self.text_widget.index(tk.INSERT)
            if insert_index in bracket_dict:
                self._add_bracket_highlight_tag(insert_index, bracket_dict)
                return
            insert_index = self.text_widget.index(tk.INSERT + " -1c")
            if insert_index in bracket_dict:
                self._add_bracket_highlight_tag(insert_index, bracket_dict)

    def _unhighlight_all_bracket_pairs(self) -> None:
        for tag_name in self.normal_tag_names:
            self.text_widget.tag_remove(tag_name, "1.0", tk.END)  # Remove each bracket color tag.

    def _create_bracket_dict(self, bracket_search_string) -> dict:
        bracket_dict = {}
        match_objects = re.finditer(
            bracket_search_string, self.text_widget.get("1.0", tk.END)
        )  # Find opening and closing brackets.
        for match_object in match_objects:
            bracket_index = self.text_widget.index(f"1.0+{match_object.start()}c")
            bracket_dict[bracket_index] = {"bracket_char": match_object.group(0)}
        return bracket_dict

    def _determine_opening_bracket_to_search(self, char_dict) -> str | None:
        # Only for a closing bracket the last character must be checked for an opening bracket.
        if char_dict["bracket_char"] == ")":
            opening_bracket_to_search = "("
        elif char_dict["bracket_char"] == "]":
            opening_bracket_to_search = "["
        elif char_dict["bracket_char"] == "}":
            opening_bracket_to_search = "{"
        else:
            opening_bracket_to_search = None
        return opening_bracket_to_search

    def _remove_found_bracket_pair(self, bracket_dict, last_index, index) -> None:
        del bracket_dict[last_index]  # Remove opening bracket for next while-loop step.
        del bracket_dict[index]  # Remove closing bracket for next while-loop step.

    def _highlight_bracket_pair(self, last_index, index, color_number) -> None:
        self.text_widget.tag_remove("bracket_color_wrong", last_index)
        self.text_widget.tag_remove("bracket_color_wrong", index)
        self.text_widget.tag_add("bracket_color_start" + str(color_number), last_index)
        self.text_widget.tag_add("bracket_color_end" + str(color_number), index)

    def _add_bracket_highlight_tag(self, insert_index, bracket_dict) -> None:
        corresponding_bracket_index = bracket_dict[insert_index]["corresponding_bracket_index"]
        if corresponding_bracket_index is not None:
            self.text_widget.tag_remove("highlight", "1.0", tk.END)
            self.text_widget.tag_add("highlight", insert_index)
            self.text_widget.tag_add("highlight", corresponding_bracket_index)

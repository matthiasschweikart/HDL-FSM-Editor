"""
The LinkDictionary shall carry all information which are needed to create hyperlinks from each line in the generated HDL
to the graphical source of the line.
The LinkDictionary is created once, when the HDL-SCHEM-Editor is started.
All accesses to the LinkDictionary are done by using the class variable link_dict_reference.
The LinkDictionary is filled when the HDL is generated and at some other events.
At HDL generation only the needed information is gathered and send to the LinkDictionary.
The LinkDictionary must then build up the dictionary which afterwards will be used by the HDL tab.
The HDL tab observes the mouse movements and at a left mouse button press at a line a method of the
LinkDictionary is called, which shows the graphical source of this HLD code line.

When the LinkDictionary is filled by the HDL generation, a HDL-file-name and a HDL-file-line-number must be handed over.
These 2 parameters are the keys of the LinkDictionary, so when the user clicks on a line in a HDL file in the HDL-tab,
line-number and file-name are determined and the corresponding entry of the LinkDictionary can be read.
"""

import tkinter as tk

import main_window
from codegen import hdl_generation
from codegen.hdl_generation_config import GenerationConfig
from constants import GuiTab
from project_manager import project_manager


class LinkDictionary:
    """
    The LinkDictionary shall carry all information which are needed to create hyperlinks from each line in
     the generated HDL to the graphical source of the line.
    """

    def __init__(self) -> None:
        self.link_dict = {}

    def add(
        self,
        file_name: str,  # Filename in which the HDL-item is stored
        file_line_number: int,  # File-line-number in which the HDL-item is stored
        hdl_item_type: str,  # One of HdlItemType enum values
        number_of_lines: int,  # How many lines does the HDL-item use in the file
        hdl_item_name: str | tk.Widget,  # String when "Control-Tab", widget-references in all other cases
    ) -> None:
        """Register a link from (file_name, line) to the given tab/widget/line for HDL navigation."""
        # print("add =", file_name, file_line_number, hdl_item_type, number_of_lines, hdl_item_name)
        if file_name not in self.link_dict:
            self.link_dict[file_name] = {}
        if hdl_item_type == "Control-Tab":
            self.link_dict[file_name][file_line_number] = {
                "tab_name": GuiTab.CONTROL,
                "widget_reference": main_window,  # TODO: das hier ist Quatsch, oder ?!
                "hdl_item_type": hdl_item_name,
                "object_identifier": "",
                "number_of_line": "",
            }
        elif hdl_item_type == "custom_text_in_interface_tab":
            for text_line_number in range(1, number_of_lines + 1):
                self.link_dict[file_name][file_line_number + text_line_number - 1] = {
                    "tab_name": GuiTab.INTERFACE,
                    "widget_reference": hdl_item_name,
                    "hdl_item_type": "",
                    "object_identifier": "",
                    "number_of_line": text_line_number,
                }
        elif hdl_item_type == "custom_text_in_internals_tab":
            for text_line_number in range(1, number_of_lines + 1):
                self.link_dict[file_name][file_line_number + text_line_number - 1] = {
                    "tab_name": GuiTab.INTERNALS,
                    "widget_reference": hdl_item_name,
                    "hdl_item_type": "",
                    "object_identifier": "",
                    "number_of_line": text_line_number,
                }
        elif hdl_item_type == "custom_text_in_diagram_tab":
            for text_line_number in range(1, number_of_lines + 1):
                self.link_dict[file_name][file_line_number + text_line_number - 1] = {
                    "tab_name": GuiTab.DIAGRAM,
                    "widget_reference": hdl_item_name,
                    "hdl_item_type": "",
                    "object_identifier": "",
                    "number_of_line": text_line_number,
                }

    def has_link(self, file_name: str, file_line_number: int) -> bool:
        """Check if a link exists for the given file and line."""
        return file_name in self.link_dict and file_line_number in self.link_dict[file_name]

    def jump_to_source(self, selected_file, file_line_number) -> None:
        """Switch to the according tab and highlight the given HDL file/line."""
        # print("jump_to_source", selected_file, file_line_number)
        tab_to_show = self.link_dict[selected_file][file_line_number]["tab_name"]
        widget = self.link_dict[selected_file][file_line_number]["widget_reference"]
        hdl_item_type = self.link_dict[selected_file][file_line_number]["hdl_item_type"]
        object_identifier = self.link_dict[selected_file][file_line_number]["object_identifier"]
        number_of_line = self.link_dict[selected_file][file_line_number]["number_of_line"]
        project_manager.notebook.show_tab(tab_to_show)
        widget.highlight_item(hdl_item_type, object_identifier, number_of_line)

    def jump_to_hdl(self, selected_file, file_line_number) -> None:
        """Switch to Generated HDL output tab and highlight the given file/line."""
        if project_manager.select_file_number_text.get() == 2:
            gen_config = GenerationConfig.from_main_window()
            file_name_architecture = gen_config.get_architecture_file()
            if file_name_architecture and selected_file == file_name_architecture:
                file_line_number += hdl_generation.last_line_number_of_file1
        project_manager.notebook.show_tab(GuiTab.GENERATED_HDL)
        project_manager.hdl_frame_text.highlight_item("", "", file_line_number)
        project_manager.hdl_frame_text.config(state="normal")
        project_manager.hdl_frame_text.focus_set()
        project_manager.hdl_frame_text.config(state="disabled")

    def clear_link_dict(self, file_name) -> None:
        """Remove all link entries for the given file name."""
        if file_name in self.link_dict:
            # print("clear_link_dict: file_name =", file_name)
            self.link_dict.pop(file_name)


_link_dictionary: LinkDictionary | None = None


def init_link_dict(root) -> None:
    """Create and store the global LinkDictionary instance."""
    global _link_dictionary
    _link_dictionary = LinkDictionary(root)


def link_dict() -> LinkDictionary:
    """Return the global LinkDictionary instance (must be initialized first)."""
    assert _link_dictionary is not None
    return _link_dictionary

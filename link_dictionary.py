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
import main_window
import hdl_generation

class LinkDictionary():
    link_dict_reference = None
    def __init__(self, root):
        self.root = root
        LinkDictionary.link_dict_reference = self
        self.link_dict = {}
    def add(self,
            file_name,        # Filename in which the HDL-item is stored
            file_line_number, # File-line-number in which the HDL-item is stored
            hdl_item_type,    # One of "Control-Tab", "custom_text_in_interface_tab", "custom_text_in_internals_tab", "custom_text_in_diagram_tab"
            number_of_lines,  # How many lines does the HDL-item use in the file
            hdl_item_name,    # String when "Control-Tab", widget-references in all other cases
            number_of_line    # not used
            ):

        #print("add =", file_name, file_line_number, hdl_item_type, number_of_lines , hdl_item_name, number_of_line)
        if file_name not in self.link_dict:
            self.link_dict[file_name] = {}
        if hdl_item_type=="Control-Tab":
            self.link_dict[file_name][file_line_number]     = {"tab_name"         : "Control",
                                                               "widget_reference" : main_window,
                                                               "hdl_item_type"    : hdl_item_name, 
                                                               "object_identifier": "",
                                                               "number_of_line"   : ""}
        elif hdl_item_type=="custom_text_in_interface_tab":
            for text_line_number in range(1, number_of_lines+1):
                self.link_dict[file_name][file_line_number] = {"tab_name"         : "Interface",
                                                               "widget_reference" : hdl_item_name,
                                                               "hdl_item_type"    : "",
                                                               "object_identifier": "",
                                                               "number_of_line"   : text_line_number}
                file_line_number += 1
        elif hdl_item_type=="custom_text_in_internals_tab":
            for text_line_number in range(1, number_of_lines+1):
                self.link_dict[file_name][file_line_number] = {"tab_name"         : "Internals",
                                                               "widget_reference" : hdl_item_name,
                                                               "hdl_item_type"    : "",
                                                               "object_identifier": "",
                                                               "number_of_line"   : text_line_number}
                file_line_number += 1
        elif hdl_item_type=="custom_text_in_diagram_tab":
            for text_line_number in range(1, number_of_lines+1):
                self.link_dict[file_name][file_line_number] = {"tab_name"         : "Diagram",
                                                               "widget_reference" : hdl_item_name,
                                                               "hdl_item_type"    : "",
                                                               "object_identifier": "",
                                                               "number_of_line"   : text_line_number}
                file_line_number += 1

    def jump_to_source(self, selected_file, file_line_number):
        #print("jump_to_source", selected_file, file_line_number)
        tab_to_show       = self.link_dict[selected_file][file_line_number]["tab_name"]
        widget            = self.link_dict[selected_file][file_line_number]["widget_reference"]
        hdl_item_type     = self.link_dict[selected_file][file_line_number]["hdl_item_type"]
        object_identifier = self.link_dict[selected_file][file_line_number]["object_identifier"]
        number_of_line    = self.link_dict[selected_file][file_line_number]["number_of_line"]
        main_window.show_tab(tab_to_show)
        widget.highlight_item(hdl_item_type, object_identifier, number_of_line)

    def jump_to_hdl(self, selected_file, file_line_number):
        if main_window.select_file_number_text.get()==2:
            _, file_name_architecture = hdl_generation.get_file_names()
            if selected_file==file_name_architecture:
                file_line_number += hdl_generation.last_line_number_of_file1
        main_window.show_tab("generated HDL")
        main_window.hdl_frame_text.highlight_item("", "", file_line_number)
        main_window.hdl_frame_text.config(state="normal")
        main_window.hdl_frame_text.focus_set()
        main_window.hdl_frame_text.config(state="disabled")

    def clear_link_dict(self, file_name):
        if file_name in self.link_dict:
            #print("clear_link_dict: file_name =", file_name)
            self.link_dict.pop(file_name)

"""
This code was copied (and extended) from https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
"""
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import re
import main_window
import linting
import hdl_generation_library
import hdl_generation_architecture_state_actions
import canvas_editing
import constants
import file_handling

class CustomText(tk.Text):
    read_variables_of_all_windows    = {}
    written_variables_of_all_windows = {}

    def __init__(self, *args, type, **kwargs):
        """A text widget that report on internal widget commands"""
        tk.Text.__init__(self, *args, **kwargs) # does not help: pady=5, pagdy is used to make sure that the undserscore line "_" is always visible at most font sizes.
        self.type = type
        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.bind("<Tab>"      , lambda event : self.replace_tabs_by_blanks())
        self.bind("<Control-e>", lambda event : self.edit_in_external_editor()) # Overwrites the default control-e = "move cursor to end of line"
        self.bind("<Control-o>", lambda event : self._open())                   # Overwrites the default control-o = "insert a new line", needed for opening a new file.
        self.bind("<Key>"      , lambda event : self.format_after_idle())
        self.bind("<Button-1>" , lambda event : self.tag_delete("highlight"))
        self.signals_list        = []
        self.constants_list      = []
        self.readable_ports_list = []
        self.writable_ports_list = []
        self.generics_list       = []
        self.port_types_list     = []
        CustomText.read_variables_of_all_windows   [self] = []
        CustomText.written_variables_of_all_windows[self] = []

    def _open(self):
        file_handling.open_file()
        return "break" # Prevent a second call of open_file() by bind_all binding (which is located in entry 4 of the bind-list).

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        try:
            result = self.tk.call(cmd)
            if command in ("insert", "delete", "replace"):
                self.event_generate("<<TextModified>>")
            return result
        except Exception as e:
            return None

    def replace_tabs_by_blanks(self):
        self.insert(tk.INSERT,"    ") # replace the Tab by 4 blanks.
        self.format_after_idle()
        return "break" # This prevents the "Tab" to be inserted in the text.

    def edit_in_external_editor(self):
        if main_window.language.get()=="VHDL":
            file_name = "hdl-fsm-editor.tmp.vhd"
        else:
            file_name = "hdl-fsm-editor.tmp.v"
        fileobject = open(file_name, 'w')
        fileobject.write(self.get("1.0", tk.END + "- 1 chars"))
        fileobject.close()
        try:
            edit_cmd = main_window.edit_cmd.get().split()
            edit_cmd.append(file_name)
            process = subprocess.Popen(edit_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        except FileNotFoundError:
            messagebox.showerror("Error", "Error when running " + main_window.edit_cmd.get() + " " + file_name)
            return
        while True:
            poll = process.poll()
            if poll is not None:
                break
        fileobject = open(file_name, 'r')
        new_text = fileobject.read()
        fileobject.close()
        os.remove(file_name)
        self.delete("1.0", tk.END)
        self.insert("1.0", new_text)
        self.format()

    def format_after_idle(self):
        self.after_idle(self.format)

    def format(self):
        text = self.get("1.0",tk.END)
        nr_of_lines=0
        nr_of_characters_in_line=0
        max_line_length=0
        if (self not in [main_window.interface_generics_text, main_window.interface_package_text, main_window.interface_ports_text,
                         main_window.internals_architecture_text, main_window.internals_process_clocked_text,
                         main_window.internals_process_combinatorial_text, main_window.internals_package_text]):
            for c in text:
                if c!='\n':
                    nr_of_characters_in_line += 1
                    if nr_of_characters_in_line>max_line_length:
                        max_line_length = nr_of_characters_in_line
                else:
                    nr_of_lines += 1
                    nr_of_characters_in_line = 0
            self.config(width=max_line_length)
            self.config(height=nr_of_lines)
        self.__update_entry_of_this_window_in_list_of_read_and_written_variables_of_all_windows()
        self.update_highlighting()

    def update_highlighting(self):
        self.update_highlight_tags(canvas_editing.fontsize, ["control" , "datatype" , "function"])
        linting.recreate_keyword_list_of_unused_signals()
        linting.update_highlight_tags_in_all_windows_for_not_read_not_written_and_comment()

    def update_highlight_tags(self, fontsize, keyword_type_list):
        for keyword_type in keyword_type_list:
            self.tag_delete(keyword_type)
            for keyword in main_window.keywords[keyword_type]:
                self.add_highlight_tag_for_single_keyword(keyword_type, keyword)
            if self.type in ("condition", "action"):
                self.tag_configure(keyword_type, foreground=main_window.keyword_color[keyword_type],
                                   font=("Courier", int(fontsize), "bold")) # int() is necessary, because fontsize can be a "real" number.
            else:
                self.tag_configure(keyword_type, foreground=main_window.keyword_color[keyword_type], font=("Courier", 10))

    def add_highlight_tag_for_single_keyword(self, keyword_type, keyword):
        count = tk.IntVar()
        start = "1.0"
        while True:
            if keyword_type=="comment":
                index = self.search(keyword, start, tk.END, count=count, regexp=True, nocase=1) # index = "line.column"
                if index=="" or count.get()==0:
                    break
                self.tag_add   ("comment"    , index, index + " + " + str(count.get()) + " chars")
                self.tag_remove("control"    , index, index + " + " + str(count.get()) + " chars")
                self.tag_remove("datatype"   , index, index + " + " + str(count.get()) + " chars")
                self.tag_remove("function"   , index, index + " + " + str(count.get()) + " chars")
                self.tag_remove("not_read"   , index, index + " + " + str(count.get()) + " chars")
                self.tag_remove("not_written", index, index + " + " + str(count.get()) + " chars")
                start = index + " + " + str(count.get()) + " chars"
            else:
                index = self.search("([^a-zA-Z0-9_]|^)" + keyword + "([^a-zA-Z0-9_]|$)", start, tk.END, count=count, regexp=True, nocase=1) # index = "line.column"
                if index=="" or count.get()==0:
                    break
                if   count.get()==len(keyword)+2:
                    index = self.index(index + " + 1 chars")
                elif count.get()==len(keyword)+1:
                    if self.get(index, index + " + " + str(count.get()) + " chars").endswith(keyword):
                        index = self.index(index + " + 1 chars")
                self.tag_add(keyword_type, index, index + " + " + str(len(keyword)) + " chars")
                start = index + " + " + str(len(keyword)) + " chars"

    def undo(self):
        #self.edit_undo() # causes a second "undo", as Ctrl-z automatically starts edit_undo()
        self.after_idle(self.update_declaration_lists)
        self.format_after_idle()

    def redo(self):
        self.edit_redo()
        self.after_idle(self.update_declaration_lists)
        self.format_after_idle()

    def update_declaration_lists(self):
        if self==main_window.internals_architecture_text:
            self.update_custom_text_class_signals_list()
        elif self==main_window.interface_ports_text:
            self.update_custom_text_class_ports_list()

    def update_custom_text_class_signals_list(self):
        all_signal_declarations  = self.get ("1.0",tk.END).lower()
        self.signals_list   = hdl_generation_library.get_all_declared_signal_names  (all_signal_declarations)
        self.constants_list = hdl_generation_library.get_all_declared_constant_names(all_signal_declarations)

    def update_custom_text_class_ports_list(self):
        all_port_declarations    = main_window.interface_ports_text.get("1.0",tk.END).lower()
        self.readable_ports_list = hdl_generation_architecture_state_actions.get_all_readable_ports(all_port_declarations, check=False)
        self.writable_ports_list = hdl_generation_architecture_state_actions.get_all_writable_ports(all_port_declarations)
        self.port_types_list     = hdl_generation_architecture_state_actions.get_all_port_types    (all_port_declarations)

    def update_custom_text_class_generics_list(self):
        all_generic_declarations = main_window.interface_generics_text.get("1.0",tk.END).lower()
        self.generics_list = hdl_generation_architecture_state_actions.get_all_generic_names(all_generic_declarations)

    def __update_entry_of_this_window_in_list_of_read_and_written_variables_of_all_windows(self):
        CustomText.read_variables_of_all_windows   [self] = []
        CustomText.written_variables_of_all_windows[self] = []
        text = self.get("1.0", tk.END + "- 1 chars")
        text = hdl_generation_library.convert_hdl_lines_into_a_searchable_string(text)
        #print("text 0 =", text)
        text = self.__remove_keywords(text)
        #print("text 1 =", text)
        if self.type=="condition":
            text = self.__remove_condition_keywords(text)
            CustomText.read_variables_of_all_windows[self] = text.split()
        elif self.type=="action":
            text = self.__add_read_variables_from_with_select_blocks_to_read_variables_of_all_windows(text)
            text = self.__add_read_variables_from_conditions_to_read_variables_of_all_windows        (text)
            text = self.__add_read_variables_from_case_constructs_to_read_variables_of_all_windows   (text)
            text = self.__add_read_variables_from_assignments_to_read_variables_of_all_windows       (text)
            text = self.__add_read_variables_from_always_statements_to_read_variables_of_all_windows (text)
            #print("read_variables_of_all_windows[self] =", CustomText.read_variables_of_all_windows[self])
            text = re.sub(" when | when$|^when |^when$", "", text, flags=re.I) # remove remaining "when" of a "case"-statement (left hand side).
            text = re.sub(" else | else$|^else |^else$", "", text, flags=re.I) # remove remaining "else" of an if-clause (left hand side).
            CustomText.written_variables_of_all_windows[self] = text.split()
            #print("text =\n", text)
            # When the ";" is missing, then the right hand side with "<=" could not be found and erased.
            # So remove "<=" and ":=" from these lists:
            if "<=" in CustomText.read_variables_of_all_windows[self]:
                CustomText.read_variables_of_all_windows[self].remove("<=")
            if ":=" in CustomText.read_variables_of_all_windows[self]:
                CustomText.read_variables_of_all_windows[self].remove(":=")
            if "<=" in CustomText.written_variables_of_all_windows[self]:
                CustomText.written_variables_of_all_windows[self].remove("<=")
            if ":=" in CustomText.written_variables_of_all_windows[self]:
                CustomText.written_variables_of_all_windows[self].remove(":=")

    def __remove_keywords(self, text):
        if main_window.language.get()=="VHDL":
            text = self.__remove_keywords_from_vhdl(text)
        else:
            text = self.__remove_keywords_from_verilog(text)
        return text

    def __remove_keywords_from_vhdl(self, text):
        for keyword in constants.vhdl_keywords_for_signal_handling + (
                    " process[^;]*?begin ",
                    " end\\s+?case\\s*?;",
                    " end\\s+?process\\s*?;",
                    " end\\s+?if\\s*?;",
                    "\\(" ,
                    "\\)" ,
                    "\\+" ,              
                    "-"   ,              
                    "/"   ,              
                    "%"   ,              
                    "&"   ,              
                    "=>",                   # something like "others =>"
                    " [0-9]+ ",             # something like " 123 "
                    "'.'" ,                 # something like the std_logic value '1' or '0'
                    '\\s"[0-9,a-f,A-F]+"',  # something like " 1234AB"
                    '[^\\s]"[0-9,a-f,A-F]+"'# something like X"1234"
                    ):
            text = re.sub(keyword, "  ", text, flags=re.I) # Keep the blanks the keyword is surrounded by.
        return text
    def __remove_keywords_from_verilog(self, text):
        for keyword in constants.verilog_keywords_for_signal_handling + (
                        " end ",
                        " endcase\\s*?;",
                        "\\(" ,
                        "\\)" ,
                        "{" ,
                        "}" ,
                        "\\+"   ,              
                        "-"   ,              
                        "/"   ,              
                        "%"   ,              
                        " [0-9]+ " ,            # something like 123
                        " [0-9]+'[^0-9][0-9]+ " # something like 3'b000
                        ):
            text = re.sub(keyword, "  ", text, flags=re.I) # Keep the blanks the keyword is surrounded by.
        return text

    def __remove_condition_keywords(self, text):
        if main_window.language.get()=="VHDL":
            for keyword in (
                        " = " ,
                        " /= ",
                        " < " ,
                        " <= ",
                        " > " ,
                        " >= "):
                text = re.sub(keyword, "  ", text, flags=re.I) # Keep the blanks the keyword is surrounded by.
        else:
            for keyword in (
                        " === ",
                        " == " ,
                        " != " ,
                        " < "  ,
                        " <= " ,
                        " > "  ,
                        " >= " ,
                        " = "  ,  # This is an uncomplete comparison, which shall not be identified as signal by highlighting.
                        " ! "     # This is an uncomplete comparison, which shall not be identified as signal by highlighting.
                        ):
                text = re.sub(keyword, "  ", text, flags=re.I) # Keep the blanks the keyword is surrounded by.
        return text

    def __add_read_variables_from_with_select_blocks_to_read_variables_of_all_windows(self, text):
        if main_window.language.get()=="VHDL":
            with_select_search_pattern = "with\\s+.*?\\s+select"
            all_with_selects = []
            while True: # Collect all with_selects and remove them from text.
                match = re.search(with_select_search_pattern, text, flags=re.IGNORECASE)
                if match:
                    all_with_selects.append(match.group(0))
                    text = text[:match.start()] + text[match.end():] # remove match from text
                else:
                    break
            for with_select in all_with_selects:
                with_select = re.sub("^with "  , " ", with_select, flags=re.I)
                with_select = re.sub(" select$", " ", with_select, flags=re.I)
                CustomText.read_variables_of_all_windows[self] += with_select.split() # split() removes only blanks here.
        return text

    def __add_read_variables_from_conditions_to_read_variables_of_all_windows(self, text):
        if main_window.language.get()=="VHDL":
            condition_search_pattern = "^if\\s+[^;]*?\\s+then| if\\s+[^;]*?\\s+then|elsif\\s+[^;]*?\\s+then|^when\\s+[^;]*?\\s+else| when\\s+[^;]*?\\s+else"
        else:
            condition_search_pattern = "^if\\s+[^;]*?\\s+begin| if\\s+[^;]*?\\s+begin" # Verilog
        all_conditions = []
        while True: # Collect all conditions and remove them from text.
            #print("text for search =", text)
            match = re.search(condition_search_pattern, text, flags=re.IGNORECASE)
            if match:
                #print("match.group(0)", match.group(0))
                all_conditions.append(match.group(0))
                text = text[:match.start()] + text[match.end():] # remove match from text
                #print(text)
            else:
                break
        for condition in all_conditions:
            if main_window.language.get()=="VHDL":
                condition = re.sub("^if| if"        , " ", condition, flags=re.I)
                condition = re.sub("^elsif| elsif"  , " ", condition, flags=re.I)
                condition = re.sub(" then$"         , " ", condition, flags=re.I)
                condition = re.sub("^when| when"    , " ", condition, flags=re.I)
                condition = re.sub(" else$"         , " ", condition, flags=re.I)
                for keyword in (
                            " = " ,
                            " /= ",
                            " < " ,
                            " <= ",
                            " > " ,
                            " >= "):
                    condition = re.sub(keyword, "  ", condition) # Keep the blanks the keyword is surrounded by.
            else:
                condition = re.sub("^if| if " , " ", condition, flags=re.I)
                condition = re.sub(" begin$"  , " ", condition, flags=re.I)
                for keyword in (
                            " === ",
                            " == " ,
                            " != " ,
                            " < "  ,
                            " <= " ,
                            " > "  ,
                            " >= " ,
                            " = "  ,  # This is an uncomplete comparison, which shall not be identified as signal by highlighting.
                            " ! " ):  # This is an uncomplete comparison, which shall not be identified as signal by highlighting.
                    condition = re.sub(keyword, "  ", condition) # Keep the blanks the keyword is surrounded by.
            CustomText.read_variables_of_all_windows[self] += condition.split()
        return text

    def __add_read_variables_from_case_constructs_to_read_variables_of_all_windows(self, text):
        if main_window.language.get()=="VHDL":
            case_search_pattern = "^case\\s+.+?\\s+is| case\\s+.+?\\s+is"
        else:
            case_search_pattern = "^case\\s*?\\(.*?\\)| case\\s*?\\(.*?\\)" # Verilog
        all_cases = []
        while True: # Collect all case-statements and remove them from text.
            match = re.search(case_search_pattern, text, flags=re.IGNORECASE)
            if match:
                all_cases.append(match.group(0))
                text = text[:match.start()] + text[match.end():] # remove match from text
            else:
                break
        for case in all_cases:
            if main_window.language.get()=="VHDL":
                case = re.sub("^case | case "  , "", case, flags=re.I)
                case = re.sub(" is$"    , "", case, flags=re.I)
            else:
                case = re.sub("^case\\s*?\\(| case\\s*?\\("  , "" , case, flags=re.I)
                case = re.sub("\\)"            , "" , case, flags=re.I)
                case = re.sub(","              , " ", case, flags=re.I)
            CustomText.read_variables_of_all_windows[self] += case.split()
        return text

    def __add_read_variables_from_assignments_to_read_variables_of_all_windows(self, text):
        right_hand_side_search_pattern = "=.*?;"
        while True: # Collect all right hand sides and remove them from text.
            match = re.search(right_hand_side_search_pattern, text, flags=re.IGNORECASE)
            if match:
                text = text[:match.start()-1] + text[match.end():] # remove not only the match but also complete ":=" or "<=".
                hit = match.group(0)[+1:-1]
                hit = re.sub(","     , "", hit) # Remove "," of a "with .. select" statement.
                hit = re.sub(" when | when$|^when |^when$", "", hit, flags=re.I) # remove remaining "when" of a "with .. select"-statement (right hand side).
                hit = re.sub(" else | else$|^else |^else$", "", hit, flags=re.I) # remove remaining "else" of an "when .. else"-clause (right hand side).
                CustomText.read_variables_of_all_windows[self] += hit.split()
            else:
                break
        return text

    def __add_read_variables_from_always_statements_to_read_variables_of_all_windows (self, text):
        while True:
            match = re.search(r"always\s*@.*?begin", text, flags=re.IGNORECASE)
            if match:
                text = text[:match.start()] + text[match.end():]
                hit = match.group(0)
                hit = re.sub(r"always\s*@", "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"begin"     , "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"\("        , "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"\)"        , "", hit, flags=re.IGNORECASE)
                hit = re.sub(r" or "      , "", hit, flags=re.IGNORECASE)
                hit = re.sub(r" and "     , "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"posedge "  , "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"negedge "  , "", hit, flags=re.IGNORECASE)
                hit = re.sub(r"\*"        , "", hit, flags=re.IGNORECASE)
                CustomText.read_variables_of_all_windows[self] += hit.split()
            else:
                break
        return text

    def highlight_item(self, hdl_item_type, object_identifier, number_of_line):
        self.tag_add("highlight", str(number_of_line) + ".0", str(number_of_line+1) + ".0" )
        #self.tag_config("highlight", background="#e9e9e9")
        self.tag_config("highlight", background="orange")
        self.see(str(number_of_line) + ".0")
        self.focus_set()

"""This module provides the CustomTextLinting class for analyzing text to determine read and written variables."""

import re

import constants
from codegen import hdl_generation_library
from project_manager import project_manager

VHDL_KEYWORD_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in constants.VHDL_KEYWORDS_FOR_SIGNAL_HANDLING
    + (
        r" procedure\s+.*?\sis\s+begin\s+(|.*?\s)end\s+.*?;",  # remove the complete procedure definition ...
        r" process[^;]*?begin ",  # ... because then the "process" regular expression can work correctly.
        r" end\s+?process\s*?;",
        r" end\s+?case\s*?;",
        r" end\s+?if\s*?;",
        r" end\s*?;",
        r" end\s+",
        r"\(",
        r"\)",
        r"\+",
        r"\*",
        r"true",
        r"false",
        r"-",
        r"/",
        r"%",
        r"&",
        r"=>",
        r"' . '",
        r" [0-9]+ ",
        r'[^\\s]"[0-9,a-f,A-F]+"',
        r'"[0,1]+"',
        r"report\s*'.*?'",
        r'report\s*".*?"',
    )
]
DATATYPE_PATTERNS = [
    re.compile(r" " + re.escape(k) + r" ", re.IGNORECASE) for k in constants.VHDL_HIGHLIGHT_PATTERN_DICT["datatype"]
]


class CustomTextLinting:
    """This class analyzes the given text and determines which variables are read and which are written."""

    def __init__(self, text, text_type, my_read_variables, my_written_variables) -> None:
        self.text_type = text_type
        self.function_names_list = []
        self.my_read_variables = my_read_variables
        self.my_written_variables = my_written_variables
        # Remove comments and returns and add blanks around special characters:
        text = hdl_generation_library.convert_hdl_lines_into_a_searchable_string(text)
        if text.isspace():  # i.e. true, if the text was only a comment.
            return
        self._update_entry_of_this_window_in_list_of_read_and_written_variables_of_all_windows(text)

    def _update_entry_of_this_window_in_list_of_read_and_written_variables_of_all_windows(self, text) -> None:
        self.my_read_variables.clear()
        self.my_written_variables.clear()
        self._fill_function_names_list(text)
        if project_manager.language.get() == "VHDL":
            text = self._remove_loop_indices(text)
        if project_manager.language.get() == "VHDL":
            text = self._add_incomplete_vhdl_variables_to_read_or_written_variables_of_all_windows(text)
        text = self._add_read_constants_from_case_when_to_read_variables_of_all_windows(text)  # Keywords are used here.
        text = self._remove_keywords(text)
        text = self._remove_vhdl_attributes(text)
        if project_manager.language.get() == "VHDL":
            text = re.sub(r"\..*?\s", " ", text)  # remove all record-element-names from their signal/variable names
        if self.text_type == "condition":
            text = self._remove_condition_keywords(text)
            self.my_read_variables = text.split()
        elif self.text_type == "action":
            text = self._process_action_read_and_written_variables(text)
            # Store the remaining variable names and remove duplicates from the list,
            # use "+=" as _add_to_read_or_written_variables_of_all_windows() already added entries:
            self.my_written_variables += list(set(text.split()))
            # When the ";" is missing, then the right hand side with "<=" could not be found and erased.
            # So remove "<=" and ":=" from these lists:
            self._remove_items_from_list(self.my_read_variables, ["<=", ":="])
            self._remove_items_from_list(self.my_read_variables, self.function_names_list)
            self._remove_items_from_list(self.my_read_variables, [";", ","])
            # ';' appears at VHDL-"null" assignments.
            self._remove_items_from_list(self.my_written_variables, [";", "<=", ":="])

    def _process_action_read_and_written_variables(self, text: str) -> None:
        text = self._add_read_variables_from_procedure_calls_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_with_select_blocks_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_conditions_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_case_constructs_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_assignments_to_read_variables_of_all_windows(text)
        text = self._add_read_variables_from_always_statements_to_read_variables_of_all_windows(text)
        # use "+=" as _add_to_read_or_written_variables_of_all_windows() already added entries:
        self.my_read_variables += list(set(self.my_read_variables))
        # remove remaining "when" of a "case/select"-statement (left hand side)
        text = re.sub(" when | when$|^when |^when$", "", text, flags=re.I)
        # remove remaining "|" of a "case"-statement
        text = re.sub(r"\|", "", text, flags=re.I)
        # remove remaining "else" of an if-clause (left hand side)
        text = re.sub(" else | else$|^else |^else$", "", text, flags=re.I)
        return text

    def _fill_function_names_list(self, text):
        match_objects = re.finditer(r"function\s+(\w+)", text, re.IGNORECASE)
        for match_object in match_objects:
            function_name = match_object.group(1)
            if function_name not in self.function_names_list:
                self.function_names_list.append(function_name)

    def _remove_vhdl_attributes(self, text):
        # remove signal-name and attribute; example: "addr ' range"
        # The character "'" is surrounded by blanks because of convert_hdl_lines_into_a_searchable_string().
        search_for_attributes = r"\w+\s+'\s+\w+"
        return re.sub(search_for_attributes, " ", text)

    def _remove_loop_indices(self, text):
        # Search for "for ... in" and remove it and also the loop index.
        match_objects = re.finditer(r"\sfor\s+(.+?)\s+in\s", text, re.IGNORECASE)
        for match_object in match_objects:
            loop_command = match_object.group(0)
            loop_index = " " + match_object.group(1) + " "
            text = re.sub(loop_command, " ", text)
            text = re.sub(loop_index, " ", text)
        return text

    def _add_incomplete_vhdl_variables_to_read_or_written_variables_of_all_windows(self, text):
        text_list, proc_list, remaining_text = self._split_in_lists_of_text_and_processes(text)
        for p_number, process in enumerate(proc_list):
            process, all_variable_names = self._remove_variable_declarations(process)
            process, written_variables = self._remove_written_variables(process, all_variable_names)
            process, read_variables = self._remove_read_variables(process, all_variable_names)
            proc_list[p_number] = process
            self._add_to_read_or_written_variables_of_all_windows(all_variable_names, written_variables, read_variables)
        new_text = ""
        # Reconstruct the text from text_list and the modified processes from proc_list:
        for i, text_before in enumerate(text_list):
            new_text += text_before + proc_list[i]
        return new_text + remaining_text

    def _split_in_lists_of_text_and_processes(self, text):
        proc_list = []
        text_list = []
        match_objects = re.finditer(
            r"process(\s|\().*?\sbegin(\s|\s.*?\s)end\s+process(\s*;|\s.*?;)", text, re.IGNORECASE
        )
        text_start_index = 0
        for match_object in match_objects:
            text_list.append(text[text_start_index : match_object.start()])
            proc_list.append(text[match_object.start() : match_object.end()])
            text_start_index = match_object.end()
        return text_list, proc_list, text[text_start_index:]

    def _remove_variable_declarations(self, process):
        all_variable_names = []
        match_objects = re.finditer(r"\svariable\s+(.*?):.*?;", process, re.IGNORECASE)
        for match_object in match_objects:
            variable_name = match_object.group(1).strip()
            if variable_name not in all_variable_names:
                all_variable_names.append(variable_name)
            process = (
                process[: match_object.start()]
                + " " * (match_object.end() - match_object.start())
                + process[match_object.end() :]
            )  # remove declaration and keep the indices of the other matches valid.
        return process, all_variable_names

    def _remove_written_variables(self, process, all_variable_names):
        written_variables = []
        for variable_name in all_variable_names:
            search_for_assignment_to_variable = rf"\s{variable_name}\s*:="
            match_objects = re.finditer(search_for_assignment_to_variable, process, flags=re.IGNORECASE)
            for match_object in match_objects:
                # Remove variable name but leave ":=":
                process = (
                    process[: match_object.start()]
                    + " " * (len(match_object.group(0)) - 2)
                    + process[match_object.end() - 2 :]
                )
                written_variables.append(variable_name)
        written_variables = list(set(written_variables))  # remove duplicates
        return process, written_variables

    def _remove_read_variables(self, process, all_variable_names):
        read_variables = []
        for variable_name in all_variable_names:
            search_for_reading_of_variable = rf"\s{variable_name}\s"
            match_objects = re.finditer(search_for_reading_of_variable, process, flags=re.IGNORECASE)
            for match_object in match_objects:
                # Insert $ to keep "case <variable> is" as a complete statement (keep match indices valid):
                process = (
                    process[: match_object.start()]
                    + " "
                    + "$" * (len(match_object.group(0)) - 2)
                    + " "
                    + process[match_object.end() :]
                )
                read_variables.append(variable_name)
        read_variables = list(set(read_variables))  # remove duplicates
        return process, read_variables

    def _add_to_read_or_written_variables_of_all_windows(self, all_variable_names, written_variables, read_variables):
        for process_variable_name in all_variable_names:
            if process_variable_name in read_variables:
                self.my_read_variables += [process_variable_name]  # may be be colored red
            if process_variable_name in written_variables:
                self.my_written_variables += [process_variable_name]  # may be colored yellow
        for used_variable_name in written_variables + read_variables:
            if used_variable_name not in all_variable_names:
                self.my_read_variables += [used_variable_name]  # may be colored red

    def _remove_keywords(self, text):
        if project_manager.language.get() == "VHDL":
            text = self._remove_keywords_from_vhdl(text)
        else:
            text = self._remove_keywords_from_verilog(text)
        return text

    def _remove_keywords_from_vhdl(self, text):
        for pattern in VHDL_KEYWORD_PATTERNS:
            text = pattern.sub("  ", text)  # Keep the blanks the keyword is surrounded by.
        for pattern in DATATYPE_PATTERNS:
            text = pattern.sub("  ", text)  # Keep the blanks the keyword is surrounded by.
        return text

    def _remove_keywords_from_verilog(self, text):
        for keyword in constants.VERILOG_KEYWORDS_FOR_SIGNAL_HANDLING + (
            " end ",
            " endcase\\s*?;",
            "\\(",
            "\\)",
            "{",
            "}",
            "\\+",
            "-",
            "/",
            "%",
            " [0-9]+ ",  # something like 123
            " [0-9]+'[^0-9][0-9]+ ",  # something like 3'b000
        ):
            text = re.sub(keyword, "  ", text, flags=re.I)  # Keep the blanks the keyword is surrounded by.
        return text

    def _remove_condition_keywords(self, text):
        if project_manager.language.get() == "VHDL":
            for keyword in (" = ", " /= ", " < ", " <= ", " > ", " >= "):
                text = re.sub(keyword, "  ", text, flags=re.I)  # Keep the blanks the keyword is surrounded by.
        else:
            for keyword in (
                " === ",
                " == ",
                " != ",
                " < ",
                " <= ",
                " > ",
                " >= ",
                " = ",  # This is an incomplete comparison, which shall not be identified as signal by highlighting.
                " ! ",  # This is an incomplete comparison, which shall not be identified as signal by highlighting.
            ):
                text = re.sub(keyword, "  ", text, flags=re.I)  # Keep the blanks the keyword is surrounded by.
        return text

    def _add_read_variables_from_procedure_calls_to_read_variables_of_all_windows(self, text) -> str:
        if project_manager.language.get() != "VHDL":
            return text
        all_procedure_calls = []
        match_objects = re.finditer(r"(?:(?<=^)|(?<=;))(?![^;]*=)[^;]*;", text, re.IGNORECASE)
        # The regular expression looks for all expressions which are not assignments:
        # (?:  Non capturing group (adds no characters to the match)
        # (?<=^)  Positive lookbehind for start of string '^'
        # (?<=;)  Positive lookbehind for semicolon ';'
        # This means the character before the match must be ^ or ';'.
        # (?![^;]*=)  Negative lookahead for assignment
        # This means, when the next characters do not have ';' but end with '=', then this is no match.
        # All other characters until the next ';' are matched:
        for match_object in match_objects:
            all_procedure_calls.append(match_object.group(0)[:-1])  # append without semicolon
            text = text[: match_object.start()] + " " * len(match_object.group(0)) + text[match_object.end() :]
        for procedure_call in all_procedure_calls:
            procedure_parameters = self._remove_procedure_name(procedure_call)
            procedure_parameter_list = procedure_parameters.split(",")
            for procedure_parameter in procedure_parameter_list:
                procedure_parameter = procedure_parameter.strip()
                if (
                    procedure_parameter != ""
                    and procedure_parameter not in ["x", "X"]
                    and not procedure_parameter.isdigit()
                ):
                    # As the procedure definition may not be part of this VHDL file,
                    # it can not for sure be determined, which parameter is read and which parameter is written.
                    if (
                        procedure_parameter
                        in project_manager.tab_interface_ref.interface_ports_text.readable_ports_list
                    ):
                        # If a parameter is an input port, then it is read.
                        self.my_read_variables += [procedure_parameter]
                    elif (
                        procedure_parameter
                        in project_manager.tab_interface_ref.interface_ports_text.writable_ports_list
                    ):
                        # If a parameter is an output port, then it is written and
                        # must be added to the variable text with a pseudo assignment:
                        text += " " + procedure_parameter + " <= ; "
                    else:
                        # If a parameter is neither an input nor an output, then the parameter is probably a signal.
                        # But it is not clear if it is written or read and
                        # to avoid false alarms it is added to both lists:
                        self.my_read_variables += [procedure_parameter]
                        text += " " + procedure_parameter + " <= ; "
        return text

    def _remove_procedure_name(self, procedure_call):
        return re.sub(r"^.*?\s", "", procedure_call.lstrip())

    def _add_read_variables_from_with_select_blocks_to_read_variables_of_all_windows(self, text) -> str:
        if project_manager.language.get() == "VHDL":
            all_with_selects = []
            match_objects = re.finditer(r"with\s+.*?\s+select", text, re.IGNORECASE)
            for match_object in match_objects:
                all_with_selects.append(match_object.group(0))
                text = text[: match_object.start()] + " " * len(match_object.group(0)) + text[match_object.end() :]
            for with_select in all_with_selects:
                with_select = re.sub("^with ", " ", with_select, flags=re.I)
                with_select = re.sub(" select$", " ", with_select, flags=re.I)
                self.my_read_variables += with_select.split()  # split() removes only blanks here.
        return text

    def _add_read_variables_from_conditions_to_read_variables_of_all_windows(self, text) -> str:
        if project_manager.language.get() == "VHDL":
            condition_search_pattern = (
                "^if\\s+[^;]*?\\s+then| if\\s+[^;]*?\\s+then|elsif\\s+[^;]*?\\s+then|"
                + "^when\\s+[^;]*?\\s+else| when\\s+[^;]*?\\s+else"
            )
        else:
            condition_search_pattern = "^if\\s+[^;]*?\\s+begin| if\\s+[^;]*?\\s+begin"  # Verilog
        all_conditions = []
        match_objects = re.finditer(condition_search_pattern, text, flags=re.IGNORECASE)
        for match_object in match_objects:
            all_conditions.append(match_object.group(0))
            text = text[: match_object.start()] + " " * len(match_object.group(0)) + text[match_object.end() :]
        for condition in all_conditions:
            if project_manager.language.get() == "VHDL":
                condition = re.sub("^if| if", " ", condition, flags=re.I)
                condition = re.sub("^elsif| elsif", " ", condition, flags=re.I)
                condition = re.sub(" then$", " ", condition, flags=re.I)
                condition = re.sub("^when| when", " ", condition, flags=re.I)
                condition = re.sub(" else$", " ", condition, flags=re.I)
                for keyword in (" = ", " /= ", " < ", " <= ", " > ", " >= "):
                    condition = re.sub(keyword, "  ", condition)  # Keep the blanks the keyword is surrounded by.
            else:
                condition = re.sub("^if| if ", " ", condition, flags=re.I)
                condition = re.sub(" begin$", " ", condition, flags=re.I)
                for keyword in (
                    " === ",
                    " == ",
                    " != ",
                    " < ",
                    " <= ",
                    " > ",
                    " >= ",
                    " = ",  # This is an incomplete comparison, which shall not be identified as signal by highlighting.
                    " ! ",
                ):  # This is an incomplete comparison, which shall not be identified as signal by highlighting.
                    condition = re.sub(keyword, "  ", condition)  # Keep the blanks the keyword is surrounded by.
            self.my_read_variables += condition.split()
        return text

    def _add_read_constants_from_case_when_to_read_variables_of_all_windows(self, text) -> str:
        if project_manager.language.get() == "VHDL":
            match_objects = re.finditer(r"\swhen\s+([^\s\"\']+?)\s+=>", text, re.IGNORECASE)
            for match_object in match_objects:
                if match_object.group(1) != "others":
                    self.my_read_variables += [match_object.group(1)]
                text = text[: match_object.start()] + " " * len(match_object.group(0)) + text[match_object.end() :]
        return text

    def _add_read_variables_from_case_constructs_to_read_variables_of_all_windows(self, text) -> str:
        if project_manager.language.get() == "VHDL":
            case_search_pattern = "^case\\s+.+?\\s+is| case\\s+.+?\\s+is"
        else:  # Verilog
            case_search_pattern = "^case\\s*?\\(.*?\\)| case\\s*?\\(.*?\\)"
        all_cases = []
        match_objects = re.finditer(case_search_pattern, text, flags=re.IGNORECASE)
        for match_object in match_objects:
            all_cases.append(match_object.group(0))
            text = text[: match_object.start()] + " " * len(match_object.group(0)) + text[match_object.end() :]
        for case in all_cases:
            if project_manager.language.get() == "VHDL":
                case = re.sub("^case | case ", "", case, flags=re.I)
                case = re.sub(" is$", "", case, flags=re.I)
            else:
                case = re.sub("^case\\s*?\\(| case\\s*?\\(", "", case, flags=re.I)
                case = re.sub("\\)", "", case, flags=re.I)
                case = re.sub(",", " ", case, flags=re.I)
            self.my_read_variables += case.split()
        return text

    def _add_read_variables_from_assignments_to_read_variables_of_all_windows(self, text) -> str:
        match_objects = re.finditer(r"=.*?;", text, re.IGNORECASE)  # Collect all right hand sides.
        for match_object in match_objects:
            # remove not only the match but also complete ":=" or "<=":
            hit = match_object.group(0)[+1:-1]  # Without '=' and without ';'
            hit = re.sub(",", "", hit)  # Remove "," of a "with .. select" statement.
            # remove remaining "when" of a "with .. select"-statement (right hand side):
            hit = re.sub(" when | when$|^when |^when$", "", hit, flags=re.I)
            # remove remaining "else" of an "when .. else"-clause (right hand side).
            hit = re.sub(" else | else$|^else |^else$", "", hit, flags=re.I)
            hit = re.sub(" ' ", "", hit, flags=re.I)  # remove remaining "ticks" of VHDL attributes
            self.my_read_variables += list(set(hit.split()))  # remove duplicates from list
            text = (  # Remove the right hand side from the text.
                text[: match_object.start() - 1] + " " * (len(match_object.group(0)) + 1) + text[match_object.end() :]
            )
        return text

    def _add_read_variables_from_always_statements_to_read_variables_of_all_windows(self, text) -> str:
        match_objects = re.finditer(r"always\s*@.*?begin", text)
        for match_object in match_objects:
            hit = match_object.group(0)
            hit = re.sub(r"always\s*@", "", hit, flags=re.IGNORECASE)
            hit = re.sub(r"begin", "", hit, flags=re.IGNORECASE)
            hit = re.sub(r"\(", "", hit, flags=re.IGNORECASE)
            hit = re.sub(r"\)", "", hit, flags=re.IGNORECASE)
            hit = re.sub(r" or ", "", hit, flags=re.IGNORECASE)
            hit = re.sub(r" and ", "", hit, flags=re.IGNORECASE)
            hit = re.sub(r"posedge ", "", hit, flags=re.IGNORECASE)
            hit = re.sub(r"negedge ", "", hit, flags=re.IGNORECASE)
            hit = re.sub(r"\*", "", hit, flags=re.IGNORECASE)
            self.my_read_variables += list(set(hit.split()))  # remove duplicates from list
            text = text[: match_object.start()] + " " * len(match_object.group(0)) + text[match_object.end() :]
        return text

    def _remove_items_from_list(self, lst: list, items) -> None:
        for item in items:
            if item in lst:
                lst.remove(item)

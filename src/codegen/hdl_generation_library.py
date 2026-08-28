"""
This module contains methods used at HDL generation.
"""

import re
import tkinter as tk

from project_manager import project_manager

from .exceptions import GenerationError

BLOCK_COMMENT_RE = re.compile(r"\/\*.*?\*\/", flags=re.DOTALL)


def indent_text_by_the_given_number_of_tabs(number_of_tabs, text) -> str:
    """Prefix each line with number_of_tabs * 4 spaces; preserve trailing newlines per line."""
    keep_newline_at_each_line_end = True
    list_of_lines = text.splitlines(keep_newline_at_each_line_end)
    result_string = ""
    for line in list_of_lines:
        for _ in range(number_of_tabs):
            line = "    " + line
        result_string += line
    return result_string


def get_text_from_text_widget(widget_id) -> str:
    """Return widget contents; empty string if only a single newline."""
    text = widget_id.get("1.0", tk.END)
    if text != "\n":
        return text
    return ""


def create_reset_condition_and_reset_action() -> list:
    """Return [condition_text, action_text, condition_widget_ref, action_widget_ref] for reset transition;
    Raises GenerationError if missing.
    """
    reset_transition_tag = _get_reset_transition_tag()
    ref = _get_condition_action_reference_of_transition(reset_transition_tag)
    if ref is None:
        reference_to_reset_condition_custom_text = None
        reference_to_reset_action_custom_text = None
        action = ""
        condition = ""
        raise GenerationError(
            "Error",
            [
                "No reset condition is specified,",
                "therefore no HDL will be generated.",
                "Please specify the reset condition by using the right",
                "mouse button at the transition from the reset-connector",
                "to the state, which shall be reached by active reset.",
            ],
        )
    reference_to_reset_condition_custom_text = ref.text_ids[0]
    condition = reference_to_reset_condition_custom_text.get("1.0", tk.END + "-1 chars")  # without "return" at the end
    all_reset_transition_tags = project_manager.canvas.gettags(reset_transition_tag)
    target_state_name = _get_target_state_name(all_reset_transition_tags)
    action = "state <= " + target_state_name + ";\n"
    reference_to_reset_action_custom_text = ref.text_ids[1]
    action_text = reference_to_reset_action_custom_text.get(
        "1.0", tk.END
    )  # action_text will always have a return as last character.
    if action_text != "\n":  # check for empty line
        action += action_text
    return [condition, action, reference_to_reset_condition_custom_text, reference_to_reset_action_custom_text]


def _get_reset_transition_tag() -> str:
    reset_entry_tags = project_manager.canvas.gettags("reset_entry")
    reset_transition_tag = ""
    for t in reset_entry_tags:
        if t.startswith("transition"):  # look for transition<n>_start
            reset_transition_tag = t[:-6]
    return reset_transition_tag


def _get_condition_action_reference_of_transition(transition_tag):
    tags = project_manager.canvas.gettags(transition_tag)
    for tag in tags:
        if tag.startswith("ca_connection"):  # Complete tag: ca_connection<n>_end
            condition_action_number = tag[13:-4]
            condition_action_tag = "condition_action" + condition_action_number
            condition_action_canvas_item_id = project_manager.canvas.find_withtag(condition_action_tag)[0]
            condition_action_reference = project_manager.canvas_windows_ref_dict[condition_action_canvas_item_id]
            return condition_action_reference
    return None


def _get_target_state_name(all_reset_transition_tags):
    target_state_tag = ""
    for t in all_reset_transition_tags:
        if t.startswith("going_to_state"):
            target_state_tag = t[9:]
    target_state_name = project_manager.canvas.itemcget(target_state_tag + "_name", "text")
    return target_state_name


def create_global_actions_before() -> tuple[str, str] | tuple:
    """Return (widget_ref, text) for clocked global 'before' block, or ('', '') if none."""
    canvas_item_ids = project_manager.canvas.find_withtag("global_actions1")
    if canvas_item_ids != ():
        ref = project_manager.canvas_windows_ref_dict[canvas_item_ids[0]]
        return ref.text_ids[0], ref.text_ids[0].get("1.0", tk.END)
    return "", ""


def create_global_actions_after() -> tuple[str, str] | tuple:
    """Return (widget_ref, text) for clocked global 'after' block, or ('', '') if none."""
    canvas_item_ids = project_manager.canvas.find_withtag("global_actions1")
    if canvas_item_ids != ():
        ref = project_manager.canvas_windows_ref_dict[canvas_item_ids[0]]
        return ref.text_ids[1], ref.text_ids[1].get("1.0", tk.END)
    return "", ""


def create_concurrent_actions() -> tuple[str, str] | tuple:
    """Return (widget_ref, text) for combinatorial global actions, or ('', '') if none."""
    canvas_item_ids = project_manager.canvas.find_withtag("global_actions_combinatorial1")
    if canvas_item_ids != ():
        ref = project_manager.canvas_windows_ref_dict[canvas_item_ids[0]]
        return ref.text_ids[0], ref.text_ids[0].get("1.0", tk.END)
    return "", ""


def remove_comments(hdl_text) -> str:
    """Strip block and line comments, normalize to space-separated string for keyword search."""
    if project_manager.language.get() == "VHDL":
        hdl_text = remove_vhdl_block_comments(hdl_text)
    else:
        hdl_text = _remove_verilog_block_comments(hdl_text)
    lines_without_return = hdl_text.split("\n")
    text = ""
    for line in lines_without_return:
        if project_manager.language.get() != "VHDL":
            line_without_comment = re.sub("//.*$", "", line)
        else:
            line_without_comment = re.sub("--.*$", "", line)
        # Add " " at the beginning of the line. Then it is possible to search for keywords
        # surrounded by blanks also at the beginning of text:
        text += " " + line_without_comment + "\n"
    text += " "  # Add " " at the end, so that keywords at the end are also surrounded by blanks.
    return text


def remove_comments_and_returns(hdl_text) -> str:
    """Strip block and line comments, normalize to space-separated string for keyword search."""
    text = remove_comments(hdl_text)
    text = text.replace("\n", "")
    return text


def remove_functions(hdl_text):
    """Remove VHDL/Verilog function declarations from text for signal/constant parsing."""
    text = re.sub(
        r"(^|\s+)function\s+.*end(\s+function\s*;|function)", "", hdl_text
    )  # Regular expression for VHDL and Verilog function declaration
    return text


def remove_type_declarations(hdl_text):
    """Remove VHDL type declarations from text for signal/constant parsing."""
    text = re.sub(
        r"(^|\s+)type\s+\w+\s+is\s+record\s+.*?\send\s+record\s*;", "", hdl_text
    )  # Regular expression for VHDL and Verilog type declaration
    text = re.sub(
        r"(^|\s+)type\s+\w+\s+is\s+.*?;", "", text
    )  # Regular expression for VHDL and Verilog type declaration
    return text


def remove_vhdl_block_comments(list_string):
    """Replace /* ... */ block comments with spaces to preserve character positions."""
    # block comments are replaced by blanks, so all remaining text holds its position.
    while True:
        match_object = BLOCK_COMMENT_RE.search(list_string)
        if match_object is None:
            break
        if match_object.start() == match_object.end():
            break
        list_string = (
            list_string[: match_object.start()]
            + " " * (match_object.end() - match_object.start())
            + list_string[match_object.end() :]
        )
    return list_string


def _remove_verilog_block_comments(hdl_text):
    return re.sub("/\\*.*\\*/", "", hdl_text, flags=re.DOTALL)


def convert_hdl_lines_into_a_searchable_string(text):
    """Remove comments and surround operators/punctuation with spaces for regex/keyword search."""
    without_comments = remove_comments_and_returns(text)
    separated = surround_character_by_blanks(";", without_comments)
    separated = surround_character_by_blanks("(", separated)
    separated = surround_character_by_blanks(")", separated)
    separated = surround_character_by_blanks(":", separated)
    separated = surround_character_by_blanks("!=", separated)
    separated = surround_character_by_blanks("!", separated)
    separated = surround_character_by_blanks("/", separated)
    separated = surround_character_by_blanks("=", separated)
    separated = surround_character_by_blanks(">", separated)
    separated = surround_character_by_blanks("<", separated)
    separated = surround_character_by_blanks(",", separated)
    separated = surround_character_by_blanks("'", separated)
    separated = surround_character_by_blanks("+", separated)
    separated = surround_character_by_blanks("-", separated)
    separated = surround_character_by_blanks("*", separated)
    separated = re.sub("<  =", "<=", separated)  # restore this operator (assignment or comparison)
    separated = re.sub(">  =", ">=", separated)  # restore this operator (comparison)
    separated = re.sub("=  >", "=>", separated)  # restore this operator (when selector in VHDL)
    separated = re.sub("=  =", "==", separated)  # restore this operator (comparison)
    separated = re.sub("/  =", "/=", separated)  # restore this operator (comparison)
    separated = re.sub(":  =", ":=", separated)  # restore this operator (assignment)
    separated = re.sub("!  =", "!=", separated)  # restore this operator (comparison)
    return separated


def surround_character_by_blanks(character, all_port_declarations_without_comments):
    """Replace each occurrence of character with ' character ' in the string."""
    # Add the escape character if necessary:
    search_character = "\\" + character if character in ("(", ")", "+", "*") else character
    return re.sub(search_character, " " + character + " ", all_port_declarations_without_comments)


def get_all_declared_signal_and_variable_names(all_signal_declarations) -> list:
    """Parse semicolon-separated declarations and return list of signal/variable names."""
    signal_declaration_list = all_signal_declarations.split(";")
    signal_list = []
    for declaration in signal_declaration_list:
        if declaration != "" and not declaration.isspace():
            declaration = (
                " " + declaration + " "
            )  # Splitting may have produced declarations without blanks but they are needed for keyword search.
            signals = _get_all_signal_names(declaration)
            if signals != "":
                signal_list.extend(signals.split(","))
    return signal_list


def get_all_declared_constant_names(all_signal_declarations) -> list:
    """Parse semicolon-separated declarations and return list of constant names."""
    signal_declaration_list = all_signal_declarations.split(";")
    constant_list = []
    for declaration in signal_declaration_list:
        if declaration != "" and not declaration.isspace():
            constants = _get_all_constant_names(declaration)
            if constants != "":
                constant_list.extend(constants.split(","))
    return constant_list


def _get_all_signal_names(declaration):
    signal_names = ""
    if " signal " in declaration and project_manager.language.get() == "VHDL":
        if ":" in declaration:
            signal_names = re.sub(":.*", "", declaration)
            signal_names = re.sub(" signal ", "", signal_names)
    elif " variable " in declaration and project_manager.language.get() == "VHDL":
        if ":" in declaration:
            signal_names = re.sub(":.*", "", declaration)
            signal_names = re.sub(" variable ", "", signal_names)
    elif project_manager.language.get() != "VHDL":
        declaration = re.sub(" integer ", " ", declaration, flags=re.I)
        declaration = re.sub(" logic ", " ", declaration, flags=re.I)
        declaration = re.sub(" reg ", " ", declaration, flags=re.I)
        signal_names = re.sub(" \\[.*?\\] ", " ", declaration)
    signal_names_without_blanks = re.sub(" ", "", signal_names)
    return signal_names_without_blanks


def _get_all_constant_names(declaration):
    constant_names = ""
    if " constant " in declaration and project_manager.language.get() == "VHDL" and ":" in declaration:
        constant_names = re.sub(":.*", "", declaration)
        constant_names = re.sub(" constant ", "", constant_names)
    if " localparam " in declaration and project_manager.language.get() != "VHDL":
        declaration = re.sub(" localparam ", " ", declaration, flags=re.I)
        constant_names = re.sub(" \\[.*?\\] ", " ", declaration)
    constant_names_without_blanks = re.sub(" ", "", constant_names)
    return constant_names_without_blanks

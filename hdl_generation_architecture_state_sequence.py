"""
This module contains methods, which are used at HDL generation.
The methods create only the HDL for the state sequence.
"""
import re
import link_dictionary

def create_vhdl_for_the_state_sequence(transition_specifications, file_name, file_line_number):
    vhdl = []
    ignore_control_for_vhdl_indent = []
    for index, transition_specification in enumerate(transition_specifications):
        if   transition_specification["command"]=="when"  :
            vhdl.append("when " + transition_specification["state_name"] + " =>\n")
            ignore_control_for_vhdl_indent.append(False)
            file_line_number += 1
            if "state_comments" in transition_specification:
                state_comments = re.sub(r"^", "    -- ", transition_specification["state_comments"], flags=re.M)
                state_comments = state_comments[:-7] # remove blanks and the comment-string from the last empty line.
                vhdl.append(state_comments)
                ignore_control_for_vhdl_indent.append(False)
                number_of_comment_lines = state_comments.count("\n")
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", number_of_comment_lines,
                                                                       transition_specification["state_comments_canvas_id"], "")
                file_line_number += number_of_comment_lines
        elif transition_specification["command"]=="if"    :
            transition_condition = transition_specification["condition"]
            if transition_condition.endswith("\n"):
                transition_condition = transition_condition[:-1]
            if transition_condition.count("\n")==0:
                if "--" in transition_condition:
                    condition = re.sub(r"\s*--.*", ""  , transition_condition)
                    comment   = re.sub(r".*--"   , "--", transition_condition)
                    vhdl.append("if "   + condition + " then " + comment + "\n")
                else:
                    vhdl.append("if "   + transition_condition + " then\n")
                ignore_control_for_vhdl_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", 1,
                                                                       transition_specification["condition_action_reference"], "")
                file_line_number += 1
                #print("\ntransition_condition =", transition_condition)
            else:
                transition_condition_list = transition_condition.split("\n")
                for index, line in enumerate(transition_condition_list):
                    if index==0:
                        vhdl.append("if " + line + "\n")
                    else:
                        vhdl.append("   " + line + "\n")
                    ignore_control_for_vhdl_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", index+1,
                                                                       transition_specification["condition_action_reference"], "")
                file_line_number += index+1
                vhdl.append("then\n")
                ignore_control_for_vhdl_indent.append(False)
                file_line_number += 1
        elif transition_specification["command"]=="elsif"  :
            transition_condition = transition_specification["condition"]
            if transition_condition.endswith("\n"):
                transition_condition = transition_condition[:-1]
            if transition_condition.count("\n")==0:
                vhdl.append("elsif "   + transition_condition + " then\n")
                ignore_control_for_vhdl_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", 1,
                                                                       transition_specification["condition_action_reference"], "")
                file_line_number += 1
            else:
                transition_condition_list = transition_condition.split("\n")
                for index, line in enumerate(transition_condition_list):
                    if index==0:
                        vhdl.append("elsif " + line + "\n")
                    else:
                        vhdl.append("      " + line + "\n")
                    ignore_control_for_vhdl_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", index+1,
                                                                       transition_specification["condition_action_reference"], "")
                file_line_number += index+1
                vhdl.append("then\n")
                ignore_control_for_vhdl_indent.append(False)
                file_line_number += 1
        elif transition_specification["command"]=="action":
            for entry in transition_specification["actions"]:
                reference_to_custom_text = entry["moved_action_ref"]
                if "moved_condition_lines" in entry:
                    reference_to_custom_text_comment = entry["moved_condition_ref"]
                    comment_and_action_lines         = entry["moved_action"].split("\n")
                    number_of_comment_lines          = entry["moved_condition_lines"]
                    comment_list = comment_and_action_lines[0:number_of_comment_lines]
                    action_list  = comment_and_action_lines[number_of_comment_lines:]
                else:
                    comment_list = []
                    action_list  = entry["moved_action"].split("\n")
                if comment_list:
                    for index, single_comment in enumerate(comment_list):
                        vhdl.append(" "*4 + single_comment + "\n")
                        ignore_control_for_vhdl_indent.append(False)
                    link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", index+1,
                                                                           reference_to_custom_text_comment, "")
                    file_line_number += index+1
                for index, single_action in enumerate(action_list):
                    vhdl.append(" "*4 + single_action + "\n")
                    single_action_raw = re.sub("^ *", "", single_action)
                    if single_action_raw.startswith("if") or single_action_raw.startswith("end if"):
                        # Because this control-statement was inserted by the user it must be handled as action at the indent process later.
                        ignore_control_for_vhdl_indent.append(True)
                    else:
                        ignore_control_for_vhdl_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", len(action_list),
                                                                    reference_to_custom_text, "")
                file_line_number += len(action_list)
            if transition_specification["target"]!="":
                vhdl.append(" "*4 + "state <= " + transition_specification["target"] + ";\n" )
                ignore_control_for_vhdl_indent.append(False)
                file_line_number += 1
        elif transition_specification["command"]=="else"  :
            vhdl.append("else\n")
            ignore_control_for_vhdl_indent.append(False)
            file_line_number += 1
        elif transition_specification["command"]=="endif"  :
            vhdl.append("end if;\n")
            ignore_control_for_vhdl_indent.append(False)
            file_line_number += 1
    indent = 0
    vhdl_indented = ""
    for index, vhdl_line in enumerate(vhdl):
        if vhdl_line.startswith("if ") and not ignore_control_for_vhdl_indent[index]:
            indent += 1
        vhdl_indented += " "*4*indent + vhdl_line
        if vhdl_line.startswith("end if") and not ignore_control_for_vhdl_indent[index]:
            indent -= 1
    return vhdl_indented, file_line_number

def create_verilog_for_the_state_sequence(transition_specifications, file_name, file_line_number):
    verilog = []
    ignore_control_for_verilog_indent = []
    for index, transition_specification in enumerate(transition_specifications):
        if   transition_specification["command"]=="when"  :
            if index!=0:
                verilog.append("end\n") # For ending the last "when"
                ignore_control_for_verilog_indent.append(False)
                file_line_number += 1
            verilog.append(transition_specification["state_name"] + ": begin\n")
            ignore_control_for_verilog_indent.append(False)
            file_line_number += 1
            if "state_comments" in transition_specification:
                state_comments = re.sub(r"^", "    // ", transition_specification["state_comments"], flags=re.M)
                state_comments = state_comments[:-7] # remove blanks and the comment-string from the last empty line.
                verilog.append(state_comments)
                ignore_control_for_verilog_indent.append(False)
                number_of_comment_lines = state_comments.count("\n")
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", number_of_comment_lines,
                                                                       transition_specification["state_comments_canvas_id"], "")
                file_line_number += number_of_comment_lines
        elif transition_specification["command"]=="if"    :
            transition_condition = transition_specification["condition"]
            if transition_condition.endswith("\n"):
                transition_condition = transition_condition[:-1]
            if transition_condition.count("\n")==0:
                if "//" in transition_condition:
                    condition = re.sub(r"\s*//.*", ""  , transition_condition)
                    comment   = re.sub(r".*//"   , "//", transition_condition)
                    verilog.append("if (" + condition + ") begin " + comment + "\n")
                else:
                    verilog.append("if (" + transition_specification["condition"] + ") begin\n")
                ignore_control_for_verilog_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", 1,
                                                                       transition_specification["condition_action_reference"], "")
                file_line_number += 1
                #print("\ntransition_condition =", transition_condition)
            else:
                transition_condition_list = transition_condition.split("\n")
                for index, line in enumerate(transition_condition_list):
                    if index==0:
                        verilog.append("if (" + line + "\n")
                    else:
                        verilog.append("    " + line + "\n")
                    ignore_control_for_verilog_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", index+1,
                                                                       transition_specification["condition_action_reference"], "")
                file_line_number += index+1
                verilog.append("   ) begin\n")
                ignore_control_for_verilog_indent.append(False)
                file_line_number += 1
        elif transition_specification["command"]=="elsif"  :
            transition_condition = transition_specification["condition"]
            if transition_condition.endswith("\n"):
                transition_condition = transition_condition[:-1]
            if transition_condition.count("\n")==0:
                verilog.append("end else if (" + transition_specification["condition"] + ") begin\n")
                ignore_control_for_verilog_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", 1,
                                                                       transition_specification["condition_action_reference"], "")
                file_line_number += 1
            else:
                transition_condition_list = transition_condition.split("\n")
                for index, line in enumerate(transition_condition_list):
                    if index==0:
                        verilog.append("end else if (" + line + "\n")
                    else:
                        verilog.append("             " + line + "\n")
                    ignore_control_for_verilog_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", index+1,
                                                                       transition_specification["condition_action_reference"], "")
                file_line_number += index+1
                verilog.append("            ) begin\n")
                ignore_control_for_verilog_indent.append(False)
                file_line_number += 1
        elif transition_specification["command"]=="action":
            for entry in transition_specification["actions"]:
                reference_to_custom_text = entry["moved_action_ref"]
                if "moved_condition_lines" in entry:
                    reference_to_custom_text_comment = entry["moved_condition_ref"]
                    comment_and_action_lines         = entry["moved_action"].split("\n")
                    number_of_comment_lines          = entry["moved_condition_lines"]
                    comment_list = comment_and_action_lines[0:number_of_comment_lines]
                    action_list  = comment_and_action_lines[number_of_comment_lines:]
                else:
                    comment_list = []
                    action_list  = entry["moved_action"].split("\n")
                if comment_list:
                    for index, single_comment in enumerate(comment_list):
                        verilog.append(" "*4 + single_comment + "\n")
                        ignore_control_for_verilog_indent.append(False)
                    link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", index+1,
                                                                           reference_to_custom_text_comment, "")
                    file_line_number += index+1
                for index, single_action in enumerate(action_list):
                    verilog.append(" "*4 + single_action + "\n")
                    single_action_raw = re.sub("^ *", "", single_action)
                    if single_action_raw.startswith("if") or single_action_raw.startswith("end"):
                        # Because this control-statement was inserted by the user it must be handled as action at the indent process later.
                        ignore_control_for_verilog_indent.append(True)
                    else:
                        ignore_control_for_verilog_indent.append(False)
                link_dictionary.LinkDictionary.link_dict_reference.add(file_name, file_line_number, "custom_text_in_diagram_tab", len(action_list),
                                                                       reference_to_custom_text, "")
                file_line_number += len(action_list)
            if transition_specification["target"]!="":
                verilog.append(" "*4 + "state <= " + transition_specification["target"] + ";\n" )
                ignore_control_for_verilog_indent.append(False)
                file_line_number += 1
        elif transition_specification["command"]=="else"  :
            verilog.append("end else begin\n")
            ignore_control_for_verilog_indent.append(False)
            file_line_number += 1
        elif transition_specification["command"]=="endif"  :
            verilog.append("end\n")
            ignore_control_for_verilog_indent.append(False)
            file_line_number += 1
    verilog.append("end\n") # For ending the last "when"
    ignore_control_for_verilog_indent.append(False)
    file_line_number += 1
    indent = -1
    verilog_indented = ""
    for index, verilog_line in enumerate(verilog):
        if (verilog_line.startswith("if") or verilog_line.endswith(": begin\n")) and not ignore_control_for_verilog_indent[index]:
            indent += 1
        verilog_indented += " "*4*indent + verilog_line
        if (    verilog_line.startswith("end")          and
            not verilog_line.startswith("end else if ") and
            not verilog_line.startswith("end else begin")
            ) and not ignore_control_for_verilog_indent[index]:
            indent -= 1
    return verilog_indented, file_line_number

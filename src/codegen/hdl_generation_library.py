"""
This module contains methods used at HDL generation.
"""

import re
import tkinter as tk

import canvas_editing
from elements import condition_action, global_actions_clocked, global_actions_combinatorial, state_comment
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


def _get_target_state_name(all_reset_transition_tags):
    target_state_tag = ""
    for t in all_reset_transition_tags:
        if t.startswith("going_to_state"):
            target_state_tag = t[9:]
    target_state_name = project_manager.canvas.itemcget(target_state_tag + "_name", "text")
    return target_state_name


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
                "therefore the generated HDL will be corrupted.",
                "Please specify the reset condition by using the right",
                "mouse button at the transition from the reset-connector",
                "to the state, which shall be reached by active reset.",
            ],
        )
    reference_to_reset_condition_custom_text = ref.condition_id
    condition = reference_to_reset_condition_custom_text.get("1.0", tk.END + "-1 chars")  # without "return" at the end
    all_reset_transition_tags = project_manager.canvas.gettags(reset_transition_tag)
    target_state_name = _get_target_state_name(all_reset_transition_tags)
    action = "state <= " + target_state_name + ";\n"
    reference_to_reset_action_custom_text = ref.action_id
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


def _get_transition_target_condition_action(transition_tag) -> tuple[str, str, str, str]:
    tags = project_manager.canvas.gettags(transition_tag)
    transition_condition = ""
    transition_action = ""
    condition_action_reference = ""
    transition_target = ""
    for tag in tags:
        if tag.startswith("going_to_state"):
            transition_target_tag = tag[9:]
            transition_target = project_manager.canvas.itemcget(transition_target_tag + "_name", "text")
        elif tag.startswith("going_to_connector"):
            transition_target = tag[9:]
        elif tag.startswith("ca_connection"):  # Complete tag: ca_connection<n>_end
            condition_action_number = tag[13:-4]
            condition_action_tag = "condition_action" + condition_action_number
            condition_action_canvas_item_id = project_manager.canvas.find_withtag(condition_action_tag)[0]
            condition_action_reference = condition_action.ConditionAction.ref_dict[condition_action_canvas_item_id]
            if condition_action_reference is not None:
                transition_condition = _get_transition_condition(condition_action_reference)
                transition_action = _get_transition_action(condition_action_reference)
    return transition_target, transition_condition, transition_action, condition_action_reference


def _get_condition_action_reference_of_transition(transition_tag) -> None:
    tags = project_manager.canvas.gettags(transition_tag)
    for tag in tags:
        if tag.startswith("ca_connection"):  # Complete tag: ca_connection<n>_end
            condition_action_number = tag[13:-4]
            condition_action_tag = "condition_action" + condition_action_number
            condition_action_canvas_item_id = project_manager.canvas.find_withtag(condition_action_tag)[0]
            condition_action_reference = condition_action.ConditionAction.ref_dict[condition_action_canvas_item_id]
            return condition_action_reference
    return None


def extract_transition_specifications_from_the_graph(state_tag_list_sorted) -> list:
    """For each state in state_tag_list_sorted, all outgoing transitions are analyzed."""
    transition_specifications = []
    for state_tag in state_tag_list_sorted:
        canvas_id_of_comment_text_widget, state_comments = _get_state_comments(state_tag)
        condition_level = 0
        moved_actions = []
        trace = []  # Is temporarily used when a path from a state to a target state passes connectors.
        trace_array = []  # Stores all paths starting from this state.
        # Each entry of trace_array shall describe a path from this state to a target state (this state is also target).
        # The entries of trace_array are ordered regarding their priority in the HDL,
        # the first entry has the highest priority.
        # Each entry is a ordered list of dictionaries.
        # The order of these dictionaries is defined by the order in which the HDL lines must be generated.
        # Each dictionary contains all information to create one or several HDL lines.
        state_name = project_manager.canvas.itemcget(state_tag + "_name", "text")
        transition_specifications.append(
            {
                "state_name": state_name,
                "command": "when",  # indicates that this dictionary must create the HDL line "when state_name =>"
                "state_comments": state_comments,
                "state_comments_canvas_id": canvas_id_of_comment_text_widget,
            }
        )
        _extract_conditions_for_all_outgoing_transitions_of_the_state(
            state_name, state_tag, moved_actions, condition_level, trace, trace_array
        )
        # The separated paths of trace_array are merged together by adding "else" commands,
        # so if the first trace depends on an "if", then the inserted "else" path of the first trace
        # contains the second trace and so on:
        transition_specifications.extend(_merge_trace_array(trace_array))
    # The list "transition_specifications" now contains all information to generate the HDL.
    # But in this list all actions are moved "down" and duplicated in a way that only
    # the transition which at last reaches the target state contains all the actions.
    # This is needed, because when traversing connectors (and collecting actions) first
    # all conditions must be collected, and only if all conditions are true, the actions can be executed.
    # But the resulting HDL code may have unnecessary duplicated actions in several branches of if-constructs.
    # So it is checked here, if actions can be moved "up" again, so that they are only present once:
    _optimize_transition_specifications(transition_specifications)
    return transition_specifications


def _get_state_comments(state_tag):
    all_tags_of_state = project_manager.canvas.gettags(state_tag)
    if state_tag + "_comment_line_end" in all_tags_of_state:
        canvas_id_of_comment_window = project_manager.canvas.find_withtag(state_tag + "_comment")[0]
        reference_to_state_comment_window = state_comment.StateComment.ref_dict[canvas_id_of_comment_window]
        canvas_id_of_comment_text_widget = reference_to_state_comment_window.text_id
        state_comments = canvas_id_of_comment_text_widget.get("1.0", "end")
        state_comments = re.sub(r"^\s*[0-9]*\s*", "", state_comments)  # Remove order comment at comment start.
        if state_comments == "":
            canvas_id_of_comment_text_widget = None
    else:
        canvas_id_of_comment_text_widget = None
        state_comments = ""
    return canvas_id_of_comment_text_widget, state_comments


def _optimize_transition_specifications(transition_specifications) -> None:
    # This method calls itself again, until no more changes were added.
    # Add an unique if-identifier to each transition_specification of the transition_specifications.
    # At each if, the identifier is incremented, at each end-if it is decremented.
    # Also add to each end-if transition specification the number of branches of this ending if-construct:
    _expand_transition_specifications_by_if_depth(transition_specifications)
    # for transition_specification in transition_specifications:
    #     temp = {}
    #     for key in transition_specification:
    #         if key == "condition_action_reference" and transition_specification[key] is not None:
    #             pass  # temp[key] = transition_specification[key].get("1.0", "end-1c")
    #         else:
    #             temp[key] = transition_specification[key]
    #     print("transition_specification =", temp)
    # action_target_array is a dictionary with the state name as key.
    # It contains for each state name a dictionary which describes the actions to a specific target state:
    action_target_array, branch_counter_array = _create_action_and_branch_array_for_each_if_construct(
        transition_specifications
    )
    # print("action_target_array =", action_target_array)
    # print("branch_counter_array =", branch_counter_array)
    changes_were_implemented = False
    index_of_if_in_transition_specifications = 0
    for state_name, action_target_if_dictionary in action_target_array.items():
        for if_depth in action_target_if_dictionary:
            if (
                # if_depth==0 means this is an entry caused by a "when"-command:
                if_depth != 0
                # This is the number of different actions&targets which exist for the if_depth:
                and len(action_target_array[state_name][if_depth])
                # This is the number of branches which exist for the if_depth:
                == branch_counter_array[state_name][if_depth]
                != 1
            ):
                # There is more than 1 branch for the if_depth.
                moved_actions = []
                moved_target = []  # will get only 1 entry
                for action_target_dict in action_target_array[state_name][if_depth]:
                    for action in action_target_dict["actions"]:
                        if _action_is_present_in_each_branch(action, state_name, if_depth, action_target_array):
                            index_of_if_in_transition_specifications = _remove_action_from_branches(
                                transition_specifications, state_name, if_depth, action, moved_actions
                            )
                            changes_were_implemented = True
                    target = action_target_dict["target"]
                    if target != "" and _target_is_present_in_each_branch(
                        target, state_name, if_depth, action_target_array
                    ):
                        index_of_if_in_transition_specifications = _remove_target_from_branches(
                            transition_specifications, state_name, if_depth, target, moved_target
                        )
                        changes_were_implemented = True
                if moved_actions or moved_target:
                    target = "" if not moved_target else moved_target[0]
                    # Insert a new entry into the list of transition_specifications:
                    transition_specifications[
                        index_of_if_in_transition_specifications:index_of_if_in_transition_specifications
                    ] = [
                        {
                            "state_name": state_name,
                            "command": "action",
                            "condition": "",
                            "actions": moved_actions,
                            "target": target,
                            "if_depth": if_depth - 1,
                        }
                    ]
    if changes_were_implemented:
        _optimize_transition_specifications(transition_specifications)


def _expand_transition_specifications_by_if_depth(transition_specifications) -> None:
    """
    Adds a "if_depth" entry to each transition_specification,
    and adds a "branch_counter" entry to each "endif" transition_specification:
    At each "if" the "if_depth" is increased by 1, at each "endif" it is decreased by 1.
    At each "if" the branch_counter is initialized by 1, at each "elsif" or "else" it is increased by 1.
    At each "endif" the branch_counter is stored in the transition_specification.
    """
    if_depth = 0
    for transition_specification in transition_specifications:
        if transition_specification["command"] == "when":
            if_depth = 0
            stack_of_if_depth = [0]
            stack_of_branch_counters = [0]
            transition_specification["if_depth"] = 0
        elif transition_specification["command"] == "if":
            if_depth += 1
            transition_specification["if_depth"] = if_depth
            stack_of_if_depth.append(if_depth)
            stack_of_branch_counters.append(1)  #  Start a new branch counter for each "if".
        elif transition_specification["command"] == "elsif" or transition_specification["command"] == "else":
            transition_specification["if_depth"] = stack_of_if_depth[-1]
            stack_of_branch_counters[-1] += 1  # Increment this branch counter because end-if is not reached
        elif transition_specification["command"] == "endif":
            transition_specification["if_depth"] = stack_of_if_depth.pop()  # stack_of_if_depth[-1]
            transition_specification["branch_counter"] = stack_of_branch_counters.pop()  # stack_of_branch_counters[-1]
        else:  # "action"
            transition_specification["if_depth"] = stack_of_if_depth[-1]


def _create_action_and_branch_array_for_each_if_construct(transition_specifications) -> tuple[dict, dict]:
    # The return dictionary action_target_array[state_name][if_depth][0..n] is an
    # dictionary with the keys "actions" and "target".
    # if_depth identifies a complete if..elsif..else..endif-construct.
    # [0..n] identifies each branch in this construct.
    # The key "actions" of the dictionary stores a list of actions which are executed in this branch.
    # The key "target" of the dictionary stores the target state of this branch.
    # The return dictionary branch_counter_array contains for each state a dictionary
    # with transition_specification["if_depth"] as key,
    # where the value is the number of branches the "if" has.
    action_target_array_of_state = {}
    branch_counter_array_of_state = {}
    action_target_array = {}
    branch_counter_array = {}
    state_name = None
    next_actions_will_be_executed_for_sure = False
    for transition_specification in transition_specifications:
        if transition_specification["command"] == "else":
            next_actions_will_be_executed_for_sure = True
        if transition_specification["command"] == "when":
            if action_target_array_of_state and state_name is not None:  # The analysis of a state is ready.
                action_target_array[state_name] = action_target_array_of_state
                branch_counter_array[state_name] = branch_counter_array_of_state
                action_target_array_of_state = {}
                branch_counter_array_of_state = {}
            state_name = transition_specification["state_name"]  # start new analysis
        elif transition_specification["command"] == "action":
            if_depth = transition_specification["if_depth"]
            if if_depth not in action_target_array_of_state:
                action_target_array_of_state[if_depth] = []
            # Create a copy because later on the list transition_specification["actions"] is modified and
            # would modify if_array also:
            copy_of_actions = []
            for entry in transition_specification["actions"]:
                copy_of_actions.append(entry)
            # For each branch (possible paths available after the "if") add the actions executed in this branch:
            action_target_array_of_state[if_depth].append(
                {
                    "actions": copy_of_actions,
                    "target": transition_specification["target"],
                    "executed_for_sure": next_actions_will_be_executed_for_sure,
                }
            )
            next_actions_will_be_executed_for_sure = False
        elif transition_specification["command"] == "endif":
            branch_counter_array_of_state[transition_specification["if_depth"]] = transition_specification[
                "branch_counter"
            ]
            next_actions_will_be_executed_for_sure = False
    if (
        action_target_array_of_state and state_name is not None
    ):  # Needed for the last state, as no new "when" will come after the last state.
        action_target_array[state_name] = action_target_array_of_state
        branch_counter_array[state_name] = branch_counter_array_of_state
    return action_target_array, branch_counter_array


def _action_is_present_in_each_branch(action, state_name, if_depth, action_target_array) -> bool:
    # Returns only True, when the action is present in each branch and a default branch exists.
    default_branch_exists = False
    for action_target_dict_check in action_target_array[state_name][if_depth]:
        if action_target_dict_check["executed_for_sure"]:
            default_branch_exists = True
        if action not in action_target_dict_check["actions"]:
            return False
        # for single_action in action_target_dict_check["actions"]:
        #     if single_action["moved_action"] != action["moved_action"]:
        #         return False
    return default_branch_exists


def _remove_action_from_branches(transition_specifications, state_name, if_depth, action, moved_actions) -> int:
    index_of_if_in_transition_specifications = 0
    for index, transition_specification in enumerate(transition_specifications):
        if transition_specification["state_name"] == state_name and transition_specification["if_depth"] == if_depth:
            if transition_specification["command"] == "if":
                index_of_if_in_transition_specifications = index
            elif transition_specification["command"] == "action":
                # This creates problems:
                # transition_specification["actions"].remove(single_action)
                # The reason is, that when the entry "action" is removed from the list, also in
                # another transition_specification["actions"] a entry disappears, if it is identical to action.
                # The solution is to create a new list:
                transition_specification["actions"] = [x for x in transition_specification["actions"] if x != action]
                #  [x for x in transition_specification["actions"] if x["moved_action"] != action["moved_action"]]
                if action not in moved_actions:
                    moved_actions.append(action)
                # action_present = False
                # for moved_single_action in moved_actions:
                #     if moved_single_action["moved_action"] == action["moved_action"]:
                #         action_present = True
                # if not action_present:
                #     moved_actions.append(action)
    return index_of_if_in_transition_specifications


def _remove_target_from_branches(transition_specifications, state_name, if_depth, target, moved_target) -> int:
    index_of_if_in_transition_specifications = 0
    for index, transition_specification in enumerate(transition_specifications):
        if transition_specification["state_name"] == state_name and transition_specification["if_depth"] == if_depth:
            if transition_specification["command"] == "if":
                index_of_if_in_transition_specifications = index
            elif transition_specification["command"] == "action" and target == transition_specification["target"]:
                transition_specification["target"] = ""
                if target not in moved_target:
                    moved_target.append(target)
    return index_of_if_in_transition_specifications


def _target_is_present_in_each_branch(target, state_name, if_depth, action_target_array) -> bool:
    for action_target_dict_check in action_target_array[state_name][if_depth]:
        if target != action_target_dict_check["target"]:
            return False
    return True


def _check_for_wrong_priorities(trace_array) -> None:
    condition_array = []
    for trace in trace_array:
        # Each trace starts like this:
        # [{'state_name': 'filled', 'command': 'if'    , 'condition': "read_fifo_i='1'"           , ...
        #  {'state_name': 'filled', 'command': 'if'    , 'condition': 'read_address=write_address', ...
        #  {'state_name': 'filled', 'command': 'action', 'condition': ''                          , ...]
        # All the conditions of a trace together determine, if the action is executed.
        # If a next trace starts with the same conditions, then this next trace is obsolete,
        # as it will never be reached.
        # This is checked here:
        condition_sequence = []
        for trace_dict in trace:
            if trace_dict["command"] == "if":
                condition_sequence.append(trace_dict["condition"])
        condition_array.append(condition_sequence)
    for index, condition_sequence in enumerate(condition_array):
        if index < len(condition_array) - 1 and (
            condition_sequence == condition_array[index + 1][0 : len(condition_sequence)]
        ):  # Check if the next trace starts with the same conditions.
            condition_sequence_string = ""
            for single_condition in condition_sequence:
                condition_sequence_string += single_condition + ","
            if condition_sequence_string != "":
                condition_sequence_string = condition_sequence_string[:-1]
                raise GenerationError(
                    "Error in HDL-FSM-Editor",
                    [
                        f"A transition starting at state {trace_array[index][0]['state_name']}",
                        f"with the condition sequence {condition_sequence_string}",
                        "hides a transition with lower priority.",
                        "This is not allowed and will corrupt the HDL.",
                    ],
                )
            raise GenerationError(
                "Error in HDL-FSM-Editor",
                [
                    f"A transition starting at state {trace_array[index][0]['state_name']}",
                    "with no condition hides a transition with lower priority.",
                    "This is not allowed and will corrupt the HDL.",
                ],
            )


def _merge_trace_array(trace_array) -> list:
    _check_for_wrong_priorities(trace_array)
    traces_of_a_state_reversed = list(reversed(trace_array))  # Start with the trace, which has lowest priority.
    for trace_index, trace in enumerate(traces_of_a_state_reversed):
        if (
            trace_index == len(traces_of_a_state_reversed) - 1
        ):  # The last trace is the result of this for-loop and will only be checked for a condition:
            if (
                trace != [] and trace[0]["command"] != "if" and trace_index != 0
            ):  # Check is only done, when more than 1 trace exists.
                raise GenerationError(
                    "Warning",
                    [
                        f"There is a transition starting at state {trace[0]['state_name']} which has no condition but",
                        " does not have the lowest priority, therefore the generated HDL may be corrupted.",
                    ],
                )
        else:
            # An empty trace may happen, when the transition with lowest priority has
            # no condition and action (and has a connector?!).
            if trace:
                first_command_of_trace = trace[0]["command"] + trace[0]["condition"]
                first_command_of_next_trace = (
                    traces_of_a_state_reversed[trace_index + 1][0]["command"]
                    + traces_of_a_state_reversed[trace_index + 1][0]["condition"]
                )
                if (
                    trace_index != 0  # This trace is not the trace with the lowest priority
                    and trace[0]["command"] != "if"
                ):  # The first command of this trace has no condition.
                    # All traces except the trace with the lowest priority must start with an "if":
                    raise GenerationError(
                        "Warning",
                        [
                            f"There is a transition starting at state {trace[0]['state_name']} which has no condition",
                            " but does not have the lowest priority, therefore the generated HDL may be corrupted.",
                        ],
                    )
                if trace[0]["command"] == "action":
                    # insert before the endif, which's existence was tested here.
                    traces_of_a_state_reversed[trace_index + 1][-1:-1] = [
                        {
                            "state_name": trace[0]["state_name"],
                            "command": "else",
                            "condition": "",
                            "condition_action_reference": None,
                        }
                    ]
                    traces_of_a_state_reversed[trace_index + 1][-1:-1] = (
                        trace  # insert before the endif, which's existence was tested here.
                    )
                elif first_command_of_trace != first_command_of_next_trace:
                    trace[0]["command"] = "elsif"
                    traces_of_a_state_reversed[trace_index + 1] = traces_of_a_state_reversed[trace_index + 1][
                        :-1
                    ]  # remove endif
                    traces_of_a_state_reversed[trace_index + 1] += trace
                else:  # Both traces start with the same command.
                    search_index = 1  # Look into the next command of the two traces.
                    target_at_error = ""
                    while (trace[search_index]["command"] + trace[search_index]["condition"]) == (
                        traces_of_a_state_reversed[trace_index + 1][search_index]["command"]
                        + traces_of_a_state_reversed[trace_index + 1][search_index]["condition"]
                    ):
                        if trace[search_index]["target"] != "":
                            target_at_error = trace[search_index]["target"]
                        if search_index in (
                            len(trace) - 1,
                            len(traces_of_a_state_reversed[trace_index + 1]) - 1,
                        ):
                            raise GenerationError(
                                "Error",
                                [
                                    f"There is a transition starting at state {trace[0]['state_name']} "
                                    f"to state {target_at_error} which will never fire,",
                                    "therefore the generated HDL may be corrupted.",
                                ],
                            )
                        search_index += 1
                    # search_index selects a different command in trace[]:
                    if trace[search_index]["command"] == "if":
                        trace[search_index]["command"] = "elsif"
                        # The "endif"s of the identical commands and the new "elsif" are all copied:
                        traces_of_a_state_reversed[trace_index + 1][-(search_index + 1) : -(search_index + 1)] = trace[
                            search_index:
                        ]
                        # Remove superfluous (search_index+1)*"endif", which were copied with trace:
                        traces_of_a_state_reversed[trace_index + 1] = traces_of_a_state_reversed[trace_index + 1][
                            : -(search_index + 1)
                        ]
                    else:  # The command is an "action" without any condition, so it must be converted into an "else".
                        traces_of_a_state_reversed[trace_index + 1][-(search_index + 1) : -(search_index + 1)] = [
                            {
                                "state_name": trace[search_index]["state_name"],
                                "command": "else",
                                "condition": "",
                                "condition_action_reference": None,
                            }
                        ]
                        traces_of_a_state_reversed[trace_index + 1][-(search_index + 1) : -(search_index + 1)] = trace[
                            search_index : search_index + 1
                        ]  # copy action to new "else" before "endif"
                        traces_of_a_state_reversed[trace_index + 1][-(search_index):-(search_index)] = trace[
                            search_index + 1 :
                        ]  # copy rest of trace after the endif
                        traces_of_a_state_reversed[trace_index + 1] = traces_of_a_state_reversed[trace_index + 1][
                            :-search_index
                        ]  # remove superfluous "endif"s
    transition_specifications = []
    if traces_of_a_state_reversed:
        for entry in traces_of_a_state_reversed[-1]:
            transition_specifications.append(entry)
    return transition_specifications


def _get_a_list_of_all_state_tags():
    state_tag_list = []
    reg_ex_for_state_tag = re.compile("^state[0-9]+$")
    all_canvas_items = project_manager.canvas.find_all()
    for item in all_canvas_items:
        all_tags = project_manager.canvas.gettags(item)
        for tag in all_tags:
            if reg_ex_for_state_tag.match(tag):
                state_tag_list.append(tag)
    return sorted(state_tag_list)


def _sort_list_of_all_state_tags(list_of_all_state_tags):
    state_tag_dict_with_prio = {}
    state_tag_list = []
    sorted_list_of_all_state_tags = []
    for state_tag in list_of_all_state_tags:
        list_of_canvas_ids = project_manager.canvas.find_withtag(state_tag + "_comment")
        if list_of_canvas_ids:
            canvas_id_of_comment_window = list_of_canvas_ids[0]
            reference_to_state_comment_window = state_comment.StateComment.ref_dict[canvas_id_of_comment_window]
            state_comments = reference_to_state_comment_window.text_id.get("1.0", "end")
            state_comments_list = state_comments.split("\n")
            if state_comments_list:
                first_line_of_state_comments = state_comments_list[0].strip()
                first_line_is_a_number = bool(all(c in "0123456789" for c in first_line_of_state_comments))
                if first_line_is_a_number:
                    state_tag_dict_with_prio[int(first_line_of_state_comments)] = state_tag
                else:
                    state_tag_list.append(state_tag)
    for _, tag in sorted(state_tag_dict_with_prio.items()):
        sorted_list_of_all_state_tags.append(tag)
    sorted_list_of_all_state_tags.extend(state_tag_list)
    return sorted_list_of_all_state_tags


def _extract_conditions_for_all_outgoing_transitions_of_the_state(
    state_name,
    start_tag,
    moved_actions,
    condition_level,
    trace,
    trace_array,  # initialized by trace_array = []
) -> None:
    outgoing_transition_tags = _get_all_outgoing_transitions_in_priority_order(start_tag)
    if not outgoing_transition_tags and start_tag.startswith("connector"):
        if trace:
            raise GenerationError(
                "Warning",
                [
                    f"There is a connector reached from state {trace[0]['state_name']} which",
                    " has no outgoing transition, therefore the generated HDL may be corrupted.",
                ],
            )
        raise GenerationError(
            "Warning",
            [
                "There is a connector which has no outgoing transition,",
                "therefore the generated HDL may be corrupted.",
            ],
        )
    for _, transition_tag in enumerate(outgoing_transition_tags):
        # Collect information about the transition:
        transition_target, transition_condition, transition_action, condition_action_reference = (
            _get_transition_target_condition_action(transition_tag)
        )
        transition_condition_is_a_comment = _check_if_condition_is_a_comment(transition_condition)
        # Handle the transition actions:
        if transition_action != "" or transition_condition_is_a_comment:
            # Create a new list which contains first all moved actions and then the action of this transition:
            if transition_action != "":
                if transition_condition_is_a_comment:
                    # Put the comment in front of the action:
                    if not transition_condition.endswith("\n"):
                        transition_condition = transition_condition + "\n"
                    transition_action = transition_condition + transition_action
                moved_actions_dict = {
                    "moved_action": transition_action,
                    "moved_action_ref": condition_action_reference.action_id,
                }
                if transition_condition_is_a_comment:
                    moved_actions_dict["moved_condition_ref"] = condition_action_reference.condition_id
                    moved_actions_dict["moved_condition_lines"] = transition_condition.count("\n")
            else:  # transition condition is a comment and transition action is empty.
                moved_actions_dict = {
                    "moved_action": transition_condition,
                    "moved_action_ref": condition_action_reference.condition_id,
                }
            transition_action_new = []
            for entry in moved_actions:
                transition_action_new.append(entry)
            transition_action_new.append(moved_actions_dict)
            # print("transition_action_new =", transition_action_new)
        else:
            # Copy the old list:
            transition_action_new = moved_actions
        # Handle the transition condition:
        trace_new = []
        for entry in trace:
            trace_new.append(entry)
        if transition_condition != "" and not transition_condition_is_a_comment:
            trace_new.append(
                {
                    "state_name": state_name,  # The state where the transition starts.
                    "command": "if",
                    "condition": transition_condition,
                    "target": transition_target,
                    "condition_level": condition_level,
                    "condition_action_reference": condition_action_reference.condition_id,
                }
            )
            condition_level_new = condition_level + 1
        else:
            condition_level_new = condition_level
        if transition_target.startswith("connector"):
            _extract_conditions_for_all_outgoing_transitions_of_the_state(
                state_name,
                transition_target,  # new start point
                transition_action_new,
                condition_level_new,
                trace_new,
                trace_array,  # initialized by transition_specifications = []
            )
        else:  # Target is a state.
            transition_target_tmp = transition_target if transition_target != state_name else ""
            # Create at jumps to itself only an entry, if actions are available.
            if transition_target != state_name or transition_action_new != []:
                trace_new.append(
                    {
                        "state_name": state_name,
                        "command": "action",
                        "condition": "",
                        "actions": transition_action_new,
                        "target": transition_target_tmp,
                        "condition_level": condition_level,
                        "condition_action_reference": None,
                    }
                )
            # Close all opened conditions by "endif" (condition-level should be actually decremented?!):
            for _ in range(condition_level_new):
                trace_new.append(
                    {
                        "state_name": state_name,
                        "command": "endif",
                        "condition": "",
                        "actions": "",
                        "target": "",
                        "condition_level": condition_level,
                        "condition_action_reference": None,
                    }
                )
            trace_array.append(trace_new)


def _check_if_condition_is_a_comment(transition_condition) -> bool:
    if transition_condition == "" or transition_condition.isspace():
        return False
    transition_condition_without_comments = remove_comments_and_returns(transition_condition)
    return bool(transition_condition_without_comments == "" or transition_condition_without_comments.isspace())


def _get_all_outgoing_transitions_in_priority_order(state_tag) -> list:
    transition_tags_and_priority = _create_outgoing_transition_list_with_priority_information(state_tag)
    transition_tags_and_priority_sorted = sorted(transition_tags_and_priority, key=lambda entry: entry[1])
    _check_for_equal_priorities(transition_tags_and_priority_sorted, state_tag)
    transition_tags_in_priority_order = _remove_priority_information(transition_tags_and_priority_sorted)
    return transition_tags_in_priority_order


def _create_outgoing_transition_list_with_priority_information(state_tag) -> list:
    all_tags_of_the_state = project_manager.canvas.gettags(state_tag)
    transition_tag_and_priority = []
    for tag in all_tags_of_the_state:
        if tag.endswith("_start"):
            transition_tag = tag[:-6]
            transition_priority_text_tag = transition_tag + "priority"
            transition_priority_string = project_manager.canvas.itemcget(transition_priority_text_tag, "text")
            transition_tag_and_priority.append([transition_tag, transition_priority_string])
    return transition_tag_and_priority


def _remove_priority_information(transition_tag_and_priority_sorted) -> list:
    transition_tags_in_priority_order = []
    for transition_tag_and_priority in transition_tag_and_priority_sorted:
        transition_tags_in_priority_order.append(transition_tag_and_priority[0])
    return transition_tags_in_priority_order


def _check_for_equal_priorities(transition_tags_and_priority_sorted, state_tag) -> None:
    for n in range(len(transition_tags_and_priority_sorted) - 1):
        if transition_tags_and_priority_sorted[n][1] == transition_tags_and_priority_sorted[n + 1][1]:
            object_coords = project_manager.canvas.coords(state_tag)
            canvas_editing.view_rectangle(
                [
                    object_coords[0] - 2 * (object_coords[2] - object_coords[0]),
                    object_coords[1] - 2 * (object_coords[3] - object_coords[1]),
                    object_coords[2] + 2 * (object_coords[2] - object_coords[0]),
                    object_coords[3] + 2 * (object_coords[3] - object_coords[1]),
                ],
                check_fit=False,
            )
            state_name = project_manager.canvas.itemcget(state_tag + "_name", "text")
            if state_name == "":
                state_name = "a connector"
            raise GenerationError(
                "Warning",
                [
                    f"Two outgoing transition of {state_name} have the same priority "
                    f"with value {transition_tags_and_priority_sorted[n + 1][1]}."
                ],
            )


def _get_transition_condition(condition_action_reference):
    return condition_action_reference.condition_id.get("1.0", tk.END + "-1 chars")  # without "return" at the end


def _get_transition_action(condition_action_reference):
    return condition_action_reference.action_id.get("1.0", tk.END + "-1 chars")  # without "return" at the end


def create_global_actions_before() -> tuple[str, str] | tuple:
    """Return (widget_ref, text) for clocked global 'before' block, or ('', '') if none."""
    canvas_item_ids = project_manager.canvas.find_withtag("global_actions1")
    if canvas_item_ids != ():
        ref = global_actions_clocked.GlobalActionsClocked.ref_dict[canvas_item_ids[0]]
        return ref.text_before_id, ref.text_before_id.get("1.0", tk.END)
    return "", ""


def create_global_actions_after() -> tuple[str, str] | tuple:
    """Return (widget_ref, text) for clocked global 'after' block, or ('', '') if none."""
    canvas_item_ids = project_manager.canvas.find_withtag("global_actions1")
    if canvas_item_ids != ():
        ref = global_actions_clocked.GlobalActionsClocked.ref_dict[canvas_item_ids[0]]
        return ref.text_after_id, ref.text_after_id.get("1.0", tk.END)
    return "", ""


def create_concurrent_actions() -> tuple[str, str] | tuple:
    """Return (widget_ref, text) for combinatorial global actions, or ('', '') if none."""
    canvas_item_ids = project_manager.canvas.find_withtag("global_actions_combinatorial1")
    if canvas_item_ids != ():
        ref = global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict[canvas_item_ids[0]]
        return ref.text_id, ref.text_id.get("1.0", tk.END)
    return "", ""


def remove_comments_and_returns(hdl_text) -> str:
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
        text += " " + line_without_comment
    text += " "  # Add " " at the end, so that keywords at the end are also surrounded by blanks.
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
        r"(^|\s+)type\s+\w+\s+is\s+.*;", "", hdl_text
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

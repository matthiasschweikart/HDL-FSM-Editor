"""
This class checks the tags of all graphical elements if they fit together.
"""
import re
import main_window

class TagPlausibility():
    def __init__(self):
        state_dict_list              = []
        state_action_dict_list       = []
        state_action_line_dict_list  = []
        state_comment_dict_list      = []
        state_comment_line_dict_list = []
        transition_dict_list         = []
        connector_dict_list          = []
        ca_anchor_line_dict_list     = []
        ca_window_dict_list          = []
        shown_state_name_dict        = {}
        transition_priority_dict     = {}
        reset_dict                   = {}
        self.__fill_dictionaries(state_dict_list, transition_dict_list, connector_dict_list, shown_state_name_dict, transition_priority_dict,
                                 reset_dict, ca_anchor_line_dict_list, ca_window_dict_list, state_action_dict_list, state_action_line_dict_list,
                                 state_comment_dict_list, state_comment_line_dict_list)
        # print("state_dict_list ="             , state_dict_list)
        # print("state_action_dict_list ="      , state_action_dict_list)
        # print("state_action_line_dict_list =" , state_action_line_dict_list)
        # print("transition_dict_list ="        , transition_dict_list)
        # print("connector_dict_list ="         , connector_dict_list)
        # print("ca_anchor_line_dict_list ="    , ca_anchor_line_dict_list)
        # print("ca_window_dict_list ="         , ca_window_dict_list)
        # print("shown_state_name_dict ="       , shown_state_name_dict)
        # print("transition_priority_dict ="    , transition_priority_dict)
        # print("reset_dict ="                  , reset_dict)
        self.tag_status_is_okay = True
        self.__check_state_dicts             (state_dict_list, shown_state_name_dict, state_action_dict_list, state_comment_dict_list)
        self.__check_state_action_dicts      (state_action_dict_list)
        self.__check_state_action_line_dicts (state_action_line_dict_list)
        self.__check_state_comment_dicts     (state_comment_dict_list)
        self.__check_state_comment_line_dicts(state_comment_line_dict_list)
        self.__check_transition_dicts        (transition_dict_list, transition_priority_dict)
        self.__check_connector_dicts         (connector_dict_list)
        self.__check_ca_window_dicts         (ca_window_dict_list)
        self.__check_ca_anchor_line_dicts    (ca_anchor_line_dict_list)
        if self.tag_status_is_okay:
            self.__check_transitions(transition_dict_list, state_dict_list, connector_dict_list, reset_dict, shown_state_name_dict, ca_anchor_line_dict_list)
            self.__check_states_and_connectors(state_dict_list, transition_dict_list, shown_state_name_dict, connector_dict_list)
            self.__check_ca_windows(ca_window_dict_list, ca_anchor_line_dict_list, transition_dict_list)
            self.__check_state_action_lines(state_action_line_dict_list, state_action_dict_list, state_dict_list)

    def get_tag_status_is_okay(self):
        return self.tag_status_is_okay

    def __fill_dictionaries(self, state_dict_list, transition_dict_list, connector_dict_list, shown_state_name_dict, transition_priority_dict,
                            reset_dict, ca_anchor_line_dict_list, ca_window_dict_list, state_action_dict_list, state_action_line_dict_list,
                            state_comment_dict_list, state_comment_line_dict_list):
        canvas_items = main_window.canvas.find_all()
        for canvas_item in canvas_items:
            if main_window.canvas.type(canvas_item)=='oval': # "state"-circle
                state_dict_list.append(self.__create_state_dict(canvas_item))
            elif main_window.canvas.type(canvas_item)=='polygon': # "reset-entry"-symbol
                self.__fill_reset_dict(canvas_item, reset_dict)
            elif main_window.canvas.type(canvas_item)=='rectangle': # "priority"-rectangle or "connector"-rectangle
                rectangle_tags = main_window.canvas.gettags(canvas_item)
                rectangle_was_identified = False
                for rectangle_tag in rectangle_tags:
                    if rectangle_tag.startswith("transition") and rectangle_tag.endswith("rectangle"):
                        rectangle_was_identified = True
                        break # A "priority"-rectangle was found
                    if rectangle_tag.startswith("connector"):
                        rectangle_was_identified = True
                        connector_dict_list.append(self.__create_connector_dict(canvas_item))
                        break # A "connector"-rectangle was found
                if not rectangle_was_identified:
                    print("Fatal in TagPlausibility-Checks: a rectangle could not be identified, because it has these unknown tags:", rectangle_tags)
            elif main_window.canvas.type(canvas_item)=='line':
                line_was_identified = False
                line_tags = main_window.canvas.gettags(canvas_item)
                for line_tag in line_tags:
                    if line_tag.startswith("transition"):
                        line_was_identified = True
                        transition_dict_list.append(self.__create_transition_dict(canvas_item))
                        break
                    if line_tag.startswith("ca_connection"):
                        line_was_identified = True
                        ca_anchor_line_dict_list.append(self.__create_ca_anchor_line_dict(canvas_item))
                        break
                    if line_tag.startswith("connection"):
                        line_was_identified = True
                        state_action_line_dict_list.append(self.__create_state_action_line_dict(canvas_item))
                        break
                    if line_tag.endswith("_comment_line"):
                        line_was_identified = True
                        state_comment_line_dict_list.append(self.__create_state_comment_line_dict(canvas_item))
                        break
                if not line_was_identified:
                    print("Fatal in TagPlausibility-Checks: a line could not be identified, because it has these unknown tags:", line_tags)
            elif main_window.canvas.type(canvas_item)=='text':
                text_was_identified = False
                text_tags = main_window.canvas.gettags(canvas_item)
                for text_tag in text_tags:
                    if text_tag.startswith("state"):
                        text_was_identified = True
                        self.__create_entry_in_shown_state_name_dict(canvas_item, shown_state_name_dict)
                        break
                    if text_tag.startswith("transition"):
                        text_was_identified = True
                        self.__create_entry_in_transition_priority_dict(canvas_item, transition_priority_dict)
                        break
                    if text_tag.startswith("reset_text"):
                        text_was_identified = True
                        break
                if not text_was_identified:
                    print("Fatal in TagPlausibility-Checks: a text could not be identified, because it has these unknown tags:", text_tags)
            elif main_window.canvas.type(canvas_item)=='window':
                window_was_identified = False
                window_tags = main_window.canvas.gettags(canvas_item)
                for window_tag in window_tags:
                    if window_tag=="global_actions1":
                        window_was_identified = True
                    elif window_tag=="global_actions_combinatorial1":
                        window_was_identified = True
                    elif window_tag=="state_actions_default":
                        window_was_identified = True
                    elif window_tag.startswith("state_action"):
                        window_was_identified = True
                        state_action_dict_list.append(self.__create_state_action_dict(canvas_item))
                    elif window_tag.startswith("state") and window_tag.endswith("_comment"):
                        window_was_identified = True
                        state_comment_dict_list.append(self.__create_state_comment_dict(canvas_item))
                    elif window_tag.startswith("condition_action"):
                        window_was_identified = True
                        ca_window_dict_list.append(self.__create_ca_window_dict(canvas_item))
                if not window_was_identified:
                    print("Fatal in TagPlausibility-Checks: a Canvas window was found, which could not be identified by its tags:", window_tags)
            else:
                print("Fatal in TagPlausibility-Checks: a Canvas item was found, which has an not expected type:", main_window.canvas.type(canvas_item))
    def __fill_reset_dict(self, canvas_item, reset_dict):
        reset_outgoing_transitions_list = []
        reset_incoming_transitions_list = []
        reset_tags = main_window.canvas.gettags(canvas_item)
        for reset_tag in reset_tags:
            if   reset_tag=="current":
                pass
            elif reset_tag.startswith("reset_entry"):
                reset_dict["reset_identifier"] = "reset_entry"
            elif reset_tag.endswith("_start"):
                reset_outgoing_transitions_list.append(re.sub("_start", "", reset_tag))
            elif reset_tag.endswith("_end"):
                reset_incoming_transitions_list.append(re.sub("_end"  , "", reset_tag))
            else:
                print("Fatal in TagPlausibility-Checks: an unknown reset tag was found:", reset_tag)
        reset_dict["reset_outgoing_transitions"] = reset_outgoing_transitions_list
        reset_dict["reset_incoming_transitions"] = reset_incoming_transitions_list

    def __create_state_dict(self, canvas_item):
        state_dict = {}
        state_outgoing_transitions_list = []
        state_incoming_transitions_list = []
        state_action_line_list          = []
        state_comment_line_list         = []
        state_tags = main_window.canvas.gettags(canvas_item)
        #print("state_tags are:", state_tags)
        #state_tags are: ('state1', 'transition0_end', 'transition1_start', 'connection1_end', 'state1_comment_line_end')
        for state_tag in state_tags:
            if   state_tag=="current":
                pass
            elif state_tag.startswith("state") and not state_tag.endswith("_comment_line_end"):
                state_dict["state_identifier"] = state_tag
            elif state_tag.startswith("state") and state_tag.endswith("_comment_line_end"):
                state_comment_line_list.append(re.sub("_end"  , "", state_tag))
            elif state_tag.startswith("transition") and state_tag.endswith("_start"):
                state_outgoing_transitions_list.append(re.sub("_start", "", state_tag))
            elif state_tag.startswith("transition") and state_tag.endswith("_end"):
                state_incoming_transitions_list.append(re.sub("_end"  , "", state_tag))
            elif state_tag.startswith("connection") and state_tag.endswith("_end"):
                state_action_line_list.append(re.sub("_end"  , "", state_tag))
            else:
                print("Fatal in TagPlausibility-Checks: an unknown state tag was found:", state_tag, "in", state_tags)
        state_dict["state_outgoing_transitions"] = state_outgoing_transitions_list
        state_dict["state_incoming_transitions"] = state_incoming_transitions_list
        state_dict["state_action_line"]          = state_action_line_list
        state_dict["state_comment_line"]         = state_comment_line_list
        return state_dict
    def __check_state_dicts(self,state_dict_list, shown_state_name_dict, state_action_dict_list, state_comment_dict_list):
        # state_dict = {"state_identifier"           : "state"<integer>,
        #               "state_outgoing_transitions" : ["transition"<integer>,"transition"<integer>,...],
        #               "state_incoming_transitions" : ["transition"<integer>,"transition"<integer>,...],
        #               "state_action_line"          : ["connection"<integer>,          ], <-- Optional entry with an array of length 1, if everything is okay
        #               "state_comment_line"         : ["state"<integer>"_comment_line",]} <-- Optional entry with an array of length 1, if everything is okay
        for state_dict in state_dict_list:
            if "state_identifier" not in state_dict:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a state was found which does not have a tag which starts with the string "state".')
            elif state_dict["state_identifier"] not in shown_state_name_dict:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a state with identifier ' + state_dict["state_identifier"] +
                      ' was found which does not have a text-box which shows the state-name.')
            # The keys "state_outgoing_transitions" and "state_incoming_transitions" exist always.
            # Both lists are allowed to be empty:
            for transition_identifier in state_dict["state_outgoing_transitions"]:
                if not transition_identifier.startswith("transition"):
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: an outgoing transition-identifier from a state was found which does not start with the string "transition":',
                          transition_identifier)
            for transition_identifier in state_dict["state_incoming_transitions"]:
                if not transition_identifier.startswith("transition"):
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: an incoming transition-identifier to a state was found which does not start with the string "transition":',
                          transition_identifier)
            if "state_action_line" in state_dict:
                if len(state_dict["state_action_line"])==0:
                    pass
                elif len(state_dict["state_action_line"])>1:
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: a state was found which has more than 1 connected state-action-line.')
                else:
                    number_of_good_hits = 0
                    for state_action_dict in state_action_dict_list:
                        if state_dict["state_action_line"][0]==state_action_dict["state_action_line_identifier"]:
                            number_of_good_hits += 1
                    if number_of_good_hits==0:
                        self.tag_status_is_okay = False
                        print('Fatal in TagPlausibility-Checks: a state-action-line ' + state_dict["state_action_line"][0] + ' was found, but no attached state action was found.')
                    elif number_of_good_hits>1:
                        self.tag_status_is_okay = False
                        print('Fatal in TagPlausibility-Checks: a state-action-line was found, but more than 1 attached state action was found.')
            if "state_comment_line" in state_dict:
                if len(state_dict["state_comment_line"])==0:
                    pass
                elif len(state_dict["state_comment_line"])>1:
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: a state was found which has more than 1 connected state-comment-line.')
                else:
                    number_of_good_hits = 0
                    for state_comment_dict in state_comment_dict_list:
                        if state_dict["state_comment_line"][0]==state_comment_dict["state_comment_line_identifier"]:
                            number_of_good_hits += 1
                    if number_of_good_hits==0:
                        self.tag_status_is_okay = False
                        print('Fatal in TagPlausibility-Checks: a state-comment-line was found, but no attached state comment was found.')
                    elif number_of_good_hits>1:
                        self.tag_status_is_okay = False
                        print('Fatal in TagPlausibility-Checks: a state-comment-line was found, but more than 1 attached state comment was found.')

    def __create_state_action_dict(self, canvas_item):
        # state_action_dict = ("state_action_identifier"      : "state_action"<integer>,
        #                      "state_action_line_identifier" : "connection"<integer>)
        # state_action tags: ('state_action1', 'connection1_start')
        state_action_dict = {}
        state_action_tags = main_window.canvas.gettags(canvas_item)
        for state_action_tag in state_action_tags:
            if   state_action_tag=="current":
                pass
            elif state_action_tag.startswith("state_action"):
                state_action_dict["state_action_identifier"] = state_action_tag # state_action_tag = "state_action"<integer>
            elif state_action_tag.startswith("connection"):
                state_action_dict["state_action_line_identifier"] = re.sub("_start", "", state_action_tag) # state_action_tag = "connection"<integer>"_start"
            else:
                print("Fatal in TagPlausibility-Checks: an unknown state-action tag was found:", state_action_tag, "in", state_action_tags)
        return state_action_dict
    def __check_state_action_dicts(self, state_action_dict_list):
        for state_action_dict in state_action_dict_list:
            if "state_action_identifier" not in state_action_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-action was found which does not have a state-action-identifier-tag")
            if "state_action_line_identifier" not in state_action_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-action was found which does not have a state-action-line-identifier-tag")

    def __create_state_action_line_dict(self, canvas_item):
        # state_action_line_dict = ("state_action_line_identifier" : "connection"<integer>,
        #                           "state_identifier"             : "state"<integer>)
        # state_action_line tags: ('connection1', 'connected_to_state1')
        state_action_line_dict = {}
        state_action_line_tags = main_window.canvas.gettags(canvas_item)
        for state_action_line_tag in state_action_line_tags:
            if   state_action_line_tag=="current":
                pass
            elif state_action_line_tag.startswith("connection"):
                state_action_line_dict["state_action_line_identifier"] = state_action_line_tag # state_action_line_tag = "connection"<integer>
            elif state_action_line_tag.startswith("connected_to_"):
                state_action_line_dict["state_identifier"] = re.sub("connected_to_", "", state_action_line_tag) # state_action_tag = "connected_to_state"<integer>"
            else:
                print("Fatal in TagPlausibility-Checks: an unknown tag at a state-action-line was found:", state_action_line_tag, "in", state_action_line_tags)
        return state_action_line_dict
    def __check_state_action_line_dicts(self, state_action_line_dict_list):
        for state_action_line_dict in state_action_line_dict_list:
            if "state_action_line_identifier" not in state_action_line_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-action-line was found which does not have a state-action-line-identifier-tag")
            if "state_identifier" not in state_action_line_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-action-line was found which does not have a state-identifier-tag")

    def __create_state_comment_dict(self, canvas_item):
        # state_comment_dict = ("state_comment_identifier"      : "state"<integer>"_comment",
        #                       "state_comment_line_identifier" : "state"<integer>"_comment_line")
        # state_comment tags: ('state1_comment', 'state1_comment_line_start')
        state_comment_dict = {}
        state_comment_tags = main_window.canvas.gettags(canvas_item) # canvas_item is a canvas-window
        for state_comment_tag in state_comment_tags:
            if   state_comment_tag=="current":
                pass
            elif state_comment_tag.startswith("state") and state_comment_tag.endswith("_comment"):
                state_comment_dict["state_comment_identifier"] = state_comment_tag
            elif state_comment_tag.startswith("state") and state_comment_tag.endswith("_comment_line_start"):
                state_comment_dict["state_comment_line_identifier"] = re.sub("_start", "", state_comment_tag)
            else:
                print("Fatal in TagPlausibility-Checks: an unknown state-comment tag was found:", state_comment_tag, "in", state_comment_tags)
        return state_comment_dict
    def __check_state_comment_dicts(self, state_comment_dict_list):
        for state_comment_dict in state_comment_dict_list:
            if "state_comment_identifier" not in state_comment_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-comment was found which does not have a state-comment-identifier-tag")
            if "state_comment_line_identifier" not in state_comment_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-comment was found which does not have a state-comment-line-identifier-tag")

    def __create_state_comment_line_dict(self, canvas_item):
        # state_comment_line_dict = ("state_comment_line_identifier" : "state"<integer>"_comment_line")
        # state_comment_line tags: ("state1_comment_line", )
        state_comment_line_dict = {}
        state_comment_line_tags = main_window.canvas.gettags(canvas_item)
        for state_comment_line_tag in state_comment_line_tags:
            if   state_comment_line_tag=="current":
                pass
            elif state_comment_line_tag.endswith("_comment_line"):
                state_comment_line_dict["state_comment_line_identifier"] = state_comment_line_tag # state_comment_line_tag = "state"<integer>"_comment_line"
            else:
                print("Fatal in TagPlausibility-Checks: an unknown tag at a state-comment-line was found:", state_comment_line_tag, "in", state_comment_line_tags)
        return state_comment_line_dict
    def __check_state_comment_line_dicts(self, state_comment_line_dict_list):
        for state_comment_line_dict in state_comment_line_dict_list:
            if "state_comment_line_identifier" not in state_comment_line_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-comment-line was found which does not have a state-comment-line-identifier-tag")

    def __create_transition_dict(self, canvas_item):
        # transition_dict = {"transition_identifier"   : "transition"<integer>,
        #                    "transition_start_state"  : ["state"|"connector"]<integer>,
        #                    "transition_end_state"    : ["state"|"connector"]<integer>,
        #                    "ca_connection_identifier": "ca_connection"<integer>} <-- This entry is optional
        transition_dict = {}
        line_tags = main_window.canvas.gettags(canvas_item)
        for transition_tag in line_tags:
            if   transition_tag=="current":
                pass
            elif transition_tag.startswith("transition"):
                transition_dict["transition_identifier"] = transition_tag
            elif transition_tag.startswith("coming_from_"):
                transition_dict["transition_start_state"]   = re.sub(r"coming_from_", "", transition_tag)
            elif transition_tag.startswith("going_to_"):
                transition_dict["transition_end_state"]     = re.sub(r"going_to_"   , "", transition_tag)
            elif transition_tag.startswith("ca_connection"):
                transition_dict["ca_connection_identifier"] = re.sub(r"_end"        , "", transition_tag)
            else:
                print("Fatal in TagPlausibility-Checks: an unknown transition tag was found:", transition_tag, "in", line_tags)
        return transition_dict
    def __check_transition_dicts(self, transition_dict_list, transition_priority_dict):
        for transition_dict in transition_dict_list:
            if "transition_identifier" not in transition_dict:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a transition was found which does not have a tag which starts with the string "transition".')
            elif transition_dict["transition_identifier"] not in transition_priority_dict:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a transition was found which does not have a text-box which shows the priority.')
            if "transition_start_state" not in transition_dict:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a transition was found which does not have a "transition_start_state" tag.')
            if "transition_end_state" not in transition_dict:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a transition was found which does not have a "transition_end_state" tag.')

    def __create_connector_dict(self, canvas_item):
        # connector_dict = {"connector_identifier"           : "connector"<integer>,
        #                   "connector_outgoing_transitions" : ["transition"<integer>,"transition"<integer>,...],
        #                   "connector_incoming_transitions" : ["transition"<integer>,"transition"<integer>,...]}
        connector_dict = {}
        connector_outgoing_tranistions_list = []
        connector_incoming_transitions_list = []
        connector_tags = main_window.canvas.gettags(canvas_item)
        for connector_tag in connector_tags:
            if  connector_tag=="current":
                pass
            elif connector_tag.startswith("connector"):
                connector_dict["connector_identifier"] = connector_tag
            elif connector_tag.endswith("_start"):
                connector_outgoing_tranistions_list.append(re.sub("_start", "", connector_tag))
            elif connector_tag.endswith("_end"):
                connector_incoming_transitions_list.append(re.sub("_end"  , "", connector_tag))
            else:
                print("Fatal in TagPlausibility-Checks: an unknown connector tag was found:", connector_tag)
        connector_dict["connector_outgoing_transitions"] = connector_outgoing_tranistions_list
        connector_dict["connector_incoming_transitions"] = connector_incoming_transitions_list
        return connector_dict
    def __check_connector_dicts(self, connector_dict_list):
        for connector_dict in connector_dict_list:
            if "connector_identifier" not in connector_dict:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a connector was found which does not have a tag which starts with the string "connector".')
            # The keys "connector_outgoing_transitions" and "connector_incoming_transitions" exist always.
            # Both lists are allowed to be empty (in this case the HDL generation creates a warning).
            for transition_identifier in connector_dict["connector_outgoing_transitions"]:
                if not transition_identifier.startswith("transition"):
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: an outgoing transition-identifier from a connector was found which does not start with the string "transition":',
                          transition_identifier)
            for transition_identifier in connector_dict["connector_incoming_transitions"]:
                if not transition_identifier.startswith("transition"):
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: an incoming transition-identifier to a connector was found which does not start with the string "transition":',
                          transition_identifier)

    def __create_ca_window_dict(self, canvas_item):
        # ca_window_dict = {"ca_window_identifier"          : "condition_action13"<integer>,
        #                   "ca_connection_identifier"      : "ca_connection"<integer>,
        #                   "connected_to_reset_transition" : ""} <-- This entry is optional.
        ca_window_dict = {}
        window_tags = main_window.canvas.gettags(canvas_item)
        for window_tag in window_tags:
            if   window_tag=="current":
                pass
            elif window_tag.startswith("condition_action"): # "condition_action"<integer>
                ca_window_dict["ca_window_identifier"] = window_tag
            elif window_tag.startswith("ca_connection"): # "ca_connection"<integer>"_anchor"
                ca_window_dict["ca_connection_identifier"] = re.sub("_anchor", "", window_tag)
            elif window_tag=="connected_to_reset_transition":
                ca_window_dict["connected_to_reset_transition"] = ""
            else:
                print("Fatal in TagPlausibility-Checks: an unknown condition-action-window tag was found:", window_tag, "in", window_tags)
        return ca_window_dict
    def __check_ca_window_dicts(self, ca_window_dict_list):
        for ca_window_dict in ca_window_dict_list:
            identifier_number1_exists = False
            identifier_number2_exists = False
            if "ca_window_identifier" not in ca_window_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a condition-action-window was found which does not have a window-identifier-tag")
            else:
                condition_action_number_from_window_identifier = re.sub("condition_action", "", ca_window_dict["ca_window_identifier"])
                identifier_number1_exists = True
            if "ca_connection_identifier" not in ca_window_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a condition-action-window was found which does not have an identifier tag for the anchor-line")
            else:
                condition_action_number_from_anchor_line_identifier = re.sub("ca_connection", "", ca_window_dict["ca_connection_identifier"])
                identifier_number2_exists = True
            if identifier_number1_exists and identifier_number2_exists:
                if condition_action_number_from_window_identifier!=condition_action_number_from_anchor_line_identifier:
                    self.tag_status_is_okay = False
                    print("Fatal in TagPlausibility-Checks: the identifier-numbers derived from the condition-action window and from the anchor-line differ:",
                          condition_action_number_from_window_identifier +"!="+condition_action_number_from_anchor_line_identifier)

    def __create_ca_anchor_line_dict(self, canvas_item):
        ca_anchor_line_dict = {}
        line_tags = main_window.canvas.gettags(canvas_item)
        for ca_connection_tag in line_tags:
            if   ca_connection_tag=="current":
                pass
            elif ca_connection_tag.startswith("ca_connection"):
                ca_anchor_line_dict["ca_connection_identifier"] = ca_connection_tag
            elif ca_connection_tag.startswith("connected_to_transition"):
                ca_anchor_line_dict["connected_to_transition"] = re.sub(r"connected_to_", "", ca_connection_tag)
            else:
                print("Fatal in TagPlausibility-Checks: an unknown condition-action-line tag was found:", ca_connection_tag, "in", line_tags)
        return ca_anchor_line_dict
    def __check_ca_anchor_line_dicts(self, ca_anchor_line_dict_list):
        for ca_anchor_line_dict in ca_anchor_line_dict_list:
            if "ca_connection_identifier" not in ca_anchor_line_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a condition-action-line was found which does not have a condition-action-line-identifier-tag")
            if "connected_to_transition" not in ca_anchor_line_dict:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a condition-action-line was found which does not have a transition-identifier-tag")

    def __create_entry_in_shown_state_name_dict(self, canvas_item, shown_state_name_dict):
        text_tags = main_window.canvas.gettags(canvas_item) # The canvas_item identifies a text box.
        for text_tag in text_tags:
            if   text_tag=="current":
                pass
            elif text_tag.startswith("state"): # The complete text_tag is "state8_name" for example.
                state_identifier = re.sub("_name", "", text_tag)
                shown_state_name = main_window.canvas.itemcget(text_tag, "text") # i.e. "idle".
                shown_state_name_dict[state_identifier] = shown_state_name
            else:
                print("Fatal in TagPlausibility-Checks: an unknown tag was found in the tags of a state text box:", text_tag, "found in", text_tags)

    def __create_entry_in_transition_priority_dict(self, canvas_item, transition_priority_dict):
        text_tags = main_window.canvas.gettags(canvas_item)
        for text_tag in text_tags:
            if   text_tag=="current":
                pass
            elif text_tag.startswith("transition"):
                transition_name = re.sub("priority", "", text_tag)
                transition_priority = main_window.canvas.itemcget(text_tag, "text")
                transition_priority_dict[transition_name] = transition_priority
            else:
                print("Fatal in TagPlausibility-Checks: an unknown tag was found in the tags of a priority text box:", text_tag, "found in", text_tags)

    def __check_transitions(self, transition_dict_list, state_dict_list, connector_dict_list, reset_dict, shown_state_name_dict, ca_anchor_line_dict_list):
        for transition_dict in transition_dict_list:
            transition_identifier = transition_dict["transition_identifier"]
            # Check if an incoming transition only starts at the specified start-point:
            transition_start_state_identifier = transition_dict["transition_start_state"]
            number_of_good_hits = 0
            number_of_bad_hits  = 0
            for state_dict in state_dict_list:
                for outgoing_transition in state_dict["state_outgoing_transitions"]:
                    if outgoing_transition==transition_identifier:
                        if state_dict["state_identifier"]==transition_start_state_identifier:
                            number_of_good_hits += 1
                        else:
                            number_of_bad_hits += 1 # The transition leaves a state which is not the defined start-state.
            for connector_dict in connector_dict_list:
                for outgoing_transition in connector_dict["connector_outgoing_transitions"]:
                    if outgoing_transition==transition_identifier:
                        if connector_dict["connector_identifier"]==transition_start_state_identifier:
                            number_of_good_hits += 1
                        else:
                            number_of_bad_hits += 1 # The transition leaves a connector which is not the defined start-state.
            for outgoing_transition in reset_dict["reset_outgoing_transitions"]:
                if outgoing_transition==transition_identifier:
                    if reset_dict["reset_identifier"]==transition_start_state_identifier:
                        number_of_good_hits += 1
                    else:
                        number_of_bad_hits += 1 # The transition leaves the reset-entry which is not the defined start-state.
            if number_of_good_hits==0:
                self.tag_status_is_okay = False
                state_name = ""
                for state_dict in state_dict_list:
                    if state_dict["state_identifier"]==transition_start_state_identifier:
                        state_name = shown_state_name_dict[transition_start_state_identifier]
                        break
                if state_name!="":
                    print('Fatal in TagPlausibility-Checks: a transition was found whose start-state does not have this transition as outgoing transition.')
                    print("The transition starts at state", state_name, "but is not in the list of outgoing transitions of this state.")
                    print("Please reenter the transition.")
                else:
                    print('Fatal in TagPlausibility-Checks: a transition was found whose start-connector does not have this transition as outgoing transition.')
            elif number_of_good_hits>1:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a transition was found which is defined as outgoing transition at several states or connectors.')
            if number_of_bad_hits>0:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a transition was found which starts at a state/connector which is not defined as its start-state.')
            # Check if an outgoing transition only ends at the specified end-point:
            transition_end_state_identifier = transition_dict["transition_end_state"]
            number_of_good_hits = 0
            number_of_bad_hits  = 0
            for state_dict in state_dict_list:
                for incoming_transition in state_dict["state_incoming_transitions"]:
                    if incoming_transition==transition_identifier:
                        if state_dict["state_identifier"]==transition_end_state_identifier:
                            number_of_good_hits += 1
                        else:
                            number_of_bad_hits += 1
            for connector_dict in connector_dict_list:
                for incoming_transition in connector_dict["connector_incoming_transitions"]:
                    if incoming_transition==transition_identifier:
                        if connector_dict["connector_identifier"]==transition_end_state_identifier:
                            number_of_good_hits += 1
                        else:
                            number_of_bad_hits += 1
            if number_of_good_hits==0:
                self.tag_status_is_okay = False
                state_name = ""
                for state_dict in state_dict_list:
                    if state_dict["state_identifier"]==transition_end_state_identifier:
                        state_name = shown_state_name_dict[transition_end_state_identifier]
                        break
                if state_name!="":
                    print('Fatal in TagPlausibility-Checks: a transition was found whose target-state does not have this transition as incoming transition.')
                    print("The transition ends at state", state_name, "but is not in the list of incoming transitions of this state.")
                    print("Please reenter the transition.")
                else:
                    print('Fatal in TagPlausibility-Checks: a transition was found whose end-connector does not have this transition as incoming transition.')
            elif number_of_good_hits>1:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a transition was found which is defined as incoming transition at several states or connectors.')
            if number_of_bad_hits>0:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a transition was found which ends at a state/connector which is not defined as its target-state.')
            # For an attached condition-action-identifier there must a condition-action-anchor line exist:
            if "ca_connection_identifier" in transition_dict:
                ca_connection_identifier = transition_dict["ca_connection_identifier"]
                number_of_good_hits = 0
                for ca_anchor_line_dict in ca_anchor_line_dict_list:
                    if ca_connection_identifier==ca_anchor_line_dict["ca_connection_identifier"]:
                        number_of_good_hits += 1
                if number_of_good_hits==0:
                    print('Fatal in TagPlausibility-Checks: a transition was found which a condition_action-anchor-line attached, but there is no such line.')
                elif number_of_good_hits>1:
                    print('Fatal in TagPlausibility-Checks: a transition was found which a condition_action-anchor-line attached, but more than 1 line exist.')
    def __check_states_and_connectors(self, state_dict_list, transition_dict_list, shown_state_name_dict, connector_dict_list):
        # As the transitions are checked first by __check_transitions, here only each defined transition must be searched.
        for state_dict in state_dict_list: # Check each state.
            for outgoing_transition in state_dict["state_outgoing_transitions"]: # Check each outgoing transition
                found_transition = False
                for transition_dict in transition_dict_list: # Search the outgoing transition.
                    if outgoing_transition==transition_dict["transition_identifier"]:
                        found_transition = True
                if not found_transition:
                    self.tag_status_is_okay = False
                    state_name = shown_state_name_dict[state_dict["state_identifier"]]
                    print('Fatal in TagPlausibility-Checks: the state' + state_name + 'has an outgoing transition, which does not exist in the list of transitions.')
            for incoming_transition in state_dict["state_incoming_transitions"]: # Check each incoming transition
                found_transition = False
                for transition_dict in transition_dict_list: # Search the incoming transition.
                    if incoming_transition==transition_dict["transition_identifier"]:
                        found_transition = True
                if not found_transition:
                    self.tag_status_is_okay = False
                    state_name = shown_state_name_dict[state_dict["state_identifier"]]
                    print('Fatal in TagPlausibility-Checks: the state' + state_name + 'has an incoming transition, which does not exist in the list of transitions.')
        for connector_dict in connector_dict_list: # Check each connector.
            for outgoing_transition in connector_dict["connector_outgoing_transitions"]: # Check each outgoing transition
                found_transition = False
                for transition_dict in transition_dict_list: # Search the outgoing transition.
                    if outgoing_transition==transition_dict["transition_identifier"]:
                        found_transition = True
                if not found_transition:
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: a connector has an outgoing transition, which does not exist in the list of transitions.')
            for incoming_transition in connector_dict["connector_incoming_transitions"]: # Check each incoming transition
                found_transition = False
                for transition_dict in transition_dict_list: # Search the incoming transition.
                    if incoming_transition==transition_dict["transition_identifier"]:
                        found_transition = True
                if not found_transition:
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: a connector has an incoming transition, which does not exist in the list of transitions.')
    def __check_ca_windows(self, ca_window_dict_list, ca_anchor_line_dict_list, transition_dict_list):
        # ca_window_dict = {"ca_window_identifier"          : "condition_action13"<integer>,
        #                   "ca_connection_identifier"      : "ca_connection"<integer>,
        #                   "connected_to_reset_transition" : ""} <-- This entry is optional.
        # For each condition-action-window there must be exact 1 anchor line:
        for ca_window_dict in ca_window_dict_list:
            ca_line_identifier = ca_window_dict["ca_connection_identifier"]
            number_of_good_hits = 0
            for ca_anchor_line_dict in ca_anchor_line_dict_list:
                if ca_anchor_line_dict["ca_connection_identifier"]==ca_line_identifier:
                    number_of_good_hits += 1
            if number_of_good_hits==0:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a condition-action-window was found which does not have an anchor-line.')
            elif number_of_good_hits>1:
                self.tag_status_is_okay = False
                print('Fatal in TagPlausibility-Checks: a condition-action-window was found which has more than 1 anchor-line.')
        for ca_anchor_line_dict in ca_anchor_line_dict_list:
            ca_connection_identifier = ca_anchor_line_dict["ca_connection_identifier"]
            ca_transition            = ca_anchor_line_dict["connected_to_transition"]
            number_of_connected_condition_action_windows = 0
            for ca_window_dict in ca_window_dict_list:
                if ca_window_dict["ca_connection_identifier"]==ca_connection_identifier:
                    number_of_connected_condition_action_windows += 1
            number_of_transitions_the_anchor_line_is_attached_to = 0
            for transition_dict in transition_dict_list:
                if transition_dict["transition_identifier"]==ca_transition:
                    number_of_transitions_the_anchor_line_is_attached_to += 1
                    if transition_dict["ca_connection_identifier"]!=ca_connection_identifier:
                        self.tag_status_is_okay = False
                        print('Fatal in TagPlausibility-Checks: a transition and a condition-action-line differ about the ca_connection_identifier.')
                    break
            if number_of_connected_condition_action_windows==0 and number_of_transitions_the_anchor_line_is_attached_to==0:
                # This problem was caused by an old version of HDL-FSM-Editor: When a state was removed, then a connected
                # transition with a condition-action-window was also removed.
                # But the anchor-line of the condition-action-window stayed in the database.
                # Such "lost" lines are removed here without any message:
                main_window.canvas.delete(ca_connection_identifier)
                #print("Removed:", ca_connection_identifier)
            else:
                if number_of_connected_condition_action_windows==0:
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: the condition-action-line ' + ca_connection_identifier + ' was found for which no condition-action-window exists.')
                elif number_of_connected_condition_action_windows>1:
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: a condition-action-line was found which is connected to more than 1 condition-action-window.')
                if number_of_transitions_the_anchor_line_is_attached_to==0:
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: the condition-action-line ' + ca_connection_identifier + ' is not attached to any transition.')
                elif number_of_transitions_the_anchor_line_is_attached_to>1:
                    self.tag_status_is_okay = False
                    print('Fatal in TagPlausibility-Checks: the condition-action-line ' + ca_connection_identifier + ' is attached to more than 1 transition.')
    def __check_state_action_lines(self, state_action_line_dict_list, state_action_dict_list, state_dict_list):
        # state_action_line_dict = ("state_action_line_identifier" : "connection"<integer>,
        #                           "state_identifier"             : "state"<integer>)
        # state_action_dict = ("state_action_identifier"      : "state_action"<integer>,
        #                      "state_action_line_identifier" : "connection"<integer>)
        # state_dict = {"state_identifier"           : "state"<integer>,
        #               "state_outgoing_transitions" : ["transition"<integer>,"transition"<integer>,...],
        #               "state_incoming_transitions" : ["transition"<integer>,"transition"<integer>,...],
        #               "state_action_line"          : ["connection"<integer>,]} <-- Optional entry with an array of length 1, if everything is okay
        for state_action_line_dict in state_action_line_dict_list:
            connection_identifier = state_action_line_dict["state_action_line_identifier"]
            number_of_good_hits = 0
            for state_action_dict in state_action_dict_list:
                if state_action_dict["state_action_line_identifier"]==connection_identifier:
                    number_of_good_hits += 1
            if number_of_good_hits==0:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-action-line does not have a corresponding state-action")
            elif number_of_good_hits>1:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-action-line does have more than 1 corresponding state-action")
            number_of_good_hits = 0
            for state_dict in state_dict_list:
                if len(state_dict["state_action_line"])==1 and state_dict["state_action_line"][0]==connection_identifier:
                    number_of_good_hits += 1
            if number_of_good_hits==0:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-action-line is not connected to any state")
            elif number_of_good_hits>1:
                self.tag_status_is_okay = False
                print("Fatal in TagPlausibility-Checks: a state-action-line is connected to more than 1 state")

"""
This class checks the sensitivity list of a HDL design.
First it converts process sensitivities and process bodies to lists of words.
Then the targets of assignments in the process body are replaced by "t-a-r-g-e-t",
because these targets are not relevant for the sensitivity check.
Then, for each VHDL process, it is checked whether any of the readable signals or ports
is only used in the sensitivity list or only used in the process body.
If such a signal/port is found, a warning is added to the messages list.
"""

import re
from typing import Any


class SensitivityCheck:
    """Checks the sensitivity list of VHDL designs"""

    def __init__(
        self,
        readable_sigs: list[str],
        process_sensitivities_and_bodies: list[dict[str, Any]],
        language: str,
        file_name: str,
    ) -> None:
        self.readable_sigs = readable_sigs
        self.language = language
        self.file_name = file_name
        self._convert_process_sensitivities_and_process_bodies_to_lists_of_words(process_sensitivities_and_bodies)
        sensitivity_and_body_lists = self._prepare_process_bodys_for_check(process_sensitivities_and_bodies)
        self.messages = self._check_sensitivity(sensitivity_and_body_lists)

    def get_results(self) -> list[str]:
        """Return a list of warnings regarding the sensitivity list of the VHDL design."""
        return self.messages

    def _convert_process_sensitivities_and_process_bodies_to_lists_of_words(
        self, sensitivity_and_body_lists: list[dict[str, Any]]
    ) -> None:
        for index, sensitivity_and_body_entry in enumerate(sensitivity_and_body_lists):
            # sensitivity_and_body_lists[index] = [
            #     [entry.strip() for entry in sensitivity_and_body_entry[0].split(",")],
            #     self._split_process_body(sensitivity_and_body_entry[1]),
            # ]
            sensitivity_and_body_lists[index]["process_sensitivity"] = [
                entry.strip() for entry in sensitivity_and_body_entry["process_sensitivity"].split(",")
            ]
            sensitivity_and_body_lists[index]["process_body"] = self._split_process_body(
                sensitivity_and_body_entry["process_body"]
            )

    def _split_process_body(self, process_body: str) -> list[str]:
        process_body = re.sub(r"\[", r" [ ", process_body)  # Surround with blanks.
        process_body = re.sub(r"\]", r" ] ", process_body)  # Surround with blanks.
        process_body = re.sub(r",", r" , ", process_body)  # Separate list elements.
        process_body = re.sub(r":", r" : ", process_body)  # Separate labels
        process_body = re.sub(r"<", r" < ", process_body)  # Surround with blanks.
        process_body = re.sub(r">", r" > ", process_body)  # Surround with blanks.
        process_body = re.sub(r"=", r" = ", process_body)  # Surround with blanks.
        process_body = re.sub(r"\/", r" / ", process_body)  # Surround with blanks.
        process_body = re.sub(r" =\s*= ", r" == ", process_body)  # Restore ==.
        process_body = re.sub(r" :\s*= ", r" := ", process_body)  # Restore :=.
        process_body = re.sub(r" \/\s*= ", r" /= ", process_body)  # Restore /=.
        process_body = re.sub(r" <\s*= ", r" <= ", process_body)  # Restore <=.
        process_body = re.sub(r" >\s*= ", r" >= ", process_body)  # Restore >=.
        process_body = re.sub(r"\(", r" ( ", process_body)  # Surround brackets with blanks
        process_body = re.sub(r"\)", r" ) ", process_body)  # Surround brackets with blanks
        process_body = re.sub(r";", r" ; ", process_body)  # Surround assignment end with blanks.
        process_body = re.sub(r"\+", r" + ", process_body)  # Surround '+' with blanks.
        process_body = re.sub(r"-", r" - ", process_body)  # Surround '-' with blanks.
        # Remove any string (check for "not blank" ([^\s]) is used to keep the "'" of attributes):
        process_body = re.sub(r"'[^\s]*?'", r"   ", process_body)
        process_body = re.sub(r'"[^\s]*?"', r"   ", process_body)
        return process_body.split()

    def _prepare_process_bodys_for_check(
        self, process_sensitivities_and_bodies: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        sensitivity_and_body_lists = []
        for sensitivity_and_body_entry in process_sensitivities_and_bodies:
            process_body_list = sensitivity_and_body_entry["process_body"]
            process_body_list = (
                SensitivityCheck.replace_targets_in_vhdl_body(process_body_list)
                if self.language == "VHDL"
                else SensitivityCheck.replace_targets_in_verilog_body(process_body_list)
            )
            sensitivity_and_body_lists.append(
                {
                    "line_number": sensitivity_and_body_entry["line_number"],
                    "process_sensitivity": sensitivity_and_body_entry["process_sensitivity"],
                    "process_body": process_body_list,
                }
            )
        return sensitivity_and_body_lists

    def _check_sensitivity(self, sensitivity_and_body_lists: list[dict[str, Any]]) -> list[str]:
        messages = []
        # for sensitivity_list, process_body_list in sensitivity_and_body_lists:
        for dictionary in sensitivity_and_body_lists:
            line_number = dictionary["line_number"]
            sensitivity_list = dictionary["process_sensitivity"]
            process_body_list = dictionary["process_body"]
            if (self.language == "VHDL" and "all" not in sensitivity_list) or (
                self.language != "VHDL" and "*" not in sensitivity_list
            ):
                found_slices_in_sensitivity_list = {}
                found_slices_in_process_body = {}
                if self.language == "VHDL":
                    self._search_slices(
                        found_slices_in_process_body,
                        found_slices_in_sensitivity_list,
                        process_body_list,
                        sensitivity_list,
                    )
                for readable_sig in self.readable_sigs:
                    message = self._check_sensitivity_of_single_sig(
                        line_number,
                        readable_sig,
                        sensitivity_list,
                        process_body_list,
                        found_slices_in_process_body,
                        found_slices_in_sensitivity_list,
                    )
                    messages.extend(message)
        return messages

    def _check_sensitivity_of_single_sig(
        self,
        line_number: int,
        readable_sig: str,
        sensitivity_list: list[str],
        process_body_list: list[str],
        found_slices_in_process_body: dict[str, list[str]],
        found_slices_in_sensitivity_list: dict[str, list[str]],
    ) -> list[str]:
        message = []
        found_in_sensitivity_list = bool(readable_sig in sensitivity_list)
        found_in_process_body_list = bool(readable_sig in process_body_list)
        if self.language == "VHDL" and found_in_sensitivity_list is False and found_in_process_body_list is False:
            # Neither the sensitivity nor the body contains the readable_sig directly.
            # So the readable_sig might be a record. So check the slices (if there are any)
            for record_slice in found_slices_in_process_body[readable_sig]:
                # There is a slice of the readable_sig in the process body ...
                if record_slice not in found_slices_in_sensitivity_list[readable_sig]:
                    # ... but not in the sensitivity:
                    message.append(self._create_message(line_number, record_slice, False))
            for record_slice in found_slices_in_sensitivity_list[readable_sig]:
                # There is a slice of the readable_sig in the sensitivity ...
                if record_slice not in found_slices_in_process_body[readable_sig]:
                    # ... but not in the process body:
                    message.append(self._create_message(line_number, record_slice, True))
        if self.language == "VHDL" and found_in_sensitivity_list and not found_in_process_body_list:
            # If there are slices of the readable_signal in the process body, found_in_process_body_list must be fixed:
            found_in_process_body_list = any(entry.startswith(readable_sig + ".") for entry in process_body_list)
        if found_in_sensitivity_list != found_in_process_body_list:
            message.append(self._create_message(line_number, readable_sig, found_in_sensitivity_list))
        return message

    def _search_slices(
        self,
        found_slices_in_process_body: dict[str, list[str]],
        found_slices_in_sensitivity_list: dict[str, list[str]],
        process_body_list: list[str],
        sensitivity_list: list[str],
    ) -> None:
        for readable_sig in self.readable_sigs:
            found_slices_in_process_body[readable_sig] = [
                entry for entry in process_body_list if entry.startswith(readable_sig + ".")
            ]
            found_slices_in_sensitivity_list[readable_sig] = [
                entry for entry in sensitivity_list if entry.startswith(readable_sig + ".")
            ]

    def _remove_record_slices_from_list_of_words(self, list_of_words: list[str]) -> list[str]:
        for index, word in enumerate(list_of_words):
            list_of_words[index] = re.sub(r"\..*", "", word)
        return list_of_words

    def _create_message(self, line_number: int, readable_sig: str, found_in_sensitivity_list: bool) -> str:
        if found_in_sensitivity_list:
            message = (
                f"{self.file_name}:{line_number}:0: "
                f"Warning: The signal/port '{readable_sig}' is included in the "
                f"sensitivity list, but not used in the process body."
            )
        else:  # found_in_process_body_list is True
            message = (
                f"{self.file_name}:{line_number}:0: "
                f"Warning: The signal/port '{readable_sig}' is not included in the sensitivity list, "
                f"but used in the process body."
            )
        return message

    @classmethod
    def replace_targets_in_vhdl_body(cls, process_body_list: list[str]) -> list[str]:
        """Replaces all targets of assignments in the process body by "t-a-r-g-e-t"."""
        remove_target = False
        line_end_hit = False
        in_bracket = 0
        new_process_body_list = []
        for word in reversed(process_body_list):  # Only the process body is relevant for the target check.
            if word in ("<=", ":="):
                in_bracket = 0  # Fix wrong number of opening or closing brackets at the right hand side.
            if word == ")":  # jump over index-bracket
                in_bracket += 1
            elif word == "(":
                in_bracket -= 1
            elif in_bracket == 0:
                if word == ";":
                    line_end_hit = True
                elif line_end_hit and word in ("<=", ":="):
                    remove_target = True
                elif remove_target:
                    word = "t-a-r-g-e-t"
                    remove_target = False
                    line_end_hit = False
            new_process_body_list.append(word)
        return list(reversed(new_process_body_list))

    @classmethod
    def replace_targets_in_verilog_body(cls, process_body_list: list[str]) -> list[str]:
        """Replaces all targets of assignments in the process body by "t-a-r-g-e-t"."""
        remove_target = False
        line_end_hit = False
        in_bracket = 0
        new_process_body_list = []
        in_square_bracket = 0
        for word in reversed(process_body_list):  # Only the process body is relevant for the target check.
            if word == ")":  # jump over condition-bracket
                in_bracket += 1
            elif word == "(":
                in_bracket -= 1
            if word == "]":  # jump over index-bracket
                in_square_bracket += 1
            elif word == "[":
                in_square_bracket -= 1
            elif in_bracket == 0 and in_square_bracket == 0:
                if remove_target:
                    word = "t-a-r-g-e-t"
                    line_end_hit = False
                    remove_target = False
                elif word == ";":
                    line_end_hit = True
                elif line_end_hit and word == "<=":
                    remove_target = True
            new_process_body_list.append(word)
        return list(reversed(new_process_body_list))

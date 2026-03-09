"""
This class starts the check of the sensitivity lists of the design.
First it collects all needed data.
Then it starts the check.
At last it copies the warnings to the messages tab and shows this tab if there are any warnings.
"""

import re
import tkinter as tk

from constants import GuiTab
from project_manager import project_manager

from . import hdl_generation_architecture_state_actions, hdl_generation_library, sensitivity_check

VHDL_PROCESS_REGEX = re.compile(r"process\s*\((.*?)\).*?\s+begin(.*?)\send\s+process\s*;", re.IGNORECASE | re.DOTALL)
VERILOG_PROCESS_REGEX = re.compile(r"always\s*@\s*\((.*?)\)\s*begin(.*?)\s*end\s*always;", re.IGNORECASE | re.DOTALL)


class SensitivityCheckHfe:
    """Checks the sensitivity list of VHDL designs"""

    def __init__(self, is_script_mode):
        language = project_manager.language.get()
        if project_manager.select_file_number_text.get() == 1:
            if language == "VHDL":
                file_name = project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + ".vhd"
            else:
                file_name = project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + ".v"
        else:
            file_name = project_manager.generate_path_value.get() + "/" + project_manager.module_name.get() + "_fsm.vhd"
        readable_sigs = hdl_generation_architecture_state_actions.create_a_list_with_all_possible_sensitivity_entries()
        process_sensitivities_and_bodies = self._collect_process_sensitivities_and_bodies(file_name)
        if process_sensitivities_and_bodies:
            messages = sensitivity_check.SensitivityCheck(
                readable_sigs, process_sensitivities_and_bodies, language, file_name
            ).get_results()
            if messages:
                if not is_script_mode:
                    project_manager.log_frame_text.config(state=tk.NORMAL)
                    for message in messages:
                        project_manager.log_frame_text.insert(tk.END, message + "\n", ("message_red"))
                    project_manager.log_frame_text.config(state=tk.DISABLED)
                    project_manager.log_frame_text.see(tk.END)
                    project_manager.notebook.show_tab(GuiTab.COMPILE_MSG)
                else:
                    for message in messages:
                        print(message)

    def _collect_process_sensitivities_and_bodies(self, file_name) -> list[tuple[str, str]]:
        with open(file_name, encoding="utf-8") as f:
            hdl = f.read()
        if hdl == "":
            return []
        process_regex = VHDL_PROCESS_REGEX if project_manager.language.get() == "VHDL" else VERILOG_PROCESS_REGEX
        process_matches = re.finditer(process_regex, hdl)
        process_sensitivities_and_bodies = []
        for process_match in process_matches:
            char_number = process_match.start()
            line_number = hdl[:char_number].count("\n") + 1
            process_sensitivity = hdl_generation_library.remove_comments_and_returns(process_match.group(1))
            process_body = hdl_generation_library.remove_comments_and_returns(process_match.group(2))
            clocked_process = re.search(r"\s*'\s*event", process_body, re.IGNORECASE)
            if "rising_edge" not in process_body and "falling_edge" not in process_body and clocked_process is None:
                process_sensitivities_and_bodies.append(
                    {
                        "line_number": line_number,
                        "process_sensitivity": process_sensitivity,
                        "process_body": process_body,
                    }
                )
        return process_sensitivities_and_bodies

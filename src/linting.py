"""
Methods needed for highlighting signals, which are not read, not written, not defined
"""

import copy

import constants
import custom_text
from elements import global_actions_combinatorial
from project_manager import project_manager


class HighLightDict:
    """
    There is only one HighLightDict object used, which is created at startup.
    The dictionary contains some predefined keywords for syntax highlighting.
    Additionally the keywords for not read and not written signals are added here.
    """

    def __init__(self) -> None:
        self.highlight_pattern_dict: dict[str, list[str]] = copy.deepcopy(constants.VHDL_HIGHLIGHT_PATTERN_DICT)
        self.recreate_after_id = None
        self.update_highlight_tags_id = None

    def recreate_keyword_list_of_unused_signals(self) -> None:
        if self.recreate_after_id is not None:
            project_manager.root.after_cancel(self.recreate_after_id)
        self.recreate_after_id = project_manager.root.after(
            300, self._recreate_keyword_list_of_unused_signals_after_idle
        )

    def _recreate_keyword_list_of_unused_signals_after_idle(self) -> None:
        self.highlight_pattern_dict["not_read"].clear()
        self.highlight_pattern_dict["not_written"].clear()

        variables_to_write = self._get_all_read_variables()
        variables_to_read = self._get_all_written_variables()
        variables_to_write = self._store_not_read_input_ports(variables_to_write)
        variables_to_read, variables_to_write = self._store_not_written_output_ports(
            variables_to_read, variables_to_write
        )
        variables_to_read, variables_to_write = self._store_not_written_not_read_signals(
            variables_to_read, variables_to_write
        )
        variables_to_read, variables_to_write = self._detect_not_written_constants(
            variables_to_read, variables_to_write
        )
        variables_to_write = self._remove_port_types(variables_to_write)
        variables_to_read, variables_to_write = self._remove_generics(variables_to_read, variables_to_write)
        self.highlight_pattern_dict["not_written"] += variables_to_write
        self.highlight_pattern_dict["not_read"] += variables_to_read

    def _get_all_read_variables(self):
        variables_to_write = []
        for _, read_variables_of_window in custom_text.CustomText.read_variables_of_all_windows.items():
            variables_to_write += read_variables_of_window
        variables_to_write = list(set(variables_to_write))  # remove duplicates
        return variables_to_write

    def _get_all_written_variables(self):
        variables_to_read = []
        for _, written_variables_of_window in custom_text.CustomText.written_variables_of_all_windows.items():
            variables_to_read += written_variables_of_window
        variables_to_read = list(set(variables_to_read))  # remove duplicates
        return variables_to_read

    def _store_not_read_input_ports(self, variables_to_write):
        for input_port in project_manager.interface_ports_text.readable_ports_list:
            if input_port in variables_to_write:
                # Input is read but must not be written:
                variables_to_write.remove(input_port)
            else:
                if input_port != project_manager.clock_signal_name.get():
                    self.highlight_pattern_dict["not_read"].append(input_port)
        return variables_to_write

    def _store_not_written_output_ports(self, variables_to_read, variables_to_write):
        for output in project_manager.interface_ports_text.writable_ports_list:
            if output in variables_to_read:
                # Outputs is written but must not be read:
                variables_to_read.remove(output)
            else:
                self.highlight_pattern_dict["not_written"].append(output)
            if project_manager.language.get() != "VHDL" and output in variables_to_write:  # A Verilog output is read.
                # Writing of outputs is checked by the variables_to_read list:
                variables_to_write.remove(output)
        return variables_to_read, variables_to_write

    def _store_not_written_not_read_signals(self, variables_to_read, variables_to_write):
        # Check if each signal or variable is written and is read:
        process_variable_list = []
        for _, ref in global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict.items():
            process_variable_list += ref.text_id.signals_list
        for signal in (
            project_manager.internals_architecture_text.signals_list
            + project_manager.internals_process_combinatorial_text.signals_list
            + project_manager.internals_process_clocked_text.signals_list
            + process_variable_list
        ):
            if signal in variables_to_read and signal in variables_to_write:
                variables_to_read.remove(signal)
                variables_to_write.remove(signal)
            elif signal in variables_to_read:
                self.highlight_pattern_dict["not_read"].append(signal)
            else:
                self.highlight_pattern_dict["not_written"].append(signal)
        return variables_to_read, variables_to_write

    def _detect_not_written_constants(self, variables_to_read, variables_to_write):
        for constant in (
            project_manager.internals_architecture_text.constants_list
            + project_manager.internals_process_combinatorial_text.constants_list
            + project_manager.internals_process_clocked_text.constants_list
        ):
            if constant in variables_to_read:
                variables_to_read.remove(constant)
            if constant not in variables_to_write:  # Then the constant is not read.
                self.highlight_pattern_dict["not_read"].append(constant)
            else:
                variables_to_write.remove(constant)
        return variables_to_read, variables_to_write

    def _remove_port_types(self, variables_to_write):
        for port_type in project_manager.interface_ports_text.port_types_list:
            if port_type in variables_to_write:
                variables_to_write.remove(port_type)
        return variables_to_write

    def _remove_generics(self, variables_to_read, variables_to_write):
        for generic in project_manager.interface_generics_text.generics_list:
            if generic in variables_to_read:
                variables_to_read.remove(generic)
            if generic in variables_to_write:
                variables_to_write.remove(generic)
        return variables_to_read, variables_to_write

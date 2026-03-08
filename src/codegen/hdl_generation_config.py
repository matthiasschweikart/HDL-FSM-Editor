"""
Configuration class for HDL generation settings
"""

from pathlib import Path
from typing import Optional

from project_manager import project_manager
from utils.hdl_paths import get_hdl_output_paths


class GenerationConfig:
    """Configuration for HDL code generation"""

    def __init__(self) -> None:
        # Core generation settings
        self.language: str = "VHDL"  # "VHDL", "Verilog", "SystemVerilog"
        self.module_name: str = ""
        self.generate_path: str = ""
        self.select_file_number: int = 1  # 1 or 2 files (VHDL only)
        self.include_timestamp: bool = False

        # Signal names
        self.clock_signal_name: str = ""
        self.reset_signal_name: str = ""

        # Code style
        self.indentation: str = "    "  # 4 spaces

        self.write_to_file: bool = False

    @classmethod
    def from_main_window(cls) -> "GenerationConfig":
        """Create a GenerationConfig instance from main_window settings"""

        config = cls()
        config.language = project_manager.language.get()
        config.module_name = project_manager.module_name.get()
        config.generate_path = project_manager.generate_path_value.get()
        config.select_file_number = project_manager.select_file_number_text.get()
        config.include_timestamp = project_manager.include_timestamp_in_output.get()
        config.clock_signal_name = project_manager.clock_signal_name.get()
        config.reset_signal_name = project_manager.reset_signal_name.get()

        return config

    def get_comment_style(self) -> str:
        """Get the appropriate comment style for the current language"""
        if self.language == "VHDL":
            return "--"
        # Verilog, SystemVerilog
        return "//"

    def get_file_extension(self) -> str:
        """Get the appropriate file extension for the current language"""
        if self.language == "VHDL":
            return ".vhd"
        if self.language == "Verilog":
            return ".v"
        if self.language == "SystemVerilog":
            return ".sv"
        raise ValueError(f"Unsupported language: {self.language}")

    def get_output_files(self) -> list[str]:
        """
        Get the list of output file paths based on language and file count settings.
        Returns a list of file paths that will be generated.
        """
        return get_hdl_output_paths(
            self.generate_path,
            self.module_name,
            self.language,
            self.select_file_number,
        )

    def get_primary_file(self) -> Optional[str]:
        """Get the primary output file path (first file in the list)"""
        files = self.get_output_files()
        return files[0] if files else None

    def get_architecture_file(self) -> Optional[str]:
        """Get the architecture file path (for VHDL two-file mode)"""
        files = self.get_output_files()
        return files[1] if len(files) > 1 else None

    def validate(self) -> list[str]:
        """
        Validate the configuration and return a list of error messages.
        Returns empty list if configuration is valid.
        """
        errors = []

        if not self.module_name or self.module_name.isspace():
            errors.append("No module name is specified")

        if not self.generate_path or self.generate_path.isspace():
            errors.append("No generate output path is specified")
        else:
            path = Path(self.generate_path)
            if not path.exists():
                errors.append(f"Generate output path does not exist: {self.generate_path}")

        if not self.reset_signal_name or self.reset_signal_name.isspace():
            errors.append("No reset signal name is specified")

        if not self.clock_signal_name or self.clock_signal_name.isspace():
            errors.append("No clock signal name is specified")

        if self.language not in ["VHDL", "Verilog", "SystemVerilog"]:
            errors.append(f"Unsupported language: {self.language}")

        if self.select_file_number not in [1, 2]:
            errors.append(f"Invalid file number setting: {self.select_file_number}")

        return errors

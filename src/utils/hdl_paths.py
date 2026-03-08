"""
Single source of truth for HDL output file path construction.
"""

from pathlib import Path
from typing import Optional


def _get_extension(language: str) -> str:
    """Return file extension for the given language."""
    if language == "VHDL":
        return ".vhd"
    if language == "Verilog":
        return ".v"
    if language == "SystemVerilog":
        return ".sv"
    raise ValueError(f"Unsupported language: {language}")


def get_hdl_output_paths(
    generate_path: str,
    module_name: str,
    language: str,
    select_file_number: int,
) -> list[str]:
    """
    Return the list of output file paths for generated HDL.

    Verilog/SystemVerilog: single file. VHDL: one or two files depending on
    select_file_number (1 or 2). Returns empty list if generate_path or
    module_name is missing/whitespace.
    """
    if not module_name or not module_name.strip():
        return []
    if not generate_path or not generate_path.strip():
        return []
    base = Path(generate_path)
    if language in ("Verilog", "SystemVerilog"):
        ext = _get_extension(language)
        return [str(base / f"{module_name}{ext}")]
    if language != "VHDL":
        return []
    if select_file_number == 1:
        return [str(base / f"{module_name}.vhd")]
    return [
        str(base / f"{module_name}_e.vhd"),
        str(base / f"{module_name}_fsm.vhd"),
    ]


def get_primary_output_path(
    generate_path: str,
    module_name: str,
    language: str,
    select_file_number: int,
) -> Optional[str]:
    """First output file path, or None if no outputs."""
    paths = get_hdl_output_paths(generate_path, module_name, language, select_file_number)
    return paths[0] if paths else None


def get_architecture_output_path(
    generate_path: str,
    module_name: str,
    language: str,
    select_file_number: int,
) -> Optional[str]:
    """Second output file (VHDL two-file mode only), or None."""
    paths = get_hdl_output_paths(generate_path, module_name, language, select_file_number)
    return paths[1] if len(paths) > 1 else None

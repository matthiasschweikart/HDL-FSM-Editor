"""
Variable expansion utilities for HDL-FSM-Editor.

This module provides functionality to expand bash-style variables in strings,
including environment variables and application-specific internal variables.
"""

import os
import re
from typing import Callable, Optional


def expand_variables(
    text: str,
    internal_vars: Optional[dict[str, str | Callable[[str], str]]] = None,
    error_on_missing: bool = False,
    use_environ: bool = True,
) -> str:
    """
    Expand bash-style variables in a string.

    Supports:
    - Environment variables: $VAR or ${VAR}
    - Internal variables: $file, $file1, $file2, $name, etc.
    - Default values: ${VAR:-default}

    Args:
        text: The input string containing variables to expand
        internal_vars: Dictionary of internal application variables, or a callable(var_name) that returns a string.
        error_on_missing: If True, raise KeyError for missing variables.
                         If False, leave unresolved variables as-is.
        use_environ: If True, include environment variables in expansion.
                    If False, only use internal_vars.

    Returns:
        String with variables expanded

    Raises:
        KeyError: If error_on_missing=True and a variable is not found
    """
    if internal_vars is None:
        internal_vars = {}

    # Combine environment variables with internal variables
    all_vars = {**os.environ, **internal_vars} if use_environ else internal_vars

    def replace_var(match: re.Match) -> str:
        """Replace a single variable match."""
        full_match: str = match.group(0)
        var_name: str = match.group(1) or match.group(2)

        # Handle default value syntax: ${VAR:-default}
        if ":-" in var_name:
            var_name, default_value = var_name.split(":-", 1)
            if var_name in all_vars:
                return all_vars[var_name]
            return default_value

        # Regular variable expansion
        if var_name in all_vars:
            value = all_vars[var_name]
            if callable(value):
                return value()
            return value
        if error_on_missing:
            raise KeyError(var_name)
        # Leave unresolved variables as-is
        return full_match

    # Pattern to match $VAR or ${VAR} syntax (group 1 for ${...}, group 2 for $name)
    pattern = r"\$\{([^}]+)\}|\$([a-zA-Z_][a-zA-Z0-9_]*)"

    return re.sub(pattern, replace_var, text)


def expand_variables_in_list(
    items: list[str],
    internal_vars: Optional[dict[str, str]] = None,
    error_on_missing: bool = False,
    use_environ: bool = True,
) -> list[str]:
    """
    Expand variables in each item of a list of strings.

    Args:
        items: List of strings to process
        internal_vars: Dictionary of internal application variables
        error_on_missing: If True, raise KeyError for missing variables
        use_environ: If True, include environment variables in expansion.

    Returns:
        List of strings with variables expanded
    """
    return [expand_variables(item, internal_vars, error_on_missing, use_environ) for item in items]

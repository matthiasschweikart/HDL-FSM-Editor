"""Utility modules for HDL-FSM-Editor."""

from .var_expansion import (
    expand_variables,
    expand_variables_in_list,
    find_git_root,
)

__all__ = [
    "expand_variables",
    "expand_variables_in_list",
    "find_git_root",
]

import pathlib
from typing import Optional


def find_git_root(start_path: Optional[str] = None) -> Optional[str]:
    """
    Search upwards from start_path (or current working dir) for a .git directory or file.
    Returns the absolute path to the directory containing .git, or None if not found.
    """
    path = pathlib.Path.cwd() if start_path is None else pathlib.Path(start_path).absolute()
    while True:
        git_path = path / ".git"
        if git_path.is_dir() or git_path.is_file():
            return str(path.as_posix())
        parent = path.parent
        if parent == path:
            # Reached the root directory
            break
        path = parent
    return None


def absolute_path(path: str) -> str:
    """Return the absolute path of the given path."""
    return str(pathlib.Path(path).absolute())

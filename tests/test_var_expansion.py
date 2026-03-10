"""
Tests for utils.var_expansion (no project/tkinter dependencies).
"""

import os
import sys
from pathlib import Path

import pytest

# Allow importing utils.var_expansion when run from project root
_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


from utils.var_expansion import (  # noqa: E402
    expand_generate_path,
    expand_variables,
    expand_variables_in_list,
    find_git_root,
)


class TestExpandVariables:
    """Tests for expand_variables()."""

    def test_empty_string(self):
        assert expand_variables("") == ""

    def test_no_variables(self):
        assert expand_variables("hello world") == "hello world"

    def test_internal_only_no_env(self):
        assert (
            expand_variables(
                "name=$name file=$file", internal_vars={"name": "mymod", "file": "/out/mymod.vhd"}, use_environ=False
            )
            == "name=mymod file=/out/mymod.vhd"
        )

    def test_bracket_syntax(self):
        assert expand_variables("${name}", internal_vars={"name": "mymod"}, use_environ=False) == "mymod"

    def test_default_value_used(self):
        assert expand_variables("${MISSING:-default}", internal_vars={}, use_environ=False) == "default"

    def test_default_value_not_used_when_defined(self):
        assert expand_variables("${x:-fallback}", internal_vars={"x": "set"}, use_environ=False) == "set"

    def test_env_included_when_use_environ_true(self):
        os.environ["_VAR_EXPAND_TEST"] = "env_value"
        try:
            assert expand_variables("$_VAR_EXPAND_TEST", internal_vars={}) == "env_value"
        finally:
            os.environ.pop("_VAR_EXPAND_TEST", None)

    def test_internal_overrides_env(self):
        os.environ["_VAR_EXPAND_OVERRIDE"] = "env"
        try:
            assert (
                expand_variables("$_VAR_EXPAND_OVERRIDE", internal_vars={"_VAR_EXPAND_OVERRIDE": "internal"})
                == "internal"
            )
        finally:
            os.environ.pop("_VAR_EXPAND_OVERRIDE", None)

    def test_unresolved_left_as_is(self):
        assert expand_variables("$UNKNOWN_VAR_XYZ", internal_vars={}, use_environ=False) == "$UNKNOWN_VAR_XYZ"

    def test_error_on_missing_raises(self):
        with pytest.raises(KeyError, match="MISSING"):
            expand_variables("$MISSING", internal_vars={}, error_on_missing=True, use_environ=False)

    def test_mixed_expansion(self):
        result = expand_variables(
            "a=$a b=${b} c=${c:-default}",
            internal_vars={"a": "1", "b": "2"},
            use_environ=False,
        )
        assert result == "a=1 b=2 c=default"

    def test_callable_value_expanded(self):
        """Callable in internal_vars is invoked (no args) and its return value is used."""
        result = expand_variables("$dynamic", internal_vars={"dynamic": lambda: "computed"}, use_environ=False)
        assert result == "computed"

    def test_callable_bracket_syntax(self):
        result = expand_variables("${dynamic}", internal_vars={"dynamic": lambda: "from_callable"}, use_environ=False)
        assert result == "from_callable"

    def test_callable_and_string_mixed(self):
        result = expand_variables(
            "$static and $dynamic",
            internal_vars={"static": "fixed", "dynamic": lambda: "computed"},
            use_environ=False,
        )
        assert result == "fixed and computed"

    def test_callable_returns_empty_string(self):
        assert expand_variables("pre$empty post", internal_vars={"empty": lambda: ""}, use_environ=False) == "pre post"

    def test_callable_called_per_expansion(self):
        """Each occurrence of the variable invokes the callable (lazy evaluation)."""
        call_count = 0

        def counter():
            nonlocal call_count
            call_count += 1
            return str(call_count)

        result = expand_variables("$x $x $x", internal_vars={"x": counter}, use_environ=False)
        assert result == "1 2 3"
        assert call_count == 3


class TestExpandVariablesInList:
    """Tests for expand_variables_in_list()."""

    def test_empty_list(self):
        assert expand_variables_in_list([]) == []

    def test_no_expansion(self):
        assert expand_variables_in_list(["a", "b"], use_environ=False) == ["a", "b"]

    def test_each_item_expanded(self):
        assert expand_variables_in_list(
            ["$a", "$b", "literal"],
            internal_vars={"a": "1", "b": "2"},
            use_environ=False,
        ) == ["1", "2", "literal"]

    def test_callable_in_list_expansion(self):
        """expand_variables_in_list forwards internal_vars to expand_variables (callables work)."""
        assert expand_variables_in_list(
            ["$x", "$x"],
            internal_vars={"x": lambda: "callable_result"},
            use_environ=False,
        ) == ["callable_result", "callable_result"]


class TestFindGitRoot:
    """Tests for find_git_root()."""

    def test_from_project_root_returns_root(self, project_root):
        # project_root is the repo root (parent of tests/)
        result = find_git_root(project_root.as_posix())
        assert result is not None
        assert (Path(result) / ".git").exists() or (Path(result) / ".git").is_file()

    def test_from_tests_dir_returns_same_root(self, project_root):
        tests_dir = project_root / "tests"
        result = find_git_root(tests_dir.as_posix())
        assert result is not None
        assert Path(result).resolve() == project_root.resolve()

    def test_from_nonexistent_subpath_uses_cwd(self):
        # Passing a path that doesn't exist - abspath still gives something; behavior is path-based
        result = find_git_root(Path("/nonexistent/dir/xyz").as_posix())
        # May return None if we're not under a git repo, or the repo containing cwd
        assert result is None or (Path(result) / ".git").exists()


class TestExpandGeneratePath:
    """Tests for expand_generate_path()."""

    def test_empty_string(self):
        assert expand_generate_path("") == ""

    def test_no_variables(self):
        assert expand_generate_path("/some/path") == "/some/path"

    def test_env_var_expanded(self):
        os.environ["_GEN_PATH_TEST"] = "/env/dir"
        try:
            assert expand_generate_path("$_GEN_PATH_TEST/build") == "/env/dir/build"
        finally:
            os.environ.pop("_GEN_PATH_TEST", None)

    def test_git_root_expanded_when_under_repo(self, project_root):
        """$git_root is expanded when hfe_file_path is under a git repo."""
        hfe_under_repo = str(project_root / "tests" / "dummy.hfe")
        result = expand_generate_path("$git_root/out", hfe_under_repo)
        assert result == f"{project_root.as_posix()}/out"

    def test_git_root_not_expanded_when_no_hfe_path(self):
        """Without hfe path, $git_root is left as-is."""
        assert expand_generate_path("$git_root/out", None) == "$git_root/out"

    def test_git_root_not_expanded_when_not_under_repo(self):
        """When path is not under a git repo, $git_root is left as-is."""
        result = expand_generate_path("$git_root/out", "/nonexistent/dir/file.hfe")
        assert result == "$git_root/out"

    def test_mixed_env_and_git_root(self, project_root):
        os.environ["_BUILD"] = "build"
        try:
            hfe = str(project_root / "x.hfe")
            result = expand_generate_path("$git_root/$_BUILD", hfe)
            assert result == f"{project_root.as_posix()}/build"
        finally:
            os.environ.pop("_BUILD", None)

    def test_unresolved_left_as_is(self):
        assert expand_generate_path("$UNKNOWN/path", None) == "$UNKNOWN/path"

    def test_hfe_file_dir_expanded_when_hfe_path_given(self):
        """$hfe_file_dir is the directory containing the .hfe file."""
        hfe_path = "/some/project/designs/foo.hfe"
        result = expand_generate_path("$hfe_file_dir/out", hfe_path)
        assert result == "/some/project/designs/out"

    def test_hfe_file_dir_not_expanded_when_no_hfe_path(self):
        """Without hfe path, $hfe_file_dir is left as-is."""
        assert expand_generate_path("$hfe_file_dir/out", None) == "$hfe_file_dir/out"

    def test_hfe_file_dir_with_trailing_slash_normalized(self):
        """hfe_file_path with trailing slash still yields parent dir without file."""
        result = expand_generate_path("$hfe_file_dir", "/a/b/bar.hfe/")
        # Path(...).parent on "/a/b/bar.hfe/" resolves to /a/b
        assert result == "/a/b"

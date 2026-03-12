# Using the HDL-FSM-Editor with Git

This document describes how to use the editor in a git-based workflow so that both the design (`.hfe`) and the generated HDL output can be tracked in version control.

---

## What to track in Git

- **`.hfe` file** — The design file (state machine, interface, internals). This is the main source and should always be committed.
- **Generated HDL file(s)** — The output from **Generate** (e.g. `*_e.vhd`, `*_fsm.vhd` or a single `.v`/`.vhd`/`.sv` file). Tracking these gives you a stable, reviewable HDL snapshot for each commit.

---

## Recommended settings for version control

### Disable timestamp in generated files

In the **Control** tab, **deselect** the option **"Include timestamp in generated HDL files"**.

When this option is enabled, every generation writes a different "Created at …" line into the HDL, so the file changes on every run even if the design did not. With the option off, regenerating from the same design produces identical output, which keeps diffs and merges meaningful.

---

## Output directory (where generated HDL is written)

The **"Directory for generated HDL"** field in the Control tab supports **variable expansion**. The expanded path is used when generating HDL and when running the compile command.

### Variables available in the output path

| Variable         | Description |
|------------------|-------------|
| `$git_root`      | Absolute path to the git repository root (directory containing `.git`). Resolved from the current `.hfe` file. If the file is not under a git repo, `$git_root` is left unchanged. |
| `$hfe_file_dir`  | Absolute path to the directory containing the current `.hfe` file. Useful for output next to the design or in a sibling directory. |
| `$VAR` / `${VAR}`| Environment variables (e.g. `$HOME`, `$BUILD_DIR`). |

You can combine these to keep output inside the repo or relative to the design:

- **Output at repository root:**
  `$git_root/generated`
  or a subfolder:
  `$git_root/hdl/generated`

- **Output next to the .hfe file:**
  `$hfe_file_dir`
  or in a subfolder:
  `$hfe_file_dir/generated`

- **Output via environment variable:**
  e.g. set `HDL_OUT_DIR` and use
  `$HDL_OUT_DIR`

Unresolved variables are left as-is (e.g. `$git_root` when not in a repo).

---

## Compile command and variables

The **Compile command** (Control tab) is expanded with its own set of variables and environment variables. See `_get_internal_variables` in `src/gui/compile_handling.py` and the [commands and variables](commands_and_variables.md) document.

### Internal variables (compile command)

| Variable  | When available | Meaning |
|-----------|----------------|---------|
| `$name`   | Always         | Module name (Control tab). |
| `$file`   | 1-file mode    | Full path to the single generated file. |
| `$file1`  | 2-file mode    | Full path to the entity file. |
| `$file2`  | 2-file mode    | Full path to the architecture file. |
| `$git_root` | When under git | Repository root (same as in output path). |

Environment variables are also expanded (e.g. for the compiler executable). Use `${VAR:-default}` to provide a default if unset.

### Examples

**VHDL (2 files, GHDL):**

```text
ghdl -a $file1 $file2; ghdl -e $name; ghdl -r $name
```

**VHDL with compiler from environment:**

```text
$GHDL -a $file1 $file2; $GHDL -e $name; $GHDL -r $name
```

**Verilog (1 file, iverilog):**

```text
iverilog $file; a.out
```

or with explicit binary name:

```text
iverilog -o $name $file; vvp $name
```

**Using default for optional env var:**

```text
${IVERILOG:-iverilog} -o $name $file; vvp $name
```

---

## Summary

1. Track the `.hfe` file and the generated HDL output in git.
2. Turn **off** "Include timestamp in generated HDL files" so generated files only change when the design changes.
3. Set **"Directory for generated HDL"** using `$git_root` and/or `$hfe_file_dir` (and optionally env vars) so output lives in a fixed place relative to the repo or the design.
4. Use the **Compile command** with `$file` / `$file1` / `$file2` and `$name`; use environment variables for tool paths (e.g. `$GHDL`, `$IVERILOG`) if you need portability or multiple tool versions.

# Editor command, compile command, and variable expansion

This document describes how to configure and use the **editor command** (external editor) and the **compile command**, and how **variable expansion** works in the HDL-FSM-Editor.

---

## Overview

- **Editor command**: Opens the current text field in an external editor (e.g. Notepad++, VS Code). No variable expansion is applied.
- **Compile command**: Runs one or more shell commands to build/simulate your HDL (e.g. GHDL, iverilog). Each command is subject to **variable expansion** (internal variables and environment variables).
- **Variable expansion**: Bash-style `$VAR` / `${VAR}` substitution. Used **only** in the compile command.

---

## Editor command

### Where to configure

**Control** tab → **Edit command (executed by Ctrl+e)**.

### How it works

You enter the **executable path** and any **optional arguments**. When you trigger the command, the application:

1. Writes the current text field content to a temporary file.
2. Runs your command with that file path **appended** as the last argument.
3. Waits for the external editor to exit, then reads the file back and updates the editor.

No variable expansion is applied to the edit command; the app always appends the temp file path for you.

### Trigger

**Ctrl+e** when focus is in any editable text area (e.g. Interface/Internals package, generics, ports, declarations, state actions, conditions, comments).

### Example

```text
C:/Program Files/Notepad++/notepad++.exe -nosession -multiInst
```

Or for VS Code:

```text
// VS Code (installed for just the current user):
"C:\Users\<user>\AppData\Local\Programs\Microsoft VS Code\Code.exe" --wait

// VS Code (installed for all users):
"C:\Program Files\Microsoft VS Code\Code.exe" --wait
```


The application will run something like: `notepad++.exe -nosession -multiInst C:\Users\...\tmpXXXX.vhd` (the temp file path is added automatically).

---

## Compile command

### Where to configure

**Control** tab → **Compile command**.

### Trigger

- **Ctrl+p**, or
- Menu **Compile**.

### How it works

- The compile command string supports **operators** and **groups** (shell-like). Commands are run according to the operator between them:
  - **`;`** — run the next command regardless of the previous command’s success or failure.
  - **`&&`** — run the next command only if the previous command succeeded.
  - **`||`** — run the next command only if the previous command failed.
  - **`{ cmd1; cmd2 }`** — group: run `cmd1` then `cmd2`; the group’s success is the success of the last command. Use groups to chain multiple commands after `||`, e.g. `cmd1 || { echo "fallback"; cmd2 }`.
- **Quoted strings** (single or double quotes) are respected: `;`, `&&`, `||`, `{`, and `}` inside quotes do not split commands.
- If **Working directory** is set in the Control tab, all commands run with that directory as the current working directory.
- Output is shown in the **Compile Messages** tab; errors and warnings are highlighted.
- **Unbalanced braces** (`{` without `}` or extra `}`) cause an error and abort the compile.

Each command is parsed with shell-like rules (quoted segments with spaces stay one token), then **every token** is expanded using variable expansion (see below). Missing variables cause an error and abort the compile.

### File variables and generation mode

- **1-file mode** (Verilog / SystemVerilog): use **`$file`** for the single generated module file. Do **not** use `$file1` or `$file2`.
- **2-file mode** (VHDL): use **`$file1`** (entity) and **`$file2`** (architecture). Do **not** use `$file`.

Using the wrong variable for the current mode (e.g. `$file` in 2-file mode) produces a clear error message.

### Examples

**VHDL (2 files, GHDL):**

```text
ghdl -a $file1 $file2; ghdl -e $name; ghdl -r $name
```

**Verilog (1 file, iverilog):**

```text
iverilog -o $name $file; vvp $name
```

**SystemVerilog (1 file, iverilog):**

```text
iverilog -g2012 -o $name $file; vvp $name
```

**With operators and group (run fallback on failure):**

```text
ghdl -a $file1 $file2 && ghdl -e $name && ghdl -r $name || { echo "Build failed"; exit 1 }
```

---

## Variable expansion

Variable expansion is applied **only** in the **compile command** (to each token of each command). The editor command does **not** use variable expansion.

### Syntax

| Form | Description |
|------|-------------|
| `$VAR` | Replace with the value of `VAR`. |
| `${VAR}` | Same; braces allow characters that would otherwise end the name. |
| `${VAR:-default}` | If `VAR` is set, use its value; otherwise use `default`. |

Variable names must start with a letter or underscore and contain only letters, digits, and underscores.

### Where variables come from

- **Internal variables**: Provided by the application (`$name`, `$file`, `$file1`, `$file2` — see below). These **override** environment variables with the same name.
- **Environment variables**: Any `$VAR` or `${VAR}` that is not an internal variable is resolved from the process environment (e.g. `$HOME`, `$PATH`).

### Internal variables (compile command only)

| Variable | When available | Meaning |
|----------|----------------|---------|
| `$name` | Always | Module name (from **Module-Name** in the Control tab). |
| `$file` | 1-file mode only | Full path to the single generated file (e.g. `{Directory for generated HDL}/{Module-Name}.v` or `.sv`). |
| `$file1` | 2-file mode only | Full path to the entity file (e.g. `{path}/{Module-Name}_e.vhd`). |
| `$file2` | 2-file mode only | Full path to the architecture file (e.g. `{path}/{Module-Name}_fsm.vhd`). |

### Default values

Use **`${VAR:-default}`** to supply a value when `VAR` is unset. Example: `${OPT:-0}` expands to `0` if `OPT` is not set.

### Errors

If a variable is referenced but not set (and no default is given), the compile is aborted and an error dialog is shown. For file variables, the message explains the mismatch with the current mode (e.g. using `$file` in 2-file mode, or `$file1`/`$file2` in 1-file mode).

---

## Persistence

Both the **editor command** and the **compile command** are stored in the design file. When you save or open a design, these values are restored with the rest of the project settings.

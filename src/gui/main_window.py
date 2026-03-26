"""
This module contains all methods to create the main-window of the HDL-FSM-Editor.
"""

import re
import sys
import tkinter as tk
import urllib.error
import urllib.request
from pathlib import Path
from tkinter import ttk

import constants
import link_dictionary
import linting
import undo_handling
import write_data_creator
from actions import canvas_editing
from gui import menu_bar, notebook_top
from project_manager import project_manager


class MainWindow:
    """This class contains all methods to create the main-window of the HDL-FSM-Editor."""

    def __init__(self) -> None:
        """Build main window, notebook, menu bar, and set project_manager references."""
        self.window_height = 0
        self.root = tk.Tk()
        self.root.withdraw()  # Because it could be batch-mode because of "-generate_hdl" switch.
        self.root.columnconfigure(0, weight=1)  # The (only) column shall expand at window resize
        self.root.rowconfigure(1, weight=1)  # The row where the notebook is placed shall expand at window resize
        self.root.grid()
        self.root.bind("<Configure>", self._check_for_window_resize)
        project_manager.root = self.root
        self._configure_gui_style(self.root)
        project_manager.undo_handling_ref = undo_handling.UndoHandling()
        project_manager.link_dict_ref = link_dictionary.LinkDictionary()
        project_manager.highlight_dict_ref = linting.HighLightDict()
        project_manager.notebook = notebook_top.NotebookTop(row=1, column=0)
        project_manager.menu_bar_ref = menu_bar.MenuBar(row=0, column=0)
        project_manager.write_data_creator_ref = write_data_creator.WriteDataCreator(project_manager.state_radius)

        # Set the application icon
        try:
            icon_path = self._get_resource_path("hfe_icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
            else:
                print(f"Warning: Icon file not found at {icon_path}")
        except Exception as e:  # pylint: disable=broad-except
            print(f"Warning: Could not set application icon: {e}")

    def _check_for_window_resize(self, event) -> None:
        if event.widget == project_manager.root and self.window_height != event.height:
            if self.window_height != 0:  # equal 0 at application start, so ignore first event
                self.root.update_idletasks()  # update geometry information of all widgets
                project_manager.tab_interface_ref.adjust_sash_positions()
                project_manager.tab_internals_ref.adjust_sash_positions()
            self.window_height = event.height

    def set_word_boundaries(self) -> None:
        """Configure Tcl word boundaries so double-click selects identifiers (e.g. signal names)."""
        # this first statement triggers tcl to autoload the library
        # that defines the variables we want to override.
        project_manager.root.tk.call("tcl_wordBreakAfter", "", 0)
        # this defines what tcl considers to be a "word". For more
        # information see http://www.tcl.tk/man/tcl8.5/TclCmd/library.htm#M19
        project_manager.root.tk.call("set", "tcl_wordchars", "[a-zA-Z0-9_]")
        project_manager.root.tk.call("set", "tcl_nonwordchars", "[^a-zA-Z0-9_]")

    def check_version(self) -> str:
        """Fetch website and print whether a newer version is available."""
        try:
            print("Checking for a newer version ...")
            with urllib.request.urlopen("http://www.hdl-fsm-editor.de/index.php") as source:
                website_source = str(source.read())
            version_start = website_source.find("Version")
            new_version = website_source[version_start : version_start + 24]
            end_index = new_version.find("(")
            new_version = new_version[:end_index]
            new_version = re.sub(" ", "", new_version)
            if new_version != "Version" + constants.VERSION:
                check_version_result = (
                    "Please update to the new version of HDL-FSM-Editor available at http://www.hdl-fsm-editor.de"
                )
            else:
                check_version_result = "Your version of HDL-FSM-Editor is up to date."
        except urllib.error.URLError:
            check_version_result = "HDL-FSM-Editor version could not be checked, as you are offline."
        print(check_version_result)
        return check_version_result

    def read_message(self, check_version_result) -> None:
        """Fetch message from website and copy it into the log tab."""
        try:
            with urllib.request.urlopen("http://www.hdl-fsm-editor.de/message.txt") as source:
                message = source.read()
            _read_message_result = message.decode()
        except urllib.error.URLError:
            _read_message_result = "No message was found."
        except ConnectionRefusedError:
            _read_message_result = ""
        print(_read_message_result)
        self._copy_message_into_log_tab(check_version_result, _read_message_result)

    def view_all_after_window_is_built(self) -> None:
        """Fit all canvas content in view and unbind Visibility (one-shot)."""
        canvas_editing.view_all()
        project_manager.canvas.unbind("<Visibility>")

    def _configure_gui_style(self, root) -> None:
        # Configure application styling
        style = ttk.Style(root)
        style.theme_use("default")
        # style.theme_use('clam')
        # style.theme_use('winnative')
        # style.theme_use('alt')
        # style.theme_use('classic')
        # style.theme_use('vista')
        # style.theme_use('xpnative')
        style.configure("Window.TFrame", background="PaleTurquoise2")
        style.configure("Window.TLabel", background="PaleTurquoise2")
        style.configure("WindowSelected.TFrame", background="PaleTurquoise3")
        style.configure("WindowSelected.TLabel", background="PaleTurquoise3")
        style.configure("Window.TMenubutton")
        style.configure("StateActionsWindow.TFrame", background="cyan2")
        style.configure("StateActionsWindow.TLabel", background="cyan2")
        style.configure("StateActionsWindowSelected.TFrame", background="turquoise1")
        style.configure("StateActionsWindowSelected.TLabel", background="turquoise1")
        style.configure("GlobalActionsWindow.TFrame", background="PaleGreen2")
        style.configure("GlobalActionsWindow.TLabel", background="PaleGreen2")
        style.configure("GlobalActionsWindowSelected.TFrame", background="lawn green")
        style.configure("GlobalActionsWindowSelected.TLabel", background="lawn green")
        style.configure("DefaultStateActions.TButton", background="cyan2")
        style.configure("GlobalActionsClocked.TButton", background="PaleGreen2")
        style.configure("GlobalActionsCombinatorial.TButton", background="PaleGreen2")
        style.configure("NewState.TButton", background="SkyBlue1")
        style.configure("NewTransition.TButton", background="deep sky blue")
        style.configure("NewConnector.TButton", background="orchid1")
        style.configure("ResetEntry.TButton", background="IndianRed1")
        style.configure("View.TButton", background="lemon chiffon")
        style.configure("Undo.TButton")
        style.configure("Redo.TButton")
        style.configure("Find.TButton")
        style.configure("Path.TButton")

    def _get_resource_path(self, resource_name: str) -> Path:
        """Get the path to a resource file, handling both development and PyInstaller environments."""
        base_path = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).parent.parent

        return base_path / "rsc" / resource_name

    def _copy_message_into_log_tab(self, check_version_result, _read_message_result) -> None:
        project_manager.tab_log_ref.log_frame_text.config(state=tk.NORMAL)
        project_manager.tab_log_ref.log_frame_text.insert(
            "1.0", constants.HEADER_STRING + "\n" + check_version_result + "\n" + _read_message_result + "\n"
        )
        project_manager.tab_log_ref.log_frame_text.config(state=tk.DISABLED)

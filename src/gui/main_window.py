"""
This module contains all methods to create the main-window of the HDL-FSM-Editor.
"""

import http
import json
import re
import sys
import tkinter as tk
import urllib.error
import urllib.request
from collections import ChainMap

# from copy import deepcopy
from pathlib import Path

import constants
import link_dictionary
import linting
import undo_handling
import write_data_creator
from actions import canvas_editing
from constants import GuiTab
from elements import (
    condition_action,
    global_actions_clocked,
    global_actions_combinatorial,
    state_action,
    state_actions_default,
    state_comment,
)
from gui import menu_bar, notebook_top, style_admin
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
        project_manager.main_window = self
        # Create background objects:
        project_manager.undo_handling_ref = undo_handling.UndoHandling()
        project_manager.link_dict_ref = link_dictionary.LinkDictionary()
        project_manager.highlight_dict_ref = linting.HighLightDict()
        project_manager.write_data_creator_ref = write_data_creator.WriteDataCreator(project_manager.state_radius)
        # Fill root with the GUI:
        project_manager.style_admin_ref = style_admin.StyleAdmin(self.root)
        project_manager.menu_bar_ref = menu_bar.MenuBar(row=0, column=0)
        project_manager.notebook = notebook_top.NotebookTop(row=1, column=0)
        # Create a combined reference dictionary for all canvas window items:
        project_manager.canvas_windows_ref_dict = ChainMap(
            condition_action.ConditionAction.ref_dict,
            global_actions_clocked.GlobalActionsClocked.ref_dict,
            global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict,
            state_action.StateAction.ref_dict,
            state_actions_default.StateActionsDefault.ref_dict,
            state_comment.StateComment.ref_dict,
        )
        self.configure_message = ""
        working_directory = self._configure_hfe()
        project_manager.tab_control_ref.working_directory_value.set(working_directory)
        self._set_word_boundaries()
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
        if event.widget == self.root and self.window_height != event.height:
            if self.window_height != 0:  # equal 0 at application start, so ignore first event
                self._move_sashes_after_window_resize()
            self.window_height = event.height

    def _move_sashes_after_window_resize(self):
        active_tab = project_manager.notebook.get_active_tab()
        project_manager.notebook.show_tab(GuiTab.INTERFACE)
        self.root.update_idletasks()  # update geometry information of all widgets
        project_manager.tab_interface_ref.adjust_sash_positions()
        project_manager.notebook.show_tab(GuiTab.INTERNALS)
        self.root.update_idletasks()  # update geometry information of all widgets
        project_manager.tab_internals_ref.adjust_sash_positions()
        project_manager.notebook.show_tab(active_tab)

    def _configure_hfe(self):
        try:
            with open(Path.home() / ".hdl-fsm-editor.rc", encoding="utf-8") as fileobject:
                data = fileobject.read()
            config_dict = json.loads(data)
            self.configure_message += "Configuration file " + str(Path.home()) + "/.hdl-fsm-editor.rc was read."
            work_dir = config_dict["working_directory"]
            project_manager.menu_bar_ref.prefs_menu.entryconfig(0, label=config_dict["graphical_mode"])
            # Now the menu reflects the graphical mode specified in the configuration file which is
            # wrong as it should reflect not the actual mode but the alternative mode.
            # But the method switch_mode() reads this wrong menu entry and interpretes it correctly as a
            # command to activate this mode. As at the end the method switch_mode() as always changes the
            # menu entry to the alternative mode, everything is correct at the end:
            project_manager.menu_bar_ref.switch_mode()
        except Exception:  # pylint: disable=broad-except
            self.configure_message += "Configuration file " + str(Path.home()) + "/.hdl-fsm-editor.rc was not found."
            work_dir = ""
        print(self.configure_message)
        return work_dir

    def _set_word_boundaries(self) -> None:
        """Configure Tcl word boundaries so double-click selects identifiers (e.g. signal names)."""
        # this first statement triggers tcl to autoload the library
        # that defines the variables we want to override.
        project_manager.root.tk.call("tcl_wordBreakAfter", "", 0)
        # this defines what tcl considers to be a "word". For more
        # information see http://www.tcl.tk/man/tcl8.5/TclCmd/library.htm#M19
        project_manager.root.tk.call("set", "tcl_wordchars", "[a-zA-Z0-9_:<=]")
        project_manager.root.tk.call("set", "tcl_nonwordchars", "[^a-zA-Z0-9_:<=]")

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
        except http.client.RemoteDisconnected:
            check_version_result = "Remote end closed connection without response, when checking the version."
        print(check_version_result)
        return check_version_result

    def put_header_into_log_tab(self, check_version_result) -> None:
        """Fetch message from website and copy it into the log tab."""
        try:
            with urllib.request.urlopen("http://www.hdl-fsm-editor.de/message.txt") as source:
                message = source.read()
            _read_message_result = message.decode() + "\n"
        except urllib.error.URLError:
            _read_message_result = "No message was found.\n"
        except http.client.RemoteDisconnected:
            _read_message_result = "Remote end closed connection without response when reading the user message."
        except ConnectionRefusedError:
            _read_message_result = ""
        print(_read_message_result)
        complete_header = (
            constants.HEADER_STRING
            + "\n"
            + check_version_result
            + "\n"
            + _read_message_result
            + self.configure_message
            + "\n"
        )
        self._put_startup_header_into_log_tab(complete_header)

    def view_all_after_window_is_built(self) -> None:
        """Fit all canvas content in view and unbind Visibility (one-shot).
        Needed when the application is launched by a command line with file argument."""
        canvas_editing.view_all()
        project_manager.canvas.unbind("<Visibility>")

    def _get_resource_path(self, resource_name: str) -> Path:
        """Get the path to a resource file, handling both development and PyInstaller environments."""
        base_path = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).parent.parent

        return base_path / "rsc" / resource_name

    def _put_startup_header_into_log_tab(self, complete_header) -> None:
        project_manager.tab_log_ref.log_frame_text.config(state=tk.NORMAL)
        project_manager.tab_log_ref.log_frame_text.insert("1.0", complete_header)
        project_manager.tab_log_ref.log_frame_text.config(state=tk.DISABLED)

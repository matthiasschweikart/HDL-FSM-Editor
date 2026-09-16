"""
This module contains all methods to create the main-window of the HDL-FSM-Editor.
"""

import http
import re
import sys
import tkinter as tk
import urllib.error
import urllib.request
from collections import ChainMap

# from copy import deepcopy
from pathlib import Path
from tkinter import ttk

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
        project_manager.main_window = self
        self._configure_gui_style(self.root)
        # Create background objects:
        project_manager.undo_handling_ref = undo_handling.UndoHandling()
        project_manager.link_dict_ref = link_dictionary.LinkDictionary()
        project_manager.highlight_dict_ref = linting.HighLightDict()
        # Build the GUI:
        project_manager.menu_bar_ref = menu_bar.MenuBar(row=0, column=0)
        project_manager.notebook = notebook_top.NotebookTop(row=1, column=0)
        project_manager.write_data_creator_ref = write_data_creator.WriteDataCreator(project_manager.state_radius)
        project_manager.canvas_windows_ref_dict = ChainMap(
            condition_action.ConditionAction.ref_dict,
            global_actions_clocked.GlobalActionsClocked.ref_dict,
            global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict,
            state_action.StateAction.ref_dict,
            state_actions_default.StateActionsDefault.ref_dict,
            state_comment.StateComment.ref_dict,
        )

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

    def set_word_boundaries(self) -> None:
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

    def read_message(self, check_version_result) -> None:
        """Fetch message from website and copy it into the log tab."""
        try:
            with urllib.request.urlopen("http://www.hdl-fsm-editor.de/message.txt") as source:
                message = source.read()
            _read_message_result = message.decode()
        except urllib.error.URLError:
            _read_message_result = "No message was found."
        except http.client.RemoteDisconnected:
            _read_message_result = "Remote end closed connection without response when reading the user message."
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
        # print("_configure_gui_style: start config TButton =", style.configure("TButton"))
        # print("_configure_gui_style: start map    TButton =", style.map("TButton"))

        # style.theme_use('clam')
        # style.theme_use('winnative')
        # style.theme_use('alt')
        # style.theme_use('classic')
        # style.theme_use('vista')
        # style.theme_use('xpnative')
        style.configure("Window.TFrame", foreground="black", background="PaleTurquoise2")
        style.configure("Window.TLabel", foreground="black", background="PaleTurquoise2")
        style.configure("WindowSelected.TFrame", foreground="black", background="PaleTurquoise3")
        style.configure("WindowSelected.TLabel", foreground="black", background="PaleTurquoise3")
        style.configure("Window.TMenubutton")
        style.configure("StateActionsWindow.TFrame", foreground="black", background="cyan2")
        style.configure("StateActionsWindow.TLabel", foreground="black", background="cyan2")
        style.configure("StateActionsWindowSelected.TFrame", foreground="black", background="turquoise1")
        style.configure("StateActionsWindowSelected.TLabel", background="turquoise1")
        style.configure("GlobalActionsWindow.TFrame", foreground="black", background="PaleGreen2")
        style.configure("GlobalActionsWindow.TLabel", foreground="black", background="PaleGreen2")
        style.configure("GlobalActionsWindowSelected.TFrame", foreground="black", background="lawn green")
        style.configure("GlobalActionsWindowSelected.TLabel", foreground="black", background="lawn green")

        style.configure("DefaultStateActions.TButton", foreground="black", background="cyan2")
        # Anders als behauptet, kann man so nicht auf den Default zurück.
        # Anscheinend gibt es im Default keine Tupel, so dass hier leere Listen erzeugt werden,
        # die ein zurück auf den default verhindern.
        # style.map(
        #     "DefaultStateActions.TButton",
        #     foreground=style.map("TButton", "foreground"),
        #     background=style.map("TButton", "background"),
        #     font=style.map("TButton", "font"),
        # )

        style.configure("GlobalActionsClocked.TButton", foreground="black", background="PaleGreen2")
        style.configure("GlobalActionsCombinatorial.TButton", foreground="black", background="PaleGreen2")
        style.configure("NewState.TButton", foreground="black", background="SkyBlue1")
        style.configure("NewTransition.TButton", foreground="black", background="deep sky blue")
        style.configure("NewConnector.TButton", foreground="black", background="orchid1")
        style.configure("ResetEntry.TButton", foreground="black", background="IndianRed1")
        style.configure("View.TButton", foreground="black", background="lemon chiffon")
        style.configure("Undo.TButton")
        style.configure("Redo.TButton")
        style.configure("Find.TButton")
        style.configure("Path.TButton")
        # print("borderwidth in normal mode =", style.lookup("NewTransition.TButton", "borderwidth"))
        # print("style map  =", style.map("DefaultStateActions.TButton", "foreground"))
        # print("style layout  =", style.layout("DefaultStateActions.TButton"))
        # print("style element options  =", style.element_options("DefaultStateActions.TButton"))

        # style map  = {'foreground': [('active', 'cyan2'), ('disabled', 'cyan2')],
        # 'font': [('active', 'TkDefaultFont 10 normal'), ('disabled', 'TkDefaultFont 10 italic')],
        # 'background': [('active', 'blue'), ('disabled', 'black')]}

    def reset_button_style_to_theme_default(self, style_name: str) -> None:
        """Reset a custom button style to the current theme's TButton defaults."""
        style = ttk.Style(project_manager.root)
        # default_config = deepcopy(style.configure("TButton"))
        default_config = style.configure("TButton")
        print("reset: default config TButton =", default_config)
        current_config = style.configure(style_name)
        print(f"reset: current_config  {style_name} = ", current_config)
        for option in current_config:
            default_config.setdefault(option, "")
        style.configure(style_name, **default_config)
        print(f"reset: current_config  {style_name} = ", style.configure(style_name))

        # default_map = deepcopy(style.map("TButton"))
        default_map = style.map("TButton")
        print("reset: current_map  TButton = ", default_map)
        current_map = style.map(style_name)
        print(f"reset: current_map  {style_name} = ", current_map)
        # map_values = {option: deepcopy(values) for option, values in default_map.items()}
        map_values = {option: values for option, values in default_map.items()}
        for option in current_map:
            map_values.setdefault(option, [])
        style.map(style_name, **map_values)
        print(f"reset: current_map  {style_name} = ", style.map(style_name))

        # style.layout(style_name, deepcopy(style.layout("TButton")))
        # style.layout(style_name, style.layout("TButton"))

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

    def switch_to_normal_mode(self):
        project_manager.menu_bar_ref.switch_menu_entry_to("Dark Mode")
        self.reset_button_style_to_theme_default("DefaultStateActions.TButton")
        self._configure_gui_style(project_manager.root)
        return

    def switch_to_dark_mode(self):
        project_manager.menu_bar_ref.switch_menu_entry_to("Normal Mode")

        style = ttk.Style(project_manager.root)
        style.theme_use("default")
        # borderwidth ist per default 1, kann so bleiben        style = ttk.Style(project_manager.root)

        style.configure("DefaultStateActions.TButton", foreground="cyan2", background="black")
        style.map(
            "DefaultStateActions.TButton",
            # background=[("GlobalActionsClockedpressed", "red"), ("active", "blue"), ("disabled", "grey")],
            # foreground=[("pressed", "white"), ("active", "white")],
            font=[("active", ("TkDefaultFont", 10, "normal")), ("disabled", ("TkDefaultFont", 10, "italic"))],
            background=[("active", "blue"), ("disabled", "black")],
            foreground=[("active", "cyan2"), ("disabled", "cyan2")],
        )
        style.configure("GlobalActionsClocked.TButton", foreground="PaleGreen2", background="black")
        style.configure("GlobalActionsCombinatorial.TButton", foreground="PaleGreen2", background="black")
        style.configure("NewState.TButton", foreground="SkyBlue1", background="black")
        style.configure("NewTransition.TButton", foreground="deep sky blue", background="black")
        # print("bg   =", style.lookup("NewTransition.TButton", "background"))
        # print("fg   =", style.lookup("NewTransition.TButton", "foreground"))
        # print("bordercolor =", style.lookup("NewTransition.TButton", "bordercolor"))
        # print("lightcolor  =", style.lookup("NewTransition.TButton", "lightcolor"))
        # print("darkcolor   =", style.lookup("NewTransition.TButton", "darkcolor"))
        # print("borderwidth in dark mode =", style.lookup("NewTransition.TButton", "borderwidth"))
        style.configure("NewConnector.TButton", foreground="orchid1", background="black")
        style.configure("ResetEntry.TButton", foreground="IndianRed1", background="black")
        style.configure("View.TButton", foreground="lemon chiffon", background="black")
        style.configure("Undo.TButton", foreground="light gray", background="black")
        style.configure("Redo.TButton", foreground="light gray", background="black")
        # dark_theme = {
        #     "NewState.TButton": {
        #         "configure": {
        #             "foreground": "SkyBlue1",
        #             "background": "black",
        #             "bordercolor": "green",
        #             "lightcolor": "white",
        #             "darkcolor": "red",
        #             "borderwidth": "10",
        #         }
        #     },
        #     "NewTransition.TButton": {"configure": {"foreground": "deep sky blue", "background": "black"}},
        #     "NewConnector.TButton": {"configure": {"foreground": "orchid1", "background": "black"}},
        #     "ResetEntry.TButton": {"configure": {"foreground": "IndianRed1", "background": "black"}},
        #     "View.TButton": {"configure": {"foreground": "lemon chiffon", "background": "black"}},
        #     "Undo.TButton": {"configure": {"foreground": "light gray", "background": "black"}},
        #     "Redo.TButton": {"configure": {"foreground": "light gray", "background": "black"}},
        # }

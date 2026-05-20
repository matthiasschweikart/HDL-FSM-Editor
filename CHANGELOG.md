# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## Added
## Changed
## Deprecated
## Removed
## Fixed
## Security

## [6.4]
## Added
- When moving a state, now state-comment, state-action and loopback transition are moved together with the state.
- Ctrl-x and Ctrl-c/v now work at whole lines if nothing is selected.
- Sash positions in Interface and Internals tab are now adapted automatically when the window is resized.
- When showing find-hits, now the diagram is zoomed properly.
- The transition menue entry "straighten shape" now does not modify loopback transition anymore.
- Following links in "generated HDL" and in "messages" tab now does not need the Ctrl-key anymore.
- Following links in "generated HDL" and in "messages" now only works at underlined characters.
- The links no longer work either over the line number or beyond the line end.
- At compile now the "messages" tab becomes visible faster.
- Highlighting works faster now.
- Highlighting a big number of lines in the "generated HDL" tab does not freeze the GUI anymore.
## Changed
## Deprecated
## Removed
## Fixed
- At zooming by Ctrl-key and mouse-wheel the diagram "jumped". Fixed.
- Changing the shape of small loopback transitions did not work well. Fixed.
- In a newly loaded design straight transitions did sometimes not snap exactly to the grid. Fixed.
- Sometimes the HFE window was resized, when Ctrl-g or Ctrl-p were pressed. Fixed.
- At loading a design straight transitions sometimes did snap to the grid. Fixed.
- Help menue entry did not work under Linux. Fixed.
- Disconnecting the transition starting at reset entry caused a fatal. Fixed.
- Sensitivity checks did not ignore HDL code in comments. Fixed.
- Sensitivity check did not work correctly if not closed brackets were in the HDL. Fixed.
- An empty additional sources field caused problems at linting. Fixed.
- A not existing additional sources file caused a exception at linting. Fixed.
- Moving a state above another state disconnected the connected transitions. Fixed.
## Security

## [6.3]
## Added
## Changed
## Deprecated
## Removed
## Fixed
- If not the entire diagram is shown, another part of the diagram becomes visible when it is saved.
- Saving the diagram with an empty module name field caused an exception.
- VHDL keywords "true" and "false" were not highlighted.
- "Find next" dialog could be placed half outside the screen.
- Pressing the Ctrl key alone caused some highlight flickering.
## Security

## [6.2]
## Added
- Added new keyboard shortcuts for all text editing actions.
- Added a help-menu entry for keyboard shortcuts.
- Added a help-menu entry for working with selections.
- Scrolling speed now depends on the zoom factor.
- Added "Ctrl-G" shortcut to jump to a specific line number in the "Generated HDL" tab.
- Added button "Find in HDL".
- Added intelligent sash-moving in "Internals"- and "Interface"-tab (entry windows are minimized at window increase).
- Scrolling horizontal with the mouse wheel is now possible by pressing the Shift key at the same time.
- Loopback-transitions are now moved completely, when the connected state is moved.
## Changed
- If VHDL is generated into 2 files, now the background in "Generated HDL"-tab is colored.
- In batch mode now "--no-version-check" and "--no-message" are active per default.
- The sensitivity list of the "state action" process now wraps, if it is longer than 80 characters.
- The "Find next" dialog does not block the main window anymore.
## Deprecated
## Removed
## Fixed
- Moving the mouse cursor into a condition&action block caused a small moving of the box. Fixed.
- Up/Down scrolling of the diagram with the mouse wheel did not work if the cursor was in a text box. Fixed.
- An aborted save-as did change the stored filename. Fixed.
- Using a VHDL variable as case-selector caused disturbed highlighting. Fixed.
- The link between generated HDL and module-name and clock-signal-name in "Control"-tab did not work since 5.0. Fixed.
- Sometimes the links from "Compile Message" tab to "Generated HDL" tab did not work (because of '/' and '\' in file paths). Fixed.
- Zooming to find-hits did sometimes not work. Fixed.
## Security

## [6.1]
## Added
## Changed
- Small feedback transitions now can be better modified by the mouse-pointer.
## Deprecated
## Removed
## Fixed
- A second accidental mouse click at finishing a transition-end-point moving caused strange moving of other items.
- Wrong HDL could be generated, if all leaving transitions at a connector had conditions.
- Transition adding did not work when the design was zoomed until the grid was deactivated.
- When VHDL record elements are read, sometimes incomplete sensitivity lists were generated in VHDL.
## Security

## [6.0]
## Added
## Changed
- Refactoring: most global variables are removed.
- Refactoring: several new classes were introduced.
- Refactoring: new folder "elements" was added.
- Refactoring: several files were renamed.
- Linting is now only updated after some inactivity for better performance.
## Deprecated
## Removed
## Fixed
## Security

## [5.9]
## Added
## Changed
- Refactoring
## Deprecated
## Removed
## Fixed
- Deleting an object in the diagram did sometimes not work or did delete the wrong object.
- At storing in afile sometimes an exception happened (caused by rounding of coordinates.)
## Security

## [5.8]
## Added
- Highlighting when VHDL attributes are used is improved.
- Find&Replace now works also in the Control-tab.
## Changed
- Scrolling and zooming does no longer modify the data written to the hfe-file, which means the content of the hfe-file will only change at "real" design changes.
- The entry boxes of the Control-tab expand now together with the window.
- The radio button for the number of files has been moved from the right-hand border to the middle
- VHDL-function calls are not highlighted red anymore.
- Refactoring: Find&Replace is now moved in its own class.
- Refactoring of linting.py.
## Deprecated
## Removed
## Fixed
- At Linux Mint at leaving a condition&action window, the condition&action block was not shrinked anymore.
- At slow Linux Mint systems the condition&action block, and all other block types too, jumped at moving.
## Security

## [5.7]
## Added
- Support of VHDL procedures for linting
- Support of several signal declarations in 1 line
- Linting for user defined processes in "Global Actions Combinatorial"
- At reading from a hfe-file now a existing ".tmp" file is always removed.
## Changed
- In batch mode the warning about a wrong state order is now printed at STDOUT and not in a pop up dialog.
- In batch mode warnings during file read are now printed at STDOUT instead in pop up dialogs.
- In batch mode the warning about a wrong state order is now printed at STDOUT and not in a pop up dialog.
- The timestamp checkbox was moved into the "Select for generation" line.
## Deprecated
## Removed
## Fixed
- Delete state and delete state-action did not work since version 5.5
- Signal names containing the string "end_" where sometimes highlighted in a wrong way.
- After changing an text by an external editor and saving the design, leaving a block with the mouse pointer signaled "design has changed".
- Linting highlighted 'x' in expressions like x"12AB" red.
- A start from command line with file-parameter does not activate script-mode anymore.
- Change detection in "global actions combinatorial" signaled design change too often
## Security

## [5.6]
## Added
- When the project file is read/written now the cursor changes its shape (visible only if the file operation is slow).
- A warning pop up dialog informs the user, when a state is placed too near to another object.
## Changed
- The call of the method design_has_changed was moved at move_handling_finish and added in move_handling_canvas_item/window.
- Improved robustness when moving transitions (avoiding null vectors).
## Deprecated
## Removed
- Removed second implementation of priority box drawing from undo_handling.
## Fixed
- When a curved transition is moved, sometimes the transition shape gets strange at pick up.
- At reading a design sometimes an exception regarding variable "trans_id" happened.
- When the "generated HDL" was opened sometimes no HDL was loaded.
## Security

## [5.5]
## Added
- The state menu can now also be opened over a state name.
## Changed
## Deprecated
## Removed
- Removed useless highlighting at entering a line to a state-action/comment box.
- Removed unused parameter move_to_grid of method move_to for canvas-windows.
- Removed second implementation of transition drawing from file_handling.
- Removed second implementation of transition priority drawing from file_handling.
## Fixed
- Inserting a new transition activated the message box "corrupt database" with no reason.
- The senseless attempt to remove the line to a state-action/comment box caused an exception.
- After an Undo operation the new move method did not work for states anymore.
- The end point of a connection line of a state action/comment jumped sometimes to the grid.
## Security

## [5.4]
## Added
## Changed
## Deprecated
## Removed
## Fixed
- A fix the for new move method was implemented
## Security

## [5.3]
## Added
- A title for the "select HDL directory" dialog.
## Changed
- Picking up objects for moving was sometimes kind of hard, now it works easy and as expected.
## Deprecated
## Removed
## Fixed
- Moving the cursor into any action or comment block (without any code change) could set the design state to "modified" .
- Names containing the string "warning" or "error" were highlighted red in the "Compile Message" tab.
- Sometimes states may be shrinked during moving.
## Security

## [5.2]
## Added
## Changed
## Deprecated
## Removed
## Fixed
- Creating HDL in batch mode did not work because of an exception.
- The number of linter warnings was reduced by refactoring.
## Security

## [5.1] - 04.08.2025
## Added
- Added the "Additional sources" entry field to the Control-tab. Will be used only by HDL-SCHEM-Editor.
- The STDOUT messages at startup are now also copied into the "Compile messages" tab.
- Linting (highlighting of never read or never written signals) now can handle VHDL-records.
## Changed
## Deprecated
## Removed
## Fixed
- When a Condition&Action box was entered, sometimes the box switched permanently between its small and big size.
- When the HDL-tab was updated, sometimes the old HDL was not removed.
## Security

## [5.0] - 01.08.2025

## Added
- The time-stamp in generated HDL can now be turned off to simplify the handling with version control.
- Additional FSM examples from http://www.hdl-fsm-editor.de/ - Designs

## Changed
- Updated command line arguments to use dashes.
- The project layout was restructured.
- Improve "project unsaved dialog" when closing the application.

## Deprecated
## Removed
## Fixed
## Security

## [4.12] - 27.07.2025

### Added
- If the first line of a state comment only contains an integer, this value will determine the order of the states in the generated HDL.

### Changed
- Using shortcuts with captitalised characters now creates a warning message.
- In VHDL 2-files mode now not only the entity-file is checked for updates (caused by another instance of HFE) but also the architecture-file.

### Fixed
- When inserting a transition was aborted by "Escape", then moving the state where the transition started, caused an exception. Fixed.
- "Undo" after deleting a textbox (like "Global Actions") created sometimes graphical artefacts. Fixed.
- The "New" button cleared the canvas but did not activate the grid. Fixed.
- Since version 4.11 the Verilog in the generated-HDL tab was completely colored as comment. Fixed.
- Control-s and Control-g inside any modified text box saved the design, but moving the cursor outside the box, did set the status of the design back to "modified". Fixed.

## [4.11] - 27.03.2025

### Added
- The new solution highlights the border of the box, when the mousepointer has reached a position, which allows to move the box.
- Now at HDL generation it is checked if a transition is hidden, because a transition with higher priority has no condition.
- VHDL block comments are now highlighted blue.
- A search for an empty string is now rejected with a message.
- Regular expressions in search- or replace-string are now always ignored.
- When the "generated HDL" tab is opened, it is now checked if newer HDL is available at disk.

### Changed
- The solution for moving textboxes by picking them inside (not at the border) introduced in Version 3.8 showed poor graphical behaviour under Linux Mint (boxes hopping around uncontrollable). This solution also prevented text selecting by the mouse inside the box, because the box was moved instead. Therefore a new solution was implemented, which behaves well under Linux and allows selecting text again.

### Fixed
- The sensitivity list of the state-action-process sometimes was incomplete. Fixed.
- If a state had a comment, it could not be renamed. Fixed.
- If a state had a comment and was deleted, the comment remained as a relic and had to be deleted separately. Fixed.
- A VHDL block comment in a port or generic list prevents correct linting-highlighting on the following identifier. Fixed.
- A condition or action which contained only a '.' caused an infinite loop at syntax highlighting. Fixed.
- When HDL-SCHEM-Editor starts HDL-FSM-Editor for HDL generation under Linux, the message "There are unsaved changes.." popped up without any reason. Fixed.
- At opening a new design the new design was marked with '*' as changed. Fixed.
- If a state name has been modified into a significantly longer one and outgoing transitions had a priority rectangle, then the new statename was sometimes not accepted. Fixed.
- At deleting a transition a wrong tag-plausibility warning was sometimes raised. Fixed.
- Editing transition priorities did not work after an Undo. Fixed.

## [4.10] - 25.02.2025

### Fixed
- A bug prevented the new backup function from working. Fixed.
- Syntax highlighting did not work correctly, when functions were declared in the "Internals"-tab. Fixed.
- Syntax highlighting did not work correctly, when '+' or '-' characters were not surrounded by blanks. Fixed.
- Again sometimes the sash positions in Interface/Internals-tab made the text fields unvisible. Fixed.

### Changed
- The VHDL type definition for the state signal now is broken into several lines, when more than 10 states exist.

## [4.9] - 21.02.2025

### Added
- HDL-FSM-Editor now creates a backup file during editing, where all changes are stored and from which the design can be automatically recovered after a crash.
- The states are now a little bit bigger to avoid overlapping of state name and state circle.
- A double click at a word now does not select the following ';' or ','.
- The "compile through hierarchy" command now inserts a "Finished"-line into the message tab.
- Added missing VHDL keywords for syntax highlighting.

### Fixed
- The values "true" and "false" were highlighted red as a "not written signal". Fixed.
- Highlighting of signal names did not work correctly if VHDL attributes were used. Fixed.
- Highlighting of signal names sometimes did not work correctly after find&replace. Fixed.
- Since version 4.5 sometimes the messages in the messages tab were highlighted in the wrong color. Fixed.
- When HDL-SCHEM-Editor opened a HDL-FSM-Editor VHDL design, "library ieee;..." was added each time to the Interface-tab. Fixed.

## [4.8] - 12.02.2025

### Added
- The tag plausibility is now not only checked at HDL generation but also at file write.

### Fixed
- There was a bug in HDL generation which caused missing transition actions in HDL. The problem showed only at complicated structures of transitions and connectors between 3 (or more) states. Fixed.
- The grid lines were not shown by the command "view area". Fixed.
- The grid lines were not redrawn after a shift by Control-Button-1. Fixed.
- "view all" sometimes did not use the full canvas area. Fixed.
- The moving of curved transitions with 3 or 4 points now works better.
- The highlighting of signal names did not always work as expected during find&replace. Fixed.
- Sometimes a priority rectangle was shown when only 1 transition leaves a connector. Fixed.
- Sometimes the sash positions in Interface/Internals-tab made the text fields unvisible. Fixed.
- When the size of a state was changed, the connected transitions were shown dashed afterwards if the grid was visible. Fixed.

### Changed
- The grid lines are not written in the hfe-file anymore.
- During syntax highlighting no "bold" characters are used anymore, in order to prevent the text from getting shifted out of its textbox (lines with bold characters are higher).

## [4.7] - 05.02.2025

### Added
- An undo of a Find&Replace-Action now also un-does changes in Interface- and Internals-Tab.
- Short-cuts for Undo/Redo are now shown at top of the text-widgets in Interface- and Internals-Tab.
- The Undo/Redo buttons in the "Diagram"-tab are now enabled/disabled depending on the content of the undo stack.
- Now the Find&Replace is able to replace a string by an empty string.

### Fixed
- After start of HDL-FSM-Editor per command line with file-parameter the opened design was not shown in "view all" view. Fixed.
- At start of HDL-FSM-Editor per command line with file-parameter now the filename-extension is checked (must be .hfe).
- If actual HDL was found to copy into "generated HDL"-tab at loading a design, then new generated HDL (identical to the actual one besides the time-stamp) was written into the "generated HDL"-tab. Fixed.
- The error message for a not existing folder for the generated HDL was changed to get more information.

### Changed
- Generated HDL now includes only a comment with its file-name and not with its complete path-name anymore.

## [4.6] - 18.12.2024

### Fixed
- The batch HDL-generation (hdl_fsm_editor -generate_hdl file.hfe, used by HDL-SCHEM-Editor) did crash for some designs. Fixed.

## [4.5] - 16.12.2024

### Added
- A grid is now displayed in the "Diagram"-tab after start up.
- The grid can be hidden by the right mouse button menu in the "Diagram"-tab.
- The background color of the "Diagram"-tab can now also be changed by the right mouse button menu in the "Diagram"-tab.
- The size of the entry windows in the "Interface" and "Internals"-tab can now be adapted by moving the separating bars.
- The size of the entry windows in the "Interface" and "Internals"-tab is now stored in the saved file.
- The search per "Find"-button now also searches in state-comments.
- There is now a "Find & Replace" button available.
- After "Find" or "Find & Replace" now the number of hits/replacements is displayed.
- In the "Compile Messages"-tab now STD_ERR and STD_OUT are not separated anymore.
- In the "Compile Messages"-tab now warnings and errors are colored red.
- In the "Compile Messages"-tab now VHDL report message are displayed green.
- The "Compile Messages"-tab now has a "Clear"-button.
- When HDL generation is started and not saved changes exist, then first the design is automatically saved.
- When HDL-FSM-Editor is started, then the IEEE.std_logic_1164-package is automatically added in the "Interface"-tab.

### Fixed
- Sometimes the arrowhead of a transition was not displayed. This caused also an exception when the transition was reshaped. Fixed.
- A left mouse button click during view-area with the right mouse button caused an exception. Fixed.
- After loading a design from file, connectors did not get highlighted when the mouse pointer entered. Fixed.
- Moving connectors by mouse pointer now works better when the connector is very small.
- Picking up a state for moving now works better when the state is very small.
- Now the transition priority rectangle gets also invisible, when the number of outgoing transitions is reduced to 1 by deleting another state.

## [4.4] - 02.10.2024

### Added
- The background color of the diagram can now be configured in the control tab.
- The color of a state can now be configured by using the right mouse button menu at the state.

### Fixed
- Since version 4.3 a state-name could no longer be changed to the name it had already. Fixed.
- When transition end points were moved from one state to another state, the priority rectangles were not shown or hidden accordingly. Fixed.
- Now also the priority rectangle of the transition from the reset-entry is hidden.
- States and Connectors can no longer be placed on top of each other (caused exceptions sometimes).
- When a design is opened always the diagram is shown, even if HDL is loaded into the "generated HDL" tab.
- A transition which starts at reset entry can no longer be ended at a connector.
- A start-point of a transition can no longer be moved to the reset-entry if there already another transition starts.

## [4.3] - 30.09.2024

### Added
- Inserting a transition can now be aborted by "Escape".
- There is the new menu entry "straighten shape" at the right mouse button menu of a transition which changes the shape of transition to a straight line.
- The priority boxes of outgoing transitions of a state are only shown if the state has more than 1 outgoing transition.
- When a transition is inserted, its priority is automatically set to the highest unused priority
- When a state-name is changed, it is now checked if the new state-name is already used.
- Generics/parameters- and ports-declaration lists are now allowed to have a list separator (;/,) even after the last entry of the list.
- When a hfe-file is read by HDL-FSM-Editor and the generated HDL is younger than the hfe-file, then the generated HDL is copied into the HDL-tab.

### Fixed
- When a transition had the shape of the letter 'S', then only the end points of the transition could be moved by the mouse pointer. Fixed.
- Unread or unwritten signalnames were highlighted red in state comment blocks. Fixed.

## [4.2] - 05.09.2024

### Added
- Adding comments to states in a comment-box is now supported.

### Fixed
- Sometimes the plausibility checks report unnecessarily an unknown tag named "current", which is a legal tag and must be ignored. Fixed.
- Sometimes comments in transition-conditions caused illegal HDL code. Fixed.
- After inserting the reset-entry it is not longer necessary to abort the reset-entry-insertion by Escape.

## [4.1] - 27.08.2024

### Added
- At HDL generation the database is checked for plausibility.
- If any error is found an error-message is shown and the errors are listed at STDOUT.
- Errors could be introduced by program malfunction or by editing manually the hfe-file.

### Fixed
- When a condition-action window was removed, sometimes the connection-line of the window was not removed from the database. Fixed.
- When a connector box had no leaving transition and HDL was generated a Python exception happened. Fixed.

## [4.0] - 14.06.2024

### Added
- Now Links from the HDL-code in the "generated HDL"-tab to the source in the "Diagram"-tab are supported.
- Now Links from the compiler messages in the "Compile Messages"-tab to the "generated HDL"-tab or the source in the "Diagram"-tab are supported.

### Fixed
- Local Variable Declarations for clocked always process were added to the HDL code in a wrong way. Fixed.
- Improved HDL formating when transition conditions are more than 1 line of code.

## [3.11] - 05.05.2024

### Fixed
- In VHDL-mode the sensitivity list of the p_state_action process sometimes had duplicate entries. Fixed.
- In Verilog-mode the declaration of an integer variable caused an error message at HDL generation. Fixed.
- In Verilog-mode the linting (giving colors to not read or not written signal names) did not always use correct colors. Fixed.

### Added
- In Verilog-mode now reg/wire/logic can be declared as "signed" or "unsigned".
- The window title now has another format, so that the design name can be read, when the window is an icon.

## [3.10] - 13.03.2024

### Fixed
- Loading a design into HDL-FSM-Editor by command line parameter did not work anymore in version 3.9. Fixed.
- Fixed wrong tool-name in the help-text shown by option "-h".

### Added
- Added new command-line parameter "-generate_hdl" for batch-mode HDL generation (used in HDL-SCHEM-Editor).

## [3.9] - 07.03.2024

### Added
- The window-title was changed, so that the filename can be read, if the window is an icon.
- The checking of the command line parameters is now done by ArgParse.
- The new command-line switch -no_message was introduced to prevent HDL-FSM-Editor to print a message at start.

## [3.8] - 23.11.2023

### Added
- Now also the Default State Action block can be moved by picking it inside.
- A working directory for the compile commands can now be specified in the control tab.

## [3.7] - 17.11.2023

### Added
- All action blocks could only be moved by touching them near there border. Now they can be touched also inside.

### Fixed
- Connectors were not inserted with the right size after a zoom. Fixed.

## [3.6] - 08.11.2023

### Fixed
- Using the "Edit command" (Control-e) under Linux did not work. Fixed.

## [3.5] - 23.10.2023

### Fixed
- At HDL generation correctly defined functions and types caused the warning "There is an illegal signal declaration". Fixed.
- When a generic is read by an assignment it was colored red, as it was never written. Fixed.

## [3.4] - 21.10.2023

### Fixed
- At HDL generation correctly defined HDL-constants caused the warning "There is an illegal signal declaration". Fixed.
- Constants were highlighted in red as "not written". Fixed.There is an illegal signal declaration

## [3.3] - 18.09.2023

### Added
- Added command line switch "-no_version_check" to forbid HDL-FSM-Editor to access the internet at start.

### Fixed
- Removed a HDL generation crash, which was caused by a transition with no condition using a connector.

## [3.2] - 20.06.2023

### Fixed
- Fixed uncritical key error (caused only error messages at StdOut) when using the Internals/Packages entry window. Error was introduced in version 2.0

## [3.1] - 19.06.2023

### Changed
- In HDL all actions of a transition from a start state to a target state were implemented in the last condition branch of the transition. Now actions which may not have to be executed in this last branch are "moved up" in the branch hierarchy, which leads to shorter and better readable code.

## [3.0] - 30.05.2023

### Added
- A new algorithm for transforming the transition conditions and actions into HDL is now implemented. The old algorithm caused problems when connectors were used excessively.
- HDL-FSM-Editor now gives a hint, when a newer version is available.

## [2.1] - 12.05.2023

### Fixed
- A Verilog wire declaration added in "Internal Declarations" will not cause an (unimportant) Error message anymore.

## [2.0] - 04.05.2023

### Added
- Now the JSON format is used when a design is saved to a file. The file menu has a new entry for reading the old format of Version 1.
- "view area" can now be also done by the right mouse button.
- When a new design is opened by open-file dialog, the old design is not not removed, when the user aborts the opening.
- When selecting the path for the generated HDL, an abort does not remove the old path entry anymore.
- Now also in any Interface/Internals text field Control-o opens a file-dialog, instead of inserting a new line.
- Deleting empty condition&action- and state-action- windows now works.
- After inserting Default-State-Actions, Global-Actions and Global Actions-Combinatorial the escape key must not be pressed anymore.

### Fixed
- Fixed loading a design by a command line with "hdl_fsm_editor design-file.hfe". This did not work since version 1.4.

## [1.9] - 09.01.2023

### Changed
- The error message, which occurs when the reset condition is missing, now gives the user a hint, where the reset condition must be specified.

## [1.8] - 07.01.2023

### Changed
- In Verilog-mode now the temporay file (which is created when ctrl+e is used in a textbox) has the extension ".v" instead of ".vhd".
- The time stamp format used in generated HDL and in the "Compile Messages" tab is now better readable.

## [1.7] - 21.12.2022

### Fixed
- Fixed: main_window.py from version 1.6 had a doubled "," in line 266 instead of a single one.

## [1.6] - 09.12.2022

### Fixed
- Fixed a bug which showed, when a VHDL port name contains the string "out".

### Changed
- For text fields now no default font is used anymore (keywords and non-keywords now always use the same font).

## [1.5] - 08.11.2022

### Added
- A change of the path for the generated HDL is now handled as a design change.

### Fixed
- A bug at moving transitions was fixed.

### Removed
- The print functionality was removed, as each action window is always printed as a black box.

## [1.4] - 25.10.2022

### Added
- Static code analysis was added: Not read signals appear in "orange", not written signals appear in "red".

### Fixed
- Several small bugs were fixed.

## [1.3] - 10.10.2022

### Added
- Find-Button was added.
- When editing text boxes an external editor can be started by Control-e.
- Improvements for moving items in the diagram tab were added.

### Fixed
- Bug at highlighting was fixed.

## [1.2] - 04.10.2022

### Added
- SystemVerilog is now supported.
- Keyword highlighting is supported.
- Verilog: Asynchronous reset is now correct implemented.

## [1.1] - 29.09.2022

### Added
- Verilog is now supported.
- VHDL or Verilog code using upper case characters is now handled correctly.
- When deleting windows from the state diagram, it is now easier to hit the target.
- HDL-Generation: 1 file mode now works.

## [1.0] - 25.09.2022

### Added
- Initial version

---

## Links

- [Project Website](http://www.hdl-fsm-editor.de)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)


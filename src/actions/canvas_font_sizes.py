"""All methods to change the font sizes of the text in the canvas at zoom."""

from project_manager import project_manager


def adapt_fontsizes_and_store_global_size_variables(factor) -> None:
    """Adapt all global size variables and font sizes by the given factor."""
    project_manager.state_radius = factor * project_manager.state_radius  # publish new state radius
    project_manager.priority_distance = factor * project_manager.priority_distance
    project_manager.reset_entry_size = factor * project_manager.reset_entry_size
    _modify_font_sizes_of_all_canvas_items(factor)


def _modify_font_sizes_of_all_canvas_items(factor) -> None:
    project_manager.fontsize *= factor
    project_manager.label_fontsize *= factor
    # Configure the font which was created by TabDiagram._create_font_for_state_names() and is used for all state names:
    project_manager.state_name_font.configure(size=int(project_manager.fontsize))
    _apply_fontsize_to_canvas_window_items()


def _apply_fontsize_to_canvas_window_items() -> None:
    for element_ref in project_manager.canvas_windows_ref_dict.values():
        element_ref.apply_new_font_size()

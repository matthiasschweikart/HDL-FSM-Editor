"""All methods to change the font sizes of the text in the canvas at zoom."""

from elements import (
    condition_action,
    global_actions_clocked,
    global_actions_combinatorial,
    state_action,
    state_actions_default,
    state_comment,
)
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
    used_label_fontsize = max(project_manager.label_fontsize, 1)
    project_manager.state_name_font.configure(size=int(project_manager.fontsize))
    _apply_fontsize_to_canvas_items(used_label_fontsize)


def _apply_fontsize_to_canvas_items(used_label_fontsize: float) -> None:
    canvas_ids = project_manager.canvas.find_all()
    handlers = [
        (state_action.StateAction.ref_dict, _apply_font_to_state_action),
        (state_comment.StateComment.ref_dict, _apply_font_to_state_comment),
        (condition_action.ConditionAction.ref_dict, _apply_font_to_condition_action),
        (global_actions_clocked.GlobalActionsClocked.ref_dict, _apply_font_to_global_actions_clocked),
        (global_actions_combinatorial.GlobalActionsCombinatorial.ref_dict, _apply_font_to_global_actions_combinatorial),
        (state_actions_default.StateActionsDefault.ref_dict, _apply_font_to_state_actions_default),
    ]
    for canvas_id in canvas_ids:
        if project_manager.canvas.type(canvas_id) != "window":
            continue
        for ref_dict, handler in handlers:
            if canvas_id in ref_dict:
                handler(ref_dict[canvas_id], used_label_fontsize)
                break
        else:
            print("canvas_editing: Fatal, unknown dictionary key ", canvas_id)


def _apply_font_to_state_action(widget, used_label_fontsize: float) -> None:
    widget.label_id.configure(font=("Arial", int(used_label_fontsize)))
    widget.text_id.configure(font=("Courier", int(project_manager.fontsize)))
    widget.text_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))


def _apply_font_to_state_comment(widget, used_label_fontsize: float) -> None:
    widget.label_id.configure(font=("Arial", int(used_label_fontsize)))
    widget.text_id.configure(font=("Courier", int(project_manager.fontsize)))
    widget.text_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))


def _apply_font_to_condition_action(widget, used_label_fontsize: float) -> None:
    widget.condition_label.configure(font=("Arial", int(used_label_fontsize)))
    widget.action_label.configure(font=("Arial", int(used_label_fontsize)))
    widget.condition_id.configure(font=("Courier", int(project_manager.fontsize)))
    widget.action_id.configure(font=("Courier", int(project_manager.fontsize)))
    widget.condition_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))
    widget.action_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))


def _apply_font_to_global_actions_clocked(widget, used_label_fontsize: float) -> None:
    widget.label_before.configure(font=("Arial", int(used_label_fontsize)))
    widget.label_after.configure(font=("Arial", int(used_label_fontsize)))
    widget.text_before_id.configure(font=("Courier", int(project_manager.fontsize)))
    widget.text_after_id.configure(font=("Courier", int(project_manager.fontsize)))
    widget.text_before_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))
    widget.text_after_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))


def _apply_font_to_global_actions_combinatorial(widget, used_label_fontsize: float) -> None:
    widget.label.configure(font=("Arial", int(used_label_fontsize)))
    widget.text_id.configure(font=("Courier", int(project_manager.fontsize)))
    widget.text_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))


def _apply_font_to_state_actions_default(widget, used_label_fontsize: float) -> None:
    widget.label.configure(font=("Arial", int(used_label_fontsize)))
    widget.text_id.configure(font=("Courier", int(project_manager.fontsize)))
    widget.text_id.configure_hdl_text_tags(font=("Courier", int(project_manager.fontsize)))

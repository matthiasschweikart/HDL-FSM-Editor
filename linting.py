import main_window
import canvas_editing
import custom_text

def recreate_keyword_list_of_unused_signals():
    main_window.keywords["not_read"   ].clear()
    main_window.keywords["not_written"].clear()

    read_variables = []
    for _, read_variables_of_window in custom_text.CustomText.read_variables_of_all_windows.items():
        read_variables += read_variables_of_window
    #print('read_variables =', read_variables)
    written_variables = []
    for _, written_variables_of_window in custom_text.CustomText.written_variables_of_all_windows.items():
        written_variables += written_variables_of_window
    #print("written_variables =", written_variables)
    # Check if each input_port is read (remove read input_ports from list, if a declaration exists):
    for input_port in main_window.interface_ports_text.readable_ports_list:
        if input_port in read_variables:
            read_variables = [value for value in read_variables if value!=input_port]
        elif input_port!=main_window.clock_signal_name.get():
            main_window.keywords["not_read"].append(input_port)
    #print('main_window.keywords["not_read"] 1 =', main_window.keywords["not_read"])
    # Check if each output is written (remove written outputs from list, if a declaration exists):
    #print("main_window.interface_ports_text.writable_ports_list =", main_window.interface_ports_text.writable_ports_list)
    for output in main_window.interface_ports_text.writable_ports_list:
        if output in written_variables:
            written_variables = [value for value in written_variables if value!=output]
        else:
            main_window.keywords["not_written"].append(output)
        if main_window.language.get()!="VHDL" and output in read_variables:  # A Verilog output can be read.
            read_variables = [value for value in read_variables if value!=output]
    # Check if each signal or variable is written and is read:
    for signal in (main_window.internals_architecture_text.signals_list +
                   main_window.internals_process_combinatorial_text.signals_list +
                   main_window.internals_process_clocked_text.signals_list):
        if signal in written_variables and signal in read_variables:
            written_variables = [value for value in written_variables if value!=signal] # remove signal from list
            read_variables    = [value for value in read_variables    if value!=signal] # remove signal from list
        elif signal in written_variables:
            main_window.keywords["not_read"].append(signal)
        else:
            main_window.keywords["not_written"].append(signal)
    for constant in (main_window.internals_architecture_text.constants_list +
                     main_window.internals_process_combinatorial_text.constants_list +
                     main_window.internals_process_clocked_text.constants_list):
        written_variables = [value for value in written_variables if value!=constant] # remove constant from list
        if constant in read_variables:
            read_variables = [value for value in read_variables if value!=constant] # remove constant from list
        else:
            main_window.keywords["not_read"].append(constant)
    #print('main_window.keywords["not_read"] 2 =', main_window.keywords["not_read"])
    #print('read_variables =', read_variables)
    for port_type in main_window.interface_ports_text.port_types_list:
        if port_type in read_variables:
            read_variables    = [value for value in read_variables if value!=port_type] # remove signal from list
    for generic in main_window.interface_generics_text.generics_list:
        written_variables = [value for value in written_variables if value!=generic] # remove generic from list
        if generic in read_variables:
            read_variables = [value for value in read_variables if value!=generic] # remove signal from list
    main_window.keywords["not_written"] += read_variables
    main_window.keywords["not_read"]    += written_variables
    #print('written_variables =', written_variables)
    #print('main_window.keywords["not_read"] 3 =', main_window.keywords["not_read"])
    #print('main_window.keywords["not_written"] 3 =', main_window.keywords["not_written"])

def update_highlight_tags_in_all_windows_for_not_read_not_written_and_comment():
    # Comment must be the last, because in the range of a comment all other tags are deleted:
    for text_id in custom_text.CustomText.read_variables_of_all_windows:
        text_id.update_highlight_tags(canvas_editing.fontsize, ["not_read" , "not_written", "comment"])
    text_ids_fixed = [main_window.interface_generics_text, main_window.interface_package_text, main_window.interface_ports_text,
                      main_window.internals_architecture_text, main_window.internals_process_clocked_text, main_window.internals_process_combinatorial_text,
                      main_window.internals_package_text]
    for text_id in text_ids_fixed:
        text_id.update_highlight_tags(10, ["not_read" , "not_written", "comment"])

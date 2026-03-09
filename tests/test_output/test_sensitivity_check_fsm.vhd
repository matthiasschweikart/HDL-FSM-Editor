-- Filename: test_sensitivity_check_fsm.vhd
-- Created by HDL-FSM-Editor
library ieee;
use ieee.std_logic_1164.all;

architecture fsm of test_sensitivity_check is
    type t_state is (S1);
    signal state : t_state;
    signal sig1, sig2, sig3, sig4, sig5, sig6, sig7: std_logic;
    
    type t_record1 is record
        slice1 : std_logic;
    end record;
    signal record_sig1, record_sig2, record_sig3, record_sig4, record_sig5 : t_record1;
begin
    p_states: process (res_i, clk_i)
    begin
        if res_i='1' then
            state <= S1;
        elsif rising_edge(clk_i) then
            -- State Machine:
            case state is
                when S1 =>
                    sig6 <= sig7;
            end case;
        end if;
    end process;
    -- Global Actions combinatorial:
    sig1 <= sig2;
    process(
       record_sig1,
    -- sig4  -- Message 2: is missing in sensitivity
       sig3, -- Message 1: not used in process
       sig1
    )
    begin
        sig2 <= sig1;
        sig3 <= sig4;
        record_sig2 <= record_sig1;
    end process;
    
    process (
       record_sig1,
       record_sig2.slice1,
       record_sig4
    )
    begin
        sig4 <= record_sig1.slice1; -- Ok: only slice used
        record_sig3 <= record_sig2; -- Message 4: only a slice is part of the sensitivity
        sig4 <= record_sig4.slice1; -- Ok: only slice used
        record_sig5.slice1 <= sig3; -- Message 3: missing in sensitivity
    end process;
    
    process (
       record_sig4.slice1 -- Message 5: not used in process
    )
    begin
        sig5 <= record_sig5.slice1; -- Message 6: not in sensitivity
    end process;
    
end architecture;

-- Filename: test_sensitivity_check_fsm.vhd
-- Created by HDL-FSM-Editor
library ieee;
use ieee.std_logic_1164.all;

architecture fsm of test_sensitivity_check is
    type t_state is (S1);
    signal state : t_state;
    signal sig1, sig2, sig3, sig4: std_logic;
begin
    p_states: process (res_i, clk_i)
    begin
        if res_i='1' then
            state <= S1;
        elsif rising_edge(clk_i) then
            -- State Machine:
            case state is
                when S1 =>
            end case;
        end if;
    end process;
    -- Global Actions combinatorial:
    process(sig1, sig3 )
    begin
        sig2 <= sig1;
        sig2 <= sig4;
    end process;
end architecture;

#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check, LoopUntilFailed, Inverter, Succeeder

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():
    
    # if early game, 
    #     focus on rapid expansion, prioritizing captures by distance
    # if not early game, but not largest fleet
    #     defensive / evasive / tacking
    # if not early game, and largest fleet
    #     greedy heuristic (send_highest_value)
    # if late game (how do we detect this?)
    #     include trading down with greedy capture 
    
    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    attackLoop = Sequence(name='Attack Loop')
    attack = Action(send_highest_value)
    attackRepeater = LoopUntilFailed(attack)

    have_largest_fleet = Check(have_largest_fleet)
    trade_down_action = Action(trade_down)

    attackLoop.child_nodes = [attackRepeater, have_largest_fleet, trade_down_action]


    # Early game
    # early_game_sequence = Sequence(name='Early Game Sequence')
    # early_game_check = Check(if_early_game)
    # attack = Action(send_highest_value)
    # attackRepeater = LoopUntilFailed(attack)
    # early_game_sequence.child_nodes = [early_game_check, attackRepeater]
    
    # # Late game
    # late_game_sequence = Sequence(name='Late Game Sequence')
    # late_game_check = Check(if_late_game)
    # fleet_size_selector = Selector(name='Fleet Size in Late Game')

    # # Offensive late game
    # offensive_late_game_sequence = Sequence(name='Offensive Late Game Strategy')
    # largest_fleet_check = Check(have_largest_fleet)
    # trade_down_action = Action(trade_down)
    # offensive_late_game_sequence.child_nodes = [largest_fleet_check, attackRepeater, trade_down_action]

    # # Defensive late game
    # defensive_late_game_sequence = Sequence(name='Defensive Late Game Strategy')
    # not_largest_fleet_check = Check(have_smallest_fleet)
    # fortification = Action(defensive_fortification)
    # defensive_late_game_sequence.child_nodes = [not_largest_fleet_check, attackRepeater, fortification]

    # fleet_size_selector.child_nodes = [offensive_late_game_sequence, defensive_late_game_sequence]
    # late_game_sequence.child_nodes = [late_game_check, fleet_size_selector]

    # root.child_nodes = [early_game_sequence, late_game_sequence]

    root.child_nodes = [attackLoop]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
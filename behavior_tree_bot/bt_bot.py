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
    
    early_game = Selector(name='Early Game Selector') # expansion vs reposition for expansion
    expansion = Action(distance_priority)
    expansionRepeater = LoopUntilFailed(expansion)
    
    offensive = Selector(name='Offensive Selector') # greedy heuristic vs reposition at frontline
    attack = Action(send_highest_value)
    attackRepeater = LoopUntilFailed(attack)
    
    defensive = Selector(name='Defensive Selector') # evasion + tacking
    
    
    ifEarlyGame = Check(if_early_game)
    haveLargestFleet = Check(have_largest_fleet)
    
    # reposition. move ships toward "frontline"
    # average position of owned planets, move ships away from that position
    
    
    
    # evasion
    # tacking
    # repeater
    
    # rebalancer = Action(rebalance)
    
    new_selector.child_nodes = [attackRepeater]

    root.child_nodes = [new_selector]

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

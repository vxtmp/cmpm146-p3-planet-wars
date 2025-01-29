#!/usr/bin/env python
#
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from planet_wars import PlanetWars, issue_order, finish_turn
from behavior_tree_bot.behaviors import *

def loop_send_behavior(state):
    try:
        while send_highest_value(state):
            pass
    except StopIteration:
        return

def do_turn(state):
    loop_send_behavior(state)


if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)

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
    except:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")

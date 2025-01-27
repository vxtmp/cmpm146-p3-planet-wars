def always_true(state):
    return True

def if_neutral_planet_available(state):
    return any(state.neutral_planets())
  
def if_early_game(state):
    total_planets = len(state.my_planets()) + len(state.enemy_planets()) + len(state.neutral_planets())
    early_game_threshold = total_planets / 3
    return len(state.my_planets()) < early_game_threshold

def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

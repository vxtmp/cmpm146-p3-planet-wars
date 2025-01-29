def always_true(state):
    return True

def if_neutral_planet_available(state):
    return any(state.neutral_planets())
  
def if_early_game(state):
    my_planets_count = len(state.my_planets())
    enemy_planets_count = len(state.enemy_planets())
    if my_planets_count < 5:
        return True
    if my_planets_count < enemy_planets_count:
        return True
    return False

def if_late_game(state):
    my_planets_count = len(state.my_planets())
    enemy_planets_count = len(state.enemy_planets())
    if my_planets_count >= 5 or (my_planets_count > enemy_planets_count and sum(p.num_ships for p in state.my_planets()) > sum(p.num_ships for p in state.enemy_planets())):
        return True
    return False

def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def have_smallest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           < sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def no_neutral_planets(state):
    return state.neutral_planets() == []
import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def highest_value_spread(state):

    # (1) Iterate over all my planets and neutral planets, and find the highest value
    # according to a heuristic weighted by ships needed to conquer, ships available, growth rate,
    # and distance to the planet.
    highest_value = 0
    closest_distance = 999999
    closest_my_planet = None
    closest_neutral_planet = None
    for my_planet in state.my_planets():
        for neutral_planet in state.neutral_planets():
            distance = state.distance(my_planet.ID, neutral_planet.ID)
            if distance < closest_distance:
                closest_distance = distance
                closest_my_planet = my_planet
                closest_neutral_planet = neutral_planet


    if not closest_my_planet or not closest_neutral_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, closest_my_planet.ID, closest_neutral_planet.ID, 1)
    
def planet_value_heuristic(my_planet, target_planet, distance):
    return (target_planet.growth_rate / distance) / my_planet.num_ships

def counter_enemy_fleet():
    # if enemy has a fleet in flight, check its target if it will attack one of our planets
    # 
    pass

#test function
def send_one_to_all(state):
    # for each neutral planet, iterate over my fleets, if there isn't a fleet heading there, send 1
    for neutral_planet in state.neutral_planets():
        for my_fleet in state.my_fleets():
            if my_fleet.destination_planet == neutral_planet.ID:
                break
        else:
            ships_to_conquer = neutral_planet.num_ships + 1
            ordered_planets_by_distance = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, neutral_planet.ID))
            # select closest planet with enough ships to conquer
            i = 1;
            closest_planet = ordered_planets_by_distance[0]
            while closest_planet.num_ships < ships_to_conquer and i < len(ordered_planets_by_distance):
                # go to next planet
                closest_planet = ordered_planets_by_distance[i]
                i += 1
            if closest_planet.num_ships >= ships_to_conquer:
                return issue_order(state, closest_planet.ID, neutral_planet.ID, ships_to_conquer)
            # else consider a joint attack
    return False

            
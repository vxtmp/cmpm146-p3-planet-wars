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
     
def rebalance(state):
    # get total fleet, get total growth rate, weight fleet distribution to each planet by growth rate
    # select random planet with fleet count > its weighted fleet distribution
    # select random planet with fleet count < its weighted fleet distribution
    # send from high to low
    # if no such planets, return False
    total_fleet = sum(planet.num_ships for planet in state.my_planets())
    total_growth_rate = sum(planet.growth_rate for planet in state.my_planets())
    total_growth_rate = max(total_growth_rate, 1)
    weighted_fleet_distribution = total_fleet / total_growth_rate
    for planet in state.my_planets():
        if planet.num_ships > planet.growth_rate * weighted_fleet_distribution:
            # send to lowest planet
            ordered_planets_by_ships = sorted(state.my_planets(), key=lambda p: p.num_ships)
            for target_planet in ordered_planets_by_ships:
                if target_planet.num_ships < target_planet.growth_rate * weighted_fleet_distribution:
                    fleet_strength = planet.num_ships - target_planet.num_ships
                    fleet_strength = min(fleet_strength, planet.num_ships - 1)
                    fleet_strength = max(fleet_strength, 1)
                    return issue_order(state, planet.ID, target_planet.ID, fleet_strength)
     
     
     
def simulate_planet (state, planet, max_turn_depth, max_fleet_depth):
    # get all fleets in transit to planet
    incoming_fleets = get_fleet_subset_targeting_planet(state.my_fleets() + state.enemy_fleets(), planet)
    incoming_fleets = sorted(incoming_fleets, key=lambda f: f.turns_remaining)
    
    i = 0
    # simulate fleets in transit
    for fleet in incoming_fleets:
        if fleet.turns_remaining > max_turn_depth:
            break
        if i > max_fleet_depth:
            
        if fleet.destination_planet == planet.ID:
            continue
        # simulate fleet
        pass
    # evaluate planet
    pass
     
     

                    
def planet_value_heuristic(target_planet, distance):
    difficulty = 1 + target_planet.growth_rate * distance + target_planet.num_ships
    value = target_planet.growth_rate
    return value / difficulty

# helper function 
def get_fleet_subset_targeting_planet (some_fleets, planet):
    fleet_subset = []
    for fleet in some_fleets:
        if fleet.destination_planet == planet.ID:
            fleet_subset.append(fleet)
    return fleet_subset
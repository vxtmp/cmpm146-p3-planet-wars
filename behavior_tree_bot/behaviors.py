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
     
# simulates in-transit fleets for all iterated planets and assigns heuristic value before deciding.
def heuristic_send(state):
    
    heuristic_value = 0
    best_value_target_planet = None
    best_value_source_planet = None
    
    sorted_my_all = sorted(state.my_fleets(), key=lambda f: f.turns_remaining)
    sorted_enemy_all = sorted(state.enemy_fleets(), key=lambda f: f.turns_remaining)
    
    # iterating owned planets. 
    for planet in state.my_planets():
        
        # run a simulation for each planet in order of fleet distance (summation). 
        # if owner is self, then heuristic value = 0
        
        my_iter = 0
        enemy_iter = 0
        turn_counter = 0
        
        # for each fleet in sorted_my_all, if the destination is the planet, pop from all, push to my_curr
        sorted_my_curr = get_fleet_subset_targeting_planet(sorted_my_all, planet)
        sorted_enemy_curr = get_fleet_subset_targeting_planet(sorted_enemy_all, planet)
                
        # O (n)
        planet_owner = 1 # coefficient to apply growth rate. 1 for me, -1 for enemy, 0 for neutral.
        planet_ships = planet.num_ships
        
        closest_planet_that_can_attack = None
        if planet_owner == 1:
            heuristic_value = 0
        else:
            heuristic_value = 0
            
        # find closest attack planet
        closest_planet_that_can_attack = None
        closest_distance = 999999 # some large value. 
        
        # get a subset of my planets that doesn't include planet (planet can't attack self)
        my_planets_subset = [p for p in state.my_planets() if p.ID != planet.ID]
        
        for my_planet in my_planets_subset:
            growth_rate_adjusted = this_planet_ships + planet.growth_rate * state.distance(my_planet.ID, planet.ID)
            if my_planet.num_ships > growth_rate_adjusted and state.distance(my_planet.ID, planet.ID) < closest_distance:
                closest_distance = state.distance(my_planet.ID, planet.ID)
                closest_planet_that_can_attack = my_planet
                
        # if there is a planet that can attack, calculate heuristic value
        if closest_planet_that_can_attack:
            heuristic_value = planet_value_heuristic(planet, closest_distance)
                
        # if heuristic value > best value, then update best value
        if heuristic_value > best_value:
            best_value = heuristic_value
            best_value_target_planet = planet
            best_value_source_planet = closest_planet_that_can_attack
            
    # iterate enemy nodes
    # iterate neutral nodes
    
    # return issue order at best value
    if best_value_target_planet and best_value_source_planet:
        return issue_order(state, best_value_source_planet.ID, best_value_target_planet.ID, best_value_source_planet.num_ships)
    else:
        return False
        
# returns planet owner; 1 for self, -1 for enemy, 0 for neutral
# returns planet ships after simulation
def simulate_fleets_for_my_planet(sorted_my_curr, sorted_enemy_curr, planet, planet_owner):
    
    this_planet_ships = planet.num_ships # planet ships starts positive for me as owner
    
    while my_iter < len(sorted_my_curr) and enemy_iter < len(sorted_enemy_curr): # loop both lists ============================================
        
        if sorted_my_curr[my_iter].turns_remaining < sorted_enemy_curr[enemy_iter].turns_remaining:
            turns_since = sorted_my_curr[my_iter].turns_remaining - turn_counter
            this_planet_ships += planet_owner * turns_since * planet.growth_rate
            this_planet_ships += sorted_my_curr[my_iter].num_ships
            if this_planet_ships < 0:
                planet_owner = -1
            elif this_planet_ships > 0:
                planet_owner = 1
            my_iter += 1
            turn_counter += turns_since
        else:
            turns_since = sorted_enemy_curr[enemy_iter].turns_remaining - turn_counter
            this_planet_ships += planet_owner * turns_since * planet.growth_rate
            this_planet_ships -= sorted_enemy_curr[enemy_iter].num_ships
            if this_planet_ships < 0:
                planet_owner = -1
            elif this_planet_ships > 0:
                planet_owner = 1
            enemy_iter += 1
            turn_counter += turns_since
            
    if my_iter < len(sorted_my_curr): # loop the remaining list ============================================
        for f in sorted_my_curr[my_iter:]:
            this_planet_ships += planet_owner * f.turns_remaining * planet.growth_rate
            this_planet_ships += f.num_ships
            if this_planet_ships < 0:
                planet_owner = -1
            elif this_planet_ships > 0:
                planet_owner = 1
    elif enemy_iter < len(sorted_enemy_curr):
        for f in sorted_enemy_curr[enemy_iter:]:
            this_planet_ships += planet_owner * f.turns_remaining * planet.growth_rate
            this_planet_ships -= f.num_ships
            if this_planet_ships < 0:
                planet_owner = -1
            elif this_planet_ships > 0:
                planet_owner = 1
                
    return planet_owner, this_planet_ships
                    
    

def planet_value_heuristic(target_planet, distance):
    difficulty = 1 + target_planet.growth_rate * distance + target_planet.num_ships
    value = target_planet.growth_rate
    return value / difficulty

# helper function 
def get_fleet_subset_targeting_planet (some_fleets, planet):
    fleet_subset = []
    for fleet in some_fleets.fleets:
        if fleet.destination_planet == planet.ID:
            fleet_subset.append(fleet)
            some_fleets.remove(fleet)
    return fleet_subset
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
    best_value = 0
    best_value_target_planet = None
    best_value_source_planet = None
    
    # sorted_my_all = sorted(state.my_fleets(), key=lambda f: f.turns_remaining)
    # sorted_enemy_all = sorted(state.enemy_fleets(), key=lambda f: f.turns_remaining)
    
    sorted_fleets = sorted(state.my_fleets() + state.enemy_fleets(), key=lambda f: f.turns_remaining)
    
    # iterating planets. O(planets) * O(fleets) time = O(n^2) 
    for planet in state.my_planets() + state.not_my_planets():
        init_owner = 0
        if planet.owner == 1:
            init_owner = 1
        elif planet.owner == 2:
            init_owner = -1
            
        # simulates fleets in transit to planet. O(fleets) time.
        heuristic_value, closest_planet_that_can_attack, capture_cost = evaluate_planet (sorted_fleets, planet, state, init_owner)

        # if heuristic value > best value, then update best value
        if heuristic_value > best_value:
            best_value = heuristic_value
            best_value_target_planet = planet
            best_value_source_planet = closest_planet_that_can_attack
    
    # capture cost is target planet ships as simulated by evaluate_planet
    fleet_strength = capture_cost
    
    # return issue order at best value
    if best_value_target_planet and best_value_source_planet:
        return issue_order(state, best_value_source_planet.ID, best_value_target_planet.ID, fleet_strength)
    else:
        return False
        
# used in heuristic_send. init_owner should be 1 for self, -1 for enemy. 
# this function should not be used for neutral planets.
def evaluate_planet (sorted_all, planet, state, init_owner):
    # run a simulation for each planet in order of fleet distance (summation). 
    # if owner is self, then heuristic value = 0
    heuristic_value = 0

    # for each fleet in sorted_my_all, if the destination is the planet, pop from all, push to my_curr
    sorted_targeting = get_fleet_subset_targeting_planet(sorted_all, planet)
    # sorted_enemy_curr = get_fleet_subset_targeting_planet(sorted_enemy_all, planet)
            
    # huge function. O(n) complexity, where n is decreasing.
    #               n = in-transit fleets that have not been simulated yet.
    #               simulates fleets in transit to planet. 1 indicates owned by self
    
    
    planet_owner, this_planet_ships = simulate_fleets_planet(sorted_targeting, planet, init_owner)
    
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
        
        target_adjusted_for_growth_rate = 0
        for my_planet in my_planets_subset:
            # this_planet_ships is planet ships adjusted for growth + incoming fleets
            target_adjusted_for_growth_rate = this_planet_ships + planet.growth_rate * state.distance(my_planet.ID, planet.ID)
            
            # We skip any planets with incoming enemies
            # as we know we are trying to defend this planet. 
            has_incoming_enemies = False
            has_incoming_allies = False
            for fleet in sorted_targeting:
                if fleet.destination_planet == my_planet.ID and fleet.owner == 2:
                    has_incoming_enemies = True
                if fleet.destination_planet == my_planet.ID and fleet.owner == 1:
                    has_incoming_allies = True
                if has_incoming_enemies and has_incoming_allies:
                    break
            
            if has_incoming_enemies and has_incoming_allies: # skips if incoming enemies
                break # NOTE WIP: if incoming enemies exceeds planet, then DONT skip. use planet to attack.
            
            if my_planet.num_ships > target_adjusted_for_growth_rate and state.distance(my_planet.ID, planet.ID) < closest_distance and planet_owner == -1:
                closest_distance = state.distance(my_planet.ID, planet.ID)
                closest_planet_that_can_attack = my_planet
                
        # if there is a planet that can attack, calculate heuristic value
        if closest_planet_that_can_attack:
            heuristic_value = planet_value_heuristic(planet, closest_distance)
        
    # get fleet_strength necessary based on owner and growth rate and distance
    # if final owner as a result of eval is self, then fleet_strength to capture = 0
    capture_cost = 0
    if planet_owner == 1:
        pass
    elif planet_owner == -1:
        capture_cost = this_planet_ships
    elif planet_owner == 0:
        capture_cost = this_planet_ships
    
    return heuristic_value, closest_planet_that_can_attack, capture_cost
    
# returns new planet owner, planet ships after simulation
def simulate_fleets_planet(sorted_fleets, planet, init_owner):
    # my_iter = 0
    # enemy_iter = 0
    turn_counter = 0
    
    i = 0
    
    planet_owner = init_owner
    this_planet_ships = planet.num_ships # planet ships starts positive for me as owner
    
    while i < len(sorted_fleets):
        fleet_sign = 0
        if sorted_fleets[i].owner == 1:
            fleet_sign = 1
        if sorted_fleets[i].owner == 2:
            fleet_sign = -1
            
        turns_since = sorted_fleets[i].turns_remaining - turn_counter
        this_planet_ships += planet_owner * turns_since * planet.growth_rate
        
        if (planet_owner == 0): # neutral planets decrement count regardless of fleet, then transfer ownership
            this_planet_ships -= sorted_fleets[i].num_ships
            if this_planet_ships < 0:
                planet_owner = fleet_sign
                this_planet_ships = abs(this_planet_ships) * fleet_sign
        else:
            this_planet_ships += sorted_fleets[i].num_ships * fleet_sign
                
        i += 1
        turn_counter += turns_since
    return planet_owner, this_planet_ships
                    
def planet_value_heuristic(target_planet, distance):
    difficulty = 1 + target_planet.growth_rate * distance + target_planet.num_ships
    value = target_planet.growth_rate
    return value / 1

# helper function 
def get_fleet_subset_targeting_planet (some_fleets, planet):
    fleet_subset = []
    for fleet in some_fleets:
        if fleet.destination_planet == planet.ID:
            fleet_subset.append(fleet)
            some_fleets.remove(fleet)
    return fleet_subset
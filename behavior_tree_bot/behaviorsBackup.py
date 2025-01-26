     
# deprecated behaviors

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
        
        # Get planet owner. 1 = self, -1 = enemy, 0 = neutral
        init_owner = 0
        if planet.owner == 1:
            init_owner = 1
        elif planet.owner == 2:
            init_owner = -1
            
        # simulates fleets in transit to planet. O(fleets) time.
        heuristic_value, closest_planet_that_can_attack, capture_cost = evaluate_planet (sorted_fleets, planet, state, init_owner)
        
        if heuristic_value == 0:
            continue
        # if heuristic value > best value, then update best value
        if heuristic_value > best_value:
            best_value = heuristic_value
            best_value_target_planet = planet
            best_value_source_planet = closest_planet_that_can_attack
    
    # capture cost is target planet ships as simulated by evaluate_planet
    fleet_strength = capture_cost
    if not best_value_target_planet or not best_value_source_planet:
        return False
    if fleet_strength >= best_value_source_planet.num_ships:
        return False
    if fleet_strength <= 0:
        return False
    # return issue order at best value
    return issue_order(state, best_value_source_planet.ID, best_value_target_planet.ID, fleet_strength)
        
# used in heuristic_send. init_owner should be 1 for self, -1 for enemy. 
# this function should not be used for neutral planets.
# heuristic value of a planet is evaluated based on vertice connecting it to
#                 the closest planet that can conquer it
def evaluate_planet (sorted_all, target_planet, state, init_owner):
    heuristic_value = 0
    incoming_fleets = get_fleet_subset_targeting_planet(sorted_all, target_planet)
    simulated_target_owner, simulated_target_ships = simulate_fleets_planet(incoming_fleets, target_planet, init_owner)
    closest_myPlanet = None
    cost_bestVertex = 0
    
    # if planet is projected to be owned by self, dont need to send.
    if simulated_target_owner == 1: 
        heuristic_value = 0
    else:
        heuristic_value = 0
        closest_dist = 999999 # some large value. 
        
        # traverse my_planets - target_planet. (if myplanet is target, cannot send self)
        my_planets_subset = [p for p in state.my_planets() if p.ID != target_planet.ID]
        for my_planet in my_planets_subset:
            
            atkTime = state.distance(my_planet.ID, target_planet.ID)
            growth = target_planet.growth_rate * atkTime * abs(simulated_target_owner)
            targetShipsAdjusted = simulated_target_ships + growth
            
            # We skip any of our own planets with incoming enemies and allies,
            # as we know we are trying to defend.
            has_incoming_enemies = False
            has_incoming_allies = False
            for fleet in incoming_fleets:
                if fleet.destination_planet == my_planet.ID and fleet.owner == 2:
                    has_incoming_enemies = True
                if fleet.destination_planet == my_planet.ID and fleet.owner == 1:
                    has_incoming_allies = True
                if has_incoming_enemies and has_incoming_allies:
                    break
            
            if has_incoming_enemies and has_incoming_allies: # skips if incoming enemies
                continue # NOTE WIP: if incoming enemies exceeds planet, then DONT skip. use planet to attack.
            
            # bools
            enough_ships_to_attack = my_planet.num_ships > targetShipsAdjusted + 1
            is_closest = state.distance(my_planet.ID, target_planet.ID) < closest_dist
            
            if enough_ships_to_attack and is_closest:
                closest_dist = state.distance(my_planet.ID, target_planet.ID)
                closest_myPlanet = my_planet
                cost_bestVertex = targetShipsAdjusted
                
        # if there is a planet that can attack, calculate heuristic value
        if closest_myPlanet:
            heuristic_value = planet_value_heuristic(target_planet, closest_dist)
        
    # get fleet_strength necessary based on owner and growth rate and distance
    # if final owner as a result of eval is self, then fleet_strength to capture = 0
    capture_cost = 0
    if simulated_target_owner == 1:
        pass
    elif simulated_target_owner == -1:
        capture_cost = cost_bestVertex
    elif simulated_target_owner == 0:
        capture_cost = cost_bestVertex
    
    return heuristic_value, closest_myPlanet, capture_cost
    
    
    
    
simulation_depth = 10 # stops simulating fleets that are more than 10 turns away
max_fleet_count_iteration = 40 # stops simulating after 40 fleets
# returns new planet owner, planet ships after simulation
def simulate_fleets_planet(sorted_fleets, planet, init_owner):
    # my_iter = 0
    # enemy_iter = 0
    turn_counter = 0
    
    i = 0
    
    planet_owner = init_owner
    this_planet_ships = planet.num_ships # planet ships starts positive for me as owner
    
    if planet_owner == -1:
        this_planet_ships *= -1
    
    # essentially a summation of growth rate + incoming fleets
    while i < len(sorted_fleets) and i < max_fleet_count_iteration:
        if sorted_fleets[i].turns_remaining > simulation_depth:
            break
        
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
            # check for sign change of planet, if so, update planet owner variable
            start_ships = this_planet_ships
            this_planet_ships += sorted_fleets[i].num_ships * fleet_sign
            if (start_ships > 0 and this_planet_ships < 0) or (start_ships < 0 and this_planet_ships > 0):
                planet_owner *= -1
                
        i += 1
        turn_counter += turns_since
    return planet_owner, abs(this_planet_ships)
import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def flee_planet (state):
    # after check (if incoming capture), send all ships to (?)
    
    pass

# good for early game expansion. target nearby nodes first.
# uses 1 / distance instead of evaluate_vertex()
def distance_priority (state):
    all_planets = state.my_planets() + state.enemy_planets() + state.neutral_planets()
    
    best_value = 0 # min value
    best_target = None # target planet
    best_source = None # source planet
    best_cost = 0 # cost to capture
    
    for target_planet in all_planets:
        simulated_planet_owner, simulated_planet_ships = simulate_planet(state, target_planet, 10, 99)
        
        if simulated_planet_owner == 1:
            continue
        
        my_planets_by_distance = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, target_planet.ID))
        for source_planet in my_planets_by_distance:
            
            distance = state.distance(source_planet.ID, target_planet.ID)
            growth_cost = target_planet.growth_rate * distance
            cost = simulated_planet_ships + 1 + growth_cost
            
            # if capturable
            if source_planet.num_ships > cost:
                # heuristic 
                value = 1 / distance
                # if new best, update best value
                if value > best_value:
                    best_value = value
                    best_target = target_planet
                    best_source = source_planet
                    best_cost = cost
                    
    if not best_target or not best_source:
        return False
    else:
        return issue_order(state, best_source.ID, best_target.ID, best_cost)
    
     
def rebalance(state):
    # get total fleet, get total growth rate, weight fleet distribution to each planet by growth rate
    # select random planet with fleet count > its weighted fleet distribution
    # select random planet with fleet count < its weighted fleet distribution
    # send from high to low
    # if no such planets, return False
    total_fleet = sum(planet.num_ships for planet in state.my_planets())
    total_growth_rate = sum(planet.growth_rate for planet in state.my_planets())
    total_growth_rate = max(total_growth_rate, 1)
    weighted_fleet_distribution = total_fleet / total_growth_rate # avg fleet per growth rate
    
    lowest_need = 999999
    lowest_planet = None
    highest_surplus = 0
    highest_planet = None
    
    for planet in state.my_planets():
        
        weighted_threshold_ships = planet.growth_rate * weighted_fleet_distribution # fleet per this planet's growth rate
        
        if planet.num_ships > planet.growth_rate * weighted_fleet_distribution:
            # send to lowest planet
            ordered_planets_by_ships = sorted(state.my_planets(), key=lambda p: p.num_ships)
            for target_planet in ordered_planets_by_ships:
                
                enemy_combat_potential = evaluate_combat_potential(state, planet, target_planet)
                # evaluate some heuristic for NEED (low value) / SURPLUS (high value)
                planet_need_heuristic = enemy_combat_potential * planet.num_ships / weighted_threshold_ships
    
                if planet_need_heuristic < lowest_need:
                    lowest_need = planet_need_heuristic
                    lowest_planet = target_planet
                elif planet_need_heuristic > highest_surplus:
                    highest_surplus = planet_need_heuristic
                    highest_planet = target_planet
    
                # if target_planet.num_ships < target_planet.growth_rate * weighted_fleet_distribution:
                #     fleet_strength = planet.num_ships - target_planet.num_ships
                #     fleet_strength = min(fleet_strength, planet.num_ships - 1)
                #     fleet_strength = max(fleet_strength, 1)
                #     return issue_order(state, planet.ID, target_planet.ID, fleet_strength)
          
    difference_threshold = 10
    if not lowest_planet or not highest_planet:
        return False
    else:
        if highest_surplus / lowest_need > difference_threshold:
            fleet_strength = highest_planet.num_ships - 1
            if fleet_strength <= 0:
                return False
            return issue_order(state, highest_planet.ID, lowest_planet.ID, fleet_strength)
        else:
            return False
     
     
# send from high response time nodes to high value enemy nodes
def throwaway(state):
    # evaluate surplus. 
    # throw surplus high value enemy planets / low response time enemy planets
    pass
     
# evaluates enemy combat potential targeting this planet.
def evaluate_combat_potential (state, source_planet, target_planet):
    # ships, distance + growth rate, number of enemy nodes
    total_weighted_combat_potential = 0

    for enemy_planet in state.enemy_planets():
        combat_potential = enemy_planet.num_ships + (enemy_planet.growth_rate * state.distance(source_planet.ID, target_planet.ID))
        distance = state.distance(enemy_planet.ID, target_planet.ID)
        total_weighted_combat_potential += combat_potential / distance

    return total_weighted_combat_potential 
    
    
# our nodes
#       low enemy response our nodes (can evaluate surplus at a lower threshold)
# enemy nodes / neutral nodes
#       low enemy combat potential = higher value (enemy will not retake quickly)
#       high enemy combat potential = lower value (enemy will retake quickly)
# low response time nodes => lower value (enemy will retake quickly) 
     

# heuristic for choosing target planet. 
def evaluate_vertex (state, source_planet, target_planet, predicted_base_cost):
    value = target_planet.growth_rate
    
    growth_delta = target_planet.growth_rate * state.distance(source_planet.ID, target_planet.ID)
    cost = predicted_base_cost + 1 + growth_delta
    
    # include response time (WIP)
    
    return value / cost

# greedy behavior. targets all owner changeable planets (defense and offense)
# good for aggressive playstyle when ahead. 
def send_highest_value (state):
    all_planets = state.my_planets() + state.enemy_planets() + state.neutral_planets()
    
    best_value = 0 # min value
    best_target = None # target planet
    best_source = None # source planet
    best_cost = 0 # cost to capture
    
    for target_planet in all_planets:
        simulated_planet_owner, simulated_planet_ships = simulate_planet(state, target_planet, 10, 99)
        
        if simulated_planet_owner == 1:
            continue
        
        my_planets_by_distance = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, target_planet.ID))
        for source_planet in my_planets_by_distance:
            
            
            distance = state.distance(source_planet.ID, target_planet.ID)
            growth_cost = target_planet.growth_rate * distance
            cost = simulated_planet_ships + 1 + growth_cost
            
            # if capturable
            if source_planet.num_ships > cost:
                # heuristic 
                value = evaluate_vertex(state, source_planet, target_planet, cost)
                # if new best, update best value
                if value > best_value:
                    best_value = value
                    best_target = target_planet
                    best_source = source_planet
                    best_cost = cost
                    
    if not best_target or not best_source:
        return False
    else:
        return issue_order(state, best_source.ID, best_target.ID, best_cost)

# deprecated for send_highest_value
def send_first(state):
    all_planets = state.my_planets() + state.enemy_planets() + state.neutral_planets()
    
    for target_planet in all_planets:
        
        # simulate based on current state (in-transit fleets + growth rate)
        simulated_planet_owner, simulated_planet_ships = simulate_planet(state, target_planet, 10, 99)
        
        # if planet is projected to be owned by self, dont need to send.
        if simulated_planet_owner == 1:
            continue
        
        # iterate by distance (to prioritize closer source planet)
        my_planets_by_distance = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, target_planet.ID))
        for source_planet in my_planets_by_distance:
            
            # estimate cost of capturing planet
            distance = state.distance(source_planet.ID, target_planet.ID)
            growth_cost = target_planet.growth_rate * distance
            cost = simulated_planet_ships + 1 + growth_cost
            
            # if capturable, capture
            if source_planet.num_ships > cost:
                return issue_order(state, source_planet.ID, target_planet.ID, cost)
            
    return False
     
def simulate_planet (state, planet, max_turn_depth, max_fleet_depth):
    # get all fleets in transit to planet
    incoming_fleets = get_fleet_subset_targeting_planet(state.my_fleets() + state.enemy_fleets(), planet)
    incoming_fleets = sorted(incoming_fleets, key=lambda f: f.turns_remaining)
    
    simulated_planet_owner = 0
    simulated_planet_ships = planet.num_ships
    
    if planet.owner == 2:               # negative represents enemy
        simulated_planet_owner = -1
        simulated_planet_ships *= -1
    if planet.owner == 1:
        simulated_planet_owner = 1
    
    i = 0
    turns_counter = 0
    # simulate fleets in transit
    for fleet in incoming_fleets:
        
        fleet_sign = 0
        if fleet.owner == 1:
            fleet_sign = 1
        elif fleet.owner == 2:
            fleet_sign = -1
            
        if fleet.turns_remaining > max_turn_depth:
            break
        if i > max_fleet_depth:
            break
        
        turns_since_last_fleet = fleet.turns_remaining - turns_counter
        turns_counter += turns_since_last_fleet
        
        # add growth rate
        #                           sign (-1, 0, 1)          growth rate               time
        #                                 |                        |                     |
        #                                 V                        V                     V
        simulated_planet_ships += simulated_planet_owner * planet.growth_rate * turns_since_last_fleet
        
        if simulated_planet_owner == 0: # neutral planet
            simulated_planet_ships -= abs(fleet.num_ships)
            if simulated_planet_ships <= 0:
                simulated_planet_owner = fleet_sign
                simulated_planet_ships = abs(simulated_planet_ships) * fleet_sign # negative for enemy
        else:
            start_ships = simulated_planet_ships
            simulated_planet_ships += fleet_sign * fleet.num_ships
            if (start_ships < 0 and simulated_planet_ships > 0) or (start_ships > 0 and simulated_planet_ships < 0):
                simulated_planet_owner *= -1
            
        i += 1
        
    if simulated_planet_owner == -1:
        simulated_planet_owner = 2
    elif simulated_planet_owner == 1:
        simulated_planet_owner = 1
    elif simulated_planet_owner == 0:
        simulated_planet_owner = 0
        
    return simulated_planet_owner, abs(simulated_planet_ships)
     
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


# =========================== deprecated functions ==============================
# test function
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
     
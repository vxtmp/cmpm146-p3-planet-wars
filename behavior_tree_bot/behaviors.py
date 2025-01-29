import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

# good for early game expansion. target nearby nodes first.
# uses 1 / distance instead of evaluate_vertex()
def distance_priority(state):
    all_planets = state.my_planets() + state.enemy_planets() + state.neutral_planets()

    best_value = float('inf')  # Initialize to max value for distance minimization
    best_target = None  # target planet
    best_source = None  # source planet
    best_cost = 0  # cost to capture

    # Simulate the planets and assess the best target for expansion
    for target_planet in all_planets:
        # Skip planets I already own
        if target_planet.owner == 1:
            continue
        
        # Calculate the minimum cost to capture the planet based on simulation
        simulated_planet_owner, simulated_planet_ships = simulate_planet(state, target_planet, 10, 99)
        
        # If the simulation suggests the planet is very difficult to capture, skip it
        if simulated_planet_owner == 1:
            continue  # Skip if planet is already owned by me
        
        # Sort my planets by distance to the target planet to minimize travel time
        my_planets_by_distance = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, target_planet.ID))
        for source_planet in my_planets_by_distance:
            # Calculate the effective distance (including a small buffer)
            distance = state.distance(source_planet.ID, target_planet.ID) + 1  # 1 turn buffer
            
            # Calculate the cost of capturing this planet, considering the planet's growth rate
            growth_cost = target_planet.growth_rate * distance
            cost = simulated_planet_ships + 1 + growth_cost  # Total cost of capturing the planet

            # Ensure we have more ships than the cost to capture
            if source_planet.num_ships > cost:
                value = distance  # Shorter distances are better

                # If this target is more favorable, update the best values
                if value < best_value:
                    best_value = value
                    best_target = target_planet
                    best_source = source_planet
                    best_cost = cost

    # If a target has been found, issue the order to capture it
    if best_target and best_source:
        return issue_order(state, best_source.ID, best_target.ID, best_cost)
    
    # If no target is found, return False
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

def trade_down(state):
    # growth rate + distance from enemy planets
    best_heuristic = 0
    best_planet = None

    for enemy_planet in state.enemy_planets():
        heuristic = trade_down_heuristic(state, enemy_planet)
        if heuristic > best_heuristic:
            best_heuristic = heuristic
            best_planet = enemy_planet

    if best_planet:
        closest_distance = 999999
        closest_planet = None
        for my_planet in state.my_planets():
            distance = state.distance(my_planet.ID, best_planet.ID)
            if distance < closest_distance:
                closest_distance = distance
                closest_planet = my_planet
        return issue_order(state, closest_planet.ID, best_planet.ID, closest_planet.num_ships)

    return False

def trade_down_heuristic(state, target_planet):
    # calculate the distance to enemy planet from a targeted planet and the growth rate
    heuristic = 0
    total_enemy_ships = 0
    for planet in state.enemy_planets():
        if planet.ID == target_planet.ID:
            continue
        total_enemy_ships += planet.num_ships
    for enemy in state.enemy_planets():
        if enemy.ID == target_planet.ID:
            continue
        if total_enemy_ships == 0:
            total_enemy_ships = 1
        distance = state.distance(target_planet.ID, enemy.ID)
        # weighted by the growth rate and ships out of total enemy ships and distance
        heuristic += enemy.num_ships / total_enemy_ships * target_planet.growth_rate / distance

    return heuristic

def defensive_fortification(state):
    # priority for high-growth planets and planets with large numbers of ships
    priority_planets = sorted(
        state.my_planets(),
        key=lambda p: (p.growth_rate, p.num_ships),
        reverse=True
    )

    enemy_fleets = state.enemy_fleets()
    orders = []
    
    # calculate threat levels for each planet and prioritize based on growth
    for planet in priority_planets:
        threat_level = 0
        for fleet in enemy_fleets:
            if fleet.destination_planet == planet.ID:
                threat_level += fleet.num_ships
        # reinforce the planet if threat exists
        if threat_level > 0:
            # more ships needed for higher threat
            required_ships = int(threat_level * 1.2)
            available_fleets = planet.num_ships - max(10, int(planet.growth_rate * 2))
            if available_fleets > 0:
                # look for planets to send ships from
                sources = sorted(
                    [p for p in state.my_planets() if p.ID != planet.ID],
                    key=lambda p: (state.distance(p.ID, planet.ID), -p.num_ships)
                )
                
                total_sent = 0
                for source in sources:
                    available = max(source.num_ships - max(10, int(source.growth_rate * 2)), 0)
                    if available <= 0:
                        continue
                    # overcommitment prevention
                    send_ships = min(available, required_ships - total_sent)
                    orders.append((source.ID, planet.ID, send_ships))
                    total_sent += send_ships
                    # stop if sufficient reinforcements are committed
                    if total_sent >= required_ships:
                        break
    
    # issue order if the reinforcement are sufficient
    for order in orders:
        issue_order(state, *order)

    return True

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
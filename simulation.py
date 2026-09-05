from typing import Dict, List, Any
from logic import main
from parsing import check_validation
from colors import color_node

class Zones:
    def __init__(self, name, max_capacity):
        self.name = name
        self.max_capacity = max_capacity
        self.current_drones = 0

class Connections:
    def __init__(self, start, end, max_link_capacity):
        self.start = start
        self.end = end
        self.max_link_capacity = max_link_capacity
        self.current_drones = 0
class Drones:
    def __init__(self, drone_id, info, path, zones_dict, connection_data,cap_connections):
        self.drone_id = drone_id
        self.path = path
        self.info = info
        self.cap_zones = zones_dict
        self.connection_data = connection_data
        self.step = 0
        self.active = False
        self.reached_goal = False

        self.cap_connections = cap_connections


        #for [zone=restricted]
        self.in_transit = False
        self.transit_turns_left = 0
        self.transit_target = ""
        self.transit_link = None

    def move_turn(self) -> str | None:
        if not self.active or self.reached_goal:
            return None
        #here i choose the path through the step 
        current_node_name = self.path[self.step]


        end_node_name = self.path[-1]
        start_node_name = self.path[0]

        # restricted zone 
        if self.in_transit:
            self.transit_turns_left -= 1
            if self.transit_turns_left == 0:
                self.in_transit = False

                if self.transit_link:
                    self.transit_link.current_drones = max(0,self.transit_link.current_drones - 1)
                    self.transit_link = None


                # free previous zone capacity
                if current_node_name not in (start_node_name, end_node_name):
                    prev_zone = self.cap_zones[current_node_name]
                    prev_zone.current_drones = max(0, prev_zone.current_drones - 1)

                self.step += 1
                if self.step >= len(self.path) - 1:
                    self.reached_goal = True
                    dest_node = end_node_name
                else:
                    dest_node = self.path[self.step]

                # if dest_node == end_node_name:
                #     self.reached_goal = True

                return f"D{self.drone_id}-{color_node(dest_node, self.info)}"

            return (
                f"D{self.drone_id}-"
                f"{color_node(current_node_name, self.info)}--"
                f"{color_node(self.transit_target, self.info)}"
            )

        # if it reached the goal it stop 
        if self.step + 1 >= len(self.path):
            self.reached_goal = True
            return None
        target_node_name = self.path[self.step + 1]
        target_z = self.cap_zones[target_node_name]

        # get the connection
        link = self.cap_connections.get((current_node_name, target_node_name))

        # Check connection capacity
        if link and link.current_drones >= link.max_link_capacity:
            return None

        
        # node capacity check
        if target_z.current_drones < target_z.max_capacity:
            if link:
                link.current_drones += 1
            #just here i check if it zone restricted
            is_restricted = (self.info.get(target_node_name, {}).get("zone") == "restricted")
            if is_restricted:
                self.in_transit = True
                self.transit_turns_left = 1
                self.transit_target = target_node_name
                target_z.current_drones += 1
                self.transit_link = link

                return (
                    f"D{self.drone_id}-"
                    f"{color_node(current_node_name, self.info)}-"
                    f"{color_node(target_node_name, self.info)}"
                )

            # here just -1 to the current drone that i go far away from it
            if current_node_name not in (start_node_name, end_node_name):
                curr_z = self.cap_zones[current_node_name]
                curr_z.current_drones = max(0, curr_z.current_drones - 1)

            self.step += 1
            if target_node_name not in (start_node_name, end_node_name):
                target_z.current_drones += 1
            if link:
                link.current_drones = max(0,link.current_drones - 1)


            if target_node_name == end_node_name:
                self.reached_goal = True

            return f"D{self.drone_id}-{color_node(target_node_name, self.info)}"

        return None


# Terminal colors

def clean_paths(raw_paths: List[List[str]]) -> List[List[str]]:
    valid = []
    for p in raw_paths:
        if len(p) == len(set(p)):
            valid.append(p)
    valid.sort(key=len)
    return valid


def func():
    info, connection, paths = main()
    if not paths:
        print("Error: No valid paths found by pathfinding logic.")
        return

    if paths and isinstance(paths[0], str):
        paths = [paths]

    try:
        nb_drones = check_validation()
    except Exception:
        nb_drones = 12
    #here take the name of the start and the end
    start_node = paths[0][0]
    end_node = paths[0][-1]



    # clean redundant paths
    # print("befooore    --->here the clears path ",paths)
    #here i thing this is not make since also clean_path 
    paths = [p for p in paths if p and p[0] == start_node]
    paths = clean_paths(paths)
    # print("here the clears path ",paths)



    #like give the class info for the max drone
    cap_zones = {}
    for name, data in info.items():
        raw_cap = data.get("max_drones", 1)
        if isinstance(raw_cap, (list, tuple)):
            raw_cap = raw_cap[0] if raw_cap else 1
        cap_zones[name] = Zones(name, int(raw_cap))
    cap_zones[start_node] = Zones(start_node, float("inf"))
    cap_zones[end_node] = Zones(end_node, float("inf"))

    print("-------",connection)    
    cap_connections = {}

    for start, neighbors in connection.items():
        for end, capacity in neighbors:
            cap_connections[(start, end)] = Connections(start,end,capacity)

    # Create drones using top non-cyclic paths
    
    top_paths = paths

    all_drones = []
    for idx in range(nb_drones):
        assigned_path = top_paths[idx % len(top_paths)]
        d = Drones(
            drone_id=idx + 1,
            info=info,
            path=assigned_path,
            zones_dict=cap_zones,
            connection_data=connection,
            cap_connections=cap_connections
        )
        all_drones.append(d)

    waiting_drones = list(all_drones)
    turn_counter = 0


    while not all(d.reached_goal for d in all_drones):
        turn_counter += 1
        turn_moves = []

        # advance active drones
        for d in [d for d in all_drones if d.active and not d.reached_goal]:
            move_str = d.move_turn()
            if move_str:
                turn_moves.append(move_str)

        # deploy waiting drones
        if waiting_drones:
            to_deploy = []
            for candidate in waiting_drones:
                first_step_node = candidate.path[1]
                first_zone = cap_zones[first_step_node]

                if first_zone.current_drones < first_zone.max_capacity:
                    candidate.active = True
                    move_str = candidate.move_turn()
                    if move_str:
                        turn_moves.append(move_str)
                        to_deploy.append(candidate)
                    else:
                        candidate.active = False

            for deployed in to_deploy:
                waiting_drones.remove(deployed)

        if turn_moves:
            print(f"Turn {turn_counter}: " + " ".join(turn_moves))

        if turn_counter > 500:
            print("\nError: Simulation aborted (exceeded turn limit).")
            break

    reached_to_goal = sum(1 for d in all_drones if d.reached_goal)
    print("\n------------------------------")
    print(f"{color_node('FINISHED', {'FINISHED': {'color': 'green'}})}")
    print(f"Drones reached goal: {reached_to_goal}/{nb_drones}")
    print(f"Total turns: {turn_counter}")


if __name__ == "__main__":
    func()
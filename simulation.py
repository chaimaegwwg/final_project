from logic import PathFinder
from parsing import check_validation
from colors import color_node
from typing import Any
import sys


class Zones:
    def __init__(
        self,
        name: str,
        max_capacity: int | float,
    ) -> None:
        self.name = name
        self.max_capacity = max_capacity
        self.current_drones = 0


class Connections:
    def __init__(
        self,
        start: str,
        end: str,
        max_link_capacity: int,
    ) -> None:
        self.start = start
        self.end = end
        self.max_link_capacity = max_link_capacity
        self.current_drones = 0


class Drones:
    def __init__(
        self,
        drone_id: int,
        info: dict[str, dict[str, Any]],
        path: list[str],
        zones_dict: dict[str, Zones],
        connection_data: dict[str, list[list[str | int]]],
        cap_connections: dict[tuple[str, str], Connections],
    ) -> None:
        self.drone_id = drone_id
        self.path = path
        self.info = info
        self.cap_zones = zones_dict
        self.connection_data = connection_data
        self.step = 0
        self.active = False
        self.reached_goal = False
        self.cap_connections = cap_connections
        self.in_transit = False
        self.transit_turns_left = 0
        self.transit_target = ""
        self.transit_link: Connections | None = None

    def move_turn(self) -> str | None:
        if not self.active or self.reached_goal:
            return None
        current_node_name = self.path[self.step]
        end_node_name = self.path[-1]
        start_node_name = self.path[0]
        if self.in_transit:
            self.transit_turns_left -= 1
            if self.transit_turns_left == 0:
                self.in_transit = False

                if self.transit_link:
                    self.transit_link.current_drones = max(
                        0, self.transit_link.current_drones - 1)
                    self.transit_link = None

                if current_node_name not in (start_node_name, end_node_name):
                    prev_zone = self.cap_zones[current_node_name]
                    prev_zone.current_drones = max(
                        0, prev_zone.current_drones - 1)

                self.step += 1
                if self.step >= len(self.path) - 1:
                    self.reached_goal = True
                    dest_node = end_node_name
                else:
                    dest_node = self.path[self.step]

                return f"D{self.drone_id}-{color_node(dest_node, self.info)}"

            return (
                f"D{self.drone_id}-"
                f"{color_node(current_node_name, self.info)}--"
                f"{color_node(self.transit_target, self.info)}"
            )
        if self.step + 1 >= len(self.path):
            self.reached_goal = True
            return None
        target_node_name = self.path[self.step + 1]
        target_z = self.cap_zones[target_node_name]

        link = self.cap_connections.get((current_node_name, target_node_name))
        if link and link.current_drones >= link.max_link_capacity:
            return None

        if target_z.current_drones < target_z.max_capacity:
            if link:
                link.current_drones += 1
            is_restricted = (
                self.info.get(
                    target_node_name, {}).get("zone") == "restricted")
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

            if current_node_name not in (start_node_name, end_node_name):
                curr_z = self.cap_zones[current_node_name]
                curr_z.current_drones = max(0, curr_z.current_drones - 1)

            self.step += 1
            if target_node_name not in (start_node_name, end_node_name):
                target_z.current_drones += 1
            if link:
                link.current_drones = max(0, link.current_drones - 1)
            if target_node_name == end_node_name:
                self.reached_goal = True
            target = color_node(target_node_name, self.info)
            return f"D{self.drone_id}-{target}"
        return None


class Function:
    def func(self) -> None:
        res = PathFinder()
        result = res.main()
        if not result:
            return

        info, connection, paths = result
        if not paths:
            print("Error: No valid paths found by pathfinding logic.")
            return

        if paths and isinstance(paths[0], str):
            paths = [paths]

        try:
            nb_drones = check_validation()
            if nb_drones is None:
                return
        except Exception:
            sys.exit()
        start_node = paths[0][0]
        end_node = paths[0][-1]

        paths = [p for p in paths if p and p[0] == start_node]
        cap_zones = {}
        for name, data in info.items():
            raw_cap = data.get("max_drones", 1)
            if isinstance(raw_cap, (list, tuple)):
                raw_cap = raw_cap[0] if raw_cap else 1
            cap_zones[name] = Zones(name, int(raw_cap))
        cap_zones[start_node] = Zones(start_node, float("inf"))
        cap_zones[end_node] = Zones(end_node, float("inf"))
        cap_connections = {}
        for start, neighbors in connection.items():
            for end, capacity in neighbors:
                cap_connections[(start, end)] = Connections(
                    start,
                    end,
                    capacity
                )

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
            for d in [
                d for d in all_drones
                if d.active and not d.reached_goal
            ]:
                move_str = d.move_turn()
                if move_str:
                    turn_moves.append(move_str)
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


def safety() -> None:
    try:
        func_tion = Function()
        func_tion.func()
    except Exception:
        print("Error: may syntax")
        sys.exit()


safety()

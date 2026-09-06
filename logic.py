import sys
from parsing import check_hub, make_a_dictionary
from typing import Any


class Grid:

    def __init__(
        self,
        name: str,
        row: int,
        col: int,
        zone: int | float = 0,
        color: int = 0,
        max_drones: int = 0,
        name_zone: str | int = 0,
        value: int = 0,
    ) -> None:
        self.name = name
        self.row = row
        self.col = col
        self.zone = zone
        self.color = color
        self.name_zone = name_zone
        self.max_drones = max_drones
        self.place = 0
        self.value = value
        self.visited = False


class PathFinder:
    def ft_info(
        self,
        info: dict[str, dict[str, Any]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> tuple[list[list[Grid]], int, int] | None:
        start_row, start_col = start
        end_row, end_col = end
        try:

            all_rows = (
                [int(v["position"][0]) for v in info.values()]
                + [start_row, end_row]
            )

            all_cols = (
                [int(v["position"][1]) for v in info.values()]
                + [start_col, end_col]
            )
        except (ValueError, TypeError, IndexError):
            print("Error: invalid number in hub position")
            return None
        try:
            min_r, max_r = min(all_rows), max(all_rows)
            min_c, max_c = min(all_cols), max(all_cols)

            if min_r < 0:
                offset_r = -min_r
            else:
                offset_r = 0

            if min_c < 0:
                offset_c = -min_c
            else:
                offset_c = 0

            grid_rows = (max_r + offset_r) + 1
            grid_cols = (max_c + offset_c) + 1

            grid = []
            for x in range(grid_rows):
                row_list = []
                for y in range(grid_cols):
                    row_list.append(Grid("anonymous", x, y))
                grid.append(row_list)
            start_r, start_c = start_row + offset_r, start_col + offset_c
            end_r, end_c = end_row + offset_r, end_col + offset_c

            grid[start_r][start_c].name = "start_hub"
            grid[end_r][end_c].name = "start_end"
            for key, value in info.items():
                row = int(value["position"][0]) + offset_r
                col = int(value["position"][1]) + offset_c
                name = value["name"]

                zone_str = str(value.get("zone", "normal")).lower()
                zone: int | float
                if zone_str in ("normal", "priority"):
                    grid[row][col].name_zone = zone_str
                    zone = 1
                elif zone_str == "restricted":
                    grid[row][col].name_zone = "restricted"
                    zone = 2
                elif zone_str == "blocked":
                    grid[row][col].name_zone = "blocked"
                    zone = float("inf")
                else:
                    zone = 1

                grid[row][col].zone = zone
                grid[row][col].place = 1
                grid[row][col].name = name

            return grid, offset_r, offset_c
        except (ValueError, TypeError, IndexError):
            print("Error: invalid ")
            return None

    def find_all_paths(
        self,
        connection: dict[str, list[list[str | int]]],
        grid: list[list[Grid]],
        info: dict[str, dict[str, Any]],
        current: str,
        goal: str,
        path: list[str],
        routes: list[list[str]],
        offset_r: int,
        offset_c: int,
    ) -> None:
        path.append(current)
        if current == goal:
            routes.append(path.copy())
        else:
            neighbors = connection.get(current, [])
            for neighbor in neighbors:
                key = str(
                    neighbor[0]
                    if isinstance(neighbor, (list, tuple))
                    else neighbor
                )
                if key in info:
                    r = int(info[key]["position"][0]) + offset_r
                    c = int(info[key]["position"][1]) + offset_c
                    if grid[r][c].name_zone == "blocked":
                        continue
                if key not in path:
                    self.find_all_paths(
                        connection,
                        grid,
                        info,
                        key,
                        goal,
                        path,
                        routes,
                        offset_r,
                        offset_c
                    )

        path.pop()

    def sort_paths(
        self,
        routes: list[list[str]],
        info: dict[str, dict[str, Any]],
        grid: list[list[Grid]],
        offset_r: int,
        offset_c: int,
    ) -> list[list[str]]:
        def path_cost(path: list[str]) -> tuple[float, int]:
            total_zone_cost: float = 0.0
            for node in path:
                if node in info:
                    r = int(info[node]["position"][0]) + offset_r
                    c = int(info[node]["position"][1]) + offset_c
                    if not grid[r][c].name_zone == "priority":
                        total_zone_cost += float(grid[r][c].zone)
                    total_zone_cost += 1.5
            return (total_zone_cost, len(path))
        return sorted(routes, key=path_cost)

    def main(
        self
    ) -> tuple[
        dict[str, dict[str, Any]],
        dict[str, list[list[str | int]]],
        list[list[str]]
    ] | None:
        dic = make_a_dictionary()
        start_name: str | None = None
        end_name: str | None = None
        start: tuple[int, int] | None = None
        end: tuple[int, int] | None = None
        try:
            for key, value in dic.items():

                if key.strip() == "start_hub":
                    v_split = value[0].split("[")[0].split()
                    if len(v_split) != 3:
                        print("Error: invalid start_hub")
                        return None

                    start_name = v_split[0]
                    start = (int(v_split[1]), int(v_split[2]))

                elif key.strip() == "end_hub":
                    d_split = value[0].split("[")[0].split()
                    if len(d_split) != 3:
                        print("Error: invalid start_hub")
                        return None
                    end_name = d_split[0]
                    end = (int(d_split[1]), int(d_split[2]))

            result = check_hub(dic["hub"])

            if not result or isinstance(result, bool):
                return None

            info, connection = result
            if (
                start is None
                or end is None
                or start_name is None
                or end_name is None
            ):
                return None

            information_info = self.ft_info(info, start, end)
            if not information_info:
                sys.exit()
            grid, offset_r, offset_c = information_info

            routes: list[list[str]] = []
            self.find_all_paths(
                connection,
                grid,
                info,
                start_name,
                end_name,
                [],
                routes,
                offset_r,
                offset_c
            )
            sorted_routes = self.sort_paths(
                routes,
                info,
                grid,
                offset_r,
                offset_c
            )

            return info, connection, sorted_routes
        except (ValueError, TypeError, IndexError):
            print("Error: invalid ")
            sys.exit()

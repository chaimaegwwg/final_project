from parsing import make_a_dictionary, check_hub
import re
import sys

# mission is make 2 array and display the place
# mission tomorrow is for make sure for parsing also add attribuite like the cost
# mission make sure u understand the dijikstra and do it
# the finale parsing for the part of connection


class Grid:

    def __init__(
        self,
        name,
        row,
        col,
        zone=0,
        color=0,
        max_drones=0,
        visited=0,
        value=0,
    ):
        self.name = name
        self.row = row
        self.col = col
        self.zone = zone
        self.color = color
        self.max_drones = max_drones
        self.place = 0
        self.value = value
        self.visited = False


# def display(grid, start, end):
#     start_row, start_col = start
#     end_row, end_col = end
#     end_col = end_col + 1
#     end_row = end_row + 1
#     for x in range(start_row, end_row):
#         for y in range(start_col, end_col):
#             if grid[x][y].place == 1:
#                 print(" + ", end="")
#             else:
#                 print(" - ", end="")

#         print()


def ft_info(info, start, end):
    start_row, start_col = start
    end_row, end_col = end
    grid = []
    max_r = max(start_row, end_row)
    max_c = max(start_col, end_col)
    for key, value in info.items():
        r, c = value["position"]
        max_r = max(max_r, int(r))
        max_c = max(max_c, int(c))
    for x in range(0, max_r + 1):
        row_list = []
        for y in range(0, max_c + 1):
            step = Grid("anonymous", x, y)
            row_list.append(step)
        grid.append(row_list)

    try:
        grid[start_row][start_col].name = "start_hub"
        grid[start_row][start_col].place = 0
        grid[end_row][end_col].name = "start_end"
        grid[end_row][end_col].place = 5
        grid[end_row][end_col].zone = 5
    except IndexError:
        sys.exit()

    for key, value in info.items():
        row, col = value["position"]
        row = int(row)
        col = int(col)
        name = value["name"]
        if row > end_row or col > end_col:
            continue

        try:
            zone_str = str(value.get("zone", "normal")).lower()

            if zone_str in ("normal", "priority"):
                zone = 1
            elif zone_str == "restricted":
                zone = 2
            elif zone_str == "blocked":
                zone = float("inf")
            else:
                zone = 1
        except:
            zone = 1
        try:
            max_drone = value["max_drones"]
            max_drone = int(max_drone)
        except:
            max_drone = 0
        try:
            color = value["color"]
        except:
            color = 0
        grid[row][col].zone = zone
        grid[row][col].visited = False
        grid[row][col].place = 1
        grid[row][col].name = name
        grid[row][col].color = color
        grid[row][col].max_drones = max_drone

    return grid

# if isinstance(neighbor, list):
            # else:
            #     key = neighbor


def find_all_paths(connection, grid, info, current, goal, path, routes):
    path.append(current)
    if current == goal:
        routes.append(path.copy())
    else:
        neighbors = connection.get(current, [])
        print("here the neighbors",neighbors)
        for neighbor in neighbors:
            print(neighbor)
            key = neighbor[0]
            if key in info:
                r, c = (int(info[key]["position"][0]),int(info[key]["position"][1]))
                if grid[r][c].zone == float("inf"):
                    continue
            if key not in path:
                find_all_paths(connection, grid, info, key, goal, path, routes)
    print("here where it s",path[-1])
    path.pop()

def sort_paths(routes, info, grid):
    def path_cost(path):
        total_zone_cost = 0
        for node in path:
            if node in info:
                r = int(info[node]["position"][0])
                c = int(info[node]["position"][1])
                if grid[r][c].zone == "priority":
                    total_zone_cost+= 1.5
                total_zone_cost += grid[r][c].zone
        return (total_zone_cost, len(path))

    return sorted(routes, key=path_cost)

def main():
    dic = make_a_dictionary()
    position = []
    lst_position = []
    for key, value in dic.items():
        if key.strip() == "start_hub":
            for x in value:
                v = x.split()
                start = (int(v[1]), int(v[2]))
                v = start
        if key.strip() == "end_hub":
            for x in value:
                d = x.split()
                end = (int(d[1]), int(d[2]))
                d = end

    dic = make_a_dictionary()
    info, connection = check_hub(dic["hub"])
    info["hub"] = {
        "name": "hub",
        "position": v,
        "zone": "first",
        "max_drones": dic["nb_drones"],
    }
    info["goal"] = {
        "name": "goal",
        "position": d,
        "zone": "normal",
        "max_drones": dic["nb_drones"],
    }
    grid = ft_info(info, start, end)

    # DIRECT FIX: Passed `grid` and `info` as required by find_all_paths signature
    routes = []
    find_all_paths(connection, grid, info, "hub", "goal", [], routes)

    print("Found routes:", routes)
    sorted_routes = sort_paths(routes, info, grid)

    print("Found routes (sorted):", sorted_routes)
    return info, connection, sorted_routes


main()




# from parsing import make_a_dictionary,check_hub
# import re
# import sys
# #mission is make 2 array and display the place 
# #mission tomorrow is for make sure for parsing also add attribuite like the cost 
# #mission make sure u understand the dijikstra and do it 
# # the finale parsing for the part of connection

# class Grid:
#     def __init__(self,name, row, col, zone=0, color =0, max_drones = 0,visited=0,value=0):
#         self.name = name 
#         self.row = row
#         self.col = col
#         self.zone = zone
#         self.color = color
#         self.max_drones = max_drones
#         self.place = 0
#         self.value = value
#         self.visited = False

# def display(grid, start , end):
#     start_row, start_col = start
#     end_row, end_col = end
#     end_col = end_col+1
#     end_row = end_row+1
#     for x in range(start_row, end_row):
#         for y in range(start_col, end_col):
#             if grid[x][y].place == 1:
#                 print(" + ",end="")
#             else:
#                 print(" - ",end="")
 
#         print()
    
# def ft_info(info, start,end):
#     start_row, start_col = start 
#     end_row ,end_col = end
#     grid = []
#     max_r = max(start_row, end_row)
#     max_c = max(start_col, end_col)
#     for key, value in info.items():
#         r, c = value["position"]
#         max_r = max(max_r, int(r))
#         max_c = max(max_c, int(c))
#     for x in range(0, max_r + 1):
#         row_list = []
#         for y in range(0, max_c + 1):
#             step = Grid("anonymous", x, y)
#             row_list.append(step)
#         grid.append(row_list)
  
#     try:
#         grid[start_row][start_col].name = "start_hub"
#         grid[start_row][start_col].place = 0
#         grid[end_row][end_col].name = "start_end"
#         grid[end_row][end_col].place = 5
#         grid[end_row][end_col].zone = 5
#     except IndexError:
#         # print(f"ERROR: Cannot access grid[{end_row}][{end_col}]. Max indices are [{max_r}][{max_c}]")
#         sys.exit()
    
#     for key , value in info.items():
#         row , col =value["position"]
#         row = int(row)
#         col = int(col)
#         name = value["name"]
#         if row > end_row or col > end_col:
#             continue
            
#         try:
#             zone = value["zone"]
#             if zone == "priority":
#                 zone = 1
#             elif zone == "normal":
#                 zone = 5
#             elif zone == "restricted":
#                 zone = 20
#             elif zone == "first":
#                 zone = 0
#             else:
#                 zone = float('inf')
#         except:
#             zone = 0
#         try:
#             max_drone = value["max_drones"]
#             max_drone = int(max_drone)
#         except:
#             max_drone = 0
#         try:
#             color = value["color"]
#         except:
#             color = 0
#         grid[row][col].zone = zone
#         grid[row][col].visited = False
#         grid[row][col].place = 1
#         grid[row][col].name = name
#         grid[row][col].color = color
#         grid[row][col].max_drones = max_drone
        
#     return grid


# # def choice_the_path(places,info,grid,dic,visited,val,current_place,path):
# #     com = float('inf')
# #     name = None
# #     for i in places:
# #         key = i[0]
# #         row ,col= info[key]["position"]
# #         row = int(row)
# #         col = int(col)
# #         zone = grid[row][col].zone
# #         # here we see if it this value is small than the previous one
# #         # if key not in dic or (val + zone) < dic[key]:
# #         #     dic[key] = val + zone
# #         #     path[key] = current_place
# #         new_value = val + zone
# #         if key not in dic or new_value < dic[key]:
# #             dic[key] = new_value
# #             path[key] = [current_place]

# #         elif new_value == dic[key]:
# #             path[key].append(current_place)
# #     # the second loop is for choose the small one name com is for the compar
# #     for node,v in dic.items():
# #         if node not in visited and v < com:
# #             print("the first com",com)
# #             com = v
# #             name = node
# #     return name,dic

# def build_paths(path, current="goal"):
#     if current == "hub":
#         return [["hub"]]

#     routes = []
#     print("pathhhhh",path)
#     for previous in path.get(current, []):
#         previous_routes = build_paths(path, previous)

#         for route in previous_routes:
#             routes.append(route + [current])
#     print("jkhjkh",routes)
#     return routes

# def find_all_paths(connection, current, goal, path, routes):
#     path.append(current)

#     if current == goal:
#         routes.append(path.copy())
#     else:
#         for neighbor in connection.get(current, []):
#             if neighbor not in path:
#                 find_all_paths(connection, neighbor, goal, path, routes)

#     path.pop()
# # def build_paths(path):
# #     routes = []

# #     def find_path(current, route):
# #         if current == "hub":
# #             routes.append(["hub"] + route[::-1])
# #             return

# #         for previous in path.get(current, []):
# #             find_path(previous, route + [current])

# #     find_path("goal", [])
# #     print("theeeee",routes)

# #     return routes
# # def dijikstra(connection, info,grid):
# #     place = "hub"
# #     path = {}
# #     visited = []
# #     value = 0
# #     dic = {"hub": 0}
# #     routes = []
# #     while place is not None:

# #         row ,col= info[place]["position"]
# #         row = int(row)
# #         col = int(col)

# #         if place not in visited:
# #             grid[row][col].visited =True
# #             visited.append(place)
    
# #         value = dic[place]
# #         print("valueee",value, dic)
# #         neighbors = connection.get(place, [])
# #         name , dic = choice_the_path(neighbors,info,grid,dic,visited,value,place,path) 
# #         if name is None:
# #             break
# #         if name == "goal":
# #             lst = [v for k, v in dic.items() if k not in visited]
# #             print("list    ",lst)
# #             if lst:
# #                 m_min = min(lst)
# #             else:
# #                 m_min = float('inf')
# #             print("min",m_min,dic["goal"])
# #             # if on the list there are only the goal is min
# #             if dic["goal"] <= m_min:
# #                 place = "goal"
# #                 route = build_paths(path)
# #                 routes.extend(route)
# #             else:
# #                 break
# #         place = name
# #         value = dic[name]
# #     # if name == "goal":
# #     #     routes = build_paths(path)
# #     print("teeees",routes)

# #     return routes
#     # route = []
#     # if name == "goal":
#     #     route = []
#     #     curr = "goal"
#     #     while curr in path:
#     #         route.append(curr)
#     #         curr = path[curr]
#     #     route.append("hub") 
#     #     route.reverse() 
    
# def choice_the_path(places, info, grid, dic, visited, val, current_place, path):
#     com = float('inf')
#     name = None

#     for i in places:
#         key = i[0] if isinstance(i, (list, tuple)) else i
        
#         row, col = info[key]["position"]
#         row, col = int(row), int(col)
#         zone = grid[row][col].zone

#         if zone == float('inf'):
#             continue

#         new_value = val + zone

#         # ------------------- MINIMAL CHANGE START -------------------
#         # 1. Strictly cheaper path found: clear and set new minimum
#         if key not in dic or new_value < dic[key]:
#             dic[key] = new_value
#             path[key] = [current_place]

#         # 2. ALSO record alternative paths (even if slightly higher cost)
#         # Change '==' to '<=' with a cost tolerance (e.g. +30 allows roof1/roof2)
#         elif new_value <= dic[key] + 30:
#             if key not in path:
#                 path[key] = []
#             if current_place not in path[key]:
#                 path[key].append(current_place)
#         # ------------------- MINIMAL CHANGE END ---------------------

#     for node, v in dic.items():
#         if node not in visited and v < com:
#             com = v
#             name = node

#     return name, dic


# def dijikstra(connection, info, grid):
#     place = "hub"
#     path = {}
#     visited = []
#     dic = {"hub": 0}

#     while place is not None:
#         row, col = info[place]["position"]
#         row, col = int(row), int(col)

#         if place not in visited:
#             grid[row][col].visited = True
#             visited.append(place)

#         value = dic[place]

#         # CRITICAL FIX: Do NOT expand neighbors out of "goal" back into the grid
#         if place != "goal":
#             neighbors = connection.get(place, [])
#             name, dic = choice_the_path(neighbors, info, grid, dic, visited, value, place, path)
#         else:
#             # If at goal, find next unvisited node without processing goal's neighbors
#             com = float('inf')
#             name = None
#             for node, v in dic.items():
#                 if node not in visited and v < com:
#                     com = v
#                     name = node

#         if name is None:
#             break

#         place = name

#     # Reconstruct all recorded paths recursively
#     routes = []
#     if "goal" in path:
#         routes = build_paths(path, current="goal")

#     print("Found routes:", routes)
#     return routes
# # def choice_the_path(places, info, grid, dic, visited, val, current_place, path):
# #     com = float('inf')
# #     name = None

# #     for i in places:
# #         # Handles both simple node names ["A"] or tuple/list structure [("A", ...)]
# #         key = i[0] if isinstance(i, (list, tuple)) else i
        
# #         row, col = info[key]["position"]
# #         row, col = int(row), int(col)
# #         zone = grid[row][col].zone

# #         new_value = val + zone

# #         # Found a strictly better path: overwrite previous predecessors
# #         if key not in dic or new_value < dic[key]:
# #             dic[key] = new_value
# #             path[key] = [current_place]

# #         # Found an EQUAL-cost alternative path: save this predecessor too!
# #         elif new_value == dic[key]:
# #             if current_place not in path[key]:
# #                 path[key].append(current_place)

# #     # Find the next unvisited node with the lowest distance value
# #     for node, v in dic.items():
# #         if node not in visited and v < com:
# #             com = v
# #             name = node

# #     return name, dic

# # def dijikstra(connection, info, grid):
# #     place = "hub"
# #     path = {}
# #     visited = []
# #     dic = {"hub": 0}

# #     # Process all reachable nodes
# #     while place is not None:
# #         row, col = info[place]["position"]
# #         row, col = int(row), int(col)

# #         if place not in visited:
# #             grid[row][col].visited = True
# #             visited.append(place)

# #         value = dic[place]
# #         neighbors = connection.get(place, [])

# #         # Added 'visited' into the 5th position to match the function definition
# #         name, dic = choice_the_path(neighbors, info, grid, dic, visited, value, place, path)

# #         if name is None:
# #             break

# #         place = name

# #     # Once the entire graph is explored, reconstruct ALL optimal paths
# #     routes = []
# #     if "goal" in path:
# #         routes = build_paths(path, current="goal")

# #     print("Found routes:", routes)
# #     return routes

# def main():
#     dic = make_a_dictionary()
#     position = []
#     lst_position = []
#     for key, value in dic.items():
#         if key.strip() == "start_hub":
#             for x in value:
#                 v = x.split()
#                 start = (int(v[1]),int(v[2]))
#                 v = start
#         if key.strip() == "end_hub":
#             for x in value:
#                 d = x.split()
#                 end = (int(d[1]),int(d[2]))
#                 d = end 
#     dic = make_a_dictionary()
#     info,connection = check_hub(dic["hub"])
#     info["hub"] = {"name": "hub", "position": v, "zone": "first", "max_drones": dic["nb_drones"]}
#     info["goal"] = {"name": "goal", "position": d, "zone": "normal", "max_drones": dic["nb_drones"]}
#     grid = ft_info(info, start,end)
#     path = dijikstra(connection,info,grid)
#     return info,connection,path

# main()

import sys
import random
import pygame
from logic import main
from parsing import check_validation


class Zones:
    def __init__(self, name, row, col, max_capacity):
        self.name = name
        self.x = int(col) * 50 + 25
        self.y = int(row) * 50 + 25
        self.max_capacity = max_capacity
        self.current_drones = 0


class Drones:
    def __init__(self, speed, start_x, start_y, info, path, zones_dict, connection_data):
        self.speed = speed
        self.x = float(start_x)
        self.y = float(start_y)
        self.connection_data = connection_data
        self.path = path  # e.g., ['hub', 'roof1', 'corridorA', 'goal']
        self.info = info
        self.cap_zones = zones_dict
        self.step = 0
        self.active = False
        self.reached_goal = False

        if len(self.path) > 1:
            next_node = self.path[1]
            self.target_x = float(self.cap_zones[next_node].x)
            self.target_y = float(self.cap_zones[next_node].y)
        else:
            self.target_x = self.x
            self.target_y = self.y

    def move(self):
        if not self.active or self.reached_goal:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # 1. Move toward current target
        if distance > 3:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        else:
            # 2. Reached current waypoint target
            current_node_name = self.path[self.step]
            target_node_name = self.path[self.step + 1]

            # Snap drone directly onto target waypoint
            self.x = float(self.cap_zones[target_node_name].x)
            self.y = float(self.cap_zones[target_node_name].y)

            # Update occupancy step counters
            current_z = self.cap_zones[current_node_name]
            target_z = self.cap_zones[target_node_name]

            if self.step > 0:
                current_z.current_drones = max(0, current_z.current_drones - 1)

            self.step += 1

            # Check if drone reached final goal node
            if self.step >= len(self.path) - 1:
                self.reached_goal = True
                if target_node_name != self.path[-1]:
                    target_z.current_drones = max(0, target_z.current_drones - 1)
                return

            # Set target coordinates for next leg of path
            next_node_name = self.path[self.step + 1]
            self.target_x = float(self.cap_zones[next_node_name].x)
            self.target_y = float(self.cap_zones[next_node_name].y)


def func():
    info, connection, paths = main()
    pygame.init()

    if paths and isinstance(paths[0], str):
        paths = [paths]

    try:
        nb_drones = check_validation()
    except Exception:
        nb_drones = 999

    start_node = paths[0][0]
    end_node = paths[0][-1]

    row, col = info[start_node]["position"]
    drone_x = int(col) * 50 + 25
    drone_y = int(row) * 50 + 25

    font = pygame.font.SysFont("arial", 14)
    RED = (255, 0, 0)

    max_row = max(int(value["position"][0]) for value in info.values())
    max_col = max(int(value["position"][1]) for value in info.values())

    win_w = max((max_col + 1) * 50 + 100, 600)
    win_h = max((max_row + 1) * 50 + 100, 600)

    try:
        icon = pygame.image.load("iconn.png")
        icon = pygame.transform.scale(icon, (25, 25))
    except Exception:
        icon = None

    screen = pygame.display.set_mode((win_w, win_h))
    clock = pygame.time.Clock()

    zones = {}
    for name, data in info.items():
        x, y = data["position"]
        raw_cap = data.get("max_drones", 1)
        if isinstance(raw_cap, (list, tuple)):
            raw_cap = raw_cap[0] if raw_cap else 1
        max_drones = int(raw_cap)

        max_cap = float("inf") if name in (start_node, end_node) else max_drones
        zones[name] = Zones(name, x, y, max_cap)

    all_drones = []
    fixed_speed = 2.5
    for idx in range(nb_drones):
        assigned_path = paths[idx % len(paths)]
        d = Drones(fixed_speed, drone_x, drone_y, info, assigned_path, zones, connection)
        all_drones.append(d)

    waiting_drones = list(all_drones)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        draw_edges = set()

        # Launch drone if capacity permits
        if waiting_drones:
            candidate = waiting_drones[0]
            first_step_node = candidate.path[1]
            first_zone = zones[first_step_node]

            if first_zone.current_drones < first_zone.max_capacity:
                launched_drone = waiting_drones.pop(0)
                launched_drone.active = True
                first_zone.current_drones += 1

        # Draw nodes & edges
        for key, value in info.items():
            r, c = value["position"]
            x = int(c) * 50 + 25
            y = int(r) * 50 + 25
            pygame.draw.circle(screen, RED, (x, y), 7)
            text = font.render(key, True, (255, 255, 255))
            screen.blit(text, (x + 5, y - 15))

            for neighbor in connection.get(key, []):
                n_name = neighbor[0]
                pairs = tuple(sorted([key, n_name]))
                if pairs in draw_edges:
                    continue
                draw_edges.add(pairs)

                r2, c2 = info[n_name]["position"]
                x2 = int(c2) * 50 + 25
                y2 = int(r2) * 50 + 25
                color = info[n_name].get("color", (255, 255, 255))
                pygame.draw.line(screen, color, (x, y), (x2, y2), 2)

        # Update & draw active drones
        for d in all_drones:
            if d.active and not d.reached_goal:
                d.move()
                if icon:
                    screen.blit(icon, (int(d.x) - 12, int(d.y) - 12))
                else:
                    pygame.draw.circle(screen, (0, 255, 0), (int(d.x), int(d.y)), 5)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    func()

# import pygame
# import sys
# import random
# from logic import main
# from parsing import check_validation

# class Zones:
#     def __init__(self, name, row, col, max_link_capacity):
#         self.name = name
#         self.x = int(col) * 50 + 25
#         self.y = int(row) * 50 + 25
#         self.max_link_capacity = max_link_capacity
#         self.current_drones = 0

# class Drones:
#     def __init__(self, speed, start_x, start_y, info, path, zones_dict, connection_data):
#         self.speed = speed 
#         self.x = float(start_x)
#         self.y = float(start_y)
#         self.connection_data = connection_data
#         self.path = path  # Assigned single route: ['hub', 'A', 'B', 'goal']
#         self.info = info
#         self.cap_zones = zones_dict
#         self.step = 0
#         self.active = False  # Track if drone has left the waiting queue

#         if len(self.path) > 1:
#             next_node = self.path[1]
#             self.target_x = float(self.cap_zones[next_node].x)
#             self.target_y = float(self.cap_zones[next_node].y)
#         else:
#             self.target_x = self.x
#             self.target_y = self.y

#     def move(self):
#         # Do not process movement if drone is still waiting to enter start zone
#         if not self.active:
#             return

#         dx = self.target_x - self.x
#         dy = self.target_y - self.y
#         distance = (dx ** 2 + dy ** 2) ** 0.5

#         if distance > 2: 
#             self.x += (dx / distance) * self.speed
#             self.y += (dy / distance) * self.speed
#         else:
#             if self.step + 1 < len(self.path):
#                 current_z = self.cap_zones[self.path[self.step]]
#                 next_z = self.cap_zones[self.path[self.step + 1]]

#                 current_name = self.path[self.step]
#                 next_name = self.path[self.step + 1]

#                 # Link capacity logic
#                 if next_name == self.path[-1] or current_name == self.path[0]:
#                     link_cap = 999
#                 else:
#                     link_cap = 1
#                     for neighbor in self.connection_data.get(current_name, []):
#                         if neighbor[0] == next_name:
#                             link_cap = neighbor[1]
#                             break
                

#                 if next_z.current_drones < link_cap and next_z.current_drones < next_z.max_link_capacity:
#                     current_z.current_drones -= 1
#                     next_z.current_drones += 1

#                     self.target_x = float(next_z.x)
#                     self.target_y = float(next_z.y)
#                     self.step += 1
#                 else:
#                     pass
#             else:
#                 pass

# def func():
#     info, connection, paths = main()
#     pygame.init()

#     # Handle single path vs multiple paths return format
#     if paths and isinstance(paths[0], str):
#         paths = [paths]

#     try:
#         nb_drones = check_validation()
#     except:
#         sys.exit()

#     # Determine start hub position from the first path
#     start_node = paths[0][0]
#     end_node = paths[0][-1]
#     row, col = info[start_node]["position"]
#     drone_x = int(col) * 50 + 25
#     drone_y = int(row) * 50 + 25

#     font = pygame.font.SysFont("arial", 14)
#     RED = (255, 0, 0)

#     max_row = max(int(value["position"][0]) for value in info.values())
#     max_col = max(int(value["position"][1]) for value in info.values())

#     i = (max_col + 1) * 50
#     j = (max_row + 1) * 50
#     try:
#         icon = pygame.image.load('iconn.png')
#         icon = pygame.transform.scale(icon, (35, 35))
#     except:
#         icon = None

#     screen = pygame.display.set_mode((i, j))
#     clock = pygame.time.Clock()
    
#     # Initialize Zones
#     zones = {}
#     for name, data in info.items():
#         x, y = data["position"]
#         max_drones = data.get("max_drones", 1)

#         max_cap = max_drones
#         # Only destination goal hub gets infinite capacity (Start hub cap = 1)
#         if name == end_node:
#             max_cap = float('inf')
#         elif name == start_node:
#             max_cap = 1

#         zones[name] = Zones(name, x, y, max_cap)

#     all_drones = []
    
#     # Create all drones in waiting state
#     for inde_x in range(nb_drones):
#         assigned_path = paths[inde_x % len(paths)]
        
#         if nb_drones < 40:
#             speed = random.uniform(1.0, 2.5)
#         elif nb_drones < 300:
#             speed = random.uniform(0.5, 1.5)
#         else:
#             speed = random.uniform(0.6, 1.5)
            
#         d = Drones(speed, drone_x, drone_y, info, assigned_path, zones, connection)
#         all_drones.append(d)

#     waiting_drones = list(all_drones)

#     running = True
#     try:
#         while running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#             screen.fill((0, 0, 0)) 
#             draw = set()
            
#             # Release 1 drone into the start zone only when start zone is empty (current_drones < 1)
#             start_zone = zones[start_node]
#             if waiting_drones and start_zone.current_drones < start_zone.max_link_capacity:
#                 next_drone = waiting_drones.pop(0)
#                 next_drone.active = True
#                 start_zone.current_drones += 1
#             # for path in paths:
#             #     first_node = path[1]
#             #     target_zone = zones[first_node]
                
#             #     # Find link capacity from start_node to the first node
#             #     link_cap = 999
#             #     for neighbor in connection.get(start_node, []):
#             #         if neighbor[0] == first_node:
#             #             link_cap = neighbor[1]
#             #             break
                
#                 # Check if target zone has space to launch a drone for this path
#                 if target_zone.current_drones < link_cap and target_zone.current_drones < target_zone.max_link_capacity:
#                     # Find the first waiting drone assigned to this specific path
#                     for d in list(waiting_drones):
#                         if d.path == path:
#                             d.active = True
#                             target_zone.current_drones += 1
#                             waiting_drones.remove(d)
#                             break
            
#             # Draw network nodes and connections
#             for key, value in info.items():
#                 row, col = value["position"]
#                 x = int(col) * 50 + 25
#                 y = int(row) * 50 + 25
#                 pygame.draw.circle(screen, RED, (x, y), 7)
#                 text = font.render(key, True, (255, 255, 255))
#                 screen.blit(text, (x + 5, y - 15))
#                 connec = connection.get(key, [])
#                 for neighbor in connec:
#                     name = neighbor[0]
#                     pairs = tuple(sorted([key, name]))
#                     if pairs in draw:
#                         continue
#                     draw.add(pairs)
#                     row2, col2 = info[name]["position"]
#                     x2 = int(col2) * 50 + 25
#                     y2 = int(row2) * 50 + 25
#                     color = info[name].get('color', (255, 255, 255))
#                     pygame.draw.line(screen, color, (x, y), (x2, y2), 5)
            
#             # Update and draw active drones
#             for d in all_drones:
#                 if d.active:
#                     d.move()
#                     if icon:
#                         screen.blit(icon, (int(d.x) - 17, int(d.y) - 17))
#                     else:
#                         pygame.draw.circle(screen, (0, 255, 0), (int(d.x), int(d.y)), 10)
            
#             pygame.display.flip()
#             clock.tick(60)
#     except KeyboardInterrupt:
#         sys.exit()
#     pygame.quit()

# func()



# # import pygame
# # import sys
# # import random
# # from logic import main
# # from parsing import check_validation

# # class Zones:
# #     def __init__(self, name, row, col, max_link_capacity):
# #         self.name = name
# #         self.x = int(col) * 50 + 25
# #         self.y = int(row) * 50 + 25
# #         self.max_link_capacity = max_link_capacity
# #         self.current_drones = 0

# # class Drones:
# #     def __init__(self, speed, start_x, start_y, info, path, zones_dict, connection_data):
# #         self.speed = speed 
# #         self.x = float(start_x)
# #         self.y = float(start_y)
# #         self.connection_data = connection_data
# #         self.path = path  # Assigned single route: ['hub', 'A', 'B', 'goal']
# #         self.info = info
# #         self.cap_zones = zones_dict
# #         self.step = 0
        
# #         # Set initial target to step 1 (or start position if path length is 1)
# #         if len(self.path) > 1:
# #             next_node = self.path[1]
# #             self.target_x = float(self.cap_zones[next_node].x)
# #             self.target_y = float(self.cap_zones[next_node].y)
# #         else:
# #             self.target_x = self.x
# #             self.target_y = self.y

# #     def move(self):
# #         dx = self.target_x - self.x
# #         dy = self.target_y - self.y
# #         distance = (dx ** 2 + dy ** 2) ** 0.5

# #         if distance > 2: 
# #             self.x += (dx / distance) * self.speed
# #             self.y += (dy / distance) * self.speed
# #         else:
# #             if self.step + 1 < len(self.path):
# #                 current_z = self.cap_zones[self.path[self.step]]
# #                 next_z = self.cap_zones[self.path[self.step + 1]]

# #                 current_name = self.path[self.step]
# #                 next_name = self.path[self.step + 1]

# #                 # Link capacity logic
# #                 if next_name == self.path[-1] or current_name == self.path[0]:
# #                     link_cap = 999
# #                 else:
# #                     link_cap = 1
# #                     for neighbor in self.connection_data.get(current_name, []):
# #                         if neighbor[0] == next_name:
# #                             link_cap = neighbor[1]
# #                             break
                
# #                 # Check both link capacity AND destination zone node capacity
# #                 if next_z.current_drones < link_cap and next_z.current_drones < next_z.max_link_capacity:
# #                     current_z.current_drones -= 1
# #                     next_z.current_drones += 1

# #                     self.target_x = float(next_z.x)
# #                     self.target_y = float(next_z.y)
# #                     self.step += 1
# #                 else:
# #                     pass
# #             else:
# #                 pass

# # def func():
# #     info, connection, paths = main()
# #     pygame.init()

# #     # Handle single path vs multiple paths return format
# #     if paths and isinstance(paths[0], str):
# #         paths = [paths]

# #     try:
# #         nb_drones = check_validation()
# #     except:
# #         sys.exit()

# #     # Determine start hub position from the first path
# #     start_node = paths[0][0]
# #     row, col = info[start_node]["position"]
# #     drone_x = int(col) * 50 + 25
# #     drone_y = int(row) * 50 + 25

# #     font = pygame.font.SysFont("arial", 14)
# #     BLUE = (0, 0, 255)
# #     RED = (255, 0, 0)

# #     max_row = max(int(value["position"][0]) for value in info.values())
# #     max_col = max(int(value["position"][1]) for value in info.values())

# #     i = (max_col + 1) * 50
# #     j = (max_row + 1) * 50
# #     try:
# #         icon = pygame.image.load('iconn.png')
# #         icon = pygame.transform.scale(icon, (35, 35))
# #     except:
# #         icon = None

# #     screen = pygame.display.set_mode((i, j))
# #     clock = pygame.time.Clock()
    
# #     # Initialize Zones
# #     zones = {}
# #     for name, data in info.items():
# #         x, y = data["position"]
# #         max_drones = data.get("max_drones", 1)

# #         max_cap = max_drones
# #         # End hub has infinite capacity
# #         if name == paths[0][0] or name == paths[0][-1]:
# #             max_cap = float('inf')
# #         zones[name] = Zones(name, x, y, max_cap)

# #     zones[start_node].current_drones = nb_drones

# #     all_drones = []
    
# #     # Distribute drones evenly across all available paths
# #     for inde_x in range(nb_drones):
# #         assigned_path = paths[inde_x % len(paths)]
        
# #         if nb_drones < 40:
# #             speed = random.uniform(1.0, 2.5)
# #             d = Drones(speed, drone_x + (inde_x * 10), drone_y, info, assigned_path, zones, connection)
# #         elif nb_drones < 300:
# #             speed = random.uniform(0.5, 1.5)
# #             d = Drones(speed, drone_x + (inde_x * 1), drone_y, info, assigned_path, zones, connection)
# #         else:
# #             speed = random.uniform(0.6, 1.5)
# #             d = Drones(speed, drone_x + inde_x, drone_y, info, assigned_path, zones, connection)

# #         all_drones.append(d)

# #     running = True
# #     try:
# #         while running:
# #             for event in pygame.event.get():
# #                 if event.type == pygame.QUIT:
# #                     running = False
# #             screen.fill((0, 0, 0)) 
# #             draw = set()
            
# #             # Draw network nodes and connections
# #             for key, value in info.items():
# #                 row, col = value["position"]
# #                 x = int(col) * 50 + 25
# #                 y = int(row) * 50 + 25
# #                 pygame.draw.circle(screen, RED, (x, y), 7)
# #                 text = font.render(key, True, (255, 255, 255))
# #                 screen.blit(text, (x + 5, y - 15))
# #                 connec = connection.get(key, [])
# #                 for neighbor in connec:
# #                     name = neighbor[0]
# #                     pairs = tuple(sorted([key, name]))
# #                     if pairs in draw:
# #                         continue
# #                     draw.add(pairs)
# #                     row2, col2 = info[name]["position"]
# #                     x2 = int(col2) * 50 + 25
# #                     y2 = int(row2) * 50 + 25
# #                     color = info[name].get('color', (255, 255, 255))
# #                     pygame.draw.line(screen, color, (x, y), (x2, y2), 5)
            
# #             # Update and draw drones
# #             for d in all_drones:
# #                 d.move()
# #                 if icon:
# #                     screen.blit(icon, (int(d.x) - 17, int(d.y) - 17))
# #                 else:
# #                     pygame.draw.circle(screen, (0, 255, 0), (int(d.x), int(d.y)), 10)
            
# #             pygame.display.flip()
# #             clock.tick(60)
# #     except KeyboardInterrupt:
# #         sys.exit()
# #     pygame.quit()

# # func()


# # import pygame
# # import sys
# # import random
# # from logic import main
# # from parsing import check_validation
# # class Zones:
# #     def __init__(self,name,row,col,max_link_capacity):
# #         self.name = name
# #         self.x = int(col) * 50 + 25
# #         self.y = int(row) * 50 + 25
# #         self.max_link_capacity = max_link_capacity
# #         self.current_drones = 0
# # class Drones:
# #     def __init__(self, speed,start_x, start_y,info,path,zones_dict,connection_data):
# #         self.speed = speed 
# #         self.x = float(start_x)
# #         self.y = float(start_y)
# #         self.connection_data = connection_data
# #         self.path = path
# #         self.info = info
# #         self.cap_zones = zones_dict
# #         self.step = 0
    
# #         self.target_x = self.x
# #         self.target_y = self.y

# #     def move(self):
# #         dx = self.target_x - self.x
# #         dy = self.target_y - self.y
# #         distance = (dx **2 +dy **2)**0.5
# #         if distance > 2: 
# #             self.x += (dx / distance) * self.speed
# #             self.y += (dy / distance) * self.speed
# #         else:
# #             if self.step + 1 < len(self.path):
# #                 current_z = self.cap_zones[self.path[self.step]]
# #                 next_z    = self.cap_zones[self.path[self.step + 1]]

# #                 current_name = self.path[self.step]
# #                 next_name = self.path[self.step + 1]
# #                 if next_name == self.path[-1] or current_name == self.path[0]:
# #                     link_cap = 999
# #                 else:
# #                     link_cap = 1
# #                     for neighbor in self.connection_data[current_name]:
# #                         if neighbor[0] == next_name:
# #                             link_cap = neighbor[1]
# #                             break
               
# #                 if next_z.current_drones < link_cap:
# #                         current_z.current_drones -= 1
# #                         next_z.current_drones    += 1

# #                         self.target_x = next_z.x
# #                         self.target_y = next_z.y
# #                         self.step += 1
# #                 else:
# #                     pass
# #             else:
# #                 pass
# # def func():
# #     info,connection,path = main()
# #     pygame.init()
# #     # print(info)

# #     try:
# #         nb_drones = check_validation()
# #     except:
# #         sys.exit()
# #     start = path[0]
# #     row, col = info[start]["position"]
# #     drone_x = int(col) * 50 + 25
# #     drone_y = int(row) * 50 + 25

# #     index = 0
# #     target = path[index]
# #     row, col = info[target]["position"]
# #     target_x = int(col) * 50 + 25
# #     target_y = int(row) * 50 + 25
# #     index += 1

# #     font = pygame.font.SysFont("arial", 14)
# #     BLUE = (0, 0, 255)
# #     RED = (255, 0, 0)

# #     max_row = max(int(value["position"][0]) for value in info.values())
# #     max_col = max(int(value["position"][1]) for value in info.values())

# #     i = (max_col+1)*50
# #     j = (max_row+1)*50
# #     try:
# #         icon = pygame.image.load('iconn.png')
# #         icon = pygame.transform.scale(icon,(35,35))
# #     except:
# #         icon = None

# #     screen = pygame.display.set_mode((i, j))
# #     clock = pygame.time.Clock()
# #     zones = {}
# #     for name,data in info.items():
# #         x, y = data["position"]
# #         max_drones = data.get("max_drones",1)

# #         max_cap = max_drones
# #         if name == path[0] or name == path[-1]:
# #             max_cap = float('inf')
# #         zones[name] = Zones(name,x,y,max_cap)
# #     zones[path[0]].current_drones = nb_drones


# #     all_drones = []
    
# #     for inde_x in range(nb_drones):
# #         if nb_drones < 40:
# #             speed = random.uniform(1.0, 2.5)
# #             d = Drones(speed, drone_x + (inde_x * 10), drone_y, info, path,zones,connection)
# #         if nb_drones < 300:
# #             speed = random.uniform(0.5, 1.5)
# #             d = Drones(speed, drone_x + (inde_x * 1), drone_y, info, path,zones,connection)
# #         else:
# #             speed = random.uniform(0.6, 1.5)
# #             d = Drones(speed, drone_x + inde_x, drone_y, info, path,zones,connection)

    
# #         all_drones.append(d)

# #     running = True
# #     try:
# #         while running:
# #             for event in pygame.event.get():
# #                 if event.type == pygame.QUIT:
# #                     running = False
# #             screen.fill((0, 0, 0)) 
# #             draw = set()
# #             for key, value in info.items():
# #                 row , col = value["position"]
# #                 x = int(col) * 50 +50 // 2
# #                 y = int(row) * 50 + 50 // 2
# #                 pygame.draw.circle(screen, RED, (x,y), 7)
# #                 text = font.render(key, True, (255, 255, 255))
# #                 screen.blit(text, (x + 5, y - 15))
# #                 connec = connection.get(key, [])
# #                 for neighbor in connec:
# #                     name = neighbor[0]
# #                     pairs = tuple(sorted([key,name]))
# #                     if pairs in draw:
# #                         continue
# #                     draw.add(pairs)
# #                     row2 ,col2 = info[name]["position"]
# #                     x2 = int(col2) * 50 + 50//2
# #                     y2 = int(row2) * 50 + 50//2
# #                     color = info[name].get('color', (255,255,255))
# #                     pygame.draw.line(screen,color, (x,y), (x2,y2), 5)
# #             for d in all_drones:
# #                 d.move()
# #                 if icon:
# #                         screen.blit(icon, (int(d.x) - 17, int(d.y) - 17))
# #                 else:
# #                     pygame.draw.circle(screen, (0,255,0), (int(d.x), int(d.y)), 10)
            
            
# #             pygame.display.flip()
# #             clock.tick(60)
# #     except KeyboardInterrupt:
# #         sys.exit()
# #     pygame.quit()
# # func()

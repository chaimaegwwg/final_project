import pygame
from logic import main
from par import check_validation


class Zones:
    def __init__(self, name, row, col, max_capacity,min_col,min_row):
        self.name = name
        self.x = (int(col) - min_col) * 50 + 25
        self.y = (int(row) - min_row) * 50 + 25
        # self.x = int(col) * 50 + 25
        # self.y = int(row) * 50 + 25
        self.max_capacity = max_capacity
        self.current_drones = 0
class Drones:
    def __init__(self, drone_id, speed, start_x, start_y, info, path, zones_dict, connection_data):
        self.drone_id = drone_id
        self.speed = speed
        self.x = float(start_x)
        self.y = float(start_y)
        self.connection_data = connection_data
        self.path = path 
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

        if distance > 3:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            return

        # We reached path[step + 1]
        current_node_name = self.path[self.step + 1]

        self.x = float(self.cap_zones[current_node_name].x)
        self.y = float(self.cap_zones[current_node_name].y)

        # =========================
        # REACHED GOAL
        # =========================
        if current_node_name == self.path[-1]:

            self.reached_goal = True

            previous_node = self.path[self.step]
            previous_zone = self.cap_zones[previous_node]

            previous_zone.current_drones = max(
                0,
                previous_zone.current_drones - 1
            )

            print(
                "Drone",
                self.drone_id,
                "REACHED GOAL"
            )

            return

        # =========================
        # NEXT ZONE
        # =========================

        next_node_name = self.path[self.step + 2]
        next_zone = self.cap_zones[next_node_name]

        # Is next zone available?
        if next_zone.current_drones < next_zone.max_capacity:

            # Enter next zone
            next_zone.current_drones += 1

            # Leave current zone
            current_zone = self.cap_zones[current_node_name]

            current_zone.current_drones = max(
                0,
                current_zone.current_drones - 1
            )

            self.step += 1

            self.target_x = float(next_zone.x)
            self.target_y = float(next_zone.y)

            print(
                "Drone",
                self.drone_id,
                "moved:",
                current_node_name,
                "->",
                next_node_name
            )

def func():
    info, connection, paths = main()
    # print("gered",paths)
    if not paths:
        print("Error: No valid paths found by pathfinding logic.")
        return
    pygame.init()
    # print("this the path 0-------",paths[0])
    #where is the place 
    if paths and isinstance(paths[0], str):
        paths = [paths]

    try:
        nb_drones = check_validation()
    except Exception:
        nb_drones = 999
    # print("here we start <---------------------------------------->")
    # print(paths)

    start_node = paths[0][0]
    end_node = paths[0][-1]

    row, col = info[start_node]["position"]
    drone_x = int(col) * 50 + 25
    drone_y = int(row) * 50 + 25

    font = pygame.font.SysFont("arial", 14)
    RED = (255, 0, 0)

    min_row = min(int(value["position"][0]) for value in info.values())
    max_row = max(int(value["position"][0]) for value in info.values())

    min_col = min(int(value["position"][1]) for value in info.values())
    max_col = max(int(value["position"][1]) for value in info.values())
    # print("the max_row and col",max_row,max_col)

    grid_size = 50
    padding = 100

    win_w = max((max_col - min_col + 1) * grid_size + padding, 600)
    win_h = max((max_row - min_row + 1) * grid_size + padding, 600)
    # print("____the max_row and col",win_w,win_h)

    try:
        icon = pygame.image.load("iconn.png")
        icon = pygame.transform.scale(icon, (25, 25))
    except Exception:
        icon = None

    screen = pygame.display.set_mode((win_w, win_h))
    clock = pygame.time.Clock()

    zones = {}
    #we do like a padding of data to the grid
    for name, data in info.items():
        x, y = data["position"]
        raw_cap = data.get("max_drones", 1)
        if isinstance(raw_cap, (list, tuple)):
            raw_cap = raw_cap[0] if raw_cap else 1
        max_drones = int(raw_cap)

        if name in (start_node, end_node):
            max_cap = float("inf")
        else:
            max_cap = max_drones
        zones[name] = Zones(name, x, y, max_cap,min_col,min_row)

    all_drones = []
    fixed_speed = 2.5
    for idx in range(nb_drones):
        assigned_path = paths[idx % len(paths)]
        d = Drones(idx,fixed_speed,drone_x,drone_y,info,assigned_path,zones,connection)
        all_drones.append(d)

    #waiting drone is object all drone at first
    waiting_drones = list(all_drones)
    print("the drone that will waiting ",waiting_drones)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        draw_edges = set()
        #like are any drone waiting here 
        if waiting_drones:
            for candidate in waiting_drones:
            #here i take the first drone 
                first_step_node = candidate.path[1]
                #here we search about this zone 
                first_zone = zones[first_step_node]

                print("this the zone",first_zone.name,first_zone.current_drones,first_zone.max_capacity)
                if first_zone.current_drones < first_zone.max_capacity:
                    waiting_drones.remove(candidate)
                    candidate.active = True
                    first_zone.current_drones += 1
             
                    break
        #i do this for display the front and the lines
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
        for d in all_drones:
            if d.active:
                d.move()
                visual_offset_x = (d.drone_id % 5) * 12 - 24
                visual_offset_y = (d.drone_id // 5) * 12 - 12

                draw_x = int(d.x) + visual_offset_x
                draw_y = int(d.y) + visual_offset_y

                if icon:
                    screen.blit(icon,(draw_x - 12, draw_y - 12))
                else:
                    color = (0, 255, 0) if not d.reached_goal else (0, 150, 255)
                    pygame.draw.circle(
                        screen,color,(draw_x, draw_y),5)

                id_text = font.render(f"D{d.drone_id}",True,(255, 255, 0))
                screen.blit(id_text,(draw_x + 8, draw_y - 8))
        # for d in all_drones:
            # if d.active and not d.reached_goal:
            #     d.move()
            #     if icon:
            #         screen.blit(icon, (int(d.x) - 12, int(d.y) - 12))
            #     else:
            #         pygame.draw.circle(screen, (0, 255, 0), (int(d.x), int(d.y)), 5)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    func()

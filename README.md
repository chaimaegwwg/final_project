*This project has been created as part of the 42 curriculum by <cramadan>.*

# Fly-in

## Description

**Fly-in** is a drone traffic simulation project developed as part of the 42 curriculum.

The goal of the project is to simulate multiple drones traveling through a network of hubs and connections from a starting hub to a destination hub while respecting different constraints.

The input configuration describes:

* The number of drones.
* The starting hub.
* The destination hub.
* Intermediate hubs.
* Connections between hubs.
* Hub capacities.
* Connection capacities.
* Special zones, such as restricted zones.
* Optional colors for visual representation.

The program parses the configuration, validates the input, calculates possible routes, and then simulates the movement of the drones turn by turn.

The simulation must take into account:

* Hub capacity limits.
* Connection capacity limits.
* Restricted zones.
* Multiple drones using the same or different routes.
* Deadlocks where drones can no longer move.
* The completion of drones reaching the destination.

---

## Features

* Configuration file parsing.
* Input validation.
* Graph construction from hubs and connections.
* Pathfinding between the starting hub and destination.
* Support for multiple possible paths.
* Drone assignment to available paths.
* Hub capacity management.
* Connection capacity management.
* Restricted-zone handling.
* Turn-by-turn drone simulation.
* Terminal-based colored output.
* Detection of simulation deadlocks or excessive execution time.
* Final simulation statistics.

---

## Algorithm

### Graph Representation

The map is represented as a graph.

Each hub is a **node**, while each connection between two hubs is an **edge**.

For example:

```text
start ---- hub1 ---- hub2 ---- goal
   \                    /
    ------ hub3 --------
```

The program stores the connections using a dictionary where each hub contains its neighboring hubs.

This representation allows the pathfinding algorithm to efficiently access the nodes connected to the current hub.

### Pathfinding

The pathfinding part of the project is responsible for finding routes from the starting hub to the destination hub.

The implementation explores the graph and stores possible routes instead of keeping only a single shortest route.

After the routes are generated, cyclic paths are removed. A path is considered valid when a hub does not appear more than once in the same path.

The resulting paths are sorted according to their length so that shorter routes can be considered first.

For example:

```text
start -> A -> B -> goal
start -> C -> D -> goal
```

Both routes can be kept and assigned to different drones.

### Path Assignment

Once the available routes are calculated, drones are assigned to the available paths.

The assignment uses the available routes cyclically:

```text
Drone 1 -> Path 1
Drone 2 -> Path 2
Drone 3 -> Path 1
Drone 4 -> Path 2
```

This allows the simulation to distribute drones across multiple routes instead of forcing every drone to use the same path.

### Capacity Management

Each hub has a maximum capacity.

For example:

```text
hub: bottleneck 1 0 [max_drones=2]
```

means that at most two drones can occupy the hub at the same time.

Connections can also have capacities:

```text
connection: start-bottleneck [max_link_capacity=2]
```

The simulation tracks the current number of drones using each connection.

A drone can only enter a hub or connection when its capacity allows the movement.

### Restricted Zones

Some hubs can be marked as restricted:

```text
hub: tunnel 4 0 [zone=restricted]
```

When a drone enters a restricted zone, the simulation treats its movement differently from a normal hub.

The drone temporarily enters a transit state:

```text
in_transit = True
```

The transit state stores:

* The number of turns remaining.
* The destination of the transit.
* The connection currently being used.

After the required transit time has passed, the drone leaves the restricted zone and continues along its route.

### Turn-Based Simulation

The simulation runs one turn at a time.

During each turn:

1. Active drones attempt to move.
2. Connection capacity is checked.
3. Destination hub capacity is checked.
4. Restricted zones are handled.
5. Occupied hub capacities are updated.
6. Connections are released when a drone leaves them.
7. Waiting drones attempt to enter the simulation.
8. The movements performed during the turn are displayed.

The simulation finishes when all drones reach the destination.

A maximum turn limit is also used to prevent an infinite simulation.

---

## Visual Representation

The project provides a terminal-based visual representation of the simulation.

Colors can be specified in the configuration file:

```text
start_hub: start 0 0 [color=green]
hub: bottleneck 1 0 [color=orange]
hub: wide_area 2 0 [color=blue]
end_hub: goal 3 0 [color=red]
```

The colors are handled separately from the simulation logic in `colors.py`.

This separation allows the simulation and visualization code to remain independent.

During execution, hub names displayed in drone movements use their configured colors.

For example:

```text
Turn 1: D1-bottleneck D2-bottleneck
Turn 2: D1-wide_area D2-wide_area
Turn 3: D1-goal D2-goal
```

The colors make it easier to distinguish different hubs and understand the movement of drones directly from the terminal.

The visualization is optional and does not affect the pathfinding or simulation algorithms.

---

## Input Format

The program uses a configuration file describing the simulation.

A simple example is:

```text
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: bottleneck 1 0 [color=orange max_drones=2]
hub: wide_area 2 0 [color=blue max_drones=3]
end_hub: goal 3 0 [color=red]

connection: start-bottleneck [max_link_capacity=4]
connection: bottleneck-wide_area [max_link_capacity=2]
connection: wide_area-goal [max_link_capacity=3]
```

The configuration defines four drones, a starting hub, two intermediate hubs, a destination, and connections between them.

---

## Example

### Input

```text
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: bottleneck 1 0 [color=orange max_drones=2]
hub: wide_area 2 0 [color=blue max_drones=3]
end_hub: goal 3 0 [color=red]

connection: start-bottleneck [max_link_capacity=4]
connection: bottleneck-wide_area [max_link_capacity=2]
connection: wide_area-goal [max_link_capacity=3]
```

### Expected Output

A possible execution is:

```text
Turn 1: D1-bottleneck D2-bottleneck
Turn 2: D1-wide_area D2-wide_area
Turn 3: D1-goal D2-goal
Turn 4: D3-bottleneck D4-bottleneck
Turn 5: D3-wide_area D4-wide_area
Turn 6: D3-goal D4-goal

------------------------------
FINISHED
Drones reached goal: 4/4
Total turns: 6
```

The exact output can vary depending on the pathfinding result, capacities, and simulation scheduling.

---

## Project Structure

A possible project structure is:

```text
.
├── configuration.txt
├── parsing.py
├── logic.py
├── colors.py
├── main.py
└── README.md
```

### `parsing.py`

Responsible for reading and validating the configuration file.

It extracts information such as:

* Number of drones.
* Hubs.
* Connections.
* Colors.
* Zone types.
* Capacity values.

### `logic.py`

Contains the pathfinding and graph-related logic.

It calculates the possible routes that drones can use.

### `colors.py`

Contains the terminal color definitions and functions used to display hubs with their configured colors.

### `main.py`

Contains the drone simulation.

It manages:

* Drone objects.
* Hub capacities.
* Connection capacities.
* Drone movement.
* Restricted zones.
* Turn management.
* Final statistics.

### `configuration.txt`

Contains the input map and simulation parameters.

---

## Installation

The project requires Python 3.

Install the required dependencies if the project contains external Python packages:

```bash
pip install -r requirements.txt
```

If the project only uses Python standard-library modules, no additional package installation is required.

---

## Execution

Run the program with:

```bash
python main.py
```

Make sure that the configuration file is available in the expected location before starting the program.

---

## Resources

The following resources were useful for understanding and implementing the project:

* Python documentation — https://docs.python.org/3/
* Python typing documentation — https://docs.python.org/3/library/typing.html
* Python `math` documentation — https://docs.python.org/3/library/math.html
* Graph theory concepts — https://en.wikipedia.org/wiki/Graph_theory
* Depth-first search — https://en.wikipedia.org/wiki/Depth-first_search
* Dijkstra's algorithm — https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
* ANSI escape codes for terminal colors — https://en.wikipedia.org/wiki/ANSI_escape_code

### AI Usage

AI was used for:

* Discussing pathfinding strategies such as DFS and Dijkstra's algorithm.
* Get explanations about pathfinding, and capacity management.

---

## Technical Choices

Python was chosen because it provides convenient data structures such as dictionaries and lists, which are useful for representing graphs, paths, hubs, connections, and drone states.

Object-oriented programming is used to represent the main entities of the simulation:

* `Drones`
* `Zones`
* `Connections`

Separating parsing, pathfinding, color handling, and simulation logic into different modules makes the project easier to maintain and debug.

The simulation uses explicit state variables for drones and capacities so that every movement can be evaluated according to the current state of the system.

---

## Limitations

The simulation depends on the correctness of the input configuration.

Very large numbers of drones or extremely complex graphs can increase the amount of computation required, especially when many possible paths exist.

A maximum turn limit is used to prevent the program from running indefinitely in situations where drones become unable to reach the destination.

---

## Conclusion

Fly-in demonstrates graph representation, pathfinding, object-oriented programming, input parsing, resource management, and turn-based simulation.

The project combines these concepts to simulate multiple drones navigating a constrained network while providing a simple colored terminal representation of their movements.

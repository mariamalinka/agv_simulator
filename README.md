# AGV Warehouse Simulator

## Overview

This project implements a simulation of an intelligent warehouse with multiple Autonomous Guided Vehicles (AGVs).

The simulator generates transport tasks between pickup and delivery locations, assigns those tasks to available robots, plans collision-free routes, and records performance metrics for later analysis.

The project is also used as an experimental platform to study two research questions:

1. How do AGV fleet size and task arrival rate affect warehouse performance?
2. Does assigning a task to the nearest available AGV improve efficiency compared with a first-available assignment strategy?

## Main Features

- Grid-based warehouse environment
- Multiple autonomous AGVs
- Random transport task generation
- Pickup and delivery task states
- Two dispatch strategies:
  - `nearest`
  - `first_available`
- Standard A* pathfinding for dispatch-distance estimation
- Space-Time A* for coordinated multi-robot routing
- Reservation-based collision avoidance
- Cell-conflict and edge/swap-conflict prevention
- Intentional waiting when a route is temporarily blocked
- Robot return-to-home / parking behaviour
- Coordinated replanning
- Visual Pygame simulation
- Headless experiment mode
- CSV result collection
- Automatic graph generation
- Automated tests with `pytest`

## Technologies

The project is written in Python and uses:

- Python
- Pygame
- NumPy
- Matplotlib
- Pytest

## Project Structure

```text
AGV_Warehouse/
│
├── main.py
├── config.py
├── warehouse.py
├── robot.py
├── task.py
├── dispatcher.py
├── pathfinding.py
├── space_time_pathfinding.py
├── reservation.py
├── planner.py
├── simulation.py
├── renderer.py
├── results.py
├── metrics.py
├── experiment.py
├── analysis.py
│
├── tests/
│   └── ...
│
├── results/
│   ├── results.csv
│   └── graphs/
│       ├── throughput_nearest.png
│       ├── queue_time_nearest.png
│       ├── cycle_time_nearest.png
│       ├── drain_time_nearest.png
│       ├── utilization_nearest.png
│       ├── completion_rate_nearest.png
│       ├── strategy_cycle_time_10s.png
│       └── strategy_distance_10s.png
│
└── README.md
```

## How the Simulator Works

Each transport task contains a pickup location and a delivery location.

When a task is created:

1. The dispatcher selects an available AGV.
2. The selected AGV travels to the pickup location.
3. The robot collects the item.
4. The robot travels to the delivery location.
5. The task is completed.
6. The AGV can return to its home position while remaining available for new work.

Robot routes are coordinated using Space-Time A*. A route therefore considers both position and simulation time.

The reservation table stores:

- occupied cells at specific time steps;
- movement edges between consecutive cells.

This prevents two important conflicts:

- two AGVs occupying the same cell at the same time;
- two AGVs swapping positions during the same movement step.

Space-Time A* can also insert a wait step when an AGV must temporarily remain in its current cell.

## Dispatch Strategies

### Nearest Available

The dispatcher calculates a path from each available AGV to the pickup location and selects the robot with the shortest reachable path.

### First Available

The dispatcher selects the first available AGV that can reach the pickup location without comparing all candidate distances.

The first-available strategy is used as a simple baseline for comparison with the nearest-available strategy.

## Running the Project

Run commands from the main project directory.

### Visual Simulation

```bash
python main.py
```

This starts the Pygame visualization of the warehouse.

### Run the Full Experiment Set

```bash
python experiment.py
```

The experiment script runs the simulator in headless mode and stores the results in:

```text
results/results.csv
```

### Generate Graphs

```bash
python analysis.py
```

Generated figures are stored in:

```text
results/graphs/
```

### Run Automated Tests

```bash
pytest -q
```

The test suite checks important behaviour including robot movement, parking, reservations, Space-Time A* waiting, swap-conflict prevention, and coordinated multi-robot planning.

## Experimental Setup

The main experimental study uses:

| Parameter | Values |
|---|---|
| Number of AGVs | 1, 2, 3, 4, 5, 6 |
| Task-generation interval | 10 s, 15 s, 20 s |
| Dispatch strategy | `nearest`, `first_available` |
| Random seeds | 1, 2, 3, 4, 5 |
| Official simulation duration | 600 simulated seconds |
| Maximum drain time | 1200 simulated seconds |

This produces:

```text
6 fleet sizes × 3 workloads × 2 dispatch strategies × 5 seeds
= 180 simulation runs
```

The same random seeds are reused across configurations to improve comparability between experiments.

## Workload Levels

The task-generation interval controls the workload:

- **10 s** — high workload
- **15 s** — medium workload
- **20 s** — low workload

Shorter intervals create transport tasks more frequently and therefore increase demand on the AGV fleet.

## Performance Metrics

The simulator records several metrics:

- **Throughput** — tasks completed per minute during the official simulation horizon
- **Average queue time** — time between task creation and assignment
- **Average cycle time** — time between task creation and completion
- **Fleet utilization** — percentage of available fleet time spent assigned to transport tasks
- **Completion rate** — percentage of generated tasks completed within the official horizon
- **Total travel distance** — total number of grid cells travelled by the fleet
- **Drain time** — additional time required after task generation stops to finish existing work
- **Wait steps** — task-related robot waiting
- **Idle steps** — time robots remain idle
- **Plans created** — number of routes generated during the simulation

## Experiment Horizon and Draining

New tasks are generated only during the first 600 simulated seconds.

After that point, the simulation enters a draining phase:

- no new tasks are created;
- existing tasks continue to be processed;
- the simulation ends when all work is completed;
- a maximum drain-time limit prevents an experiment from running indefinitely.

Throughput and completion rate use the official 600-second horizon, so the draining phase does not artificially increase those metrics.

## Main Findings

The experiments show that fleet size has a strong effect when the warehouse is under heavy load.

- A single AGV becomes a major bottleneck, especially when tasks are generated every 10 seconds.
- Adding AGVs sharply reduces queue time, cycle time, and drain time.
- Under the highest tested workload, performance improves strongly up to approximately three AGVs and then begins to plateau.
- Lower workloads require fewer AGVs before additional robots provide only small performance gains.
- Fleet utilization decreases as more AGVs are added because the available workload is distributed across a larger fleet.
- The nearest-available and first-available strategies produce similar cycle times in smaller fleets.
- With larger fleets, nearest-available dispatching reduces total AGV travel distance compared with first-available dispatching, while the improvement in cycle time remains relatively small.

The results suggest that selecting an appropriate fleet size has a larger effect on overall warehouse performance than changing between the two tested dispatch strategies.

## Reproducibility

Task generation uses a configured random seed.

Running the same configuration with the same seed reproduces the same sequence of randomly selected pickup and delivery locations, allowing meaningful comparisons between different fleet sizes and dispatch strategies.

## Limitations

The simulator intentionally uses a simplified warehouse model.

Current limitations include:

- fixed warehouse layout;
- fixed pickup and delivery locations;
- no battery or charging model;
- no dynamic obstacles;
- uniform grid-based movement;
- no acceleration or turning-time model;
- only two dispatch strategies;
- simplified task demand.

These limitations keep the experimental scope focused on fleet sizing, workload, dispatching, and collision-free multi-AGV routing.

## Report

The full project report contains the system design, experimental methodology, results, discussion, limitations, and conclusions in greater detail.

## Author

Maria M

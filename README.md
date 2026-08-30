# AGV Warehouse Simulator

## Overview

This project implements a multi-AGV warehouse simulation in Python. Autonomous Guided Vehicles (AGVs) receive transport tasks, move between pickup and delivery locations, and coordinate their routes to avoid collisions.

The project is also used as an experimental platform to study how fleet size, task arrival rate, and dispatch strategy affect warehouse performance.

## Features

- Grid-based warehouse environment
- Multiple autonomous AGVs
- Random pickup and delivery task generation
- `nearest` and `first_available` dispatch strategies
- A* pathfinding for dispatch-distance estimation
- Space-Time A* for coordinated multi-robot routing
- Reservation-based collision avoidance
- Intentional waiting and coordinated replanning
- Visual Pygame simulation
- Headless experiment mode
- CSV result collection and automatic graph generation
- Automated tests with `pytest`

## Technologies

- Python
- Pygame
- NumPy
- Matplotlib
- Pytest

## How to Run

Run all commands from the main project directory.

### Visual simulation

```bash
python main.py
```

### Run experiments

```bash
python experiment.py
```

Experiment results are saved to:

```text
results/results.csv
```

### Generate graphs

```bash
python analysis.py
```

Generated figures are saved to:

```text
results/graphs/
```

### Run tests

```bash
pytest -q
```

## Experimental Setup

| Parameter | Values |
|---|---|
| Number of AGVs | 1, 2, 3, 4, 5, 6 |
| Task-generation interval | 10 s, 15 s, 20 s |
| Dispatch strategy | `nearest`, `first_available` |
| Random seeds | 1, 2, 3, 4, 5 |
| Simulation horizon | 600 simulated seconds |
| Maximum drain time | 1200 simulated seconds |

The full experiment contains:

```text
6 fleet sizes × 3 workloads × 2 dispatch strategies × 5 seeds
= 180 simulation runs
```

## Main Findings

- A single AGV becomes a major bottleneck under high workload.
- Increasing fleet size strongly reduces queue time, cycle time, and drain time.
- Under the highest workload, performance improves strongly up to about three AGVs and then begins to plateau.
- Lower workloads require fewer AGVs before additional robots provide only small benefits.
- The `nearest` strategy reduces total AGV travel distance for larger fleets compared with `first_available`.
- The difference in cycle time between the two dispatch strategies is relatively small.

Overall, fleet size has a stronger effect on warehouse performance than the difference between the two tested dispatch strategies.

## Project Structure

```text
AGV_Warehouse/
├── main.py
├── simulation.py
├── warehouse.py
├── robot.py
├── task.py
├── dispatcher.py
├── pathfinding.py
├── space_time_pathfinding.py
├── reservation.py
├── planner.py
├── config.py
├── results.py
├── metrics.py
├── experiment.py
├── analysis.py
├── tests/
├── results/
│   ├── results.csv
│   └── graphs/
└── README.md
```

## Report

The full research report contains the system design, experimental methodology, validation, results, discussion, limitations, and conclusions in greater detail.

## Author

Maria Malinka

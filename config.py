# ==========================================
# DEFAULT VISUAL SIMULATION SETTINGS
# ==========================================

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    number_of_robots: int = 5
    simulation_duration: int = 600
    task_generation_interval: int = 15
    random_seed: int = 42

    # Only affects visualization speed
    move_delay: int = 300

    visual: bool = True
    max_drain_time: int = 1200
    replan_interval: int = 5
    dispatch_strategy: str = "nearest"

# ==========================================
# EXPERIMENT SETTINGS
# ==========================================

EXPERIMENT_ROBOT_COUNTS = [
    1,
    2,
    3,
    4,
    5,
    6,
]

EXPERIMENT_SEEDS = [
    1,
    2,
    3,
    4,
    5,
]

EXPERIMENT_TASK_INTERVALS = [
    10,
    15,
    20,
]
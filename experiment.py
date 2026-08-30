from main import main
from config import SimulationConfig
from metrics import save_result
import os


ROBOT_COUNTS = [1, 2, 3, 4, 5, 6]
SEEDS = [1, 2, 3, 4, 5]
TASK_INTERVALS = [10, 15, 20]
dispatch_strategies = [
    "nearest",
    "first_available",
]

for strategy in dispatch_strategies:
    for task_interval in TASK_INTERVALS:

        for robot_count in ROBOT_COUNTS:

            for seed in SEEDS:

                config = SimulationConfig(
                    number_of_robots=robot_count,
                    random_seed=seed,
                    simulation_duration=600,
                    task_generation_interval=task_interval,
                    visual=False,

                    dispatch_strategy=strategy,
                )

                print(
                    f"Running: "
                    f"strategy={strategy}, "
                    f"{robot_count} robots, "
                    f"seed={seed}, "
                    f"interval={task_interval}"
                )


                os.makedirs(
                    "results",
                    exist_ok=True,
                )

                result = main(config)

                save_result(
                    "results/results.csv",
                    result,
                )

                print(
                    f"Completed: "
                    f"{result.completed_tasks}, "
                    f"Throughput: "
                    f"{result.throughput:.2f}"
                )
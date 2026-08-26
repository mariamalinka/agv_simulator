import csv
import os

from results import SimulationResult


def save_result(
    filename: str,
    result: SimulationResult,
) -> None:

    file_exists = os.path.exists(filename)

    with open(
        filename,
        "a",
        newline="",
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "experiment_id",
                "robots",
                "random_seed",
                "simulation_duration",
                "simulated_time",
                "task_interval",
                "tasks_generated",
                "completed_tasks",
                "completed_by_horizon",
                "waiting_tasks",
                "throughput",
                "distance",
                "wait_steps",
                "idle_steps",
                "plans_created",
                "average_queue_time",
                "average_cycle_time",
                "drain_time",
            ])

        writer.writerow([
            result.experiment_id,

            result.robots,
            result.random_seed,

            result.simulation_duration,
            result.simulated_time,
            result.task_interval,

            result.tasks_generated,
            result.completed_tasks,
            result.completed_by_horizon,
            result.waiting_tasks,

            round(result.throughput, 2),

            result.distance,
            result.wait_steps,
            result.idle_steps,
            result.plans_created,

            round(
                result.average_queue_time,
                2,
            ),

            round(
                result.average_cycle_time,
                2,
            ),
            result.drain_time,
        ])
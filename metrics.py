import csv
import os

def calculate_average_queue_time(tasks) -> float:
        values = [
            task.assigned_at - task.created_at
            for task in tasks
            if task.assigned_at is not None
        ]

        if not values:
            return 0.0

        return sum(values) / len(values)


def calculate_average_cycle_time(tasks) -> float:
        values = [
            task.completed_at - task.created_at
            for task in tasks
            if task.completed_at is not None
        ]

        if not values:
            return 0.0

        return sum(values) / len(values)


def save_results(
    filename: str,
    robots,
    tasks,
    random_seed: int,
    simulation_duration: int,
    throughput: float,
) -> None:

    completed_tasks = sum(
        1
        for task in tasks
        if task.status == "completed"
    )

    waiting_tasks = sum(
        1
        for task in tasks
        if task.status == "waiting"
    )

    total_distance = sum(
        robot.distance_travelled
        for robot in robots
    )

    total_wait_steps = sum(
        robot.total_wait_steps
        for robot in robots
    )

    total_idle_steps = sum(
        robot.idle_steps
        for robot in robots
    )

    total_plans = sum(
        robot.plans_created
        for robot in robots
    )

    avg_queue_time = calculate_average_queue_time(
        tasks
    )

    avg_cycle_time = calculate_average_cycle_time(
        tasks
    )

    file_exists = os.path.exists(filename)

    with open(
        filename,
        "a",
        newline="",
    ) as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "robots",
                "random_seed",
                "simulation_duration",
                "tasks_generated",
                "completed_tasks",
                "waiting_tasks",
                "throughput",
                "distance",
                "wait_steps",
                "idle_steps",
                "plans_created",
                "average_queue_time",
                "average_cycle_time",
            ])

        writer.writerow([
            len(robots),
            random_seed,
            simulation_duration,
            len(tasks),
            completed_tasks,
            waiting_tasks,
            round(throughput, 2),
            total_distance,
            total_wait_steps,
            total_idle_steps,
            total_plans,
            round(avg_queue_time, 2),
            round(avg_cycle_time, 2),
        ])


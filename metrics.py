import csv
import os


def save_results(
    filename: str,
    robots,
    tasks,
    collisions_avoided: int,
) -> None:

    completed_tasks = sum(
        1
        for task in tasks
        if task.status == "completed"
    )

    total_distance = sum(
        robot.distance_travelled
        for robot in robots
    )

    total_wait_steps = sum(
        robot.total_wait_steps
        for robot in robots
    )

    total_replans = sum(
        robot.replan_count
        for robot in robots
    )

    file_exists = os.path.exists(filename)

    with open(
        filename,
        "a",
        newline="",
    ) as file:

        writer = csv.writer(file)

        # Write headers only once
        if not file_exists:
            writer.writerow([
                "robots",
                "tasks",
                "completed_tasks",
                "distance",
                "wait_steps",
                "replans",
                "collisions_avoided",
            ])

        writer.writerow([
            len(robots),
            len(tasks),
            completed_tasks,
            total_distance,
            total_wait_steps,
            total_replans,
            collisions_avoided,
        ])
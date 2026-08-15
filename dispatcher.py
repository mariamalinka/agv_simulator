from pathfinding import astar


def assign_waiting_tasks(
    robots,
    tasks,
    warehouse,
) -> None:
    """Assign waiting tasks to the nearest idle robot."""

    waiting_tasks = [
        task
        for task in tasks
        if task.status == "waiting"
    ]

    idle_robots = [
        robot
        for robot in robots
        if robot.state == "idle"
    ]

    for task in waiting_tasks:

        if not idle_robots:
            return

        best_robot = None
        best_path = None
        best_distance = float("inf")

        for robot in idle_robots:

            path = astar(
                warehouse,
                robot.position,
                task.pickup,
            )

            if not path:
                continue

            distance = len(path)

            if distance < best_distance:
                best_distance = distance
                best_robot = robot
                best_path = path

        if best_robot is not None:

            best_robot.assign_task(
                task,
                best_path,
            )

            print(
                f"Task {task.id} assigned "
                f"to Robot {best_robot.id}"
            )

            idle_robots.remove(best_robot)
from pathfinding import astar


def assign_waiting_tasks(
    robots,
    tasks,
    warehouse,
    simulation_time,
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
        if robot.current_task is None

    ]

    for task in waiting_tasks:

        if not idle_robots:
            return

        best_robot = None
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
             

        if best_robot is not None:

            best_robot.assign_task(task)
            task.assigned_at = simulation_time

            print(
                f"Task {task.id} assigned "
                f"to Robot {best_robot.id}"
            )

            idle_robots.remove(best_robot)
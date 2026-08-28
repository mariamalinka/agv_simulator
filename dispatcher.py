from pathfinding import astar


def assign_waiting_tasks(
    robots,
    tasks,
    warehouse,
    simulation_time,
    strategy="nearest",
) -> None:
    """
    Assign waiting tasks to available robots.

    Strategies:
    - "nearest": choose the available robot
      with the shortest path to the pickup.
    - "first_available": choose the first
      available robot that can reach the pickup.
    """

    if strategy not in (
        "nearest",
        "first_available",
    ):
        raise ValueError(
            f"Unknown dispatch strategy: {strategy}"
        )

    waiting_tasks = [
        task
        for task in tasks
        if task.status == "waiting"
    ]

    # A robot is available if it currently
    # has no transport task.
    #
    # This includes robots returning
    # to parking.
    available_robots = [
        robot
        for robot in robots
        if robot.current_task is None
    ]

    for task in waiting_tasks:

        if not available_robots:
            return

        selected_robot = None

        # =================================
        # STRATEGY 1:
        # FIRST AVAILABLE
        # =================================

        if strategy == "first_available":

            for robot in available_robots:

                path = astar(
                    warehouse,
                    robot.position,
                    task.pickup,
                )

                # Skip robots that cannot
                # reach this pickup.
                if not path:
                    continue

                selected_robot = robot
                break

        # =================================
        # STRATEGY 2:
        # NEAREST AVAILABLE
        # =================================

        elif strategy == "nearest":

            best_distance = float("inf")

            for robot in available_robots:

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
                    selected_robot = robot

        # =================================
        # ASSIGN TASK
        # =================================

        if selected_robot is not None:

            selected_robot.assign_task(task)

            task.assigned_at = (
                simulation_time
            )

            available_robots.remove(
                selected_robot
            )
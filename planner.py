from reservation import ReservationTable
from space_time_pathfinding import space_time_astar


PLANNING_HORIZON = 100


def get_robot_goal(robot):

    if robot.state == "to_parking":
        return robot.home_position

    if robot.current_task is None:
        return None

    if robot.state == "to_pickup":
        return robot.current_task.pickup

    if robot.state == "to_delivery":
        return robot.current_task.delivery

    return None


def validate_planned_paths(
    robots,
    simulation_step,
) -> None:
    """
    Validate paths only until the next guaranteed
    replanning event.

    The first moving robot that reaches the end
    of its path causes coordinated replanning.
    """

    moving_robots = [
        robot
        for robot in robots
        if len(robot.path) > 1
    ]

    if not moving_robots:
        return

    # Earliest point where one moving robot
    # reaches its current goal.
    check_until = min(
        len(robot.path) - 1
        for robot in moving_robots
    )

    for path_index in range(
        check_until + 1
    ):

        positions = {}

        for robot in robots:

            # Stationary robot
            if len(robot.path) <= 1:
                position = robot.position

            # Moving robot
            else:
                position = robot.path[
                    path_index
                ]

            if position in positions:

                other_id = positions[
                    position
                ]

                raise RuntimeError(
                    f"PLANNER CONFLICT at "
                    f"time "
                    f"{simulation_step + path_index}: "
                    f"Robot {other_id} and "
                    f"Robot {robot.id} both at "
                    f"{position}"
                )

            positions[position] = robot.id


def replan_all_robots(
    robots,
    warehouse,
    simulation_step,
    priority_offset=0,
):
    max_time = (
        simulation_step + PLANNING_HORIZON
    )

    sorted_robots = sorted(
        robots,
        key=lambda robot: robot.id,
    )

    if sorted_robots:
        offset = (
            priority_offset
            % len(sorted_robots)
        )

        sorted_robots = (
            sorted_robots[offset:]
            + sorted_robots[:offset]
        )

    # Robots with no task are stationary.
    stationary_robot_ids = {
        robot.id
        for robot in sorted_robots
        if get_robot_goal(robot) is None
    }

    while True:

        # Start planning from scratch
        reservations = ReservationTable()

        # ---------------------------------
        # 1. Reserve stationary robots
        # ---------------------------------

        for robot in sorted_robots:

            if robot.id not in stationary_robot_ids:
                continue

            for time in range(
                simulation_step,
                max_time + 1,
            ):
                reservations.cells.add(
                    (
                        robot.position,
                        time,
                    )
                )

        planned_paths = {}

        failed_robot = None

        # ---------------------------------
        # 2. Plan moving robots
        # ---------------------------------

        for robot in sorted_robots:

            if robot.id in stationary_robot_ids:
                continue

            goal = get_robot_goal(robot)

            if goal is None:
                continue

            path = space_time_astar(
                warehouse=warehouse,
                start=robot.position,
                goal=goal,
                reservations=reservations,
                start_time=simulation_step,
                max_time=max_time,
            )

            # This robot cannot currently move safely
            if not path:
                failed_robot = robot
                break

            planned_paths[robot.id] = path

            arrival_time = (
                simulation_step
                + len(path)
                - 1
            )

            reservations.reserve_path(
                path,
                start_time=simulation_step,
                hold_until=min(
                    arrival_time + 1,
                    max_time,
                ),
            )

        # ---------------------------------
        # 3. Everything was planned safely
        # ---------------------------------

        if failed_robot is None:

            for robot in sorted_robots:

                if robot.id in stationary_robot_ids:
                    robot.set_path(
                        [robot.position]
                    )

                else:
                    path = planned_paths.get(
                        robot.id
                    )

                    if path:
                        robot.set_path(path)
                        robot.plans_created += 1


            validate_planned_paths(
                sorted_robots,
                simulation_step,
            )

            return reservations

        # ---------------------------------
        # 4. A robot failed to find a path
        # ---------------------------------

        print(
            f"Robot {failed_robot.id} "
            f"cannot find a safe path. "
            f"It will wait."
        )

        # Treat it as stationary
        stationary_robot_ids.add(
            failed_robot.id
        )

        # IMPORTANT:
        # while loop now starts again
        # and replans EVERY robot around it.
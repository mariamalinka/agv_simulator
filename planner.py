from reservation import ReservationTable
from space_time_pathfinding import space_time_astar


PLANNING_HORIZON = 100


def get_robot_goal(robot):
    """Return the robot's current destination."""

    if robot.current_task is None:
        return None

    if robot.state == "to_pickup":
        return robot.current_task.pickup

    if robot.state == "to_delivery":
        return robot.current_task.delivery

    return None


def replan_all_robots(
    robots,
    warehouse,
    simulation_step,
):
    max_time = (
        simulation_step + PLANNING_HORIZON
    )

    sorted_robots = sorted(
        robots,
        key=lambda robot: robot.id,
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

            reservations.reserve_path(
                path,
                start_time=simulation_step,
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
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
    """
    Plan collision-free paths for all robots.

    Lower robot ID = higher priority.
    """

    reservations = ReservationTable()

    max_time = (
        simulation_step + PLANNING_HORIZON
    )

    sorted_robots = sorted(
        robots,
        key=lambda robot: robot.id,
    )

    for robot in sorted_robots:

        goal = get_robot_goal(robot)

        # No task -> robot stays where it is
        if goal is None:

            for time in range(
                simulation_step,
                max_time + 1,
            ):
                reservations.cells.add(
                    (robot.position, time)
                )

            continue

        path = space_time_astar(
            warehouse=warehouse,
            start=robot.position,
            goal=goal,
            reservations=reservations,
            start_time=simulation_step,
            max_time=max_time,
        )

        if path:
            robot.set_path(path)

            robot.plans_created+=1

            reservations.reserve_path(
                path,
                start_time=simulation_step,
            )

            print(
                f"Robot {robot.id} planned "
                f"{len(path)} steps to {goal}"
            )

        else:
            print(
                f"Robot {robot.id}: "
                f"no path to {goal}"
            )

            robot.set_path(
                [robot.position]
            )

    return reservations
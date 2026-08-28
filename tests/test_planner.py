from planner import replan_all_robots
from robot import Robot


class DummyTask:
    def __init__(
        self,
        pickup,
        delivery,
    ):
        self.pickup = pickup
        self.delivery = delivery
        self.status = "assigned"


class SmallWarehouse:
    """
    Small 3x2 warehouse:

    (0,0) -- (1,0) -- (2,0)
      |        |        |
    (0,1) -- (1,1) -- (2,1)

    The second row gives robots room
    to avoid each other.
    """

    def get_neighbors(
        self,
        position,
    ):
        x, y = position

        possible = [
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
        ]

        return [
            (nx, ny)
            for nx, ny in possible
            if (
                0 <= nx <= 2
                and 0 <= ny <= 1
            )
        ]


def make_robot(
    robot_id,
    start,
    goal,
):
    robot = Robot(
        robot_id=robot_id,
        start_position=start,
        color=(0, 0, 0),
    )

    robot.current_task = DummyTask(
        pickup=goal,
        delivery=goal,
    )

    robot.state = "to_pickup"

    return robot


def test_replanning_produces_collision_free_paths():
    warehouse = SmallWarehouse()

    robot_1 = make_robot(
        robot_id=1,
        start=(0, 0),
        goal=(2, 0),
    )

    robot_2 = make_robot(
        robot_id=2,
        start=(2, 0),
        goal=(0, 0),
    )

    robots = [
        robot_1,
        robot_2,
    ]

    replan_all_robots(
        robots=robots,
        warehouse=warehouse,
        simulation_step=0,
    )

    # Both robots should receive paths.
    assert robot_1.path
    assert robot_2.path

    # Paths must start at their
    # actual current positions.
    assert robot_1.path[0] == (0, 0)
    assert robot_2.path[0] == (2, 0)

    # Check the paths step by step.
    max_length = max(
        len(robot_1.path),
        len(robot_2.path),
    )

    for step in range(max_length):

        position_1 = robot_1.path[
            min(
                step,
                len(robot_1.path) - 1,
            )
        ]

        position_2 = robot_2.path[
            min(
                step,
                len(robot_2.path) - 1,
            )
        ]

        # Same-cell collision
        assert position_1 != position_2

        if step == 0:
            continue

        previous_1 = robot_1.path[
            min(
                step - 1,
                len(robot_1.path) - 1,
            )
        ]

        previous_2 = robot_2.path[
            min(
                step - 1,
                len(robot_2.path) - 1,
            )
        ]

        # Swap collision
        swapped = (
            position_1 == previous_2
            and
            position_2 == previous_1
        )

        assert not swapped
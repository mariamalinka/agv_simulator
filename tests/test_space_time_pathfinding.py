from reservation import ReservationTable
from space_time_pathfinding import space_time_astar


class LineWarehouse:
    """
    Tiny warehouse:

    (0, 0) -- (1, 0) -- (2, 0)
    """

    def get_neighbors(
        self,
        position,
    ):
        x, y = position

        neighbors = []

        if x > 0:
            neighbors.append(
                (x - 1, y)
            )

        if x < 2:
            neighbors.append(
                (x + 1, y)
            )

        return neighbors


def test_robot_waits_for_reserved_cell():
    warehouse = LineWarehouse()

    reservations = ReservationTable()

    # Middle cell is occupied at t=1.
    reservations.cells.add(
        ((1, 0), 1)
    )

    path = space_time_astar(
        warehouse=warehouse,
        start=(0, 0),
        goal=(2, 0),
        reservations=reservations,
        start_time=0,
        max_time=5,
    )

    assert path == [
        (0, 0),
        (0, 0),
        (1, 0),
        (2, 0),
    ]


def test_robot_cannot_swap_positions():
    warehouse = LineWarehouse()
    reservations = ReservationTable()

    reservations.reserve_path(
        [
            (0, 0),
            (1, 0),
        ],
        start_time=0,
    )

    path = space_time_astar(
        warehouse=warehouse,
        start=(1, 0),
        goal=(0, 0),
        reservations=reservations,
        start_time=0,
        max_time=3,
    )

    # The robot may wait or take a detour,
    # but it must never perform the direct swap.
    assert not (
        len(path) >= 2
        and path[0] == (1, 0)
        and path[1] == (0, 0)
    )


def test_robot_waits_for_reserved_cell():
    warehouse = LineWarehouse()
    reservations = ReservationTable()

    # Another robot occupies (1, 0) at t=1.
    #
    # Our robot:
    # t=0: (0, 0)
    #
    # It wants to reach (2, 0).
    #
    # It cannot move through (1, 0) at t=1,
    # so it should wait at (0, 0) and then continue.
    reservations.reserve_path(
        [
            (1, 0),
        ],
        start_time=1,
    )

    path = space_time_astar(
        warehouse=warehouse,
        start=(0, 0),
        goal=(2, 0),
        reservations=reservations,
        start_time=0,
        max_time=4,
    )

    assert path != []
    assert path[0] == (0, 0)


def test_robot_cannot_enter_reserved_cell():
    warehouse = LineWarehouse()
    reservations = ReservationTable()

    # Another robot occupies (1, 0) at t=1.
    reservations.reserve_path(
        [
            (1, 0),
        ],
        start_time=1,
    )

    path = space_time_astar(
        warehouse=warehouse,
        start=(0, 0),
        goal=(2, 0),
        reservations=reservations,
        start_time=0,
        max_time=4,
    )

    assert path != []

    # The robot must not enter the reserved cell at t=1.
    assert path[:2] != [(0, 0), (1, 0)]


def test_no_path_when_goal_is_fully_blocked():
    warehouse = LineWarehouse()
    reservations = ReservationTable()

    # Block the only way to reach the goal.
    reservations.reserve_path(
        [
            (1, 0),
            (1, 0),
            (1, 0),
            (1, 0),
        ],
        start_time=1,
    )

    path = space_time_astar(
        warehouse=warehouse,
        start=(0, 0),
        goal=(2, 0),
        reservations=reservations,
        start_time=0,
        max_time=4,
    )

    assert path == []
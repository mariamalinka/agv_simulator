import heapq

from warehouse import Warehouse
from reservation import ReservationTable


def heuristic(
    first: tuple[int, int],
    second: tuple[int, int],
) -> int:

    return (
        abs(first[0] - second[0])
        + abs(first[1] - second[1])
    )


def reconstruct_path(
    came_from,
    current_state,
) -> list[tuple[int, int]]:

    states = [current_state]

    while current_state in came_from:
        current_state = came_from[current_state]
        states.append(current_state)

    states.reverse()

    # We only return positions.
    return [
        position
        for position, time in states
    ]


def space_time_astar(
    warehouse: Warehouse,
    start: tuple[int, int],
    goal: tuple[int, int],
    reservations: ReservationTable,
    start_time: int = 0,
    max_time: int = 100,
) -> list[tuple[int, int]]:

    start_state = (
        start,
        start_time,
    )

    open_list = []

    heapq.heappush(
        open_list,
        (
            heuristic(start, goal),
            0,
            start,
            start_time,
        )
    )

    came_from = {}

    best_cost = {
        start_state: 0
    }

    while open_list:

        _, cost, position, time = (
            heapq.heappop(open_list)
        )

        state = (
            position,
            time,
        )

        if position == goal:
            return reconstruct_path(
                came_from,
                state,
            )

        if time >= max_time:
            continue

        # Normal movement options
        neighbors = warehouse.get_neighbors(
            position
        )

        # Robot is also allowed to WAIT.
        neighbors.append(position)

        for next_position in neighbors:

            next_time = time + 1

            # -------------------------
            # Cell conflict
            # -------------------------

            if reservations.is_cell_reserved(
                next_position,
                next_time,
            ):
                continue

            # -------------------------
            # Swap / edge conflict
            # -------------------------

            if reservations.is_edge_reserved(
                next_position,
                position,
                next_time,
            ):
                continue

            next_state = (
                next_position,
                next_time,
            )

            new_cost = cost + 1

            if (
                next_state not in best_cost
                or
                new_cost < best_cost[next_state]
            ):
                best_cost[next_state] = new_cost

                came_from[next_state] = state

                priority = (
                    new_cost
                    + heuristic(
                        next_position,
                        goal,
                    )
                )

                heapq.heappush(
                    open_list,
                    (
                        priority,
                        new_cost,
                        next_position,
                        next_time,
                    )
                )

    return []
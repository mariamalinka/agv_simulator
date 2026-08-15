import heapq

from warehouse import Warehouse


#how far are positions from eachother
def heuristic(
    first: tuple[int, int],
    second: tuple[int, int],
) -> int:
    return (
        abs(first[0] - second[0])
        + abs(first[1] - second[1])
    )


def reconstruct_path(
    came_from: dict[
        tuple[int, int],
        tuple[int, int],
    ],
    current: tuple[int, int],
) -> list[tuple[int, int]]:
    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


def astar(
    warehouse: Warehouse,
    start: tuple[int, int],
    goal: tuple[int, int],
    blocked_positions=None,
) -> list[tuple[int, int]]:
    open_list = [(0, start)]

    if blocked_positions is None:
        blocked_positions = set()

    came_from = {}

    movement_cost = {
        start: 0,
    }

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            return reconstruct_path(
                came_from,
                current,
            )

        for neighbor in warehouse.get_neighbors(current):

            if (
                neighbor in blocked_positions
                and neighbor != goal
            ):
                continue
            
            new_cost = movement_cost[current] + 1

            if (
                neighbor not in movement_cost
                or new_cost < movement_cost[neighbor]
            ):
                movement_cost[neighbor] = new_cost
                came_from[neighbor] = current

                priority = (
                    new_cost
                    + heuristic(neighbor, goal)
                )

                heapq.heappush(
                    open_list,
                    (priority, neighbor),
                )

    return []
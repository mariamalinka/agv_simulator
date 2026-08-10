import numpy as np

FREE = 0
SHELF = 1
PICKUP = 2
DELIVERY = 3



PICKUP_POSITIONS = [
    (1, 18),
    (10, 1),
]

DELIVERY_POSITIONS = [
    (12, 18),
    (13, 5),
]


class Warehouse:
    def __init__(self, rows: int, columns: int) -> None:
        self.rows = rows
        self.columns = columns

        # Every cell starts as a free cell.
        self.grid = np.zeros(
            (rows, columns),
            dtype=np.int8,
        )

    def add_shelf(self, row: int, column: int) -> None:
        """Place a shelf at the given grid position."""
        if self.is_inside(row, column):
            self.grid[row, column] = SHELF

    def is_inside(self, row: int, column: int) -> bool:
        """Check whether a position is inside the warehouse."""
        return (
            0 <= row < self.rows
            and 0 <= column < self.columns
        )

    def is_walkable(self, row: int, column: int) -> bool:
        """Check whether a robot can enter a cell."""
        if not self.is_inside(row, column):
            return False

        return self.grid[row, column] != SHELF
    
    def get_neighbors(
        self,
        position: tuple[int, int],
    ) -> list[tuple[int, int]]:
        row, column = position

        possible_positions = [
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        ]

        return [
            position
            for position in possible_positions
            if self.is_walkable(position[0], position[1])
        ]
    
    def add_pickup(self, row: int, column: int) -> None:
        if self.is_inside(row, column):
            self.grid[row, column] = PICKUP


    def add_delivery(self, row: int, column: int) -> None:
        if self.is_inside(row, column):
            self.grid[row, column] = DELIVERY
    


def create_default_warehouse() -> Warehouse:
    """Create the first warehouse layout."""
    warehouse = Warehouse(rows=15, columns=20)

    shelf_cells = {
        (3, 3),
        (4, 3),
        (5, 3),
        (6, 3),
        (7, 3),

        (3, 7),
        (4, 7),
        (5, 7),
        (6, 7),
        (7, 7),

        (3, 11),
        (4, 11),
        (5, 11),
        (6, 11),
        (7, 11),

        (3, 15),
        (4, 15),
        (5, 15),
        (6, 15),
        (7, 15),
    }

    for row, column in shelf_cells:
        warehouse.add_shelf(row, column)

    for row, column in PICKUP_POSITIONS:
        warehouse.add_pickup(row, column)

    for row, column in DELIVERY_POSITIONS:
        warehouse.add_delivery(row, column)

    return warehouse
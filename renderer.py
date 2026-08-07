import pygame

from warehouse import (
    SHELF,
    PICKUP,
    DELIVERY,
    Warehouse,
)

CELL_SIZE = 40

BACKGROUND_COLOR = (240, 240, 240)
GRID_COLOR = (190, 190, 190)

SHELF_COLOR = (80, 80, 80)
ROBOT_COLOR = (50, 120, 220)
PICKUP_COLOR = (50, 200, 80)
DELIVERY_COLOR = (220, 80, 80)


def draw_warehouse(
    screen: pygame.Surface,
    warehouse: Warehouse,
) -> None:
    """Draw the warehouse cells and grid."""

    for row in range(warehouse.rows):
        for column in range(warehouse.columns):

            rectangle = pygame.Rect(
                column * CELL_SIZE,
                row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            cell = warehouse.grid[row, column]

            if cell == SHELF:
                pygame.draw.rect(
                    screen,
                    SHELF_COLOR,
                    rectangle,
                )

            elif cell == PICKUP:
                pygame.draw.rect(
                    screen,
                    PICKUP_COLOR,
                    rectangle,
                )

            elif cell == DELIVERY:
                pygame.draw.rect(
                    screen,
                    DELIVERY_COLOR,
                    rectangle,
                )

            pygame.draw.rect(
                screen,
                GRID_COLOR,
                rectangle,
                width=1,
            )


def draw_robot(
    screen: pygame.Surface,
    position: tuple[int, int],
) -> None:
    """Draw a robot on the warehouse grid."""

    row, column = position

    center = (
        column * CELL_SIZE + CELL_SIZE // 2,
        row * CELL_SIZE + CELL_SIZE // 2,
    )

    pygame.draw.circle(
        screen,
        ROBOT_COLOR,
        center,
        CELL_SIZE // 3,
    )
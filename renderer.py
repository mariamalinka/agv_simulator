import pygame

from warehouse import (
    SHELF,
    PICKUP,
    DELIVERY,
    Warehouse,
)

CELL_SIZE = 40
PANEL_WIDTH = 300

PANEL_COLOR = (225, 225, 225)
TEXT_COLOR = (30, 30, 30)

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
    color: tuple[int, int, int],
    carrying: bool = False,
) -> None:

    row, column = position

    center = (
        column * CELL_SIZE + CELL_SIZE // 2,
        row * CELL_SIZE + CELL_SIZE // 2,
    )

    pygame.draw.circle(
        screen,
        color,
        center,
        CELL_SIZE // 3,
    )

    if carrying:
        package_color = (255, 180, 50)

        package_size = CELL_SIZE // 3

        package_rect = pygame.Rect(
            center[0] - package_size // 2,
            center[1] - package_size // 2,
            package_size,
            package_size,
        )

        pygame.draw.rect(
            screen,
            package_color,
            package_rect,
        )


def draw_dashboard(
    screen: pygame.Surface,
    robots,
    tasks,
    warehouse_width: int,
) -> None:

    panel_rect = pygame.Rect(
        warehouse_width,
        0,
        PANEL_WIDTH,
        screen.get_height(),
    )

    pygame.draw.rect(
        screen,
        PANEL_COLOR,
        panel_rect,
    )

    title_font = pygame.font.Font(None, 32)
    text_font = pygame.font.Font(None, 24)

    x = warehouse_width + 20
    y = 20

    title = title_font.render(
        "AGV Status",
        True,
        TEXT_COLOR,
    )

    screen.blit(title, (x, y))

    y += 50

    # Robot information
    for robot in robots:

        robot_text = text_font.render(
            f"Robot {robot.id}",
            True,
            robot.color,
        )

        screen.blit(robot_text, (x, y))
        y += 25

        state_text = text_font.render(
            f"State: {robot.state}",
            True,
            TEXT_COLOR,
        )

        screen.blit(state_text, (x, y))
        y += 25

        if robot.current_task is not None:
            task_number = robot.current_task.id
        else:
            task_number = "-"

        task_text = text_font.render(
            f"Task: {task_number}",
            True,
            TEXT_COLOR,
        )

        screen.blit(task_text, (x, y))
        y += 25

        carrying_text = text_font.render(
            f"Carrying: {'Yes' if robot.carrying else 'No'}",
            True,
            TEXT_COLOR,
        )

        screen.blit(carrying_text, (x, y))
        
        y += 45

        distance_text = text_font.render(
            f"Distance: {robot.distance_travelled}",
            True,
            TEXT_COLOR,
        )

        screen.blit(distance_text, (x, y))
        y += 25

        wait_text = text_font.render(
            f"Wait steps: {robot.total_wait_steps}",
            True,
            TEXT_COLOR,
        )

        screen.blit(wait_text, (x, y))
        y += 25

        replan_text = text_font.render(
            f"Replans: {robot.replan_count}",
            True,
            TEXT_COLOR,
        )

        screen.blit(replan_text, (x, y))
        y += 40

 

    waiting_tasks = sum(
        1
        for task in tasks
        if task.status == "waiting"
    )

    completed_tasks = sum(
        1
        for task in tasks
        if task.status == "completed"
    )

    waiting_text = text_font.render(
        f"Waiting tasks: {waiting_tasks}",
        True,
        TEXT_COLOR,
    )

    screen.blit(waiting_text, (x, y))
    y += 30

    completed_text = text_font.render(
        f"Completed tasks: {completed_tasks}",
        True,
        TEXT_COLOR,
    )

    screen.blit(completed_text, (x, y))
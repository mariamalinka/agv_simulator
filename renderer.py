import pygame

from warehouse import (
    SHELF,
    PICKUP,
    DELIVERY,
    Warehouse,
)

CELL_SIZE = 40
PANEL_WIDTH = 400

PANEL_COLOR = (225, 225, 225)
TEXT_COLOR = (30, 30, 30)

BACKGROUND_COLOR = (240, 240, 240)
GRID_COLOR = (190, 190, 190)

SHELF_COLOR = (80, 80, 80)

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
    simulation_time,
    simulation_duration,
    throughput,
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

    # --------------------------------
    # ROBOT STATUS
    # --------------------------------

    robot_start_y = 70

    column_width = 205
    row_height = 135

    for index, robot in enumerate(robots):

        column = index % 2
        row = index // 2

        robot_x = (
            warehouse_width
            + 15
            + column * column_width
        )

        robot_y = (
            robot_start_y
            + row * row_height
        )

        # Robot name
        robot_text = text_font.render(
            f"Robot {robot.id}",
            True,
            robot.color,
        )

        screen.blit(
            robot_text,
            (robot_x, robot_y),
        )

        robot_y += 25

        # State
        state_text = text_font.render(
            f"State: {robot.state}",
            True,
            TEXT_COLOR,
        )

        screen.blit(
            state_text,
            (robot_x, robot_y),
        )

        robot_y += 22

        # Task
        if robot.current_task is not None:
            task_id = robot.current_task.id
        else:
            task_id = "-"

        task_text = text_font.render(
            f"Task: {task_id}",
            True,
            TEXT_COLOR,
        )

        screen.blit(
            task_text,
            (robot_x, robot_y),
        )

        robot_y += 22

        # Carrying + distance
        carrying = (
            "Yes"
            if robot.carrying
            else "No"
        )

        info_text = text_font.render(
            f"Carry: {carrying}  Dist: {robot.distance_travelled}",
            True,
            TEXT_COLOR,
        )

        screen.blit(
            info_text,
            (robot_x, robot_y),
        )

        robot_y += 22

        # Waiting + plans
        stats_text = text_font.render(
            f"Wait: {robot.total_wait_steps}  Plans: {robot.plans_created}",
            True,
            TEXT_COLOR,
        )

        screen.blit(
            stats_text,
            (robot_x, robot_y),
        )


    number_of_rows = (
        len(robots) + 1
    ) // 2

    y = (
        robot_start_y
        + number_of_rows * row_height
        + 10
    )
 

    waiting_tasks = sum(
        1
        for task in tasks
        if task.status == "waiting"
    )

    idle_robots = sum(
        1
        for robot in robots
        if robot.state == "idle"
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

    idle_text = text_font.render(
        f"Idle robots: {idle_robots}",
        True,
        TEXT_COLOR,
    )

    screen.blit(idle_text, (x, y))
    y += 30



    completed_text = text_font.render(
        f"Completed tasks: {completed_tasks}",
        True,
        TEXT_COLOR,
    )

    screen.blit(completed_text, (x, y))
    y+=30

    simulation_text = text_font.render(
        f"Simulated time: {simulation_time}/{simulation_duration}s",
        True,
        TEXT_COLOR,
    )

    screen.blit(
        simulation_text,
        (x, y),
    )
    
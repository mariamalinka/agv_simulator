import pygame

from warehouse import (
    create_default_warehouse,
    PICKUP_POSITIONS,
    DELIVERY_POSITIONS,
)

from renderer import (
    CELL_SIZE,
    PANEL_WIDTH,
)

from robot import Robot
from task import Task
from dispatcher import assign_waiting_tasks
from planner import replan_all_robots

from simulation import Simulation


def main() -> None:
    pygame.init()

    # ------------------------
    # Create warehouse
    # ------------------------
    warehouse = create_default_warehouse()

    # ------------------------
    # Create initial tasks
    # ------------------------
    tasks = [
        Task(
            id=1,
            pickup=PICKUP_POSITIONS[0],
            delivery=DELIVERY_POSITIONS[0],
        ),
        Task(
            id=2,
            pickup=PICKUP_POSITIONS[1],
            delivery=DELIVERY_POSITIONS[1],
        ),
        Task(
            id=3,
            pickup=PICKUP_POSITIONS[0],
            delivery=DELIVERY_POSITIONS[1],
        ),
        Task(
            id=4,
            pickup=PICKUP_POSITIONS[1],
            delivery=DELIVERY_POSITIONS[0],
        ),
    ]

    # ------------------------
    # Create robots
    # ------------------------
    robots = [
        Robot(
            robot_id=1,
            start_position=(1, 1),
            color=(50, 120, 220),
        ),
        Robot(
            robot_id=2,
            start_position=(13, 18),
            color=(180, 80, 200),
        ),
    ]

    # ------------------------
    # Assign initial tasks
    # ------------------------
    assign_waiting_tasks(
        robots,
        tasks,
        warehouse,
    )

    # ------------------------
    # Initial coordinated planning
    # ------------------------
    simulation_step = 0

    reservations = replan_all_robots(
        robots,
        warehouse,
        simulation_step,
    )

    # ------------------------
    # Create Pygame window
    # ------------------------
    warehouse_width = (
        warehouse.columns * CELL_SIZE
    )

    window_width = (
        warehouse_width + PANEL_WIDTH
    )

    window_height = (
        warehouse.rows * CELL_SIZE
    )

    screen = pygame.display.set_mode(
        (window_width, window_height)
    )

    pygame.display.set_caption(
        "AGV Warehouse Simulator"
    )

    # ------------------------
    # Start simulation
    # ------------------------
    simulation = Simulation(
        screen=screen,
        warehouse=warehouse,
        robots=robots,
        tasks=tasks,
        reservations=reservations,
        simulation_step=simulation_step,
        warehouse_width=warehouse_width,
    )

    simulation.run()

    pygame.quit()


if __name__ == "__main__":
    main()
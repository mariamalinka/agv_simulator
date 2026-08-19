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


NUMBER_OF_ROBOTS = 6

ROBOT_START_POSITIONS = [
    (1, 1),
    (13, 18),
    (13, 1),
    (1, 17),
    (10, 5),
    (10, 14),
]

ROBOT_COLORS = [
    (50, 120, 220),   # blue
    (180, 80, 200),   # purple
    (240, 140, 40),   # orange
    (40, 170, 160),   # turquoise
    (220, 80, 120),   # pink/red
    (120, 160, 60),   # green
]

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

    if NUMBER_OF_ROBOTS > len(ROBOT_START_POSITIONS):
        raise ValueError(
            "Not enough robot start positions."
        )
    
    robots = []

    for i in range(NUMBER_OF_ROBOTS):

        robot = Robot(
            robot_id=i + 1,
            start_position=ROBOT_START_POSITIONS[i],
            color=ROBOT_COLORS[i],
        )

        robots.append(robot)

    # ------------------------
    # Assign initial tasks
    # ------------------------
    assign_waiting_tasks(
        robots,
        tasks,
        warehouse,
        simulation_time=0,
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
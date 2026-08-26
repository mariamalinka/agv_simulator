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
from config import SimulationConfig

from results import SimulationResult


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


def main(
    config: SimulationConfig | None = None,
) -> SimulationResult:

    # ---------------------------------
    # Default configuration
    # ---------------------------------

    if config is None:
        config = SimulationConfig()

    pygame.init()


    # =================================
    # 1. CREATE WAREHOUSE
    # =================================

    warehouse = create_default_warehouse()


    # =================================
    # 2. CREATE INITIAL TASKS
    # =================================

    tasks = [
        Task(
            id=1,
            pickup=PICKUP_POSITIONS[0],
            delivery=DELIVERY_POSITIONS[0],
            created_at=0,
        ),

        Task(
            id=2,
            pickup=PICKUP_POSITIONS[1],
            delivery=DELIVERY_POSITIONS[1],
            created_at=0,
        ),

        Task(
            id=3,
            pickup=PICKUP_POSITIONS[0],
            delivery=DELIVERY_POSITIONS[1],
            created_at=0,
        ),

        Task(
            id=4,
            pickup=PICKUP_POSITIONS[1],
            delivery=DELIVERY_POSITIONS[0],
            created_at=0,
        ),
    ]


    # =================================
    # 3. CREATE ROBOTS
    # =================================

    if (
        config.number_of_robots
        > len(ROBOT_START_POSITIONS)
    ):
        raise ValueError(
            "Not enough robot start positions."
        )

    if (
        config.number_of_robots
        > len(ROBOT_COLORS)
    ):
        raise ValueError(
            "Not enough robot colors."
        )


    robots = []

    for i in range(
        config.number_of_robots
    ):

        robot = Robot(
            robot_id=i + 1,
            start_position=ROBOT_START_POSITIONS[i],
            color=ROBOT_COLORS[i],
        )

        robots.append(robot)


    # =================================
    # 4. ASSIGN INITIAL TASKS
    # =================================

    assign_waiting_tasks(
        robots,
        tasks,
        warehouse,
        simulation_time=0,
    )


    # =================================
    # 5. INITIAL COORDINATED PLANNING
    # =================================

    simulation_step = 0

    reservations = replan_all_robots(
        robots,
        warehouse,
        simulation_step,
    )


    # =================================
    # 6. WINDOW DIMENSIONS
    # =================================

    warehouse_width = (
        warehouse.columns * CELL_SIZE
    )

    window_height = (
        warehouse.rows * CELL_SIZE
    )


    # Only create a window in visual mode
    if config.visual:

        window_width = (
            warehouse_width + PANEL_WIDTH
        )

        screen = pygame.display.set_mode(
            (
                window_width,
                window_height,
            )
        )

        pygame.display.set_caption(
            "AGV Warehouse Simulator"
        )

    else:
        # Headless experiment mode
        screen = None


    # =================================
    # 7. CREATE SIMULATION
    # =================================

    simulation = Simulation(
        screen=screen,
        warehouse=warehouse,
        robots=robots,
        tasks=tasks,
        reservations=reservations,
        simulation_step=simulation_step,
        warehouse_width=warehouse_width,
        config=config,
    )


    # =================================
    # 8. RUN
    # =================================

    result = simulation.run()

    pygame.quit()

    return result


if __name__ == "__main__":
    main()
import sys

import pygame

from warehouse import (
    create_default_warehouse,
    PICKUP_POSITION,
    DELIVERY_POSITION,
)
from pathfinding import astar

from renderer import (
    CELL_SIZE,
    BACKGROUND_COLOR,
    draw_warehouse,
    draw_robot,
)

from robot import Robot

from task import Task

def main() -> None:
    pygame.init()

    # ------------------------
    # Create warehouse
    # ------------------------

    warehouse = create_default_warehouse()

    start = (1, 1)

    task = Task(
        id=1,
        pickup=PICKUP_POSITION,
        delivery=DELIVERY_POSITION,
    )

    # ------------------------
    # Calculate robot route
    # ------------------------


    robot = Robot(
            robot_id=1,
            start_position=start,
        )

    
    
    path_to_pickup = astar(
        warehouse,
        start,
        task.pickup,
    )

    robot.assign_task(
        task,
        path_to_pickup,
    )
    

    # ------------------------
    # Create Pygame window
    # ------------------------

    window_width = (
        warehouse.columns * CELL_SIZE
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

    clock = pygame.time.Clock()



    running = True

    # ------------------------
    # Main simulation loop
    # ------------------------

    while running:

        # Handle events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # ------------------------
        # Update simulation
        # ------------------------

        current_time = pygame.time.get_ticks()


        robot.update(current_time)

        if (
            robot.state == "to_pickup"
            and robot.has_reached_destination()
        ):
            print("Robot reached pickup!")

            robot.carrying = True
            robot.current_task.status = "picked_up"

            path_to_delivery = astar(
                warehouse,
                robot.position,
                robot.current_task.delivery,
            )

            robot.state = "to_delivery"

            robot.set_path(
                path_to_delivery
            )


        elif (
            robot.state == "to_delivery"
            and robot.has_reached_destination()
        ):
            print("Task completed!")

            robot.current_task.status = "completed"

            robot.carrying = False
            robot.state = "idle"

            robot.current_task = None

        # ------------------------
        # Draw simulation
        # ------------------------

        screen.fill(BACKGROUND_COLOR)

        draw_warehouse(
            screen,
            warehouse,
        )

        draw_robot(
            screen,
            robot.position,
            robot.carrying,)

        
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
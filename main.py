import sys

import pygame

from warehouse import (
    create_default_warehouse,
    PICKUP_POSITIONS,
    DELIVERY_POSITIONS,
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

from dispatcher import assign_waiting_tasks

def main() -> None:
    pygame.init()

    # ------------------------
    # Create warehouse
    # ------------------------

    warehouse = create_default_warehouse()

    start = (1, 1)

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

    current_task_index = 0

    # ------------------------
    # Calculate robot route
    # ------------------------

    task = tasks[current_task_index]

    robots = [
        Robot(
            robot_id=1,
            start_position=(1, 1),
            color=(50, 120, 220),  # blue
        ),

        Robot(
            robot_id=2,
            start_position=(13, 18),
            color=(180, 80, 200),  # purple
        ),
    ]

    assign_waiting_tasks(
        robots,
        tasks,
        warehouse,
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

    MOVE_DELAY = 300
    last_move_time = pygame.time.get_ticks()

    while running:

        # ========================================
        # 1. HANDLE PYGAME EVENTS
        # ========================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False


        # ========================================
        # 2. GET CURRENT TIME
        # ========================================

        current_time = pygame.time.get_ticks()


        # ========================================
        # 3. MOVE ROBOTS
        # ========================================

        if current_time - last_move_time >= MOVE_DELAY:

            # First ask every robot:
            # "Where do you want to move next?"
            proposed_positions = {}

            for robot in robots:
                proposed_positions[robot.id] = (
                    robot.get_next_position()
                )


            # Now decide which robots are allowed to move
            for robot in robots:

                next_position = proposed_positions[robot.id]

                collision = False
                should_replan = False

                # Compare this robot with every other robot
                for other_robot in robots:

                    # Don't compare robot with itself
                    if robot.id == other_robot.id:
                        continue

                    other_next_position = (
                        proposed_positions[other_robot.id]
                    )


                    # --------------------------------
                    # Collision type 1:
                    # Both robots want the same cell
                    # --------------------------------

                    if next_position == other_next_position:

                        # Lower ID gets priority
                        if robot.id > other_robot.id:
                            collision = True
                            should_replan = True
                            break


                    # --------------------------------
                    # Collision type 2:
                    # Another robot is staying
                    # in the cell we want
                    # --------------------------------

                    if (
                        next_position == other_robot.position
                        and
                        other_next_position == other_robot.position
                    ):
                        collision = True
                        should_replan = True
                        break


                    # --------------------------------
                    # Collision type 3:
                    # Robots want to swap positions
                    # --------------------------------

                    if (
                        next_position == other_robot.position
                        and
                        other_next_position == robot.position
                    ):
                        collision = True

                        # Only the robot with the higher ID
                        # is responsible for finding another route.
                        if robot.id > other_robot.id:
                            should_replan = True

                        break


                # Move only when there is no collision
                if not collision:
                    robot.move_one_step()
                    robot.reset_wait()

                else:
                    if should_replan:
                        robot.add_wait()

                    else:
                        robot.reset_wait()

                    if should_replan and robot.wait_steps >= 3:

                        blocked_positions = {
                            other_robot.position
                            for other_robot in robots
                            if other_robot.id != robot.id
                            }

                        if robot.current_task is not None:

                            if robot.state == "to_pickup":
                                goal = robot.current_task.pickup

                            elif robot.state == "to_delivery":
                                goal = robot.current_task.delivery

                            else:
                                goal = None

                            if goal is not None:

                                new_path = astar(
                                    warehouse,
                                    robot.position,
                                    goal,
                                    blocked_positions,
                                )

                                if new_path:
                                    robot.set_path(new_path)

                                    print(
                                        f"Robot {robot.id} replanned its route."
                                    )

                        robot.reset_wait()


            # Reset movement timer
            last_move_time = current_time


        # ========================================
        # 4. CHECK ROBOT TASK STATES
        # ========================================

        for robot in robots:

            # --------------------------------
            # Robot reached pickup
            # --------------------------------

            if (
                robot.state == "to_pickup"
                and robot.has_reached_destination()
            ):
                print(
                    f"Robot {robot.id} reached pickup!"
                )

                # Robot now has the package
                robot.carrying = True

                robot.current_task.status = "picked_up"

                # Calculate route to delivery
                path_to_delivery = astar(
                    warehouse,
                    robot.position,
                    robot.current_task.delivery,
                )

                robot.state = "to_delivery"

                robot.set_path(
                    path_to_delivery
                )


            # --------------------------------
            # Robot reached delivery
            # --------------------------------

            elif (
                robot.state == "to_delivery"
                and robot.has_reached_destination()
            ):
                print(
                    f"Robot {robot.id} completed "
                    f"Task {robot.current_task.id}!"
                )

                robot.current_task.status = "completed"

                # Drop package
                robot.carrying = False

                # Robot becomes available again
                robot.state = "idle"

                robot.current_task = None

        assign_waiting_tasks(
                robots,
                tasks,
                warehouse,
            )


        # ========================================
        # 5. DRAW EVERYTHING
        # ========================================

        screen.fill(BACKGROUND_COLOR)

        draw_warehouse(
            screen,
            warehouse,
        )

        # Draw every robot
        for robot in robots:
            draw_robot(
                screen,
                robot.position,
                robot.color,
                robot.carrying,
            )

        pygame.display.flip()


        # ========================================
        # 6. LIMIT PYGAME TO 60 FPS
        # ========================================

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()